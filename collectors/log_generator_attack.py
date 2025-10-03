#!/usr/bin/env python3
"""
log_generator_alert.py

Generates JSON log lines and triggers alerts on FAILs.

Usage examples:
    python log_generator_alert.py --attack-ip 1.2.3.4 --attack-count 6 --one-shot
    python log_generator_alert.py --noise-rate 0.2 --attack-every 30
"""
import json, time, random, argparse, os, sqlite3
from datetime import datetime
from alerts import send_slack_alert, send_email_alert

# --- Config ---
OUT = "logs/logs.txt"
DB_FILE = os.getenv("DB_PATH", "db/security_logs.db")
os.makedirs(os.path.dirname(OUT), exist_ok=True)

USERS = ["alice","bob","charlie","david","eve"]
SERVICES = ["auth","ssh","vpn","web"]
LEVELS = ["INFO","WARN","ERROR"]

# --- Helpers ---
def write_line(d):
    """Write JSON log to file"""
    with open(OUT, "a") as f:
        f.write(json.dumps(d, separators=(",",":")) + "\n")
        f.flush()

def trigger_alert(d):
    """If FAIL, insert into DB and send alerts"""
    if d["status"] != "FAIL":
        return

    # --- Insert into DB ---
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("""
        INSERT INTO logs (ts, username, ip, status, service, level)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (d["ts"], d["user"], d["ip"], d["status"], d["service"], d["level"]))
    conn.commit()
    conn.close()

    # --- Prepare alert message ---
    msg = f"[ALERT] FAIL detected!\nUser: {d['user']}\nIP: {d['ip']}\nService: {d['service']}\nLevel: {d['level']}\nTime: {d['ts']}"

    # --- Send Slack alert ---
    try:
        send_slack_alert(msg)
    except Exception as e:
        print("[alert] Slack failed:", e)

    # --- Send Email alert ---
    try:
        to_addrs = os.environ.get("ALERT_EMAIL_TO", "youremail@example.com").split(",")
        subject = "[SECURITY ALERT] FAIL detected"
        send_email_alert(body=msg, subject=subject, to_addrs=to_addrs)
    except Exception as e:
        print("[alert] Email failed:", e)

def gen_noise_line():
    ts = datetime.utcnow().replace(microsecond=0).isoformat() + "Z"
    return {
        "ts": ts,
        "user": random.choice(USERS),
        "ip": f"10.{random.randint(0,255)}.{random.randint(0,255)}.{random.randint(1,254)}",
        "status": random.choices(["OK","FAIL"], weights=[0.9,0.1])[0],
        "service": random.choice(SERVICES),
        "level": random.choice(LEVELS)
    }

def gen_attack_line(ip, user="attacker"):
    ts = datetime.utcnow().replace(microsecond=0).isoformat() + "Z"
    return {
        "ts": ts,
        "user": user,
        "ip": ip,
        "status": "FAIL",
        "service": "auth",
        "level": "ERROR"
    }

# --- Main ---
def main():
    p = argparse.ArgumentParser()
    p.add_argument("--noise-rate", type=float, default=1.0)
    p.add_argument("--attack-ip", type=str, default=None)
    p.add_argument("--attack-count", type=int, default=6)
    p.add_argument("--attack-interval", type=float, default=0.5)
    p.add_argument("--attack-every", type=int, default=60)
    p.add_argument("--one-shot", action="store_true")
    args = p.parse_args()

    print("[generator] Writing to", OUT)
    next_attack = time.time() + args.attack_every if args.attack_every > 0 else None

    try:
        # --- One-shot attack ---
        if args.one_shot:
            if not args.attack_ip:
                print("one-shot requires --attack-ip")
                return
            for i in range(args.attack_count):
                line = gen_attack_line(args.attack_ip)
                write_line(line)
                trigger_alert(line)
                print("[generator] attack", i+1, "->", args.attack_ip)
                time.sleep(args.attack_interval)
            print("[generator] one-shot attack done.")
            return

        # --- Continuous run ---
        while True:
            # Generate noise
            noise = gen_noise_line()
            write_line(noise)
            trigger_alert(noise)
            print("[generator] noise ->", noise["ip"], noise["status"])

            # Periodic attack burst
            if args.attack_ip and args.attack_every > 0 and time.time() >= next_attack:
                print("[generator] starting attack burst against", args.attack_ip)
                for i in range(args.attack_count):
                    attack_line = gen_attack_line(args.attack_ip)
                    write_line(attack_line)
                    trigger_alert(attack_line)
                    print("[generator] attack ->", attack_line["ip"], attack_line["ts"])
                    time.sleep(args.attack_interval)
                next_attack = time.time() + args.attack_every

            time.sleep(args.noise_rate)

    except KeyboardInterrupt:
        print("\n[generator] stopped by user")

if __name__ == "__main__":
    main()
