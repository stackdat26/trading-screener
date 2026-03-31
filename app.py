from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
import threading
import logging
import time
from datetime import datetime
from screener import run_screener, ALL_ASSETS

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

_cache = {
    "results": [],
    "last_updated": None,
    "is_scanning": False,
    "scan_progress": {"current": 0, "total": 0, "category": ""},
    "error": None
}
_cache_lock = threading.Lock()


def background_scan(categories=None):
    """Run screener in background and cache results."""
    with _cache_lock:
        if _cache["is_scanning"]:
            return
        _cache["is_scanning"] = True
        _cache["error"] = None

    try:
        logger.info("Starting background scan...")
        results = run_screener(categories=categories, max_per_category=50)
        with _cache_lock:
            _cache["results"] = results
            _cache["last_updated"] = datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')
            _cache["is_scanning"] = False
        logger.info(f"Scan complete. Found {len(results)} liquidity sweeps.")
    except Exception as e:
        logger.error(f"Scan error: {e}")
        with _cache_lock:
            _cache["is_scanning"] = False
            _cache["error"] = str(e)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/api/scan', methods=['POST'])
def start_scan():
    data = request.get_json() or {}
    categories = data.get('categories', None)

    with _cache_lock:
        if _cache["is_scanning"]:
            return jsonify({"status": "already_scanning", "message": "Scan already in progress"}), 200

    thread = threading.Thread(target=background_scan, args=(categories,), daemon=True)
    thread.start()
    return jsonify({"status": "started", "message": "Scan started"}), 200


@app.route('/api/results')
def get_results():
    category = request.args.get('category', 'all')
    sweep_type = request.args.get('type', 'all')
    min_strength = float(request.args.get('min_strength', 0))
    sort_by = request.args.get('sort_by', 'strength')

    with _cache_lock:
        results = list(_cache["results"])
        last_updated = _cache["last_updated"]
        is_scanning = _cache["is_scanning"]
        error = _cache["error"]

    if category != 'all':
        results = [r for r in results if r['category'] == category]
    if sweep_type != 'all':
        results = [r for r in results if r['sweep_type'] == sweep_type]
    results = [r for r in results if r['strength'] >= min_strength]

    if sort_by == 'strength':
        results.sort(key=lambda x: x['strength'], reverse=True)
    elif sort_by == 'volume':
        results.sort(key=lambda x: x['volume_surge'] or 0, reverse=True)
    elif sort_by == 'ticker':
        results.sort(key=lambda x: x['ticker'])

    return jsonify({
        "results": results,
        "last_updated": last_updated,
        "is_scanning": is_scanning,
        "total_found": len(results),
        "error": error
    })


@app.route('/api/status')
def get_status():
    with _cache_lock:
        return jsonify({
            "is_scanning": _cache["is_scanning"],
            "last_updated": _cache["last_updated"],
            "total_results": len(_cache["results"]),
            "error": _cache["error"],
            "asset_counts": {k: len(v) for k, v in ALL_ASSETS.items()},
            "total_assets": sum(len(v) for v in ALL_ASSETS.values())
        })


@app.route('/api/categories')
def get_categories():
    return jsonify({"categories": list(ALL_ASSETS.keys())})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
