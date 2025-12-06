import numpy as np
import pandas as pd
import quantstats as qs

qs.extend_pandas()

def portfolio_value_from_prices(price_df: pd.DataFrame, shares: dict) -> pd.Series:
    if price_df.empty:
        return pd.Series(dtype=float)
    shares_series = pd.Series(shares)
    aligned = price_df.loc[:, price_df.columns.intersection(shares_series.index)].copy()
    value_df = aligned.multiply(shares_series, axis=1)
    pf = value_df.sum(axis=1)
    return pf.dropna()


def compute_portfolio_metrics(
        portfolio_value: pd.Series,
        buy_price: dict = None,
        latest_price: dict = None,
        shares: dict = None,
        buy_date_actual: dict = None,
        risk_free_rate: float = 0.068):

    metrics = {}

    if portfolio_value.empty or len(portfolio_value) < 2:
        metrics.update({"cumulative_return": 0.0,
                        "investor_cagr": 0.0,
                        "volatility": 0.0,
                        "cagr": 0.0,
                        "sharpe": np.nan,
                        "sortino": np.nan,
                        "max_dd": np.nan,
                        "returns": pd.Series(dtype=float)})
        return metrics

    returns = portfolio_value.pct_change().dropna()
    metrics["returns"] = returns
    metrics["volatility"] = returns.std() * np.sqrt(252)
    metrics["cagr"] = qs.stats.cagr(returns)
    try:
        daily_rf = risk_free_rate / 252
        ann_return = (1 + returns.mean())**252 - 1
        ann_vol = returns.std() * np.sqrt(252)

        if ann_vol == 0:
            metrics["sharpe"] = np.nan
        else:
            metrics["sharpe"] = (ann_return - risk_free_rate) / ann_vol

    except Exception:
        metrics["sharpe"] = np.nan
    try:
        downside = returns[returns < daily_rf]

        if downside.empty:
            metrics["sortino"] = np.nan
        else:
            downside_vol = downside.std() * np.sqrt(252)
            metrics["sortino"] = (ann_return - risk_free_rate) / downside_vol

    except Exception:
        metrics["sortino"] = np.nan
    try:
        roll_max = portfolio_value.cummax()
        drawdown = (portfolio_value - roll_max) / roll_max
        metrics["max_dd"] = drawdown.min()
    except Exception:
        metrics["max_dd"] = np.nan

    if buy_price and latest_price and shares and buy_date_actual:
        total_invested = 0.0
        total_current = 0.0
        latest_buy_date = None

        for t in buy_price:
            bp = buy_price.get(t)
            lp = latest_price.get(t)
            sh = shares.get(t, 0)
            bdt = buy_date_actual.get(t)

            if bp not in (None, 0) and lp not in (None, 0) and sh > 0:
                total_invested += bp * sh
                total_current += lp * sh

                if bdt is not None:
                    if latest_buy_date is None or bdt > latest_buy_date:
                        latest_buy_date = bdt

        if total_invested > 0:
            investor_cum_return = (total_current / total_invested) - 1
        else:
            investor_cum_return = 0.0

        metrics["cumulative_return"] = investor_cum_return

        if latest_buy_date:
            days = (pd.Timestamp.today() - latest_buy_date).days
            years = days / 365.0

            if years > 0:
                investor_cagr = (total_current / total_invested) ** (1 / years) - 1
            else:
                investor_cagr = 0.0
        else:
            investor_cagr = 0.0

        metrics["cagr"] = investor_cagr

    return metrics


def safe_float(x):
    try:
        if x is None:
            return np.nan
        return float(x)
    except Exception:
        return np.nan


def compute_rsi(series: pd.Series, period: int = 14) -> pd.Series:

    if isinstance(series, pd.DataFrame):
        series = series.iloc[:, 0]

    s = series.astype(float).dropna()
    if len(s) < period + 1:
        return pd.Series(index=series.index, dtype=float)

    delta = s.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)

    avg_gain = gain.ewm(alpha=1/period, adjust=False).mean()
    avg_loss = loss.ewm(alpha=1/period, adjust=False).mean()

    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    rsi = rsi.reindex(series.index)
    return rsi


def get_rsi_category(rsi_value):
    try:
        if rsi_value is None or (isinstance(rsi_value, float) and np.isnan(rsi_value)):
            return None
        r = float(rsi_value)
        if r >= 70:
            return "Overbought"
        elif r <= 30:
            return "Oversold"
        else:
            return "Neutral"
    except Exception:
        return None
    

def compute_adx(df, period=14):
    high = df["High"]
    low = df["Low"]
    close = df["Close"]

    plus_dm = high.diff()
    minus_dm = low.diff().abs()

    plus_dm = np.where((plus_dm > minus_dm) & (plus_dm > 0), plus_dm, 0)
    minus_dm = np.where((minus_dm > plus_dm) & (minus_dm > 0), minus_dm, 0)

    tr1 = high - low
    tr2 = (high - close.shift()).abs()
    tr3 = (low - close.shift()).abs()
    tr = np.maximum.reduce([tr1, tr2, tr3])

    atr = pd.Series(tr).rolling(period).mean()

    pdi = 100 * (pd.Series(plus_dm).rolling(period).mean() / atr)
    ndi = 100 * (pd.Series(minus_dm).rolling(period).mean() / atr)

    dx = (abs(pdi - ndi) / (pdi + ndi)) * 100
    adx = dx.rolling(period).mean()
    return adx


def classify_trend(df):
    close = df["Close"]

    ma20 = close.rolling(20).mean()
    ma50 = close.rolling(50).mean()

    slope20 = ma20.diff()

    adx = compute_adx(df).iloc[-1]

    last = close.iloc[-1]
    last_ma20 = ma20.iloc[-1]
    last_ma50 = ma50.iloc[-1]
    ma20_slope = slope20.iloc[-1]

    if adx > 25:  
        if last > last_ma20 and last > last_ma50 and ma20_slope > 0:
            return "Strong Bullish"
        elif last > last_ma20 and ma20_slope > 0:
            return "Bullish"
        elif last < last_ma20 and last < last_ma50 and ma20_slope < 0:
            return "Strong Bearish"
        elif last < last_ma20 and ma20_slope < 0:
            return "Bearish"
    else:
        if abs(last - last_ma20) / last < 0.01:  
            return "Range-Bound"
        elif last > last_ma20:
            return "Weak Bullish"
        else:
            return "Weak Bearish"
    return "Neutral"


def compute_position_health(price_dict: dict):

    records = []

    for t, df in (price_dict or {}).items():
        if df is None or (hasattr(df, "empty") and df.empty):
            continue

        try:
            df = df[["High", "Low", "Close"]].dropna().astype(float)
        except Exception:
            continue

        if df.empty:
            continue

        close = df["Close"]

        rsi_series = compute_rsi(close)
        rsi = None
        if not rsi_series.empty:
            rsi_valid = rsi_series.dropna()
            if not rsi_valid.empty:
                try:
                    rsi = float(rsi_valid.iloc[-1])
                except Exception:
                    rsi = None

        rsi_cat = get_rsi_category(rsi) if rsi is not None else None

        trend_class = classify_trend(df)

        momentum_20d = None
        if len(close) > 20:
            try:
                prev = float(close.iloc[-20])
                if prev != 0:
                    momentum_20d = (float(close.iloc[-1]) - prev) / prev
                else:
                    momentum_20d = None
            except Exception:
                momentum_20d = None

        high_52w = None
        low_52w = None

        if len(df) >= 252:
            try:
                window = df.iloc[-252:]
                high_52w = float(window["High"].max())
                low_52w = float(window["Low"].min())

            except Exception:
                high_52w = None
                low_52w = None

        last_price = None
        try:
            last_price = float(df["Close"].iloc[-1])
        except Exception:
            last_price = None

        pct_from_high = None
        pct_from_low = None
        if last_price is not None and high_52w not in (None, 0):
            try:
                pct_from_high = (last_price - high_52w) / high_52w
            except Exception:
                pct_from_high = None
        if last_price is not None and low_52w not in (None, 0):
            try:
                pct_from_low = (last_price - low_52w) / low_52w
            except Exception:
                pct_from_low = None

        records.append({"Ticker": t,
                        "Trend": trend_class,
                        "RSI": rsi,
                        "RSI Category": rsi_cat,
                        "20D Momentum %": momentum_20d,
                        "52W High": high_52w,
                        "% from 52W High": pct_from_high,
                        "52W Low": low_52w, 
                        "% from 52W Low": pct_from_low})
    df = pd.DataFrame(records)
    return df


def portfolio_unrealized_pnl(price_df: pd.DataFrame, shares: dict, buy_price: dict, buy_date: dict):
    if price_df is None or price_df.empty:
        return pd.DataFrame()

    tickers = [t for t in price_df.columns if t in shares]
    if not tickers:
        return pd.DataFrame()

    pnl_df = pd.DataFrame(index=price_df.index)
    total_pnl = pd.Series(0.0, index=price_df.index)

    for t in tickers:
        s = shares.get(t, 0)
        bp = safe_float(buy_price.get(t)) if buy_price is not None else None
        if bp is None or s == 0:
            continue
        per_share = price_df[t].astype(float) - float(bp)
        series_pnl = per_share * float(s)
        total_pnl = total_pnl.add(series_pnl, fill_value=0.0)

    pnl_df["Unrealized_PnL"] = total_pnl
    return pnl_df


def compute_stock_risk_metrics(price_df: pd.DataFrame, market_df: pd.DataFrame):
    if price_df.empty or market_df.empty:
        return pd.DataFrame()
    
    try:
        market_returns = market_df["Close"].pct_change().dropna()
    except Exception:
        return pd.DataFrame()

    returns = price_df.pct_change().dropna()
    records = []
    
    for t in price_df.columns:
        ser = returns[t].dropna()
        if ser.empty:
            continue

        combined = pd.concat([ser, market_returns], axis=1).dropna()
        if combined.empty:
            continue

        stock_rtn = combined.iloc[:, 0]
        mkt_rtn = combined.iloc[:, 1]

        vol = stock_rtn.std() * np.sqrt(252)
        cov = np.cov(stock_rtn, mkt_rtn)[0][1]
        var_pf = np.var(mkt_rtn)
        beta = cov / var_pf if var_pf != 0 else np.nan
        cumulative = (1 + stock_rtn).cumprod()
        rolling_max = cumulative.cummax()
        drawdown = (cumulative - rolling_max) / rolling_max
        max_dd = drawdown.min()
        var_95 = np.percentile(stock_rtn, 5)
        cvar_95 = stock_rtn[stock_rtn <= var_95].mean() if not ser.empty else np.nan

        records.append({"Ticker": t,
                        "Volatility (Annualized)": vol,
                        "Beta": beta,
                        "Max Drawdown": max_dd,
                        "VaR 95%": var_95,
                        "CVaR 95%": cvar_95,
                        "Returns": stock_rtn})

    df = pd.DataFrame(records)
    df = df.dropna(subset=["Ticker"])
    return df


def compute_rolling_metrics(returns: pd.Series, window: int = 60, risk_free_rate: float = 0.068):
    daily_rf = risk_free_rate / 252
    excess = returns - daily_rf
    rolling_mean = excess.rolling(window).mean()
    roll_std = excess.rolling(window).std()

    rolling_vol = roll_std * np.sqrt(252)
    rolling_sharpe = ((rolling_mean * 252) / (roll_std* np.sqrt(252)))
    return rolling_vol, rolling_sharpe

