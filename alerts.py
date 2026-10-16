import os
import requests

# Paste your webhook URL between the quotes, or set the DISCORD_WEBHOOK environment variable
WEBHOOK_URL = os.environ.get("DISCORD_WEBHOOK", "PASTE_YOUR_WEBHOOK_URL_HERE")

DASHBOARD_URL = "http://127.0.0.1:5000"


def send_change_alert(page_name, url, old_snapshot_id, new_snapshot_id):
    """Send one Discord message about a change. Never crashes the checker."""
    if "PASTE_YOUR" in WEBHOOK_URL:
        print("[alert] No webhook set, skipping alert")
        return

    diff_link = f"{DASHBOARD_URL}/diff?old={old_snapshot_id}&new={new_snapshot_id}"
    message = (
        f"**Change detected: {page_name}**\n"
        f"Page: {url}\n"
        f"See what changed: {diff_link}"
    )
    try:
        requests.post(WEBHOOK_URL, json={"content": message}, timeout=10)
    except Exception as e:
        print(f"[alert] Failed to send: {e}")