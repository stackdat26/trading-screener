import numpy as np
import pandas as pd
import logging

logger = logging.getLogger(__name__)

STATES = ["BULLISH", "BEARISH", "OVERBOUGHT", "OVERSOLD", "HIGH_VOL", "SIDEWAYS"]
STATE_IDX = {s: i for i, s in enumerate(STATES)}


def classify_state(rsi: float, close: float, ema20: float, atr: float, avg_atr: float) -> str:
    """Classify a single candle into a market state."""
    if rsi is None or np.isnan(rsi):
        return "SIDEWAYS"

    if rsi > 70:
        return "OVERBOUGHT"
    if rsi < 30:
        return "OVERSOLD"
    if avg_atr and avg_atr > 0 and atr > avg_atr * 1.5:
        return "HIGH_VOL"
    if ema20 and close > ema20 and 40 <= rsi <= 60:
        return "BULLISH"
    if ema20 and close < ema20 and 40 <= rsi <= 60:
        return "BEARISH"
    return "SIDEWAYS"


def build_state_sequence(df_15m: pd.DataFrame, rsi_series: pd.Series,
                         atr_series: pd.Series, ema20: float, lookback: int = 30) -> list:
    """Build sequence of market states for last `lookback` candles."""
    n = min(lookback, len(df_15m))
    if n < 5:
        return []

    df_slice = df_15m.iloc[-n:]
    rsi_slice = rsi_series.iloc[-n:].values
    atr_slice = atr_series.iloc[-n:].values
    close_slice = df_slice["Close"].values
    avg_atr = float(np.nanmean(atr_slice)) if len(atr_slice) > 0 else None

    states = []
    for i in range(n):
        r = rsi_slice[i] if not np.isnan(rsi_slice[i]) else 50.0
        c = close_slice[i]
        a = atr_slice[i] if not np.isnan(atr_slice[i]) else 0.0
        states.append(classify_state(r, c, ema20, a, avg_atr))

    return states


def build_transition_matrix(states: list) -> np.ndarray:
    """Build a 6x6 transition matrix from state sequence."""
    n = len(STATES)
    matrix = np.zeros((n, n))

    for i in range(len(states) - 1):
        from_idx = STATE_IDX.get(states[i], 5)
        to_idx = STATE_IDX.get(states[i + 1], 5)
        matrix[from_idx][to_idx] += 1

    row_sums = matrix.sum(axis=1, keepdims=True)
    row_sums[row_sums == 0] = 1
    return matrix / row_sums


def get_next_state_probs(current_state: str, transition_matrix: np.ndarray) -> dict:
    """Get probability distribution over next states."""
    idx = STATE_IDX.get(current_state, 5)
    probs = transition_matrix[idx]
    return {state: float(probs[i]) for i, state in enumerate(STATES)}


def markov_confidence_boost(next_probs: dict, current_state: str) -> float:
    """
    Returns confidence multiplier:
    +20% boost if max next-state prob > 0.55
    -20% reduction if max next-state prob < 0.40
    """
    if not next_probs:
        return 1.0
    max_prob = max(next_probs.values())
    if max_prob > 0.55:
        return 1.20
    if max_prob < 0.40:
        return 0.80
    return 1.0


def run_markov(df_15m: pd.DataFrame, rsi_series: pd.Series,
               atr_series: pd.Series, ema20: float) -> dict:
    """Full Markov analysis. Returns current_state, next_probs, confidence_boost."""
    states = build_state_sequence(df_15m, rsi_series, atr_series, ema20)

    if len(states) < 5:
        return {
            "current_state": "SIDEWAYS",
            "next_probs": {},
            "confidence_boost": 1.0,
            "transition_matrix": None
        }

    matrix = build_transition_matrix(states)
    current_state = states[-1]
    next_probs = get_next_state_probs(current_state, matrix)
    boost = markov_confidence_boost(next_probs, current_state)

    return {
        "current_state": current_state,
        "next_probs": next_probs,
        "confidence_boost": boost,
        "transition_matrix": matrix.tolist()
    }
