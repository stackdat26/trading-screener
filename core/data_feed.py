import time
import logging
import requests
import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta
from config.settings import (
    BINANCE_KLINES_URL, CANDLE_INTERVAL_15M, CANDLE_LIMIT_15M,
    DAILY_LOOKBACK_DAYS, CACHE_TTL_SECONDS
)

logger = logging.getLogger(__name__)

_cache = {}


def _cache_key(symbol, data_type):
    return f"{symbol}:{data_type}"


def _get_cached(key):
    entry = _cache.get(key)
    if entry and (time.time() - entry["ts"]) < CACHE_TTL_SECONDS:
        return entry["data"]
    return None


def _set_cached(key, data):
    _cache[key] = {"data": data, "ts": time.time()}


def fetch_binance_candles(symbol, interval="15m", limit=100):
    key = _cache_key(symbol, f"binance_{interval}")
    cached = _get_cached(key)
    if cached is not None:
        return cached

    try:
        params = {"symbol": symbol, "interval": interval, "limit": limit}
        resp = requests.get(BINANCE_KLINES_URL, params=params, timeout=10)
        resp.raise_for_status()
        raw = resp.json()
        if not raw or isinstance(raw, dict):
            return None
        df = pd.DataFrame(raw, columns=[
            "open_time", "open", "high", "low", "close", "volume",
            "close_time", "quote_volume", "trades", "taker_buy_base",
            "taker_buy_quote", "ignore"
        ])
        df["open_time"] = pd.to_datetime(df["open_time"], unit="ms")
        df.set_index("open_time", inplace=True)
        for col in ["open", "high", "low", "close", "volume"]:
            df[col] = pd.to_numeric(df[col], errors="coerce")
        df.rename(columns={"open": "Open", "high": "High", "low": "Low",
                            "close": "Close", "volume": "Volume"}, inplace=True)
        df = df[["Open", "High", "Low", "Close", "Volume"]].dropna()
        _set_cached(key, df)
        return df
    except Exception as e:
        logger.debug(f"Binance fetch error {symbol}: {e}")
        return None


def fetch_binance_daily(symbol, days=90):
    key = _cache_key(symbol, "binance_1d")
    cached = _get_cached(key)
    if cached is not None:
        return cached

    try:
        params = {"symbol": symbol, "interval": "1d", "limit": days}
        resp = requests.get(BINANCE_KLINES_URL, params=params, timeout=10)
        resp.raise_for_status()
        raw = resp.json()
        if not raw or isinstance(raw, dict):
            return None
        df = pd.DataFrame(raw, columns=[
            "open_time", "open", "high", "low", "close", "volume",
            "close_time", "quote_volume", "trades", "taker_buy_base",
            "taker_buy_quote", "ignore"
        ])
        df["open_time"] = pd.to_datetime(df["open_time"], unit="ms")
        df.set_index("open_time", inplace=True)
        for col in ["open", "high", "low", "close", "volume"]:
            df[col] = pd.to_numeric(df[col], errors="coerce")
        df.rename(columns={"open": "Open", "high": "High", "low": "Low",
                            "close": "Close", "volume": "Volume"}, inplace=True)
        df = df[["Open", "High", "Low", "Close", "Volume"]].dropna()
        _set_cached(key, df)
        return df
    except Exception as e:
        logger.debug(f"Binance daily fetch error {symbol}: {e}")
        return None


def fetch_yf_15m(symbol):
    key = _cache_key(symbol, "yf_15m")
    cached = _get_cached(key)
    if cached is not None:
        return cached

    try:
        ticker = yf.Ticker(symbol)
        df = ticker.history(period="5d", interval="15m")
        if df is None or len(df) < 20:
            df = ticker.history(period="7d", interval="15m")
        if df is None or len(df) == 0:
            return None
        df = df[["Open", "High", "Low", "Close", "Volume"]].dropna()
        df = df.tail(CANDLE_LIMIT_15M)
        _set_cached(key, df)
        return df
    except Exception as e:
        logger.debug(f"yfinance 15m fetch error {symbol}: {e}")
        return None


def fetch_yf_daily(symbol):
    key = _cache_key(symbol, "yf_daily")
    cached = _get_cached(key)
    if cached is not None:
        return cached

    try:
        ticker = yf.Ticker(symbol)
        end = datetime.utcnow()
        start = end - timedelta(days=DAILY_LOOKBACK_DAYS)
        df = ticker.history(start=start.strftime("%Y-%m-%d"),
                            end=end.strftime("%Y-%m-%d"), interval="1d")
        if df is None or len(df) == 0:
            return None
        df = df[["Open", "High", "Low", "Close", "Volume"]].dropna()
        _set_cached(key, df)
        return df
    except Exception as e:
        logger.debug(f"yfinance daily fetch error {symbol}: {e}")
        return None


def get_candles(symbol, asset_class):
    """Return (df_15m, df_daily) for any asset class."""
    if asset_class == "Crypto":
        df_15m = fetch_binance_candles(symbol, interval=CANDLE_INTERVAL_15M,
                                       limit=CANDLE_LIMIT_15M)
        df_daily = fetch_binance_daily(symbol, days=DAILY_LOOKBACK_DAYS)
    else:
        df_15m = fetch_yf_15m(symbol)
        df_daily = fetch_yf_daily(symbol)
    return df_15m, df_daily
