import time
from playwright.sync_api import sync_playwright
import database
import cleaner
import alerts

# If a page contains any of these phrases, we treat it as a block/CAPTCHA page
BLOCK_WORDS = [
    "verify you are human",
    "captcha",
    "are you a robot",
    "unusual traffic",
    "access denied",
    "checking your browser",
]

MAX_ATTEMPTS = 3


def fetch_page(url):
    """Visit the page, return (text, screenshot_path, http_status_code)."""
    screenshot_path = f"screenshots/{int(time.time())}.png"
    with sync_playwright() as p:
        browser = p.chromium.launch()
        try:
            page = browser.new_page()
            response = page.goto(url, timeout=30000)
            status_code = response.status if response else None
            text = page.inner_text("body")
            page.screenshot(path=screenshot_path, full_page=True)
        finally:
            browser.close()  # always close, even if something failed
    return text, screenshot_path, status_code


def looks_blocked(text, status_code):
    """Is this a CAPTCHA / block page instead of the real page?"""
    if status_code in (403, 429):
        return True
    lowered = text.lower()
    return any(word in lowered for word in BLOCK_WORDS)


def check_page(page_id, url):
    """Fetch a page (with retries) and save a snapshot only if content changed."""
    last_error = None

    for attempt in range(1, MAX_ATTEMPTS + 1):
        try:
            text, screenshot_path, status_code = fetch_page(url)
        except Exception as e:
            # page failed to load at all (timeout, site down, bad URL)
            last_error = e
            time.sleep(2 * attempt)
            continue

        # CAPTCHA / block page: don't retry, don't save
        if looks_blocked(text, status_code):
            database.update_status(page_id, "blocked")
            return "blocked"

        # HTTP 404 / 500 etc.: treat as error and retry
        if status_code is not None and status_code >= 400:
            last_error = Exception(f"HTTP {status_code}")
            time.sleep(2 * attempt)
            continue

        # Good page: clean the noise, then compare fingerprints
        page_row = database.get_page(page_id)
        sensitivity = page_row["sensitivity"] if page_row else "medium"
        clean = cleaner.clean_text(text, sensitivity)

        new_hash = database.make_hash(clean)
        old_hash = database.get_latest_hash(page_id)

        if new_hash == old_hash:
            database.update_status(page_id, "OK")
            return "no change"

        previous = database.get_snapshots(page_id)
        previous_id = previous[0]["id"] if previous else None

        new_id = database.save_snapshot(page_id, clean, new_hash, screenshot_path)
        database.update_status(page_id, "OK")

        if previous_id is None:
            return "first snapshot"   # first version: nothing to compare, no alert

        alerts.send_change_alert(page_row["name"], url, previous_id, new_id)
        return "CHANGED"

    # All attempts failed
    database.update_status(page_id, "error")
    return f"error ({last_error})"