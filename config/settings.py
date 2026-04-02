US_STOCKS = [
    "AAPL", "MSFT", "NVDA", "AMZN", "GOOGL", "META", "TSLA", "BRK-B",
    "JPM", "JNJ", "V", "PG", "UNH", "HD", "MA", "DIS", "BAC", "XOM", "PFE",
    "KO", "WMT", "AMD", "NFLX", "PYPL", "INTC", "CSCO", "ADBE", "CRM",
    "ORCL", "IBM", "GS", "MS", "C", "WFC", "AXP", "SPGI", "BLK", "CB",
    "MMM", "CAT", "DE", "BA", "LMT", "RTX", "NOC", "GD", "HON", "UPS",
    "FDX", "DAL", "UAL", "AAL", "SBUX", "MCD", "YUM", "CMG", "NKE",
    "LULU", "TGT", "COST", "CVS", "WBA", "TMO", "ABT", "MDT", "SYK",
    "ISRG", "REGN", "BIIB", "AMGN", "GILD", "MRK", "LLY", "BMY",
    "NEE", "DUK", "SO", "AEP", "EXC", "SRE", "PCG", "ED", "FE", "ETR",
    "AMT", "PLD", "CCI", "EQIX", "PSA", "SPG", "O", "VICI", "AVB",
    "EOG", "PXD", "COP", "MPC", "VLO", "PSX", "OXY", "HAL", "SLB",
    "NEM", "FCX", "AA", "X", "CLF", "MP", "ALB", "LTHM", "SQM"
]

UK_STOCKS = [
    "HSBA.L", "BP.L", "SHEL.L", "AZN.L", "ULVR.L", "RIO.L",
    "GSK.L", "BATS.L", "LSEG.L", "NG.L", "VOD.L", "LLOY.L",
    "BARC.L", "NWG.L", "BT-A.L", "MKS.L", "JD.L", "ABF.L",
    "IMB.L", "PRU.L", "STAN.L", "AAL.L", "ADM.L",
    "AGK.L", "ANTO.L", "AUTO.L", "AV.L", "AVV.L", "BA.L",
    "BAB.L", "BGEO.L", "BKG.L", "BLND.L", "BME.L", "BNZL.L",
    "BOO.L", "BRBY.L", "BVB.L", "CCH.L", "CCL.L", "CNA.L",
    "CPG.L", "CRDA.L", "CRH.L", "DCC.L", "DGE.L", "DLN.L",
    "DPLM.L", "EDV.L", "ENT.L", "EXPN.L", "EZJ.L", "FERG.L",
    "FLTR.L", "FRES.L", "GFS.L", "GLEN.L", "HIK.L", "HL.L",
    "HLMA.L", "HLN.L", "HWDN.L", "IAG.L", "IHG.L", "III.L",
    "INF.L", "ITRK.L", "ITV.L", "JET2.L", "KGF.L", "LAND.L",
    "LGND.L", "LGEN.L", "LMP.L", "MNDI.L", "MNG.L", "MRO.L",
    "MTO.L", "MXCT.L", "NXT.L", "OCDO.L", "PHNX.L", "POLYP.L",
    "PSH.L", "PSON.L", "REL.L", "RKT.L", "RMV.L", "RR.L",
    "RS1.L", "SBRY.L", "SDR.L", "SGE.L", "SGRO.L", "SKG.L",
    "SMDS.L", "SMIN.L", "SMT.L", "SN.L", "SPX.L", "SSE.L",
    "SVT.L", "TSCO.L", "TW.L", "UU.L",
    "VIC.L", "WPP.L", "WTB.L"
]

CRYPTO = [
    "BTCUSDT", "ETHUSDT", "BNBUSDT", "SOLUSDT", "XRPUSDT", "ADAUSDT",
    "AVAXUSDT", "DOGEUSDT", "DOTUSDT", "MATICUSDT", "LINKUSDT",
    "UNIUSDT", "ATOMUSDT", "LTCUSDT", "ETCUSDT", "XLMUSDT",
    "ALGOUSDT", "VETUSDT", "FILUSDT", "TRXUSDT", "NEARUSDT",
    "FTMUSDT", "SANDUSDT", "MANAUSDT", "AXSUSDT", "GALAUSDT",
    "APEUSDT", "GMTUSDT", "OPUSDT", "ARBUSDT", "INJUSDT",
    "SUIUSDT", "SEIUSDT", "TIAUSDT", "JUPUSDT", "WIFUSDT",
    "BONKUSDT", "PENDLEUSDT", "STRKUSDT", "PYTHUSDT"
]

FOREX = [
    "EURUSD=X", "GBPUSD=X", "USDJPY=X", "AUDUSD=X", "USDCAD=X",
    "NZDUSD=X", "USDCHF=X", "EURGBP=X", "EURJPY=X", "GBPJPY=X",
    "AUDJPY=X", "CADJPY=X", "CHFJPY=X", "EURCHF=X", "EURAUD=X",
    "EURCAD=X", "EURNZD=X", "GBPAUD=X", "GBPCAD=X", "GBPCHF=X",
    "GBPNZD=X", "AUDCAD=X", "AUDCHF=X", "AUDNZD=X", "CADCHF=X",
    "NZDCAD=X", "NZDCHF=X", "NZDJPY=X", "USDMXN=X", "USDZAR=X",
    "USDTRY=X", "USDSEK=X", "USDNOK=X", "USDDKK=X", "USDSGD=X",
    "USDHKD=X", "USDCNH=X", "USDINR=X", "USDKRW=X", "USDBRL=X"
]

INDICES = [
    "^GSPC", "^IXIC", "^FTSE", "^DJI", "^VIX", "^GDAXI", "^FCHI",
    "^N225", "^HSI", "^AXJO", "^STOXX50E", "^AEX", "^IBEX",
    "^SSMI", "^BVSP", "^MXX", "^NSEI", "^BSESN", "^KS11",
    "^TWII", "^STI", "^KLSE", "^JKSE", "^TA125.TA"
]

COMMODITIES = [
    "GC=F", "SI=F", "CL=F", "BZ=F", "NG=F", "HG=F", "PL=F",
    "PA=F", "ZC=F", "ZW=F", "ZS=F", "KC=F", "CT=F", "SB=F",
    "CC=F", "LE=F", "GF=F", "HE=F", "RB=F", "HO=F"
]

ASSET_CLASSES = {
    "US Stocks": US_STOCKS,
    "UK Stocks": UK_STOCKS,
    "Crypto": CRYPTO,
    "Forex": FOREX,
    "Indices": INDICES,
    "Commodities": COMMODITIES,
}

BINANCE_KLINES_URL = "https://api.binance.com/api/v3/klines"

CANDLE_INTERVAL_15M = "15m"
CANDLE_LIMIT_15M = 100
DAILY_LOOKBACK_DAYS = 90

CACHE_TTL_SECONDS = 900

SWEEP_THRESHOLD_PCT = 20.0  # legacy fallback

SWEEP_THRESHOLDS = {
    "Crypto": 20.0,
    "US Stocks": 15.0,
    "UK Stocks": 15.0,
    "Forex": 10.0,
    "Indices": 12.0,
    "Commodities": 15.0,
}

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
