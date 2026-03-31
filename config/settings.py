US_STOCKS = [
    "AAPL", "MSFT", "NVDA", "AMZN", "GOOGL", "META", "TSLA", "JPM", "JNJ",
    "V", "PG", "UNH", "HD", "MA", "DIS", "BAC", "XOM", "PFE", "KO", "WMT",
    "AMD", "NFLX", "PYPL", "INTC", "CSCO", "ADBE", "CRM", "ORCL", "IBM", "GS"
]

UK_STOCKS = [
    "HSBA.L", "BP.L", "SHEL.L", "AZN.L", "ULVR.L", "RIO.L", "GSK.L",
    "BATS.L", "LSEG.L", "NG.L", "VOD.L", "LLOY.L", "BARC.L", "NWG.L",
    "BT-A.L", "MKS.L", "JD.L", "ABF.L", "IMB.L", "PRU.L"
]

CRYPTO = [
    "BTCUSDT", "ETHUSDT", "BNBUSDT", "SOLUSDT", "XRPUSDT", "ADAUSDT",
    "AVAXUSDT", "DOGEUSDT", "DOTUSDT", "MATICUSDT", "LINKUSDT",
    "UNIUSDT", "ATOMUSDT", "LTCUSDT", "ETCUSDT", "XLMUSDT",
    "ALGOUSDT", "VETUSDT", "FILUSDT", "TRXUSDT"
]

FOREX = [
    "EURUSD=X", "GBPUSD=X", "USDJPY=X", "AUDUSD=X", "USDCAD=X",
    "NZDUSD=X", "USDCHF=X", "EURGBP=X", "EURJPY=X", "GBPJPY=X"
]

INDICES = [
    "^GSPC", "^IXIC", "^FTSE", "^DJI", "^VIX", "^GDAXI", "^FCHI",
    "^N225", "^HSI", "^AXJO"
]

ASSET_CLASSES = {
    "US Stocks": US_STOCKS,
    "UK Stocks": UK_STOCKS,
    "Crypto": CRYPTO,
    "Forex": FOREX,
    "Indices": INDICES
}

BINANCE_KLINES_URL = "https://api.binance.com/api/v3/klines"

CANDLE_INTERVAL_15M = "15m"
CANDLE_LIMIT_15M = 100
DAILY_LOOKBACK_DAYS = 90

CACHE_TTL_SECONDS = 900

SWEEP_THRESHOLD_PCT = 20.0

BASE_WEIGHTS = {
    "sweep_confirmed": 30,
    "rsi": 20,
    "ema20": 15,
    "pivot": 25,
    "fibonacci": 20,
    "confirmation_candle": 30,
    "monthly_demand": 15,
}

MIN_SCORE = 60
SIGNAL_DIFF = 30

STOP_LOSS_ATR_MULT = 2.0
TAKE_PROFIT_FIB_LEVEL = 1.618
TAKE_PROFIT_ATR_MULT = 3.0

SCAN_INTERVAL_MINUTES = 15
MORNING_WATCHLIST_HOUR_UTC = 7
MORNING_WATCHLIST_TOP_N = 10
