import streamlit as st
import pandas as pd
import numpy as np

def metric_row(items):
        cols = st.columns(len(items))
        for col, (label, value, delta) in zip(cols, items):
            if delta is None:
                col.metric(label, value)
            else:
                col.metric(label, value, delta)


def get_first_available(df, possible_labels):
    if df is None or df.empty:
        return None

    for label in possible_labels:
        if label in df.index:
            try:
                val = df.loc[label].iloc[0]
                return float(val) if pd.notna(val) else None
            except Exception:
                return None
    return None


def available_series(df, possible_labels):
    if df is None or df.empty:
        return None

    for label in possible_labels:
        if label in df.index:
            try:
                return df.loc[label]
            except Exception:
                return None
    return None


def format_market_cap(value):
    if value in (None, 0) or pd.isna(value):
        return "N/A"
    units = [("T", 1e12), ("B", 1e9), ("M", 1e6), ("K", 1e3)]
    for suffix, factor in units:
        if value >= factor:
            return f"₹{round(value / factor, 2)} {suffix}"
    return str(value)


def yoy_growth(series):
    if series is None or len(series) < 2:
        return None
    latest, previous = series.iloc[-1], series.iloc[-2]
    if previous == 0:
        return None
    return (latest / previous - 1) * 100


def cagr(series, min_yrs=3 ):
    if series is None or len(series) < min_yrs + 1:
        return np.nan, min_yrs
    start = series.iloc[0]
    end = series.iloc[-1]
    years = len(series) - 1
    if start <= 0 or years <= 0:
        return np.nan, years
    cagr_y = ((end / start) ** (1 / years) - 1) * 100
    return cagr_y, years


def safe_float(x):
    try:
        if x is None:
            return np.nan
        return float(x)
    except Exception:
        return np.nan
    

def safe_divide(a, b):
    if a is None or b is None or b==0:
        return None
    return a / b

def safe_round(value, multiplier=1, decimal=2):
    if value is None:
        return None
    return round(value * multiplier, decimal)


def safe_subtract(a, b):
    if a is None or b is None:
        return None
    return a - b


def safe_margin(n, d):
    if d == 0 or n is None or d is None:
        return None
    return round((n / d) * 100, 2)
