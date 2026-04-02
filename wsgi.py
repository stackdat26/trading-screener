import threading
import logging

logger = logging.getLogger(__name__)

from main import do_scan, scheduler_loop
from dashboard.app import app

_started = False


def _start_background():
    global _started
    if _started:
        return
    _started = True

    init_thread = threading.Thread(target=do_scan, daemon=True)
    init_thread.start()

    sched_thread = threading.Thread(target=scheduler_loop, daemon=True)
    sched_thread.start()

    logger.info("Background scan + scheduler threads started via wsgi.py")


_start_background()
