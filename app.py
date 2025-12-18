import streamlit as st
import pandas as pd
from utils.ui import apply_custom_css, header, sidebar_config, home_page
from utils.data_fetch import load_tickers, fetch_all_data
from utils.analytics import portfolio_value_from_prices, compute_portfolio_metrics



st.set_page_config(page_title='Portfolio Analysis Dashboard', layout='wide')
apply_custom_css()
header()
sidebar_config()

if 'selected_tickers' not in st.session_state:
    st.session_state.selected_tickers = []
if 'generated' not in st.session_state:
    st.session_state.generated = False
if 'active_tab' not in st.session_state:
    st.session_state.active_tab = 0

tickers_df = load_tickers("Tickers.xlsx")

if not tickers_df.empty:
    search = st.sidebar.text_input("Search Stocks", placeholder="Search Ticker or Company...")
    if search:
        s = search.lower()
        matched = tickers_df[tickers_df.apply(lambda r: s in str(r["Symbol"]).lower() or s in str(r["Company Name"]).lower(), axis=1)]
        if not matched.empty:
            sel = st.sidebar.selectbox("Matching Results", matched.apply(lambda r: f"{r['Symbol']} — {r['Company Name']}", axis=1).tolist())
            sym = sel.split(" — ")[0]
            if st.sidebar.button("➕ Add Ticker"):
                if sym not in st.session_state.selected_tickers:
                    st.session_state.selected_tickers.append(sym)
                    st.sidebar.success(f"Added {sym}")
                else:
                    st.sidebar.info("Already added.")
        else:
            st.sidebar.info("No matches found.")

portfolio = st.sidebar.multiselect("Selected Tickers:", options=st.session_state.selected_tickers, default=st.session_state.selected_tickers)
st.session_state.selected_tickers = portfolio

if not portfolio:
    home_page()
    st.stop()

shares = {}
date_ranges = {}
for t in portfolio:
    with st.sidebar.expander(f"{t} Configuration", expanded=False):
        start_end = st.date_input(f"Holding Period {t}", value=(pd.to_datetime("2022-01-01"), pd.Timestamp.today()))
        date_ranges[t] = (pd.to_datetime(start_end[0]), pd.to_datetime(start_end[1]))
        shares[t] = st.number_input(f"Quantity Held {t}", min_value=0, value=10, step=1)

if st.sidebar.button("🚀 Generate Analysis"):
    st.session_state.generated = True
    st.session_state.loaded_data = None

if not st.session_state.generated:
    home_page()
    st.stop()
    
if st.session_state.generated:
    with st.spinner("Fetching & preparing data..."):
        data_bundle = fetch_all_data(portfolio, date_ranges)
        st.session_state.loaded_data = data_bundle

    price_df = st.session_state.loaded_data["price_df"]
    price_dict = st.session_state.loaded_data["price_dict"]
    div_dict = st.session_state.loaded_data["div_dict"]
    buy_price = st.session_state.loaded_data["buy_price"]
    buy_date_actual = st.session_state.loaded_data["buy_date_actual"]
    latest_price = st.session_state.loaded_data["latest_price"]
    missing = st.session_state.loaded_data["missing"]

    if missing:
        st.warning(f"No price data for: {', '.join(missing)}. They will be skipped in calculations.")

    valid_tickers = [c for c in price_df.columns if c in portfolio] if not price_df.empty else []

    pf_value = portfolio_value_from_prices(price_df[valid_tickers] if not price_df.empty else pd.DataFrame(), shares)
    metrics = compute_portfolio_metrics(pf_value,  buy_price=buy_price, latest_price=latest_price, shares=shares, buy_date_actual=buy_date_actual)
    pf_returns = metrics.get("returns", pd.Series(dtype=float))

    tab1, tab2, tab3, tab4, tab5 = st.tabs(["Overview", "Risk Analysis", "Fundamentals Insight", "Dividends & Income", "Report"])

    with tab1:
        from tabs.overview import overview
        pf_summary_table = overview(price_df, shares, metrics, buy_price, latest_price, buy_date_actual, valid_tickers, date_ranges, price_dict)

    with tab2:
        from tabs.risk import risk_analysis
        risk_analysis(metrics, price_df, valid_tickers, pf_returns)

    with tab3:
        from tabs.fundamentals import fundamental_insights
        fundamentals_df = fundamental_insights(valid_tickers, latest_price)

    with tab4:
        from tabs.dividends import dividend_income
        div_df = dividend_income(valid_tickers, div_dict, date_ranges, buy_price, latest_price, shares)

    with tab5:
        from tabs.reports import report
        report(pf_summary_table, fundamentals_df, div_df, pf_returns)

