# Trading Screener

A quantitative trading screener that scans 685+ assets for institutional liquidity sweeps across US stocks, UK stocks, crypto, forex, and indices.

## Architecture

- **Backend**: Python 3.11 + Flask web server running on port 5000
- **Frontend**: Vanilla HTML/CSS/JavaScript (served by Flask as static files)
- **Data**: Yahoo Finance (yfinance) for real-time market data
- **Concurrency**: Threading for background scans, polling-based status updates

## Project Structure

```
app.py          # Flask web application & API endpoints
screener.py     # Core scanning logic, liquidity sweep detection, asset lists
templates/
  index.html    # Main UI template
static/
  css/style.css # Dark-themed UI styles
  js/app.js     # Frontend JavaScript (scan control, result rendering)
```

## Key Features

- Scans 685+ assets: US stocks, UK stocks, crypto, forex, indices
- Detects institutional liquidity sweeps (bullish and bearish)
- Calculates sweep strength, volume surge, RSI, ATR
- Real-time background scanning with polling updates
- Filtering by category, direction, strength
- Sort by strength, volume surge, or ticker

## Running

```bash
python app.py
```

The app runs on `0.0.0.0:5000`.

## API Endpoints

- `GET /` — Main UI
- `POST /api/scan` — Start a background scan (body: `{ categories: [...] }`)
- `GET /api/results` — Get filtered results (query params: category, type, min_strength, sort_by)
- `GET /api/status` — Get scan status and totals
- `GET /api/categories` — List available categories

## Dependencies

- flask, flask-cors
- yfinance
- pandas, numpy
- gunicorn (production server)

## Deployment

Configured for autoscale deployment using gunicorn:
```
gunicorn --bind=0.0.0.0:5000 --reuse-port app:app
```
