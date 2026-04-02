# QuantBot Screener

A real-time institutional liquidity sweep detector and market analyzer built with Python and Flask.

## Overview

Scans 90+ assets (US/UK stocks, crypto, forex, and indices) every 15 minutes to identify high-probability trading signals based on liquidity sweeps, technical indicators, and a Markov regime model.

## Architecture

- **`core/`** — Screener engine, sweep detector, Markov chain, data feed (yfinance + Binance), and indicators (RSI, ATR, EMA, VWAP, Fibonacci, Pivot Points)
- **`dashboard/`** — Flask API (`app.py`) and vanilla JS/Chart.js frontend (`templates/index.html`)
- **`config/settings.py`** — Asset lists (90+ symbols), scoring weights, thresholds
- **`main.py`** — Local entry point: starts background scan thread + scheduler, then Flask on port 5000
- **`wsgi.py`** — Production WSGI entry point (used by gunicorn), starts same background threads

## Running

The app starts via `python main.py` on port 5000. The workflow is named **Start application**.

On startup it:
1. Fires an initial scan in a background thread
2. Schedules scans every 15 minutes and a morning watchlist at 07:00 UTC
3. Serves the dashboard at `/`

## Key Dependencies

- Flask, Flask-CORS, Flask-SQLAlchemy
- yfinance (market data)
- pandas, numpy (data processing)
- schedule (background job scheduling)
- gunicorn (production WSGI server)
- psycopg2-binary (PostgreSQL, if needed)

## Deployment

Configured for Replit autoscale deployment using gunicorn:
```
gunicorn --bind 0.0.0.0:5000 main:app
```
