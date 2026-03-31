import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

US_STOCKS = [
    "AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "META", "TSLA", "BERKB", "LLY", "V",
    "JPM", "UNH", "XOM", "MA", "AVGO", "HD", "CVX", "MRK", "ABBV", "COST",
    "PEP", "ADBE", "WMT", "BAC", "KO", "PFE", "CSCO", "CRM", "TMO", "MCD",
    "DHR", "ABT", "NEE", "TXN", "ORCL", "LIN", "PM", "WFC", "RTX", "AMGN",
    "IBM", "INTU", "SPGI", "CAT", "GS", "HON", "SCHW", "MS", "BKNG", "LOW",
    "ISRG", "AXP", "SYK", "T", "MDT", "GILD", "PLD", "DE", "MMC", "ADI",
    "C", "NOW", "SBUX", "GE", "AMT", "LRCX", "VRTX", "CI", "CME", "ZTS",
    "REGN", "MO", "TJX", "USB", "EOG", "APD", "BSX", "HUM", "PGR", "PANW",
    "SO", "F", "GM", "KLAC", "SLB", "NOC", "ETN", "HCA", "DUK", "FCX",
    "SNPS", "MCO", "TT", "PSA", "CDNS", "NSC", "BK", "ROP", "WM", "ADP",
    "SPY", "QQQ", "IWM", "DIA", "GLD", "SLV", "TLT", "HYG", "EEM", "XLF",
    "XLE", "XLK", "XLV", "XLI", "XLY", "XLP", "XLU", "XLRE", "XLB", "XLC",
    "BAX", "BDX", "BLK", "BMY", "BR", "CB", "CEG", "CL", "COP", "CTAS",
    "D", "DD", "DOV", "DVN", "EL", "EMR", "EW", "EXC", "FAST", "FDX",
    "FIS", "FITB", "FMC", "FRC", "FTNT", "HAL", "ICE", "IDXX", "IFF", "IT",
    "ITW", "JCI", "JNPR", "KEY", "KMB", "KMI", "L", "LH", "LMT", "LUV",
    "MAA", "MAS", "MCK", "MET", "MGM", "MLM", "MMM", "MRNA", "MSI", "MTB",
    "MU", "NFLX", "NKE", "NOV", "NUE", "NVAX", "O", "OKE", "OTIS", "OXY",
    "PAYX", "PCAR", "PH", "PKI", "PPG", "PPL", "PRU", "PTC", "RE", "RF",
    "RMD", "ROK", "RSG", "RVTY", "SHW", "SJM", "SNA", "SWKS", "SYF", "SYY",
    "TAP", "TEL", "TFC", "TMUS", "TROW", "TRV", "UAL", "URI", "VFC", "VLO",
    "VMC", "VTR", "VZ", "WAB", "WAT", "WBA", "WDC", "WELL", "WHR", "WRB",
    "WST", "WY", "XEL", "XRAY", "XYL", "YUM", "ZBH", "ZBRA", "ZION", "ZTS"
]

UK_STOCKS = [
    "AZN.L", "SHEL.L", "HSBA.L", "ULVR.L", "BP.L", "RIO.L", "GSK.L", "LSEG.L",
    "DGE.L", "NG.L", "BHP.L", "VOD.L", "REL.L", "PRU.L", "AAL.L", "BARC.L",
    "LLOY.L", "NWG.L", "BATS.L", "IMB.L", "CPG.L", "EXPN.L", "FERG.L", "HIK.L",
    "IAG.L", "IHG.L", "INF.L", "JET2.L", "KGF.L", "LAND.L", "MNDI.L", "MNG.L",
    "MRO.L", "PSON.L", "RKT.L", "RS1.L", "SBRY.L", "SDR.L", "SGE.L", "SGRO.L",
    "SKG.L", "SMDS.L", "SMIN.L", "SMT.L", "SSE.L", "SVT.L", "TSCO.L", "TUI.L",
    "UU.L", "WPP.L", "AUTO.L", "ABF.L", "ADM.L", "AGR.L", "AHT.L", "ANTO.L",
    "AVV.L", "AWK.L", "BA.L", "BRBY.L", "CCH.L", "CCL.L", "CNA.L", "CRH.L",
    "DCC.L", "DPLM.L", "EDV.L", "EIGR.L", "ENT.L", "EZJ.L", "FLTR.L", "GLEN.L",
    "HAL.L", "HLN.L", "HMSO.L", "HTW.L", "HWDN.L", "ICG.L", "III.L", "IMCD.L",
    "IMI.L", "ITRK.L", "JD.L", "JMAT.L", "JUST.L", "LSE.L", "M&G.L", "MGAM.L",
    "MKS.L", "MONY.L", "MXCT.L", "NXT.L", "OCO.L", "PETS.L", "PLUS.L", "PMO.L",
    "POLR.L", "PSH.L", "PTEM.L", "RDW.L", "RMV.L", "RTO.L", "SCCO.L", "SLA.L"
]

CRYPTO = [
    "BTC-USD", "ETH-USD", "BNB-USD", "XRP-USD", "SOL-USD", "ADA-USD", "DOGE-USD",
    "DOT-USD", "AVAX-USD", "SHIB-USD", "LTC-USD", "LINK-USD", "BCH-USD", "TRX-USD",
    "NEAR-USD", "MATIC-USD", "UNI-USD", "XLM-USD", "ETC-USD", "APT-USD",
    "ICP-USD", "ATOM-USD", "HBAR-USD", "ALGO-USD", "VET-USD", "SAND-USD", "MANA-USD",
    "FIL-USD", "THETA-USD", "EOS-USD", "XTZ-USD", "AAVE-USD", "MKR-USD", "SNX-USD",
    "CRV-USD", "COMP-USD", "YFI-USD", "SUSHI-USD", "ZEC-USD", "DASH-USD",
    "WAVES-USD", "BAT-USD", "ZIL-USD", "ENJ-USD", "ANKR-USD", "HOT-USD",
    "RVN-USD", "SC-USD", "TFUEL-USD", "OMG-USD", "BTT-USD", "WIN-USD", "SXP-USD",
    "RUNE-USD", "1INCH-USD", "GRT-USD", "OCEAN-USD", "NMR-USD", "BAND-USD",
    "KNC-USD", "STORJ-USD", "CELR-USD", "ALPHA-USD", "SKL-USD", "NKN-USD"
]

FOREX = [
    "EURUSD=X", "GBPUSD=X", "USDJPY=X", "USDCHF=X", "AUDUSD=X", "USDCAD=X",
    "NZDUSD=X", "EURGBP=X", "EURJPY=X", "GBPJPY=X", "EURCHF=X", "AUDJPY=X",
    "CADJPY=X", "AUDNZD=X", "AUDCAD=X", "AUDCHF=X", "NZDJPY=X", "NZDCAD=X",
    "NZDCHF=X", "CADCHF=X", "EURAUD=X", "EURCAD=X", "EURNZD=X", "GBPAUD=X",
    "GBPCAD=X", "GBPCHF=X", "GBPNZD=X", "CHFJPY=X", "EURCZK=X", "EURDKK=X",
    "EURHUF=X", "EURNOK=X", "EURPLN=X", "EURSEK=X", "USDBRL=X", "USDCNH=X",
    "USDDKK=X", "USDHKD=X", "USDINR=X", "USDKRW=X", "USDMXN=X", "USDNOK=X",
    "USDPLN=X", "USDSEK=X", "USDSGD=X", "USDTRY=X", "USDZAR=X", "USDTHB=X",
    "USDPHP=X", "USDTWD=X"
]

INDICES = [
    "^GSPC", "^DJI", "^IXIC", "^RUT", "^VIX", "^FTSE", "^GDAXI", "^FCHI",
    "^STOXX50E", "^N225", "^HSI", "^AORD", "^BSESN", "^NSEI", "^KS11",
    "^TWII", "^AXJO", "^NZ50", "^TA125.TA", "^MERV", "^BVSP", "^MXX",
    "^IBEX", "^AEX", "^BFX", "^SSMI", "^PSI20", "^ATX", "^OSEAX", "^OMXS30",
    "^OMXHPI", "^OMXCGI", "^GSPTSE", "^TNX", "^TYX", "^IRX", "^FVX",
    "^XAU", "^XAG", "^XPT", "^XPD"
]

ALL_ASSETS = {
    "US Stocks": US_STOCKS,
    "UK Stocks": UK_STOCKS,
    "Crypto": CRYPTO,
    "Forex": FOREX,
    "Indices": INDICES
}


def detect_liquidity_sweep(df, lookback=20, threshold=0.5):
    """
    Detect institutional liquidity sweeps.
    A liquidity sweep occurs when price breaks a significant high/low (sweeping liquidity),
    then reverses sharply, indicating institutional order flow.
    """
    if df is None or len(df) < lookback + 5:
        return None

    results = []
    close = df['Close'].values
    high = df['High'].values
    low = df['Low'].values
    volume = df['Volume'].values if 'Volume' in df.columns else None

    for i in range(lookback, len(df) - 1):
        window_high = max(high[i - lookback:i])
        window_low = min(low[i - lookback:i])
        current_high = high[i]
        current_low = low[i]
        current_close = close[i]
        prev_close = close[i - 1]

        range_size = window_high - window_low
        if range_size == 0:
            continue

        sweep_type = None
        sweep_strength = 0

        if current_high > window_high and current_close < window_high:
            penetration = (current_high - window_high) / range_size * 100
            rejection = (current_high - current_close) / (current_high - current_low + 1e-10) * 100
            if penetration > threshold and rejection > 60:
                sweep_type = "Bearish Sweep"
                sweep_strength = min(100, (penetration + rejection) / 2)

        elif current_low < window_low and current_close > window_low:
            penetration = (window_low - current_low) / range_size * 100
            rejection = (current_close - current_low) / (current_high - current_low + 1e-10) * 100
            if penetration > threshold and rejection > 60:
                sweep_type = "Bullish Sweep"
                sweep_strength = min(100, (penetration + rejection) / 2)

        if sweep_type:
            vol_surge = 1.0
            if volume is not None and i > 5:
                avg_vol = np.mean(volume[i - 5:i])
                if avg_vol > 0:
                    vol_surge = volume[i] / avg_vol

            results.append({
                "index": i,
                "type": sweep_type,
                "strength": round(sweep_strength, 1),
                "volume_surge": round(vol_surge, 2),
                "price": round(current_close, 4),
                "sweep_level": round(window_high if sweep_type == "Bearish Sweep" else window_low, 4),
                "date": df.index[i].strftime('%Y-%m-%d %H:%M') if hasattr(df.index[i], 'strftime') else str(df.index[i])
            })

    return results[-1] if results else None


def calculate_atr(df, period=14):
    """Average True Range for volatility measurement."""
    if df is None or len(df) < period + 1:
        return None
    high = df['High']
    low = df['Low']
    close = df['Close']
    tr = pd.concat([
        high - low,
        abs(high - close.shift(1)),
        abs(low - close.shift(1))
    ], axis=1).max(axis=1)
    return tr.rolling(period).mean().iloc[-1]


def calculate_rsi(close, period=14):
    """Relative Strength Index."""
    if len(close) < period + 1:
        return None
    delta = pd.Series(close).diff()
    gain = (delta.where(delta > 0, 0)).rolling(period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(period).mean()
    rs = gain / loss
    return round(100 - (100 / (1 + rs.iloc[-1])), 1)


def scan_asset(ticker, category, period="5d", interval="1h"):
    """Scan a single asset for liquidity sweeps."""
    try:
        asset = yf.Ticker(ticker)
        df = asset.history(period=period, interval=interval)

        if df is None or len(df) < 25:
            df = asset.history(period="10d", interval="1h")

        if df is None or len(df) < 25:
            return None

        sweep = detect_liquidity_sweep(df, lookback=20)

        if not sweep:
            return None

        atr = calculate_atr(df)
        rsi = calculate_rsi(df['Close'].values)

        change_1d = None
        if len(df) >= 24:
            start_price = df['Close'].iloc[-24]
            end_price = df['Close'].iloc[-1]
            if start_price > 0:
                change_1d = round((end_price - start_price) / start_price * 100, 2)

        return {
            "ticker": ticker,
            "category": category,
            "sweep_type": sweep["type"],
            "strength": sweep["strength"],
            "volume_surge": sweep["volume_surge"],
            "price": sweep["price"],
            "sweep_level": sweep["sweep_level"],
            "sweep_date": sweep["date"],
            "rsi": rsi,
            "atr": round(atr, 4) if atr else None,
            "change_1d": change_1d,
            "scanned_at": datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')
        }
    except Exception as e:
        logger.debug(f"Error scanning {ticker}: {e}")
        return None


def run_screener(categories=None, max_per_category=50):
    """Run the screener across all or selected categories."""
    results = []
    errors = []

    if categories is None:
        categories = list(ALL_ASSETS.keys())

    for category in categories:
        if category not in ALL_ASSETS:
            continue
        tickers = ALL_ASSETS[category][:max_per_category]
        logger.info(f"Scanning {len(tickers)} {category} assets...")

        for ticker in tickers:
            result = scan_asset(ticker, category)
            if result:
                results.append(result)

    results.sort(key=lambda x: x['strength'], reverse=True)
    return results
