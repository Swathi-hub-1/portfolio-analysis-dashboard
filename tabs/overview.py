import streamlit as st
import pandas as pd
import numpy as np
from utils.analytics import compute_position_health, portfolio_unrealized_pnl, safe_float
from utils.charts import pie_chart, line_chart
from utils.ui import color_rsi_category, color_gain_loss, color_trend_class 


def metric_row(items):
        cols = st.columns(len(items))
        for col, (label, value, delta) in zip(cols, items):
            if delta is None:
                col.metric(label, value)
            else:
                col.metric(label, value, delta)


def overview(price_df, shares, metrics, buy_price, latest_price, buy_date_actual, valid_tickers, date_ranges, price_dict):
        st.markdown("<h2 style='text-align:center; color:#a2d2ff;'>Portfolio Summary Overview</h2>", unsafe_allow_html=True)
        st.markdown("<hr style='opacity:0.2;'>", unsafe_allow_html=True)

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
        
        metric_row([("Top Performer", best_stock or "–", f"{gain_pct.get(best_stock, 0):.2%}" if best_stock else None),
                    ("Portfolio Value", f"₹{total_value:,.2f}", None),
                    ("Cumulative Return", f"{metrics['cumulative_return']:.2%}", None),
                    ("Portfolio CAGR", f"{metrics['cagr']:.2%}", None),
                    ("Worst Performer", worst_stock or "–", f"{gain_pct.get(worst_stock, 0):.2%}" if worst_stock else None),])
        
        st.markdown("<hr style='opacity:0.2;'>", unsafe_allow_html=True)

        pf_summary_table = pd.DataFrame({"Ticker": valid_tickers,
                                         "Shares": [shares[t] for t in valid_tickers],
                                         "Buy Date": [pd.to_datetime(date_ranges[t][0]).date() for t in valid_tickers],
                                         "Buy Price (₹)": [safe_float(buy_price.get(t)) for t in valid_tickers],
                                         "Latest Price (₹)": [safe_float(latest_price.get(t)) for t in valid_tickers],
                                         "Gain/Loss %": [gain_pct.get(t) for t in valid_tickers],
                                         "Gain/Loss (₹)": [gain_val.get(t) for t in valid_tickers],
                                         "Share Value (₹)": [share_values.get(t) for t in valid_tickers],
                                         "Weights %": [weights.get(t, 0) * 100 for t in valid_tickers]}).sort_values("Share Value (₹)", ascending=False).reset_index(drop=True)
        pf_summary_table.index += 1
        pf_summary_table.index.name = 'Sl. No.'

        st.subheader("Holdings Breakdown")
        st.dataframe(pf_summary_table.style.format({'Buy Price (₹)': '₹{:,.2f}',
                                                    'Latest Price (₹)': '₹{:,.2f}',
                                                    'Gain/Loss %': '{:.2%}',
                                                    'Gain/Loss (₹)': '₹{:,.2f}',
                                                    'Share Value (₹)': '₹{:,.2f}',
                                                    'Weights %': '{:.2f}%'}).map(color_gain_loss, subset=["Gain/Loss %", "Gain/Loss (₹)"]), width="stretch")
        
        st.markdown("<hr style='opacity:0.2;'>", unsafe_allow_html=True)

        health_df = compute_position_health(price_dict)
        gains_df = pd.DataFrame({"Ticker": list(gain_pct.keys())})

        if not health_df.empty:
            merged = health_df.merge(gains_df, on="Ticker", how="left")
        else:
            merged = gains_df

        display_df = merged.copy()
        for c in ["RSI", "20D Momentum %", "52W High", "% from 52W High", "52W Low", "% from 52W Low"]:
            if c in display_df.columns:
                display_df[c] = display_df[c].apply(lambda v: np.nan if v in (None, "None", "-") else safe_float(v))

        st.subheader("Technical Position Health")
        st.dataframe(
            display_df.style.format({"RSI": "{:.2f}",
                                     "20D Momentum %": "{:.2%}",
                                     "52W High": "{:.2f}",
                                     "% from 52W High": "{:.2%}",
                                     "52W Low": "{:.2f}",
                                     "% from 52W Low": "{:.2%}"}).map(color_rsi_category, subset=["RSI Category"]).map(color_trend_class, subset=["Trend"]), hide_index=True, width="stretch")
        
        st.markdown("<hr style='opacity:0.2;'>", unsafe_allow_html=True)

        if valid_tickers:
            labels = [f"{t} ({share_values[t]:,.0f} ₹)" for t in valid_tickers]
            vals = [weights[t] * 100 for t in valid_tickers]
            fig = pie_chart(labels, vals, title="Portfolio Allocation by Value")
            st.plotly_chart(fig, width="stretch")
            st.markdown("<hr style='opacity:0.2;'>", unsafe_allow_html=True)
        
        try:
            view_mode = st.segmented_control("Unrealized P/L View", ["Portfolio-Level", "Individual Stock"], default="Portfolio-Level")
            pnl_df = portfolio_unrealized_pnl(price_df[valid_tickers] if not price_df.empty else pd.DataFrame(), shares, buy_price, buy_date_actual)
            if view_mode == "Portfolio-Level":
                if not pnl_df.empty:
                    pnl_df = pnl_df.dropna()
                    if not pnl_df.empty:
                        pnl_df_reset = pnl_df.reset_index().rename(columns={"index": "Date"})
                        fig_pnl = line_chart(pnl_df_reset, x="Date", y="Unrealized_PnL", title="Unrealized P/L Trend", labels={"Unrealized_PnL": "Unrealized P/L (₹)"})
                        st.plotly_chart(fig_pnl, width="stretch")
                    else:
                        st.info("Not enough data to compute Unrealized P/L.")
                else:
                    st.info("Unrealized P/L data not available.")
        
            elif view_mode == "Individual Stock":
                per_stock_lines = pd.DataFrame(index=price_df.index)

                for t in valid_tickers:
                    s = shares.get(t, 0)
                    bp = safe_float(buy_price.get(t))
                    if s and bp is not None and t in price_df.columns:
                        start_dt = buy_date_actual.get(t)
                        per_share = price_df[t].loc[price_df.index >= start_dt].astype(float) - bp
                        per_stock_lines[t] = per_share * s

                if not per_stock_lines.empty:
                    per_stock_reset = per_stock_lines.reset_index().rename(columns={"index": "Date"})
                    fig_stock_lines = line_chart(per_stock_reset,
                                                 x="Date",
                                                 y=list(per_stock_lines.columns),
                                                 title="Unrealized P/L by Stock")
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
            view_mode = st.segmented_control("Performance View", ["Price Trend", "Indexed Performance (Base 100)"], default="Price Trend")
            hist_df["Indexed"] = hist_df["Close Price (₹)"] / hist_df.groupby("Ticker")["Close Price (₹)"].transform("first") * 100
            df_hist = hist_df.copy()
            if view_mode == "Price Trend":
                fig_hist = line_chart(df_hist,
                                      x="Date",
                                      y="Close Price (₹)",
                                      color="Ticker",
                                      markers=False,
                                      labels={"Close Price (₹)": "Price (₹)", "Date": "Date"},
                                      title="Price Trend – Historical")

            elif view_mode == "Indexed Performance (Base 100)":
                df_hist["Indexed"] = (df_hist["Close Price (₹)"] / df_hist.groupby("Ticker")["Close Price (₹)"].transform("first")) * 100

                fig_hist = line_chart(df_hist,
                                      x="Date",
                                      y="Indexed",
                                      color="Ticker",
                                      markers=False,
                                      labels={"Indexed": "Performance (Base 100)", "Date": "Date"},
                                      title="Indexed Performance (Base 100 = Start Value)")
            st.plotly_chart(fig_hist, width="stretch")
        else:
            st.info("No historical data to plot for the selected date ranges.")
        st.markdown("<hr style='opacity:0.2;'>", unsafe_allow_html=True)

        return pf_summary_table