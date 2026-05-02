#!/usr/bin/env python3
import os
import requests
from pathlib import Path
from datetime import datetime, timezone

TIMEOUT = float(os.getenv("CHECK_TIMEOUT", "10"))
URLS_FILE = os.getenv("URLS_FILE", "urls.txt")
BASE_DIR = Path(__file__).resolve().parent
URLS_PATH = (BASE_DIR / URLS_FILE).resolve() if not Path(URLS_FILE).is_absolute() else Path(URLS_FILE)

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
CHAT_ID = os.getenv("CHAT_ID", "").strip()


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def load_urls(path: Path):
    if not path.exists():
        raise FileNotFoundError(f"urls file not found: {path}")
    urls = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        urls.append(line)
    return urls


def send_telegram_alert(text: str):
    if not TELEGRAM_BOT_TOKEN or not CHAT_ID:
        print(f"[WARN] {now_iso()} telegram is not configured, skip alert")
        return False

    api_url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": text, "disable_web_page_preview": True}
    try:
        resp = requests.post(api_url, json=payload, timeout=10)
        ok = resp.status_code == 200 and resp.json().get("ok")
        print(f"[ALERT] {now_iso()} telegram_send status={resp.status_code} ok={ok}")
        return bool(ok)
    except Exception as exc:
        print(f"[ERROR] {now_iso()} telegram_send_failed error={exc}")
        return False


def check_url(url: str):
    try:
        r = requests.get(url, timeout=TIMEOUT)
        if 500 <= r.status_code <= 599:
            return False, f"http_{r.status_code}"
        return True, f"http_{r.status_code}"
    except requests.Timeout:
        return False, "timeout"
    except Exception as exc:
        return False, f"error={exc}"


def run():
    urls = load_urls(URLS_PATH)
    print(f"[INFO] {now_iso()} run_started urls_count={len(urls)} urls_file={URLS_PATH}")

    failed = 0
    for url in urls:
        ok, status = check_url(url)
        level = "OK" if ok else "FAIL"
        print(f"[{level}] {now_iso()} url={url} status={status}")
        if not ok:
            failed += 1
            send_telegram_alert(
                "🚨 Health check failed\n"
                f"service={url}\n"
                f"status={status}\n"
                f"checked_at={now_iso()}"
            )

    print(f"[INFO] {now_iso()} run_finished failed={failed} total={len(urls)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(run())
