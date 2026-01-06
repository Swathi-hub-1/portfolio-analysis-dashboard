import streamlit as st
import pandas as pd
import numpy as np
from utils.analytics import compute_stock_risk_metrics, compute_rolling_metrics
from utils.charts import area_chart, scatter_plot, heatmap_chart, dual_axis_line_chart
from utils.ui import beta_color, interpretation_box

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
                    ("Max Drawdown", f"{abs(metrics['max_dd']):.2%}", None)])
        
        st.markdown("<hr style='opacity:0.2;'>", unsafe_allow_html=True)

        risk_df = compute_stock_risk_metrics(price_df[valid_tickers], market_df = st.session_state.loaded_data["market_df"])

        if not risk_df.empty:
            display_risk_df = risk_df[["Ticker", 
                                       "Volatility (Annualized)", 
                                       "Beta", 
                                       "Max Drawdown", 
                                       "VaR 95%", 
                                       "CVaR 95%"]].copy()
            st.markdown("<h3 style='color:#7161ef;'>Stock-Level Risk Metrics</h3>", unsafe_allow_html=True)
            st.dataframe(display_risk_df.style.format({"Volatility (Annualized)": "{:.2%}",
                                                       "Beta": "{:.2f}",
                                                       "Max Drawdown": "{:.2%}",
                                                       "VaR 95%": "{:.2%}",
                                                       "CVaR 95%": "{:.2%}"}).map(beta_color, subset=["Beta"]), hide_index=True, width="stretch")
        else:
            st.info("Insufficient data for stock-wise risk metrics.")

        st.markdown("<hr style='opacity:0.2;'>", unsafe_allow_html=True)

        st.markdown("<h3 style='color:#7161ef;'>Drawdown History (From Peak)</h3>", unsafe_allow_html=True)
        if not pf_returns.empty:
            dd = pf_returns.to_drawdown_series()
            fig_dd = area_chart(dd.index, dd.values, title=None)
            st.plotly_chart(fig_dd, width="stretch")
        else:
            st.info("Insufficient returns data for drawdown chart.")
        st.markdown("<hr style='opacity:0.2;'>", unsafe_allow_html=True)
        
        st.markdown("<h3 style='color:#7161ef;'>Risk–Return Positioning (Annualized)</h3>", unsafe_allow_html=True)
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
                                  title="",
                                  reference_line=True)
            st.plotly_chart(fig_rr, width="stretch")
        else:
            st.info("Not enough data for Risk/Return scatter plot.")

        st.markdown("<hr style='opacity:0.2;'>", unsafe_allow_html=True)
        
        st.markdown("<h3 style='color:#7161ef;'>Correlation Matrix</h3>", unsafe_allow_html=True)
        if not price_df.empty:
            corr = np.log(price_df[valid_tickers] / price_df[valid_tickers].shift(1)).dropna().corr()
            fig_corr = heatmap_chart(corr, title="")
            st.plotly_chart(fig_corr, width="stretch")
        else:
            st.info("Correlation heatmap cannot be created (no price data).")

        st.markdown("<h3 style='color:#7161ef;'>Rolling Volatility & Sharpe Ratio</h3>", unsafe_allow_html=True)
        rolling_vol, rolling_sharpe = compute_rolling_metrics(metrics["log_returns"], window=60)
        df_roll = pd.DataFrame({"Date": metrics["log_returns"].index,
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
        st.markdown("<hr style='opacity:0.2;'>", unsafe_allow_html=True)

        if metrics['sharpe'] is not None:
            if metrics['sharpe'] < 0:
                sharpe_performance = "underperforming"
            elif metrics['sharpe'] < 1.0:
                sharpe_performance = "inefficient"
            else:
                sharpe_performance = "efficient"
        
        vol = metrics['volatility'] * 100
        if metrics['volatility'] is not None:
            if vol <= 10:
                vol_performance = "low"
            elif vol <= 20 :
                vol_performance = "moderate"
            else:
                vol_performance = "high"

        dd_performance = "contained" if abs(metrics['max_dd']) <= -20 else "significant"

        corr_matrix = corr.values
        upper_tri = corr_matrix[np.triu_indices_from(corr_matrix, k=1)]
        avg_corr = np.nanmean(upper_tri)
        if avg_corr is not None:
            if avg_corr < 0.30:
                corr_performance = "well diversified"
            elif avg_corr < 0.60:
                corr_performance = "moderately diversified"
            else:
                corr_performance = "poorly diversified"

        rank_df = display_risk_df.dropna()
        rank_df["vol_rank"] = rank_df["Volatility (Annualized)"].rank(ascending=True)
        rank_df["beta_rank"] = rank_df["Beta"].rank(ascending=True)
        rank_df["dd_rank"] = rank_df["Max Drawdown"].rank(ascending=True)
        rank_df["var_rank"] = rank_df["VaR 95%"].rank(ascending=True)
        rank_df["cvar_rank"] = rank_df["CVaR 95%"].rank(ascending=True)
        rank_df["risk_score"] = (rank_df["vol_rank"] + rank_df["beta_rank"] + rank_df["dd_rank"] + rank_df["var_rank"] + rank_df["cvar_rank"])

        stable_stk = None
        risky_stk = None

        if len(rank_df) > 2:
            stable = rank_df.loc[rank_df["risk_score"].idxmin()] 
            risk = rank_df.loc[rank_df["risk_score"].idxmax()]

            stable_stk = stable["Ticker"]
            risky_stk = risk["Ticker"]

        summary = [f"{stable_stk} provides stability through lower volatility, beta, drawdown, and tail-risk measures, helping smooth overall portfolio fluctuations. In contrast, {risky_stk} contributes the highest risk, driven by elevated volatility, stronger market linkage, and deeper drawdowns",
                   
                   f"The portfolio exhibits {vol_performance} volatility, with a Sharpe ratio of {metrics['sharpe']:.2f}, indicating {sharpe_performance} risk-adjusted returns.", 

                   f"The maximum drawdown of {abs(metrics['max_dd']):.2%} suggests downside risk is {dd_performance}, while correlation analysis shows {corr_performance} across holdings.",]
                           
        interpretation_box("Risk Summary", summary)
