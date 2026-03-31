import numpy as np
import pandas as pd
import logging

logger = logging.getLogger(__name__)


def calc_rsi(close: pd.Series, period: int = 14) -> pd.Series:
    delta = close.diff()
    gains = delta.where(delta > 0, 0.0).rolling(period).mean()
    losses = (-delta.where(delta < 0, 0.0)).rolling(period).mean()
    rs = gains / losses.replace(0, np.nan)
    return 100 - (100 / (1 + rs))


def calc_atr(df: pd.DataFrame, period: int = 14) -> pd.Series:
    high = df["High"]
    low = df["Low"]
    prev_close = df["Close"].shift(1)
    tr = pd.concat([
        high - low,
        (high - prev_close).abs(),
        (low - prev_close).abs()
    ], axis=1).max(axis=1)
    return tr.rolling(period).mean()


def calc_ema(close: pd.Series, span: int) -> pd.Series:
    return close.ewm(span=span, adjust=False).mean()


def calc_vwap(df: pd.DataFrame) -> pd.Series:
    tp = (df["High"] + df["Low"] + df["Close"]) / 3
    cum_vol = df["Volume"].cumsum()
    cum_tpvol = (tp * df["Volume"]).cumsum()
    return cum_tpvol / cum_vol.replace(0, np.nan)


def calc_pivot_points(prev_high: float, prev_low: float, prev_close: float) -> dict:
    pp = (prev_high + prev_low + prev_close) / 3
    r1 = (2 * pp) - prev_low
    r2 = pp + (prev_high - prev_low)
    s1 = (2 * pp) - prev_high
    s2 = pp - (prev_high - prev_low)
    return {"pp": pp, "r1": r1, "r2": r2, "s1": s1, "s2": s2}


def calc_fibonacci(df_recent: pd.DataFrame) -> dict:
    """Calculate Fibonacci levels from recent 20-candle swing high/low."""
    highs = df_recent["High"]
    lows = df_recent["Low"]
    swing_high = highs.max()
    swing_low = lows.min()
    diff = swing_high - swing_low

    retrace_levels = [0.236, 0.382, 0.500, 0.618, 0.786]
    ext_levels = [1.272, 1.414, 1.618, 2.000, 2.618]

    retracements = {lvl: swing_high - (diff * lvl) for lvl in retrace_levels}
    extensions = {lvl: swing_high + (diff * (lvl - 1)) for lvl in ext_levels}

    return {
        "swing_high": swing_high,
        "swing_low": swing_low,
        "diff": diff,
        "retracements": retracements,
        "extensions": extensions,
    }


def get_monthly_demand_zones(df_daily: pd.DataFrame, n_months: int = 6) -> list:
    """Return last n_months monthly close prices as demand zone levels."""
    if df_daily is None or len(df_daily) < 20:
        return []
    monthly = df_daily["Close"].resample("ME").last()
    return monthly.dropna().tail(n_months).tolist()


def price_near_level(price: float, level: float, tolerance_pct: float = 1.0) -> bool:
    if level == 0:
        return False
    return abs(price - level) / abs(level) * 100 <= tolerance_pct


def compute_all_indicators(df_15m: pd.DataFrame, df_daily: pd.DataFrame) -> dict:
    """Compute all indicators and return as dict."""
    result = {}

    if df_15m is None or len(df_15m) < 20:
        return result

    close_15m = df_15m["Close"]

    rsi_series = calc_rsi(close_15m)
    result["rsi"] = float(rsi_series.iloc[-1]) if not rsi_series.empty else None

    atr_15m = calc_atr(df_15m)
    result["atr_15m"] = float(atr_15m.iloc[-1]) if not atr_15m.empty else None

    if df_daily is not None and len(df_daily) >= 14:
        atr_daily = calc_atr(df_daily)
        result["atr_daily"] = float(atr_daily.iloc[-1]) if not atr_daily.empty else None
        result["avg_atr_daily"] = float(atr_daily.mean()) if not atr_daily.empty else None
    else:
        result["atr_daily"] = result.get("atr_15m")
        result["avg_atr_daily"] = result.get("atr_15m")

    ema20 = calc_ema(close_15m, 20)
    ema50 = calc_ema(close_15m, 50)
    result["ema20"] = float(ema20.iloc[-1]) if not ema20.empty else None
    result["ema50"] = float(ema50.iloc[-1]) if len(ema50) >= 50 else None

    if df_daily is not None and len(df_daily) >= 2:
        prev = df_daily.iloc[-2]
        pivots = calc_pivot_points(prev["High"], prev["Low"], prev["Close"])
        result["pivots"] = pivots
    else:
        result["pivots"] = None

    if len(df_15m) >= 20:
        fib = calc_fibonacci(df_15m.tail(20))
        result["fibonacci"] = fib
    else:
        result["fibonacci"] = None

    if df_daily is not None:
        result["monthly_zones"] = get_monthly_demand_zones(df_daily)
    else:
        result["monthly_zones"] = []

    vwap = calc_vwap(df_15m)
    result["vwap"] = float(vwap.iloc[-1]) if not vwap.empty else None

    result["rsi_series"] = rsi_series
    result["atr_15m_series"] = atr_15m

    return result
