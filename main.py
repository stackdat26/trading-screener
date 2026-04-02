import logging
import threading
import schedule
import time
from datetime import datetime, timedelta
from dashboard.app import app, _state
from core.screener_engine import run_full_scan
from config.settings import (
    SCAN_INTERVAL_MINUTES,
    MORNING_WATCHLIST_HOUR_UTC,
    MORNING_WATCHLIST_TOP_N,
    ASSET_CLASSES
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s — %(message)s"
)
logger = logging.getLogger(__name__)


def do_scan():
    """Run full scan and update state."""
    if _state["is_scanning"]:
        logger.info("Scan already in progress, skipping.")
        return

    _state["is_scanning"] = True
    _state["error"] = None
    logger.info("Starting scheduled scan...")

    try:
        results = run_full_scan()
        _state["signals"] = results
        _state["scan_count"] = sum(len(v) for v in ASSET_CLASSES.values())
        _state["last_scan"] = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
        nxt = datetime.utcnow() + timedelta(minutes=SCAN_INTERVAL_MINUTES)
        _state["next_scan"] = nxt.strftime("%H:%M UTC")
        logger.info(f"Scan complete. {len(results)} signals found.")
    except Exception as e:
        logger.error(f"Scan failed: {e}")
        _state["error"] = str(e)
    finally:
        _state["is_scanning"] = False


def do_morning_watchlist():
    """Run morning watchlist scan at 07:00 UTC."""
    logger.info("Running morning watchlist scan...")
    do_scan()
    top = sorted(_state["signals"], key=lambda x: x["score"], reverse=True)[:MORNING_WATCHLIST_TOP_N]
    _state["watchlist"] = top
    logger.info(f"Morning watchlist ready: {len(top)} assets.")


def scheduler_loop():
    """Background scheduler thread."""
    schedule.every(SCAN_INTERVAL_MINUTES).minutes.do(do_scan)
    schedule.every().day.at(f"{MORNING_WATCHLIST_HOUR_UTC:02d}:00").do(do_morning_watchlist)

    logger.info(
        f"Scheduler started: scan every {SCAN_INTERVAL_MINUTES}min, "
        f"morning watchlist at {MORNING_WATCHLIST_HOUR_UTC:02d}:00 UTC"
    )

    while True:
        schedule.run_pending()
        time.sleep(30)


if __name__ == "__main__":
    import os

    init_thread = threading.Thread(target=do_scan, daemon=True)
    init_thread.start()

    sched_thread = threading.Thread(target=scheduler_loop, daemon=True)
    sched_thread.start()

    port = int(os.environ.get("PORT", 5000))
    logger.info(f"Starting Flask server on 0.0.0.0:{port}")
    app.run(host="0.0.0.0", port=port, debug=False, use_reloader=False)
