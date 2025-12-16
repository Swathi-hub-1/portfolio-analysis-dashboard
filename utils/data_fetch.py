import yfinance as yf
import pandas as pd
import streamlit as st
import requests
import os
from dotenv import load_dotenv
from typing import Tuple, Dict

load_dotenv() 

@st.cache_data(show_spinner=False)
def load_tickers(path: str = "Tickers.xlsx") -> pd.DataFrame:
    try:
        df = pd.read_excel(path)
    except Exception:
        return pd.DataFrame(columns=["Symbol", "Company Name"])

    df = df.rename(columns=lambda c: c.strip())
    expected = ["Symbol", "Company Name"]
    for col in expected:
        if col not in df.columns:
            df[col] = ""

    df["Symbol"] = df["Symbol"].astype(str).str.strip().str.upper()
    df["Company Name"] = df["Company Name"].astype(str).fillna("").str.strip()
    df = df[df["Symbol"] != ""].drop_duplicates(subset=["Symbol"])
    df = df.reset_index(drop=True)
    return df[["Symbol", "Company Name"]]


@st.cache_data(show_spinner=False)
def download_price_series(ticker: str, start: pd.Timestamp, end: pd.Timestamp) -> pd.Series:
    try:
        df = yf.download(ticker, start=start, end=end, progress=False, auto_adjust=False)
        if df is None or df.empty:
             return pd.DataFrame(columns=["High", "Low", "Close"])
        df = df[["High", "Low", "Close"]].sort_index()
        df.columns = ["High", "Low", "Close"]
        return df
    except Exception:
        return pd.DataFrame(columns=["High", "Low", "Close"])


@st.cache_data(show_spinner=False)
def fetch_fundamentals(ticker: str) -> dict:
    try:
        t = yf.Ticker(ticker)
        income = t.financials
        balance = t.balance_sheet
        shares = t.get_shares_full()
        shares_outstanding = shares[-1] if shares is not None and not shares.empty else None
        return{"income": income,
               "balance": balance,
               "s_o": shares_outstanding}
    except Exception:
        return{}

   
@st.cache_data(show_spinner=False)
def fetch_dividends(ticker: str) -> pd.Series:
    try:
        t = yf.Ticker(ticker)
        div = t.dividends
        if div is None:
            return pd.Series(dtype=float)
        return div.sort_index()
    except Exception:
        return pd.Series(dtype=float)
    

def first_price_after(series: pd.Series, start_dt: pd.Timestamp):
    if series is None or series.empty:
        return (None, None)
    mask = series.index >= pd.to_datetime(start_dt)
    s = series.loc[mask]
    if not s.empty:
        return (s.index[0], float(s.iloc[0]))
    return (series.index[0], float(series.iloc[0]))


@st.cache_data(show_spinner=False)
def fetch_all_data(tickers: list, date_ranges: Dict[str, Tuple[pd.Timestamp, pd.Timestamp]]):
    starts = []
    ends = []
    for t in tickers:
        if t in date_ranges:
            s, e = date_ranges[t]
            starts.append(pd.to_datetime(s))
            ends.append(pd.to_datetime(e))
    if not starts:
        starts = [pd.Timestamp.now() - pd.DateOffset(years=5)]
    if not ends:
        ends = [pd.Timestamp.now()]

    global_start = min(starts)
    global_end = max(ends) + pd.Timedelta(days=1)

    price_dict = {}
    div_dict = {}
    buy_price = {}
    buy_date_actual = {}
    latest_price = {}
    missing = []

    try:
        market_df = download_price_series("^NSEI", global_start, global_end)
    except Exception:
        market_df = pd.DataFrame(columns=["High", "Low", "Close"])

    for t in tickers:
        ser = download_price_series(t, global_start, global_end)
        if ser is None or ser.empty:
            missing.append(t)
            price_dict[t] = pd.Series(dtype=float, name=t)
            div_dict[t] = pd.Series(dtype=float)
            buy_price[t] = None
            buy_date_actual[t] = None
            latest_price[t] = None
            continue

        price_dict[t] = ser
        div = fetch_dividends(t)
        div_dict[t] = div

        if t in date_ranges:
            s_dt = pd.to_datetime(date_ranges[t][0])
        else:
            s_dt = ser.index[0]

        idx, p = first_price_after(ser["Close"], s_dt)
        buy_date_actual[t] = idx
        buy_price[t] = p
        latest_price[t] = float(ser["Close"].iloc[-1]) if (ser is not None and not ser.empty) else None

    available_close = [df["Close"].rename(t) for t, df in price_dict.items() if not df.empty]
    if available_close:
        price_df = pd.concat(available_close, axis=1).sort_index()
        price_df = price_df.loc[~price_df.index.duplicated(keep="first")]
        price_df = price_df.ffill(limit=5).dropna(axis=1, how="all")
    else:
        price_df = pd.DataFrame()

    return {"price_df": price_df,
            "price_dict": price_dict,
            "div_dict": div_dict,
            "buy_price": buy_price,
            "buy_date_actual": buy_date_actual,
            "latest_price": latest_price,
            "market_df": market_df, 
            "missing": missing}