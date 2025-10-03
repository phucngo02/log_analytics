# abuseipdb_check.py
"""
AbuseIPDB check with simple in-memory TTL cache and exponential backoff.

Functions:
- check_ip(ip, max_age_days=90, threshold=50, use_cache=True)
    -> returns dict: {"score": int|None, "is_blacklisted": bool, "raw": {...}} or None if no API key.

Notes:
- Cache TTL and backoff params can be controlled via environment variables:
    ABUSEIPDB_CACHE_TTL  (seconds, default 1800 = 30min)
    ABUSEIPDB_MAX_RETRIES (default 3)
    ABUSEIPDB_BACKOFF_BASE (seconds, default 1)
"""
import os
import time
import requests

API_KEY = os.environ.get("ABUSEIPDB_KEY")
API_URL = "https://api.abuseipdb.com/api/v2/check"

# Configurable via env
CACHE_TTL = int(os.getenv("ABUSEIPDB_CACHE_TTL", str(60 * 30)))  # default 30 minutes
MAX_RETRIES = int(os.getenv("ABUSEIPDB_MAX_RETRIES", "3"))
BACKOFF_BASE = float(os.getenv("ABUSEIPDB_BACKOFF_BASE", "1.0"))

# Simple in-memory cache: ip -> {"ts": epoch_seconds, "res": result_dict}
_CACHE = {}

def _call_abuse_api(ip, max_age_days=90):
    """Low-level call to AbuseIPDB with retries/backoff. Returns the parsed dict or raises."""
    headers = {
        "Accept": "application/json",
        "Key": API_KEY
    }
    params = {"ipAddress": ip, "maxAgeInDays": max_age_days}

    backoff = BACKOFF_BASE
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            resp = requests.get(API_URL, headers=headers, params=params, timeout=6)
        except requests.RequestException as e:
            # Network error, decide whether to retry
            if attempt == MAX_RETRIES:
                raise
            time.sleep(backoff)
            backoff *= 2
            continue

        if resp.status_code == 200:
            return resp.json().get("data", {})
        elif resp.status_code == 429:
            # rate limited: sleep and retry (exponential)
            # If server provides Retry-After, prefer that.
            retry_after = None
            try:
                retry_after = int(resp.headers.get("Retry-After"))
            except Exception:
                retry_after = None

            wait = retry_after if retry_after is not None else backoff
            # Sleep then increase backoff
            time.sleep(wait)
            backoff *= 2
            # loop to retry
            continue
        else:
            # other HTTP errors -> raise to be handled by caller
            resp.raise_for_status()

    # If we exit loop without return, raise generic error
    raise RuntimeError("AbuseIPDB: max retries exceeded")

def check_ip(ip, max_age_days=90, threshold=50, use_cache=True):
    """
    Check IP on AbuseIPDB with caching and backoff.
    Returns:
      - None if API_KEY not configured (caller should handle)
      - dict: {"score": int|None, "is_blacklisted": bool, "raw": {...}} on success or structured failure
    """
    if not API_KEY:
        # No API key configured; return None so caller can fallback to local detection.
        # Keep behavior consistent with previous code.
        #print("[abuseipdb] No API key found, skipping AbuseIPDB check.")
        return None

    now = time.time()

    # Check cache
    if use_cache and ip in _CACHE:
        entry = _CACHE[ip]
        if now - entry["ts"] < CACHE_TTL:
            return entry["res"]
        else:
            # expired
            del _CACHE[ip]

    # Call API with backoff
    try:
        data = _call_abuse_api(ip, max_age_days=max_age_days)
        score = data.get("abuseConfidenceScore", 0) if isinstance(data, dict) else 0
        result = {"score": score, "is_blacklisted": score >= threshold, "raw": data}
    except Exception as e:
        # On error, return a structured dict (do not cache failure with a real score)
        result = {"score": None, "is_blacklisted": False, "error": str(e)}

    # Cache successful results (and also cache structured failures to avoid repeated failing calls).
    if use_cache:
        _CACHE[ip] = {"ts": now, "res": result}

    return result

# Utility helpers for interactive use / debugging
def cache_info():
    """Return cache summary (for debugging)."""
    return {ip: {"age_seconds": int(time.time() - v["ts"]), "score": v["res"].get("score")} for ip, v in _CACHE.items()}

def clear_cache():
    """Clear the in-memory cache."""
    _CACHE.clear()
