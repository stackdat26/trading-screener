import os
import math
import json
import logging
import threading
from flask import Flask, render_template, request, Response
from flask_cors import CORS
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

app = Flask(__name__,
            template_folder=os.path.join(os.path.dirname(__file__), "templates"),
            static_folder=os.path.join(os.path.dirname(__file__), "static"))
CORS(app)

_state = {
    "signals": [],
    "watchlist": [],
    "last_scan": None,
    "next_scan": None,
    "is_scanning": False,
    "scan_count": 0,
    "error": None,
}


def _clean(obj):
    """Recursively replace NaN/Inf floats with None."""
    if isinstance(obj, float):
        if math.isnan(obj) or math.isinf(obj):
            return None
        return obj
    if isinstance(obj, dict):
        return {k: _clean(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [_clean(v) for v in obj]
    return obj


def safe_json(data, status=200):
    """Return a JSON Response with NaN/Inf cleaned."""
    body = json.dumps(_clean(data))
    return Response(body, status=status, mimetype="application/json")


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/signals")
def api_signals():
    asset_class = request.args.get("class", "All")
    direction = request.args.get("direction", "All")
    try:
        min_conf = float(request.args.get("min_conf", 60))
    except ValueError:
        min_conf = 60.0

    signals = list(_state["signals"])

    if asset_class and asset_class != "All":
        signals = [s for s in signals if s.get("asset_class") == asset_class]
    if direction and direction != "All":
        signals = [s for s in signals if s.get("action") == direction]
    signals = [s for s in signals if (s.get("confidence") or 0) >= min_conf]

    all_sigs = list(_state["signals"])
    buy_count = sum(1 for s in all_sigs if s.get("action") == "BUY")
    sell_count = sum(1 for s in all_sigs if s.get("action") == "SELL")
    high_conf = sum(1 for s in all_sigs if (s.get("confidence") or 0) >= 80)

    return safe_json({
        "signals": signals,
        "total_scanned": _state.get("scan_count", 0),
        "buy_count": buy_count,
        "sell_count": sell_count,
        "high_conf": high_conf,
        "last_scan": _state["last_scan"],
        "next_scan": _state["next_scan"],
        "is_scanning": _state["is_scanning"],
        "error": _state["error"],
    })


@app.route("/api/watchlist")
def api_watchlist():
    return safe_json({
        "watchlist": _state["watchlist"],
        "last_scan": _state["last_scan"],
    })


@app.route("/api/status")
def api_status():
    return safe_json({
        "is_scanning": _state["is_scanning"],
        "last_scan": _state["last_scan"],
        "next_scan": _state["next_scan"],
        "total_signals": len(_state["signals"]),
        "error": _state["error"],
    })


@app.route("/healthz")
def healthz():
    return safe_json({"status": "ok"})


@app.route("/api/scan", methods=["POST"])
def api_scan():
    from core.screener_engine import run_full_scan
    from config.settings import SCAN_INTERVAL_MINUTES, ASSET_CLASSES

    if _state["is_scanning"]:
        return safe_json({"status": "already_scanning"})

    req_data = request.get_json(silent=True) or {}
    classes = req_data.get("classes", None)

    def do_scan():
        _state["is_scanning"] = True
        _state["error"] = None
        try:
            results = run_full_scan(classes)
            _state["signals"] = results
            _state["scan_count"] = sum(len(v) for v in ASSET_CLASSES.values())
            _state["last_scan"] = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
            nxt = datetime.utcnow() + timedelta(minutes=SCAN_INTERVAL_MINUTES)
            _state["next_scan"] = nxt.strftime("%H:%M UTC")
        except Exception as e:
            logger.error(f"Scan failed: {e}")
            _state["error"] = str(e)
        finally:
            _state["is_scanning"] = False

    t = threading.Thread(target=do_scan, daemon=True)
    t.start()
    return safe_json({"status": "started"})
