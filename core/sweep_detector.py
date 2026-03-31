import pandas as pd
import logging

logger = logging.getLogger(__name__)

SWEEP_THRESHOLD_PCT = 20.0


def detect_sweeps(df_15m: pd.DataFrame, daily_atr: float) -> list:
    """
    Detect all liquidity sweeps in the 15m candle data.

    sweep_percent = ((candle_high - candle_low) / daily_ATR) * 100
    Flag as sweep if sweep_percent > 20%
    Bullish confirmed: candle bullish AND next candle closes above sweep candle high
    Bearish confirmed: candle bearish AND next candle closes below sweep candle low

    Returns list of sweep dicts, most recent last.
    """
    if df_15m is None or len(df_15m) < 3 or not daily_atr or daily_atr == 0:
        return []

    sweeps = []
    candles = df_15m.reset_index(drop=True)

    for i in range(len(candles) - 1):
        candle = candles.iloc[i]
        next_candle = candles.iloc[i + 1]

        candle_range = candle["High"] - candle["Low"]
        if candle_range <= 0:
            continue

        sweep_pct = (candle_range / daily_atr) * 100

        if sweep_pct <= SWEEP_THRESHOLD_PCT:
            continue

        is_bullish_candle = candle["Close"] > candle["Open"]
        is_bearish_candle = candle["Close"] < candle["Open"]

        direction = None
        confirmed = False

        if is_bullish_candle and next_candle["Close"] > candle["High"]:
            direction = "BUY"
            confirmed = True
        elif is_bearish_candle and next_candle["Close"] < candle["Low"]:
            direction = "SELL"
            confirmed = True
        elif is_bullish_candle:
            direction = "BUY"
            confirmed = False
        elif is_bearish_candle:
            direction = "SELL"
            confirmed = False

        if direction is None:
            continue

        ts = df_15m.index[i]
        ts_str = ts.strftime("%Y-%m-%d %H:%M") if hasattr(ts, "strftime") else str(ts)

        sweeps.append({
            "index": i,
            "timestamp": ts_str,
            "direction": direction,
            "confirmed": confirmed,
            "sweep_pct": round(sweep_pct, 2),
            "candle_high": float(candle["High"]),
            "candle_low": float(candle["Low"]),
            "candle_close": float(candle["Close"]),
            "next_close": float(next_candle["Close"]),
        })

    return sweeps


def get_latest_sweep(df_15m: pd.DataFrame, daily_atr: float) -> dict | None:
    """Return the most recent sweep or None."""
    sweeps = detect_sweeps(df_15m, daily_atr)
    if not sweeps:
        return None
    confirmed = [s for s in sweeps if s["confirmed"]]
    return confirmed[-1] if confirmed else sweeps[-1]
