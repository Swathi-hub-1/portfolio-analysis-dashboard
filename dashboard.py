import streamlit as st
import pandas as pd
import numpy as np
import io
import os
from datetime import datetime
import plotly.express as px

from utils.data_fetch import load_tickers, fetch_all_data, fetch_fundamentals 
from utils.analytics import portfolio_value_from_prices, compute_portfolio_metrics, safe_float, compute_position_health, compute_stock_risk_metrics, portfolio_unrealized_pnl, compute_rolling_metrics
from utils.charts import pie_chart, line_chart, area_chart, box_chart, scatter_plot, heatmap_chart, bubble_chart, dual_axis_line_chart
from utils.ui import apply_custom_css, header, sidebar_config, home_page, color_gain_loss, color_rsi_category, color_trend_class

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
    search = st.sidebar.text_input("Search (Symbol or Company)", placeholder="Type symbol or company...")
    if search:
        s = search.lower()
        matched = tickers_df[tickers_df.apply(lambda r: s in str(r["Symbol"]).lower() or s in str(r["Company Name"]).lower(), axis=1)]
        if not matched.empty:
            sel = st.sidebar.selectbox("Matches", matched.apply(lambda r: f"{r['Symbol']} — {r['Company Name']}", axis=1).tolist())
            sym = sel.split(" — ")[0]
            if st.sidebar.button("➕ Add Ticker"):
                if sym not in st.session_state.selected_tickers:
                    st.session_state.selected_tickers.append(sym)
                    st.sidebar.success(f"Added {sym}")
        else:
            st.sidebar.info("No matches found.")

portfolio = st.sidebar.multiselect("Your Portfolio List:", options=st.session_state.selected_tickers, default=st.session_state.selected_tickers)
st.session_state.selected_tickers = portfolio

if not portfolio:
    home_page()
    st.stop()

shares = {}
date_ranges = {}
for t in portfolio:
    with st.sidebar.expander(f"{t} Settings", expanded=False):
        start_end = st.sidebar.date_input(f"Date range {t}", value=(pd.to_datetime("2022-01-01"), pd.Timestamp.today()))
        date_ranges[t] = (pd.to_datetime(start_end[0]), pd.to_datetime(start_end[1]))
        shares[t] = st.sidebar.number_input(f"{t} Shares", min_value=0, value=10, step=1)

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

    share_values = {t: safe_float(latest_price.get(t)) * float(shares.get(t, 0)) for t in valid_tickers}
    total_value = float(sum(share_values.values())) if share_values else 0.0
    weights = {t: (share_values[t] / total_value if total_value > 0 else 0.0) for t in valid_tickers}

    gain_pct = {}
    gain_val = {}
    for t in valid_tickers:
        bp = buy_price.get(t)
        lp = latest_price.get(t)
        gain_pct[t] = ((lp - bp) / bp) if (bp and lp) else np.nan
        gain_val[t] = (lp-bp) if (bp and lp) else np.nan

    best_stock = max(gain_pct, key=lambda k: gain_pct.get(k, -np.inf)) if gain_pct else None
    worst_stock = min(gain_pct, key=lambda k: gain_pct.get(k, np.inf)) if gain_pct else None

   
    tabs = st.tabs(["Overview", "Risk Analysis", "Fundamentals Insight", "Dividends & Income", "Report"])

    def metric_row(items):
        cols = st.columns(len(items))
        for col, (label, value, delta) in zip(cols, items):
            if delta is None:
                col.metric(label, value)
            else:
                col.metric(label, value, delta)

    with tabs[0]:
        st.markdown("<h2 style='text-align:center; color:#0096c7;'>Portfolio Overview</h2>", unsafe_allow_html=True)
        st.markdown("<hr style='opacity:0.2;'>", unsafe_allow_html=True)
        metric_row([
            ("Best Performer", best_stock or "–", f"{gain_pct.get(best_stock, 0):.2%}" if best_stock else None),
            ("Portfolio Value", f"₹{total_value:,.2f}", None),
            ("Cumulative Return", f"{metrics['cumulative_return']:.2%}", None),
            ("CAGR", f"{metrics['cagr']:.2%}", None),
            ("Worst Performer", worst_stock or "–", f"{gain_pct.get(worst_stock, 0):.2%}" if worst_stock else None),
        ])
        st.markdown("<hr style='opacity:0.2;'>", unsafe_allow_html=True)

        pf_summary_table = pd.DataFrame({
            "Ticker": valid_tickers,
            "Shares": [shares[t] for t in valid_tickers],
            "Buy Date": [pd.to_datetime(date_ranges[t][0]).date() for t in valid_tickers],
            "Buy Price (₹)": [safe_float(buy_price.get(t)) for t in valid_tickers],
            "Latest Price (₹)": [safe_float(latest_price.get(t)) for t in valid_tickers],
            "Gain/Loss %": [gain_pct.get(t) for t in valid_tickers],
            "Gain/Loss (₹)": [gain_val.get(t) for t in valid_tickers],
            "Share Value (₹)": [share_values.get(t) for t in valid_tickers],
            "Weights %": [weights.get(t, 0) * 100 for t in valid_tickers]
        }).sort_values("Share Value (₹)", ascending=False).reset_index(drop=True)
        pf_summary_table.index += 1
        pf_summary_table.index.name = 'Sl. No.'

        st.subheader("Portfolio Summary")
        st.dataframe(pf_summary_table.style.format({
            'Buy Price (₹)': '₹{:,.2f}',
            'Latest Price (₹)': '₹{:,.2f}',
            'Gain/Loss %': '{:.2%}',
            'Gain/Loss (₹)': '₹{:,.2f}',
            'Share Value (₹)': '₹{:,.2f}',
            'Weights %': '{:.2f}%'
        }).map(color_gain_loss, subset=["Gain/Loss %", "Gain/Loss (₹)"]), width="stretch")
        st.markdown("<hr style='opacity:0.2;'>", unsafe_allow_html=True)

        health_df = compute_position_health(price_dict)
        gains_df = pd.DataFrame({"Ticker": list(gain_pct.keys())})

        if not health_df.empty:
            merged = health_df.merge(gains_df, on="Ticker", how="left")
        else:
            merged = gains_df

        def fmt_pct(x):
            try:
                if x is None or (isinstance(x, float) and np.isnan(x)):
                    return "-"
                return f"{x:.2%}"
            except Exception:
                return "-"

        display_df = merged.copy()
        for c in ["RSI", "20D Momentum %", "52W High", "% from 52W High", "52W Low", "% from 52W Low"]:
            if c in display_df.columns:
                display_df[c] = display_df[c].apply(lambda v: np.nan if v in (None, "None", "-") else safe_float(v))

        st.subheader("Position Health")
        st.dataframe(
            display_df.style.format({
                "RSI": "{:.2f}",
                "20D Momentum %": "{:.2%}",
                "52W High": "{:.2f}",
                "% from 52W High": "{:.2%}",
                "52W Low": "{:.2f}",
                "% from 52W Low": "{:.2%}"
                }).map(color_rsi_category, subset=["RSI Category"])
                .map(color_trend_class, subset=["Trend"]), hide_index=True, width="stretch")
        st.markdown("<hr style='opacity:0.2;'>", unsafe_allow_html=True)

        if valid_tickers:
            labels = [f"{t} ({share_values[t]:,.0f} ₹)" for t in valid_tickers]
            vals = [weights[t] * 100 for t in valid_tickers]
            fig = pie_chart(labels, vals, title="Portfolio Allocation by Value")
            st.plotly_chart(fig, width="stretch")
            st.markdown("<hr style='opacity:0.2;'>", unsafe_allow_html=True)
        
        try:
            view_mode = st.segmented_control("Unrealized P/L View", ["Portfolio", "Per Stock"], default="Portfolio")
            pnl_df = portfolio_unrealized_pnl(price_df[valid_tickers] if not price_df.empty else pd.DataFrame(), shares, buy_price, buy_date_actual)
            if view_mode == "Portfolio":
                if not pnl_df.empty:
                    pnl_df = pnl_df.dropna()
                    if not pnl_df.empty:
                        pnl_df_reset = pnl_df.reset_index().rename(columns={"index": "Date"})
                        fig_pnl = line_chart(pnl_df_reset, x="Date", y="Unrealized_PnL", title="Unrealized P/L (₹)", labels={"Unrealized_PnL": "Unrealized P/L (₹)"})
                        st.plotly_chart(fig_pnl, width="stretch")
                    else:
                        st.info("Not enough data to compute Unrealized P/L.")
                else:
                    st.info("Unrealized P/L data not available.")
        
            elif view_mode == "Per Stock":
                per_stock_lines = pd.DataFrame(index=price_df.index)

                for t in valid_tickers:
                    s = shares.get(t, 0)
                    bp = safe_float(buy_price.get(t))
                    if s and bp is not None and t in price_df.columns:
                        per_share = price_df[t].astype(float) - bp
                        per_stock_lines[t] = per_share * s

                if not per_stock_lines.empty:
                    per_stock_reset = per_stock_lines.reset_index().rename(columns={"index": "Date"})
                    fig_stock_lines = line_chart(
                        per_stock_reset,
                        x="Date",
                        y=list(per_stock_lines.columns),
                        title="Per Stock Unrealized P/L Over Time"
                    )

                    fig_stock_lines.update_yaxes(title_text="Unrealized P/L (₹)")
                    st.plotly_chart(fig_stock_lines, width="stretch")
                else:
                    st.info("Not enough data to compute per-stock P/L trend.")
        
        except Exception as e:
            st.warning(f"Unrealized P/L error: {e}")
        st.markdown("<hr style='opacity:0.2;'>", unsafe_allow_html=True)

        combined = []
        for t in valid_tickers:
            ser = price_df[t].loc[price_df[t].index >= date_ranges[t][0]]
            df_temp = pd.DataFrame({"Date": ser.index, "Close Price (₹)": ser.values, "Ticker": t})
            combined.append(df_temp)
        if combined:
            hist_df = pd.concat(combined, ignore_index=True)
            view_mode = st.segmented_control("Performance View", ["Price", "Indexed (Base 100)", "Cumulative Returns"], default="Price")
            hist_df["Indexed"] = hist_df["Close Price (₹)"] / hist_df.groupby("Ticker")["Close Price (₹)"].transform("first") * 100
            df_hist = hist_df.copy()
            if view_mode == "Price":
                fig_hist = line_chart(
                    df_hist,
                    x="Date",
                    y="Close Price (₹)",
                    color="Ticker",
                    markers=False,
                    labels={"Close Price (₹)": "Price (₹)", "Date": "Date"},
                    title="Historical Price Chart"
                )

            elif view_mode == "Indexed (Base 100)":
                df_hist["Indexed"] = (
                    df_hist["Close Price (₹)"] /
                    df_hist.groupby("Ticker")["Close Price (₹)"].transform("first")
                ) * 100

                fig_hist = line_chart(
                    df_hist,
                    x="Date",
                    y="Indexed",
                    color="Ticker",
                    markers=False,
                    labels={"Indexed": "Performance (Base 100)", "Date": "Date"},
                    title="Indexed Performance (Base 100)"
                )

            else:
                df_hist["Returns"] = df_hist.groupby("Ticker")["Close Price (₹)"].pct_change()

                df_hist["Cumulative"] = df_hist.groupby("Ticker")["Returns"].transform(
                    lambda x: (1 + x.fillna(0)).cumprod()
                )

                fig_hist = line_chart(
                    df_hist,
                    x="Date",
                    y="Cumulative",
                    color="Ticker",
                    markers=False,
                    labels={"Cumulative": "Cumulative Growth (x)", "Date": "Date"},
                    title="Cumulative Returns Over Time"
                )
            st.plotly_chart(fig_hist, width="stretch")
        else:
            st.info("No historical data to plot for the selected date ranges.")
        st.markdown("<hr style='opacity:0.2;'>", unsafe_allow_html=True)

    with tabs[1]:
        st.markdown("<h2 style='text-align:center; color:#0096c7;'>Risk Analysis</h2>", unsafe_allow_html=True)
        st.markdown("<hr style='opacity:0.2;'>", unsafe_allow_html=True)
        metric_row([
            ("Annualized Volatility", f"{metrics['volatility']:.2%}", None),
            ("Sharpe", f"{metrics['sharpe']:.2f}", None),
            ("Sortino", f"{metrics['sortino']:.2f}", None),
            ("Max Drawdown", f"{metrics['max_dd']:.2%}", None)
        ])
        st.markdown("<hr style='opacity:0.2;'>", unsafe_allow_html=True)

        risk_df = compute_stock_risk_metrics(price_df[valid_tickers], market_df = st.session_state.loaded_data["market_df"])

        if not risk_df.empty:
            display_risk_df = risk_df[[
                "Ticker", 
                "Volatility (Annualized)", 
                "Beta", 
                "Max Drawdown", 
                "VaR 95%", 
                "CVaR 95%"
            ]].copy()
            st.subheader("Risk Breakdown Table")
            st.dataframe(
                display_risk_df.style.format({
                    "Volatility (Annualized)": "{:.2%}",
                    "Beta": "{:.2f}",
                    "Max Drawdown": "{:.2%}",
                    "VaR 95%": "{:.2%}",
                    "CVaR 95%": "{:.2%}"
                }), hide_index=True, width="stretch")
        else:
            st.info("Insufficient data for stock-wise risk metrics.")
        st.markdown("<hr style='opacity:0.2;'>", unsafe_allow_html=True)

        if not pf_returns.empty:
            dd = pf_returns.to_drawdown_series()
            fig_dd = area_chart(dd.index, dd.values, title="Portfolio Drawdown History")
            st.plotly_chart(fig_dd, width="stretch")
        else:
            st.info("Insufficient returns data for drawdown chart.")
        st.markdown("<hr style='opacity:0.2;'>", unsafe_allow_html=True)

        if not risk_df.empty:
            rr_df = pd.DataFrame({
                "Ticker": risk_df["Ticker"],
                "Volatility": risk_df["Volatility (Annualized)"],
                "Returns": [ser.mean() * 252 for ser in risk_df["Returns"]]
            })

            fig_rr = scatter_plot(
                df=rr_df,
                x="Volatility",
                y="Returns",
                color=None,          
                hover="Ticker",
                trendline=None,      
                title="Risk vs Return — Annualized"
            )

            st.plotly_chart(fig_rr, width="stretch")
        else:
            st.info("Not enough data for Risk/Return scatter plot.")
        st.markdown("<hr style='opacity:0.2;'>", unsafe_allow_html=True)

        if not price_df.empty:
            corr = price_df[valid_tickers].pct_change().dropna().corr()
            fig_corr = heatmap_chart(corr, title="Correlation Matrix (Returns)")
            st.plotly_chart(fig_corr, width="stretch")
        else:
            st.info("Correlation heatmap cannot be created (no price data).")

        rolling_vol, rolling_sharpe = compute_rolling_metrics(metrics["returns"], window=60)
        df_roll = pd.DataFrame({
            "Date": metrics["returns"].index,
            "Rolling Vol": rolling_vol,
            "Rolling Sharpe": rolling_sharpe
        })

        fig_rolling = dual_axis_line_chart(
            df_roll,
            x="Date",
            y1="Rolling Vol",
            y2="Rolling Sharpe",
            y1_name="Rolling Volatility",
            y2_name="Rolling Sharpe Ratio",
            title="Rolling Volatility & Sharpe"
        )
        st.plotly_chart(fig_rolling, width="stretch")


    with tabs[2]:
        st.markdown("<h2 style='text-align:center; color:#a2d2ff;'>Fundamentals Insight</h2>", unsafe_allow_html=True)
        st.markdown("<hr style='opacity:0.2;'>", unsafe_allow_html=True)

        def get_first_available(df, possible_labels):
            if df is None or df.empty:
                return None

            for label in possible_labels:
                if label in df.index:
                    try:
                        return float(df.loc[label].iloc[0])
                    except Exception:
                        return None
            return None


        def format_market_cap(value):
            if value is None:
                return "N/A"
            units = [("T", 1e12), ("B", 1e9), ("M", 1e6), ("K", 1e3)]
            for suffix, factor in units:
                if value >= factor:
                    return f"₹{round(value / factor, 2)} {suffix}"
            return str(value)
        
        rows = []
        for t in valid_tickers:
            fs = fetch_fundamentals(t)
            if not fs:
                continue
             
            income = fs.get("income")
            balance = fs.get("balance")
            share_outstanding = fs.get("s_o")
            price = latest_price.get(t)

            net_income = get_first_available(income,["Net Income",   
                                                     "Net Income Common Stockholders",
                                                     "Net Income Applicable To Common Shares"])

            revenue = get_first_available(income,["Total Revenue",
                                                  "Operating Revenue"])

            equity = get_first_available(balance,["Total Stockholder Equity",
                                                  "Stockholders Equity",
                                                  "Total Equity",
                                                  "Total Equity Gross Minority Interest"])
            
            if any(v is None for v in [net_income, revenue, equity, share_outstanding, price]):
                continue

            eps = net_income / share_outstanding if share_outstanding else None
            pe = price / eps if eps and eps !=0 else None

            book_value_per_share = equity / share_outstanding
            pb = price / book_value_per_share if book_value_per_share else None

            roe = net_income / equity
            profit_margin = net_income / revenue

            market_cap = price * share_outstanding

            rows.append({"Symbol": t,
                        "Market Cap Display": format_market_cap(market_cap),
                        "Market Cap": market_cap,
                        "EPS (TTM)": round(eps, 2),
                        "P/E Ratio": round(pe, 2) if pe else None,
                        "P/B Ratio": round(pb, 2) if pb else None,
                        "ROE (%)": round(roe * 100, 2),
                        "Profit Margin (%)": round(profit_margin * 100, 2)})
        fundamentals_df = pd.DataFrame(rows)

        if not fundamentals_df.empty:
            avg_roe = fundamentals_df["ROE (%)"].dropna().mean()
            avg_margin = fundamentals_df["Profit Margin (%)"].dropna().mean()
            median_pe = fundamentals_df["P/E Ratio"].dropna().median()
            median_pb = fundamentals_df["P/B Ratio"].dropna().median()

            metric_row([
                ("Avg ROE (%)", f"{avg_roe:.2f}%", None),
                ("Avg Profit Margin (%)", f"{avg_margin:.2f}%", None),
                ("Median P/E", f"{median_pe:.2f}", None),
                ("Median P/B", f"{median_pb:.2f}", None),
            ])
            st.markdown("<hr style='opacity:0.2;'>", unsafe_allow_html=True)
        
        st.subheader("Fundamental Health")
        display_df = fundamentals_df.drop(columns=["Market Cap"])
        display_df = display_df.rename(columns={"Market Cap Display": "Market Cap"})

        st.dataframe(display_df, hide_index=True, width="stretch")        
        quality_df = fundamentals_df.dropna(subset=["ROE (%)", "Profit Margin (%)", "Market Cap", "Quality Bucket"])

        if not quality_df.empty:
            quality_df = quality_df.rename(columns={"Market Cap": "Market Cap"})
            fig_quality = bubble_chart(
                quality_df,
                x="ROE (%)",
                y="Profit Margin (%)",
                size="Market Cap",
                color="Quality Bucket",
                hover="Symbol",
                title="Quality Map (ROE vs Profit Margin)"
            )
            st.plotly_chart(fig_quality, width="stretch")
        else:
            st.info("Insufficient fundamental data to show quality bubble map.")
        st.markdown("<hr style='opacity:0.2;'>", unsafe_allow_html=True)

        val_box_df = fundamentals_df[["Symbol", "P/E Ratio", "P/B Ratio"]].dropna()
        if not val_box_df.empty:
            melted = val_box_df.melt(
                id_vars="Symbol",
                value_vars=["P/E Ratio", "P/B Ratio"],
                var_name="Metric",
                value_name="Value"
            )

            fig = box_chart(
                melted,
                x_col="Metric",
                y_col="Value",
                hover_label_col="Symbol",
                title="Portfolio Valuation Distribution (P/E & P/B)"
            )

            st.plotly_chart(fig, width="stretch")
            st.markdown("<hr style='opacity:0.2;'>", unsafe_allow_html=True)


    with tabs[3]:
        st.markdown("<h2 style='text-align:center; color:#0096c7;'>Dividends & Income</h2>", unsafe_allow_html=True)
        st.markdown("<hr style='opacity:0.2;'>", unsafe_allow_html=True)
        div_rows = []
        total_portfolio_dividend = 0

        for t in valid_tickers:
            divs = div_dict.get(t)
            if divs is None or divs.empty:
                divs = pd.Series(dtype=float)

            start_dt = pd.to_datetime(date_ranges[t][0])
            div_index_tz = getattr(divs.index, "tz", None)
            if div_index_tz is not None:
                if start_dt.tzinfo is None:
                    start_dt = start_dt.tz_localize(div_index_tz)
                else:
                    start_dt = start_dt.tz_convert(div_index_tz)
            else:
                if getattr(start_dt, "tzinfo", None) is not None:
                    start_dt = start_dt.tz_convert(None)

            if not divs.empty:
                try:
                    div_since_buy = divs.loc[divs.index >= start_dt].sum()
                except Exception:
                    try:
                        divs_naive = divs.copy()
                        divs_naive.index = divs_naive.index.tz_localize(None)
                        start_dt_naive = pd.to_datetime(start_dt).tz_localize(None) if getattr(start_dt, "tzinfo", None) is not None else pd.to_datetime(start_dt)
                        div_since_buy = divs_naive.loc[divs_naive.index >= start_dt_naive].sum()
                    except Exception:
                        div_since_buy = 0.0
            else:
                div_since_buy = 0.0

            if not divs.empty:

                try:
                    one_year_ago = pd.Timestamp.now(tz=divs.index.tz) - pd.DateOffset(years=1) if getattr(divs.index, "tz", None) is not None else pd.Timestamp.now() - pd.DateOffset(years=1)
                    last_year_div = divs.loc[divs.index >= one_year_ago].sum()
                except Exception:
                    last_year_div = 0.0
            else:
                last_year_div = 0.0

            try:
                last_ex_dividend = divs.index[-1].date() if divs is not None and not divs.empty else None
            except:
                last_ex_dividend = None

            if not divs.empty:
                try:
                    annual_div = divs.resample("YE").sum()
                    if len(annual_div) > 1 and annual_div.iloc[0] > 0:
                        periods = len(annual_div) - 1
                        div_cagr = ((annual_div.iloc[-1] / annual_div.iloc[0]) ** (1 / periods) - 1) * 100
                    else:
                        div_cagr = None
                except:
                    div_cagr = None
            else:
                div_cagr = None

            buy_p = buy_price.get(t) or 0.0
            yoc = (last_year_div / buy_p) * 100 if buy_p else 0.0
            current_yield = (last_year_div / latest_price.get(t)) * 100 if latest_price.get(t) else 0.0
            total_income = float(div_since_buy) * float(shares.get(t, 0))
            projected_annual_income = last_year_div * shares.get(t, 0)
            total_portfolio_dividend += projected_annual_income

            div_rows.append({
                "Ticker": t,
                "Shares": shares.get(t, 0),
                "Ex-Date": last_ex_dividend.strftime("%b %d, %Y") if last_ex_dividend else "-",
                "Last 12M Div (₹)": float(last_year_div),
                "Total Dividend Since Buy (₹)": round(total_income, 2),
                "YOC (%)": round(yoc, 2),
                "Div Yield (%)": round(current_yield, 2),
                "Projected Div (₹)": round(projected_annual_income, 2),
                "Dividend CAGR (%)": round(div_cagr, 2) if div_cagr else None,
            })
        div_df = pd.DataFrame(div_rows)

        st.subheader("Income & Yield Summary")
        st.dataframe(div_df, hide_index=True, width="stretch")
        st.markdown("<hr style='opacity:0.2;'>", unsafe_allow_html=True)

        if not div_df.empty and div_df["Total Dividend Since Buy (₹)"].sum() > 0:
            fig_income = pie_chart(div_df["Ticker"].tolist(), div_df["Total Dividend Since Buy (₹)"].tolist(), title="Income Contribution by Stock")
            st.plotly_chart(fig_income, width="stretch")
        else:
            st.info("No dividend income to visualize for the selected holdings/date ranges.")
        st.markdown("<hr style='opacity:0.2;'>", unsafe_allow_html=True)

        combined = []
        for t in valid_tickers:
            divs = div_dict.get(t)
            if divs is not None and not divs.empty:
                df_temp = pd.DataFrame({
                    "Date": divs.index,
                    "Dividend (₹)": divs.cumsum(),
                    "Ticker": t
                })
                combined.append(df_temp)
        if combined:
            cum_div_df = pd.concat(combined, ignore_index=True)
            fig_cum = line_chart(
                cum_div_df,
                x="Date",
                y="Dividend (₹)",
                color="Ticker",
                markers=True,
                title="Cumulative Dividend Income Over Time",
                labels={"Date": "Date", "Dividend (₹)": "Cumulative Dividend (₹)"}
            )
            st.plotly_chart(fig_cum, width="stretch")
            st.markdown("<hr style='opacity:0.2;'>", unsafe_allow_html=True)

        fig_bar = px.bar(
            div_df,
            x="Ticker",
            y="Last 12M Div (₹)",
            text="Div Yield (%)",
            color="Dividend CAGR (%)",
            color_continuous_scale=px.colors.sequential.Viridis,
            template="plotly_dark",
            title="Dividend per Share vs Dividend Yield & Growth"
        )
        fig_bar.update_traces(texttemplate="%{text:.2f}%", textposition="outside")
        st.plotly_chart(fig_bar, width="stretch")
        st.markdown("<hr style='opacity:0.2;'>", unsafe_allow_html=True)

    with tabs[4]:
        st.markdown("<h2 style='text-align:center; color:#0096c7;'>Export Reports & Insights</h2>", unsafe_allow_html=True)
        st.markdown("<p style='text-align:center; color:#0096c7;'>Export your portfolio analytics as an Excel summary or QuantStats report.</p>", unsafe_allow_html=True)

        try:
            buffer = io.BytesIO()
            with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
                if not pf_summary_table.empty:
                    pf_summary_table.to_excel(writer, index=False, sheet_name="Portfolio_Summary")
                if "fundamentals_df" in locals() and not fundamentals_df.empty:
                    fundamentals_df.to_excel(writer, index=False, sheet_name="Fundamentals")
                if not div_df.empty:
                    div_df.to_excel(writer, index=False, sheet_name="Dividends")
            buffer.seek(0)
            st.download_button("📘 Download Excel Summary", data=buffer.getvalue(), file_name="Portfolio_Summary.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        except Exception as e:
            st.warning(f"Could not export Excel: {e}")

        if not pf_returns.empty:
            try:
                import quantstats as qs
                import tempfile
                tmpdir = tempfile.TemporaryDirectory()
                report_path = os.path.join(tmpdir.name, "portfolio_report.html")
                qs.reports.html(pf_returns, output=report_path, title="Portfolio Performance Report")
                with open(report_path, "r", encoding="utf-8") as f:
                    html_data = f.read()
                st.download_button("📊 Download QuantStats HTML Report", data=html_data, file_name="Portfolio_Report.html", mime="text/html")
                tmpdir.cleanup()
            except Exception as e:
                st.warning(f"Could not generate QuantStats report: {e}")

    st.success("✅ Analysis ready — downloads won't wipe generated results (cached & preserved).")

else:
    st.info('Click "Generate Analysis" in the sidebar to pull data and compute metrics.')

