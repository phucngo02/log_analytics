import os, time, json, sqlite3
from collections import deque, defaultdict
from datetime import datetime, timedelta
from abuseipdb_check import check_ip
from alerts import send_slack_alert, send_email_alert
from dotenv import load_dotenv

# --- Load env ---
load_dotenv()

LOG_FILE = "logs/logs.txt"
DB_FILE = os.getenv("DB_PATH", "db/security_logs.db")

# Detection params (configurable via .env)
FAIL_THRESHOLD = int(os.getenv("ALERT_THRESHOLD", 5))      # số lần FAIL
WINDOW_MINUTES = int(os.getenv("ALERT_WINDOW_MINUTES", 5)) # thời gian xét (phút)

# In-memory: ip -> deque(timestamp FAIL)
ip_fail_windows = defaultdict(deque)

# --- Prepare DB ---
os.makedirs("db", exist_ok=True)
conn = sqlite3.connect(DB_FILE, check_same_thread=False)
c = conn.cursor()
c.execute("""
CREATE TABLE IF NOT EXISTS logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ts TEXT,
    username TEXT,
    ip TEXT,
    status TEXT,
    service TEXT,
    level TEXT
)
""")
c.execute("""
CREATE TABLE IF NOT EXISTS alerts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ts TEXT,
    ip TEXT,
    reason TEXT,
    abuse_score INTEGER
)
""")
conn.commit()

# --- DB helper ---
def insert_log(ts, user, ip, status, service, level):
    c.execute("""
        INSERT INTO logs (ts, username, ip, status, service, level)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (ts, user, ip, status, service, level))
    conn.commit()

def record_alert(ip, reason, score=None):
    ts = datetime.utcnow().isoformat() + "Z"
    c.execute("INSERT INTO alerts (ts, ip, reason, abuse_score) VALUES (?,?,?,?)",
              (ts, ip, reason, score))
    conn.commit()
    print(f"[ALERT][DB] Stored alert for {ip} — {reason} (score={score})")

# --- Detection ---
def check_ip_window(ip):
    """Kiểm tra số lần FAIL trong cửa sổ thời gian, nếu vượt ngưỡng -> alert"""
    now = datetime.utcnow()
    window_start = now - timedelta(minutes=WINDOW_MINUTES)
    dq = ip_fail_windows[ip]

    # loại bỏ fail cũ ngoài window
    while dq and dq[0] < window_start:
        dq.popleft()

    # nếu vượt ngưỡng thì alert
    if len(dq) >= FAIL_THRESHOLD:
        abuse = check_ip(ip, threshold=50)
        score = abuse.get("score") if abuse else None
        reason = f"{len(dq)} failed logins within {WINDOW_MINUTES} minutes"
        alert_text = f"🔴 Potential brute-force from IP {ip} — {reason}. AbuseIPDB score: {score}"

        print(f"[ALERT] {alert_text}")

        # Slack
        if os.environ.get("SLACK_WEBHOOK_URL"):
            send_slack_alert(alert_text)
        else:
            print("[warn] SLACK_WEBHOOK_URL not set, skipping Slack alert.")

        # Email
        if os.environ.get("ALERT_NOTIFY_EMAIL"):
            send_email_alert(
                subject=f"[Security Alert] Brute-force {ip}",
                body=alert_text,
                to_addrs=[os.environ["ALERT_NOTIFY_EMAIL"]]
            )
        else:
            print("[warn] ALERT_NOTIFY_EMAIL not set, skipping Email alert.")

        record_alert(ip, reason, score)

        # giữ lại 1 log để tiếp tục theo dõi
        while len(dq) > 1:
            dq.popleft()

# --- Process line ---
def process_line(line):
    try:
        log = json.loads(line.strip())
        ts = log.get("ts")
        user = log.get("user")
        ip = log.get("ip")
        status = log.get("status", "").upper()
        service = log.get("service")
        level = log.get("level")

        print(f"[processor] {ts} | {user}@{ip} | {status} | {service} | {level}")

        # Ghi DB
        insert_log(ts, user, ip, status, service, level)

        # Nếu FAIL -> kiểm tra brute force
        if status == "FAIL":
            try:
                if ts.endswith("Z"):
                    dt = datetime.fromisoformat(ts.replace("Z", "+00:00"))
                else:
                    dt = datetime.fromisoformat(ts)
            except Exception:
                dt = datetime.utcnow()

            ip_fail_windows[ip].append(dt)
            check_ip_window(ip)

    except Exception as e:
        print("[processor] Parse error:", e, "Line:", line)

# --- Tail loop ---
def tail_loop():
    with open(LOG_FILE, "r") as f:
        f.seek(0, os.SEEK_END)
        while True:
            where = f.tell()
            line = f.readline()
            if not line:
                time.sleep(1)
                f.seek(where)
            else:
                process_line(line)

if __name__ == "__main__":
    print("[main] Starting tail loop. LOG_FILE:", LOG_FILE)
    print(f"[config] FAIL_THRESHOLD={FAIL_THRESHOLD}, WINDOW_MINUTES={WINDOW_MINUTES}")
    tail_loop()
