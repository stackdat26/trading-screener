import logging
import numpy as np
from config.settings import (
    BASE_WEIGHTS, MIN_SCORE, SIGNAL_DIFF,
    STOP_LOSS_ATR_MULT, TAKE_PROFIT_FIB_LEVEL, TAKE_PROFIT_ATR_MULT,
    ASSET_CLASSES, SWEEP_THRESHOLDS, SWEEP_THRESHOLD_PCT
)
from core.data_feed import get_candles
from core.indicators import compute_all_indicators, price_near_level
from core.sweep_detector import get_latest_sweep
from core.markov import run_markov

logger = logging.getLogger(__name__)


def detect_market_context(ema20, ema50, atr_daily, avg_atr_daily):
    """
    CRISIS: current ATR > average ATR * 2.0
    TRENDING: abs(EMA20 - EMA50) / EMA50 > 2%
    NORMAL: everything else
    """
    if atr_daily and avg_atr_daily and avg_atr_daily > 0:
        if atr_daily > avg_atr_daily * 2.0:
            return "CRISIS"

    if ema20 and ema50 and ema50 > 0:
        if abs(ema20 - ema50) / ema50 > 0.02:
            return "TRENDING"

    return "NORMAL"


def apply_context_weights(weights: dict, context: str) -> dict:
    """Adjust weights based on market context."""
    w = dict(weights)
    if context == "CRISIS":
        return {k: v * 0.70 for k, v in w.items()}
    elif context == "TRENDING":
        w["sweep_confirmed"] = w["sweep_confirmed"] * 1.20
        w["ema20"] = w["ema20"] * 1.20
        return w
    return w


def score_asset(symbol: str, asset_class: str) -> dict | None:
    """
    Fetch data, compute indicators, detect sweep, score asset.
    Returns signal dict or None.
    """
    try:
        df_15m, df_daily = get_candles(symbol, asset_class)

        if df_15m is None or len(df_15m) < 20:
            return None

        indicators = compute_all_indicators(df_15m, df_daily)
        if not indicators:
            return None

        rsi = indicators.get("rsi")
        ema20 = indicators.get("ema20")
        ema50 = indicators.get("ema50")
        atr_daily = indicators.get("atr_daily")
        avg_atr_daily = indicators.get("avg_atr_daily")
        pivots = indicators.get("pivots")
        fib = indicators.get("fibonacci")
        monthly_zones = indicators.get("monthly_zones", [])
        vwap = indicators.get("vwap")
        rsi_series = indicators.get("rsi_series")
        atr_15m_series = indicators.get("atr_15m_series")

        current_price = float(df_15m["Close"].iloc[-1])
        effective_atr = atr_daily if atr_daily else indicators.get("atr_15m")

        threshold_pct = SWEEP_THRESHOLDS.get(asset_class, SWEEP_THRESHOLD_PCT)
        sweep = get_latest_sweep(df_15m, effective_atr, threshold_pct=threshold_pct)

        context = detect_market_context(ema20, ema50, atr_daily, avg_atr_daily)
        weights = apply_context_weights(BASE_WEIGHTS, context)

        markov_result = run_markov(df_15m, rsi_series, atr_15m_series, ema20)
        markov_state = markov_result.get("current_state", "SIDEWAYS")
        markov_boost = markov_result.get("confidence_boost", 1.0)

        buy_score = 0.0
        sell_score = 0.0

        if sweep and sweep["confirmed"]:
            if sweep["direction"] == "BUY":
                buy_score += weights["sweep_confirmed"]
                buy_score += weights["confirmation_candle"]
            else:
                sell_score += weights["sweep_confirmed"]
                sell_score += weights["confirmation_candle"]
        elif sweep and not sweep["confirmed"]:
            if sweep["direction"] == "BUY":
                buy_score += weights["sweep_confirmed"] * 0.5
            else:
                sell_score += weights["sweep_confirmed"] * 0.5

        if rsi is not None:
            if rsi < 30:
                buy_score += weights["rsi"]
            elif rsi > 70:
                sell_score += weights["rsi"]

        if ema20 is not None:
            if current_price > ema20:
                buy_score += weights["ema20"]
            else:
                sell_score += weights["ema20"]

        if pivots:
            pp = pivots["pp"]
            r1, r2 = pivots["r1"], pivots["r2"]
            s1, s2 = pivots["s1"], pivots["s2"]
            tol = 0.5
            if price_near_level(current_price, s1, tol) or price_near_level(current_price, s2, tol):
                buy_score += weights["pivot"]
            elif price_near_level(current_price, r1, tol) or price_near_level(current_price, r2, tol):
                sell_score += weights["pivot"]

        if fib:
            for lvl_val in fib["retracements"].values():
                if price_near_level(current_price, lvl_val, 0.5):
                    buy_score += weights["fibonacci"]
                    break
            for lvl_val in fib["extensions"].values():
                if price_near_level(current_price, lvl_val, 0.5):
                    sell_score += weights["fibonacci"]
                    break

        for zone in monthly_zones:
            if zone and price_near_level(current_price, zone, 1.0):
                buy_score += weights["monthly_demand"]
                break

        buy_score = min(buy_score * markov_boost, 200)
        sell_score = min(sell_score * markov_boost, 200)

        max_score = max(buy_score, sell_score)
        if max_score < MIN_SCORE:
            return None

        if buy_score >= sell_score + SIGNAL_DIFF:
            action = "BUY"
            score = round(buy_score, 1)
        elif sell_score >= buy_score + SIGNAL_DIFF:
            action = "SELL"
            score = round(sell_score, 1)
        else:
            return None

        max_one_side = sum(BASE_WEIGHTS.values())
        confidence = round(min(score / max(max_one_side, 1) * 100, 100), 1)

        stop_loss = None
        take_profit = None
        if effective_atr:
            if action == "BUY":
                stop_loss = round(current_price - effective_atr * STOP_LOSS_ATR_MULT, 4)
            else:
                stop_loss = round(current_price + effective_atr * STOP_LOSS_ATR_MULT, 4)

        if fib and effective_atr:
            ext_lvl = fib["extensions"].get(TAKE_PROFIT_FIB_LEVEL)
            if ext_lvl and ext_lvl > 0:
                take_profit = round(ext_lvl, 4)
            else:
                if action == "BUY":
                    take_profit = round(current_price + effective_atr * TAKE_PROFIT_ATR_MULT, 4)
                else:
                    take_profit = round(current_price - effective_atr * TAKE_PROFIT_ATR_MULT, 4)

        sweep_pct = sweep["sweep_pct"] if sweep else 0.0

        def safe(v, digits=4):
            import math
            if v is None:
                return None
            try:
                if math.isnan(v) or math.isinf(v):
                    return None
                return round(float(v), digits)
            except Exception:
                return None

        return {
            "symbol": symbol,
            "asset_class": asset_class,
            "action": action,
            "score": safe(score, 1),
            "confidence": safe(confidence, 1),
            "rsi": safe(rsi, 1),
            "sweep_pct": safe(sweep_pct, 2),
            "entry": safe(current_price, 4),
            "stop": safe(stop_loss, 4),
            "target": safe(take_profit, 4),
            "market_context": context,
            "markov_state": markov_state,
            "markov_boost": safe(markov_boost, 2),
            "ema20": safe(ema20, 4),
            "vwap": safe(vwap, 4),
            "sweep_confirmed": sweep["confirmed"] if sweep else False,
            "sweep_direction": sweep["direction"] if sweep else None,
        }

    except Exception as e:
        logger.error(f"Error scoring {symbol}: {e}")
        return None


def run_full_scan(asset_classes=None):
    """Scan all assets and return scored signals above threshold."""
    if asset_classes is None:
        asset_classes = list(ASSET_CLASSES.keys())

    signals = []
    for cls in asset_classes:
        symbols = ASSET_CLASSES.get(cls, [])
        logger.info(f"Scanning {len(symbols)} {cls} assets...")
        for sym in symbols:
            result = score_asset(sym, cls)
            if result:
                signals.append(result)

    signals.sort(key=lambda x: x["score"], reverse=True)
    return signals
