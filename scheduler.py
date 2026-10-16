from datetime import datetime, timedelta
from apscheduler.schedulers.background import BackgroundScheduler
import database
import checker


def run_due_checks():
    """Check every page whose interval has passed."""
    now = datetime.now()
    for p in database.get_all_pages():
        last = p["last_checked"]
        if last is not None:
            due_time = datetime.fromisoformat(last) + timedelta(minutes=p["interval_minutes"])
            if now < due_time:
                continue  # not due yet, skip

        try:
            result = checker.check_page(p["id"], p["url"])
            print(f"[auto] {p['name']}: {result}")
        except Exception as e:
            database.update_status(p["id"], "error")
            print(f"[auto] {p['name']}: error ({e})")


def start_scheduler():
    scheduler = BackgroundScheduler()
    # wake up every 60 seconds; max_instances=1 stops overlapping runs
    scheduler.add_job(run_due_checks, "interval", seconds=60, max_instances=1)
    scheduler.start()
    return scheduler