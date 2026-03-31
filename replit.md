# QuantBot Screener

A quantitative trading screener built by a 17-year-old quant trader. Scans 80+ assets across US stocks, UK stocks, crypto, forex, and indices for institutional liquidity sweeps, scores them using a multi-factor system with a Markov regime model, and displays live signals on a GitHub dark-themed dashboard.

## Architecture

- **Entry point**: `main.py` — starts Flask server + background scheduler
- **Backend**: Python 3.11 + Flask on port 5000
- **Scheduler**: `schedule` library — scans every 15 minutes, morning watchlist at 07:00 UTC
- **Data**: yfinance (stocks/forex/indices), Binance public API (crypto)
- **Frontend**: Pure HTML/CSS/JS served by Flask (no React, no frameworks)

## File Structure

```
main.py                   # Entry point, scheduler
requirements.txt
config/
  settings.py             # Asset lists, constants, weights
core/
  data_feed.py            # Binance + yfinance data fetching with 15-min cache
  indicators.py           # RSI, ATR, EMA, VWAP, pivots, Fibonacci, monthly zones
  sweep_detector.py       # Liquidity sweep detection formula
  screener_engine.py      # Scoring system, market context, risk levels
  markov.py               # 6-state Markov regime model, transition matrix
dashboard/
  app.py                  # Flask routes and state management
  templates/index.html    # Full SPA dashboard
```

## Key Concepts

### Sweep Detection
`sweep_percent = ((candle_high - candle_low) / daily_ATR) × 100`
- Flag if sweep_percent > 20%
- Bullish confirmed: bullish candle + next closes above sweep high
- Bearish confirmed: bearish candle + next closes below sweep low

### Scoring (buy_score / sell_score)
| Factor | Points |
|--------|--------|
| Liquidity sweep confirmed | 30 |
| Confirmation candle | 30 |
| Pivot S1/S2 or R1/R2 proximity | 25 |
| RSI oversold/overbought | 20 |
| Fibonacci retracement/extension | 20 |
| EMA20 above/below | 15 |
| Monthly demand zone | 15 |

- Min score to show: 60 points
- Signal requires 30-point gap between buy/sell score

### Market Context
- **CRISIS**: ATR > avg_ATR × 2.0 → all weights × 0.70
- **TRENDING**: |EMA20 - EMA50| / EMA50 > 2% → sweep & EMA weights × 1.20
- **NORMAL**: base weights

### Markov Regime Model
- 6 states: BULLISH, BEARISH, OVERBOUGHT, OVERSOLD, HIGH_VOL, SIDEWAYS
- Transition matrix built from last 30 candles
- Prob > 0.55 → +20% confidence; Prob < 0.40 → -20% confidence

## Running

```bash
python main.py
```

## Dependencies

flask, flask-cors, yfinance, pandas, numpy, requests, schedule, gunicorn
