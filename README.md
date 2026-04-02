# QuantBot Screener

> Real-time institutional liquidity sweep detector scanning 335+ assets across global markets — built with Python, Flask, and a Markov regime model.
https://trading-bot-1-q7he.onrender.com/
---

## What It Does

Traditional retail traders watch price. Institutional traders move price — and when they do, they leave a footprint called a **liquidity sweep**.

A liquidity sweep happens when a large player pushes price briefly beyond a key level (like a recent high or low) to trigger stop-loss orders from retail traders sitting on the wrong side. Once that liquidity is collected, price reverses sharply. This is where the real move begins.

**QuantBot Screener** scans 335+ assets every 15 minutes looking for these sweeps in real time. It doesn't just flag them — it scores each one across 7 technical factors, models the current market regime using a Markov chain, and delivers a ranked signal with a directional bias, confidence score, entry price, stop loss, and take-profit target.

---

## Assets Covered

| Category      | Count    | Examples                                                    |
|---------------|----------|-------------------------------------------------------------|
| US Stocks     | 111      | AAPL, MSFT, NVDA, TSLA, JPM, AMZN, META, LMT, NEE, NEM    |
| UK Stocks     | 100      | HSBA.L, BP.L, AZN.L, SHEL.L, ULVR.L, GLEN.L, RIO.L        |
| Crypto        | 40       | BTCUSDT, ETHUSDT, SOLUSDT, ARBUSDT, INJUSDT, JUPUSDT        |
| Forex         | 40       | EURUSD, GBPUSD, USDJPY, USDMXN, USDZAR, USDCNH             |
| Indices       | 24       | S&P 500, NASDAQ, FTSE 100, DAX, Nikkei 225, KOSPI, TA125   |
| Commodities   | 20       | GC=F (Gold), CL=F (Oil), SI=F (Silver), ZC=F (Corn), NG=F  |
| **Total**     | **335+** | **6 asset classes across global markets**                   |

---

## How It Works

### 1. Liquidity Sweep Detection

Every 15-minute candle is tested against this formula:

```
sweep_percent = (candle_high − candle_low) / daily_ATR × 100
```

If `sweep_percent` exceeds the **dynamic threshold for that asset class**, the candle qualifies as a sweep candidate. A sweep is then **confirmed** by checking the next candle's close:

- **Bullish sweep confirmed:** Candle is bullish AND next close is above the sweep candle's high → `BUY` signal
- **Bearish sweep confirmed:** Candle is bearish AND next close is below the sweep candle's low → `SELL` signal

Unconfirmed sweeps are still scored but carry half the weight.

#### Dynamic Sweep Thresholds

Each asset class has a calibrated sensitivity threshold, reflecting its typical volatility profile:

| Asset Class   | Sweep Threshold |
|---------------|-----------------|
| Crypto        | 20% of daily ATR |
| US Stocks     | 15% of daily ATR |
| UK Stocks     | 15% of daily ATR |
| Commodities   | 15% of daily ATR |
| Indices       | 12% of daily ATR |
| Forex         | 10% of daily ATR |

---

### 2. Multi-Factor Scoring System

Each asset is scored independently for BUY and SELL pressure across 7 factors. The side with the higher score wins — only if it exceeds the other by at least 30 points.

| Factor                | Max Points | What It Measures                                      |
|-----------------------|------------|-------------------------------------------------------|
| Sweep Confirmed       | 30         | Institutional candle detected and confirmed           |
| Confirmation Candle   | 30         | Follow-through candle validates the sweep direction   |
| Pivot Point Proximity | 25         | Price near daily S1/S2 (buy) or R1/R2 (sell)         |
| RSI                   | 20         | Oversold < 30 (buy) / Overbought > 70 (sell)         |
| Fibonacci Level       | 20         | Price at retracement (buy) or extension (sell) level  |
| EMA 20                | 15         | Price above EMA20 (bullish) / below (bearish)         |
| Monthly Demand Zone   | 15         | Price at a key monthly close level                    |
| **Total**             | **155**    |                                                       |

**Confidence** is expressed as a percentage of the 155-point maximum:

```
confidence = (winning_side_score / 155) × 100
```

---

### 3. Market Context Detection

Before scoring, the screener classifies the current market regime:

| Context    | Condition                                              | Effect on Scoring          |
|------------|--------------------------------------------------------|----------------------------|
| `CRISIS`   | Current ATR > average ATR × 2.0 (extreme volatility)  | All weights reduced by 30% |
| `TRENDING` | \|EMA20 − EMA50\| / EMA50 > 2%                        | Sweep & EMA weights +20%   |
| `NORMAL`   | Everything else                                        | Weights unchanged           |

---

### 4. Markov Regime Model

A 6-state Markov chain is built from the last 30 candles to model the probability of the next market state. The six states are:

`BULLISH` · `BEARISH` · `OVERBOUGHT` · `OVERSOLD` · `HIGH_VOL` · `SIDEWAYS`

A 6×6 transition matrix is computed from observed state-to-state transitions. If the highest-probability next state has:

- **Probability > 55%** → confidence multiplied by `×1.20` (+20% boost)
- **Probability < 40%** → confidence multiplied by `×0.80` (−20% penalty)
- **Otherwise** → no adjustment

This prevents high-scoring signals from being acted on when the regime is ambiguous or transitioning unpredictably.

---

## Tech Stack

| Layer         | Technology                                                           |
|---------------|----------------------------------------------------------------------|
| Language      | Python 3.11                                                          |
| Web Framework | Flask + Flask-CORS                                                   |
| Market Data   | yfinance (stocks, forex, indices, commodities), Binance REST API (crypto) |
| Indicators    | Custom NumPy / Pandas implementations (no TA-Lib dependency)         |
| Regime Model  | Custom Markov chain (NumPy)                                          |
| Frontend      | Vanilla JS, Chart.js, GitHub dark CSS theme                          |
| Scheduling    | Python `schedule` + threading (background scan loop)                 |
| Caching       | In-memory 15-minute TTL cache                                        |
| Server        | Gunicorn (production), Flask dev server (local)                      |

---

## File Structure

```
quantbot-screener/
│
├── main.py                     # Entry point — starts Flask + background scan loop
├── wsgi.py                     # Gunicorn entry point
│
├── config/
│   └── settings.py             # Asset lists, per-class sweep thresholds, scoring weights
│
├── core/
│   ├── data_feed.py            # Binance + yfinance fetchers with 15m cache
│   ├── indicators.py           # RSI, ATR, EMA, VWAP, Fibonacci, Pivot Points
│   ├── sweep_detector.py       # Dynamic sweep detection (threshold per asset class)
│   ├── markov.py               # 6-state Markov chain regime model
│   └── screener_engine.py      # Scoring, context detection, signal builder
│
├── dashboard/
│   ├── app.py                  # Flask routes + NaN-safe JSON serialisation
│   ├── templates/
│   │   └── index.html          # Dark-themed live dashboard
│   └── static/                 # CSS / JS assets
│
└── README.md
```

---

## Getting Started

### Prerequisites

- Python 3.11+
- pip

### Installation

```bash
# 1. Clone the repository
git clone https://github.com/stackdat26/trading-screener.git
cd trading-screener

# 2. Install dependencies
pip install flask flask-cors yfinance requests pandas numpy schedule gunicorn

# 3. Run the screener
python main.py
```

The dashboard will be available at **http://localhost:5000**

### First Run

On startup the screener immediately runs a full scan across all 335+ assets. This takes a few minutes depending on your connection speed. After that, a background thread rescans every 15 minutes automatically.

You can also trigger a manual scan at any time directly from the dashboard.

---

## Dashboard Features

- Live signal table with sortable columns
- Filter by asset class (US Stocks, UK Stocks, Crypto, Forex, Indices, Commodities), direction (BUY / SELL), and minimum confidence
- Summary stats: total scanned, BUY / SELL counts, high-confidence signals (≥ 80%)
- Per-signal detail: entry price, stop loss, take-profit, RSI, sweep %, Markov state, market context
- Morning watchlist — top 10 signals generated at 07:00 UTC
- Next scan countdown timer
- GitHub dark theme throughout

---

## Roadmap

- [x] Core screener engine
- [x] All indicator formulas (RSI, ATR, EMA, VWAP, Fibonacci, Pivot Points)
- [x] Liquidity sweep detection with confirmation logic
- [x] Dynamic sweep thresholds per asset class
- [x] Multi-factor scoring system (7 factors, 155 points max)
- [x] Markov regime model (6-state, 6×6 transition matrix)
- [x] Market context detection (CRISIS / TRENDING / NORMAL)
- [x] Morning watchlist (top 10 signals at 07:00 UTC)
- [x] Web dashboard with live filtering
- [x] Full asset expansion — 335+ symbols across 6 classes including Commodities
- [ ] Historical signal performance tracking
- [ ] Price alerts (email / webhook)
- [ ] Mobile optimised view

---

## Author

Built by a 17-year-old quant trader who got tired of watching price action without a systematic edge.

---

## License

MIT License — free to use, modify, and distribute. See [LICENSE](LICENSE) for details.
