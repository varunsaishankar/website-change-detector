# Website Change Detector

A tool that watches web pages and sends an alert when something meaningful
changes. It ignores things that change on every visit, like clocks and visitor counters.

**Built by:** Varun Sai Shankar, B.Tech CSE Core, 1st year
**For:** VinnovateIT Round 1

## What it does
- Add a page with a name, a URL, a check interval (15 min to 24 hours) and a sensitivity (High, Medium or Low)
- Opens pages in a headless browser (Playwright), so pages that load content with JavaScript also work
- Checks pages automatically when their interval has passed
- Saves the page text and a screenshot, but stores a new version only when the content actually changes
- Removes noise (times, dates, "5 minutes ago", visitor counters, random tokens) before comparing
- Keeps a version history for each page, with a side-by-side text diff of any two versions
- Sends a Discord alert with a link to the diff
- Dashboard with last checked, last changed and status (OK, error, blocked)

## Tech used
Python, Flask, Playwright, SQLite, APScheduler, difflib, requests

## How to run
1. Install Python 3.11 or newer
2. `python -m venv venv` and activate it (`venv\Scripts\activate` on Windows)
3. `pip install -r requirements.txt`
4. `playwright install chromium`
5. Optional: set the `DISCORD_WEBHOOK` environment variable to your Discord webhook URL to get alerts
6. `python app.py` and open http://127.0.0.1:5000

## How it works
1. Every 60 seconds the scheduler checks which pages are due.
2. Playwright opens the page and saves its text and a screenshot.
3. The text is cleaned based on the page's sensitivity setting.
4. The cleaned text is turned into a hash (a short fingerprint) and compared with the last saved one.
5. If the hash is different, a new version is saved and one alert is sent. If it is the same, only "last checked" is updated.

## Answers to the design questions

**1. Is a site outage or CAPTCHA a change?**
No. If a page fails to load, it is retried up to 3 times and then marked "error".
If the site returns 403/429 or shows CAPTCHA-style text, it is marked "blocked"
and not retried. In both cases nothing is saved and no alert is sent.

**2. If 200 users watch the same URL, is it fetched 200 times?**
Right now the app is single-user, so each URL is fetched once per interval.
For many users, the plan would be to store each URL only once, fetch it once per
interval, and share the result with everyone watching it. I have not built this part yet.

**3. How do we avoid endless alerts on pages that differ on every load?**
Noise like times, dates and counters is removed before the hash is made, and the
sensitivity setting controls how much is removed. An alert is sent only when a new
version is saved, so unchanged content never alerts twice. I tested this with a page
that shows a live clock and a random counter: Medium stays quiet, High reacts.

**4. How do we avoid hammering a site?**
The minimum interval is 15 minutes, pages are checked only when they are due,
retries wait longer each time, and blocked pages are not retried.
A per-domain delay and a robots.txt check are not built yet.

## Testing
- `test_clean.py` checks that two noisy versions of the same page clean to the same text.
- I made a small local test site (`testsite/`) with a noisy page, a CAPTCHA-like page
  and a page I edit by hand, to test change detection, noise filtering, the error and
  blocked statuses, and Discord alerts.

## Limitations
- Block detection uses keyword matching, so it can wrongly flag a normal page.
- Not built: email alerts, region picker, screenshot diff highlighting, daily digest.
- Two checks of the same page at the same moment could save a duplicate version.
- Diff links only work on the computer running the app.