import streamlit as st
import pandas as pd
from utils.analytics import compute_stock_risk_metrics, compute_rolling_metrics
from utils.charts import area_chart, scatter_plot, heatmap_chart, dual_axis_line_chart
from utils.ui import beta_color

def metric_row(items):
        cols = st.columns(len(items))
        for col, (label, value, delta) in zip(cols, items):
            if delta is None:
                col.metric(label, value)
            else:
                col.metric(label, value, delta)

def risk_analysis(metrics, price_df, valid_tickers, pf_returns):
        st.markdown("<h2 style='text-align:center; color:#7161ef;'>Risk & Volatility Analytics</h2>", unsafe_allow_html=True)
        st.markdown("<hr style='opacity:0.2;'>", unsafe_allow_html=True)
        
        metric_row([("Annualized Volatility", f"{metrics['volatility']:.2%}", None),
                    ("Sharpe Ratio", f"{metrics['sharpe']:.2f}", None),
                    ("Sortino Ratio", f"{metrics['sortino']:.2f}", None),
                    ("Max Drawdown", f"{metrics['max_dd']:.2%}", None)])
        
        st.markdown("<hr style='opacity:0.2;'>", unsafe_allow_html=True)

        risk_df = compute_stock_risk_metrics(price_df[valid_tickers], market_df = st.session_state.loaded_data["market_df"])

        if not risk_df.empty:
            display_risk_df = risk_df[["Ticker", 
                                       "Volatility (Annualized)", 
                                       "Beta", 
                                       "Max Drawdown", 
                                       "VaR 95%", 
                                       "CVaR 95%"]].copy()
            st.markdown("<h3 style=color:#7161ef;'>Stock-Level Risk Metrics</h3>", unsafe_allow_html=True)
            st.dataframe(display_risk_df.style.format({"Volatility (Annualized)": "{:.2%}",
                                                       "Beta": "{:.2f}",
                                                       "Max Drawdown": "{:.2%}",
                                                       "VaR 95%": "{:.2%}",
                                                       "CVaR 95%": "{:.2%}"}).map(beta_color, subset=["Beta"]), hide_index=True, width="stretch")
        else:
            st.info("Insufficient data for stock-wise risk metrics.")

        st.markdown("<hr style='opacity:0.2;'>", unsafe_allow_html=True)

        st.markdown("<h3 style=color:#7161ef;'>Drawdown History (From Peak)</h3>", unsafe_allow_html=True)
        if not pf_returns.empty:
            dd = pf_returns.to_drawdown_series()
            fig_dd = area_chart(dd.index, dd.values, title=None)
            st.plotly_chart(fig_dd, width="stretch")
        else:
            st.info("Insufficient returns data for drawdown chart.")
        st.markdown("<hr style='opacity:0.2;'>", unsafe_allow_html=True)
        
        st.markdown("<h3 style=color:#7161ef;'>Risk–Return Positioning (Annualized)</h3>", unsafe_allow_html=True)
        if not risk_df.empty:
            rr_df = pd.DataFrame({"Ticker": risk_df["Ticker"],
                                  "Volatility": risk_df["Volatility (Annualized)"],
                                  "Returns": [ser.mean() * 252 for ser in risk_df["Returns"]]})

            fig_rr = scatter_plot(df=rr_df,
                                  x="Volatility",
                                  y="Returns",
                                  color=None,          
                                  hover="Ticker",
                                  trendline=None,      
                                  title="")
            st.plotly_chart(fig_rr, width="stretch")
        else:
            st.info("Not enough data for Risk/Return scatter plot.")

        st.markdown("<hr style='opacity:0.2;'>", unsafe_allow_html=True)
        
        st.markdown("<h3 style=color:#7161ef;'>Correlation Matrix</h3>", unsafe_allow_html=True)
        if not price_df.empty:
            corr = price_df[valid_tickers].pct_change().dropna().corr()
            fig_corr = heatmap_chart(corr, title="")
            st.plotly_chart(fig_corr, width="stretch")
        else:
            st.info("Correlation heatmap cannot be created (no price data).")

        st.markdown("<h3 style=color:#7161ef;'>Rolling Volatility & Sharpe Ratio</h3>", unsafe_allow_html=True)
        rolling_vol, rolling_sharpe = compute_rolling_metrics(metrics["returns"], window=60)
        df_roll = pd.DataFrame({"Date": metrics["returns"].index,
                                "Rolling Vol": rolling_vol,
                                "Rolling Sharpe": rolling_sharpe})

        fig_rolling = dual_axis_line_chart(df_roll,
                                           x="Date",
                                           y1="Rolling Vol",
                                           y2="Rolling Sharpe",
                                           y1_name="Rolling Volatility",
                                           y2_name="Rolling Sharpe Ratio",
                                           title="")
        st.plotly_chart(fig_rolling, width="stretch")