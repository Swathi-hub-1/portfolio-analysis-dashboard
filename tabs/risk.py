import streamlit as st
import pandas as pd
import numpy as np
from utils.analytics import compute_stock_risk_metrics, compute_rolling_metrics
from utils.helper import metric_row
from utils.charts import area_chart, scatter_plot, heatmap_chart, dual_axis_line_chart
from utils.ui import beta_color, interpretation_box


def risk_analysis(metrics, price_df, valid_tickers, pf_returns, pf_summary_table):
        st.markdown("<h2 style='text-align:center; color:#7161ef;'>Risk & Volatility Analytics</h2>", unsafe_allow_html=True)
        st.markdown("<hr style='opacity:0.2;'>", unsafe_allow_html=True)
        
        metric_row([("Annualized Volatility", f"{metrics['volatility']:.2%}", None),
                    ("Sharpe Ratio", f"{metrics['sharpe']:.2f}", None),
                    ("Sortino Ratio", f"{metrics['sortino']:.2f}", None),
                    ("Max Drawdown", f"{abs(metrics['max_dd']):.2%}", None)])
        
        st.markdown("<hr style='opacity:0.2;'>", unsafe_allow_html=True)

        risk_df = compute_stock_risk_metrics(price_df[valid_tickers], market_df = st.session_state.loaded_data["market_df"])

        st.markdown("<h3 style='color:#7161ef;'>Stock-Level Risk Metrics</h3>", unsafe_allow_html=True)
        if not risk_df.empty:
            display_risk_df = risk_df[["Ticker", "Volatility (Annualized)", "Beta", "Max Drawdown", "VaR 95%", "CVaR 95%"]].copy()
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
        
        st.markdown("<h3 style='color:#7161ef;'>Risk vs Return: Stock Positioning Map</h3>", unsafe_allow_html=True)
        if not risk_df.empty:
            rr_df = pd.DataFrame({"Ticker": risk_df["Ticker"],
                                  "Risk (Annualized Volatility)": risk_df["Volatility (Annualized)"],
                                  "Return (Annualized)": [ser.mean() * 252 for ser in risk_df["Returns"]]})
            
            fig_rr = scatter_plot(df=rr_df,
                                  x="Risk (Annualized Volatility)",
                                  y="Return (Annualized)",
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
        else:
            sharpe_performance = "unavailable"

        if metrics['sortino'] is not None:
            if metrics['sortino'] < 0:
                sortino_performance = "weak"
            elif metrics['sortino'] < 1.0:
                sortino_performance = "moderate"
            else:
                sortino_performance = "strong"
        else:
            sortino_performance = "unavailable"
      
        vol = metrics['volatility'] * 100
        if metrics['volatility'] is not None:
            if vol <= 10:
                vol_performance = "low"
            elif vol <= 20 :
                vol_performance = "moderate"
            else:
                vol_performance = "high"
        else:
            vol_performance = "unknown"
        
        stk_beta = risk_df[["Ticker", "Beta"]].dropna()
        stk_weights = pf_summary_table[["Ticker", "Weights %"]].dropna()
        beta_df = stk_beta.merge(stk_weights, on="Ticker", how="inner")
        beta_df["weight"] = beta_df["Weights %"] / 100
        pf_beta = (beta_df["weight"] * beta_df["Beta"]).sum()
        if pf_beta is not None:
            if pf_beta < 1:
                beta_performance = "defensive"
            elif pf_beta == 1:
                beta_performance = "market-aligned"
            else:
                beta_performance = "aggressive"
        else:
            beta_performance = "unclassified"

        dd_performance = "contained" if abs(metrics['max_dd']) <= 0.20 else "significant"
        
        display_risk_df = risk_df[["Ticker", "Volatility (Annualized)", "Beta", "Max Drawdown", "VaR 95%", "CVaR 95%"]].copy()
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

        tail_stk = rank_df.loc[rank_df["CVaR 95%"].idxmax()]
        tail_ticker = tail_stk["Ticker"]
        tail_value_row = pf_summary_table.loc[pf_summary_table["Ticker"] == tail_ticker, "Share Value (₹)"]
        tail_value = tail_value_row.iloc[0]
        tail_var = tail_stk["VaR 95%"]
        tail_cvar = tail_stk["CVaR 95%"]
        var_value = tail_var * tail_value 
        cvar_value = tail_cvar * tail_value
        tail_ratio = tail_cvar / tail_var if tail_var != 0 else np.nan

        if tail_ratio < 1.3:
            tail_risk_desc = "tail losses remain relatively contained beyond the VaR threshold"
        elif tail_ratio < 2.0:
            tail_risk_desc = "losses deepen meaningfully during extreme downside events"
        else:
            tail_risk_desc = "the portfolio is exposed to fat-tailed risk, with severe losses during stress periods"

        s_s_performance = "rewarded" if (metrics['sharpe'] >= 1 or metrics['sortino'] >= 1) else "only partially compensated"
        overall = "active market exposure and elevated volatility" if beta_performance == "aggressive" and vol_performance == "high" else "market-aligned movements with measured volatility" if beta_performance == "market-aligned" else "defensive positioning with controlled volatility"


        summary = [f"{stable_stk} emerges as the portfolio’s most stable position, ranking lowest across combined risk measures, thereby contributing to smoother overall portfolio behavior. " 
                   f"In contrast, {risky_stk} ranks highest contributing the highest risk, driven by elevated volatility, stronger market linkage, and deeper drawdowns",
                
                   f"At the portfolio level, volatility is assessed as {vol_performance}, with a Sharpe ratio of {metrics['sharpe']:.2f} indicating overall risk-adjusted performance is {sharpe_performance}, " 
                   f"and a Sortino ratio of {metrics['sortino']:.2f} reflects {sortino_performance} downside risk management.",

                   f"{tail_ticker} contributes the highest downside exposure. At the 95% confidence level, VaR implies a potential loss of {tail_var:.2%} (approximately ₹{var_value:,.0f}), " 
                   f"while CVaR increases to {tail_cvar:.2%} (around ₹{cvar_value:,.0f}) during extreme market conditions, indicating that {tail_risk_desc}.",

                   f"Overall risk structure suggests that portfolio fluctuations are primarily driven by {overall}, while drawdown behavior remains {dd_performance}. " 
                   f"Combined Sharpe and Sortino ratios suggest that portfolio's risk-taking has been {s_s_performance}, resulting in a {'balanced' if sharpe_performance == 'efficient' and sortino_performance == 'strong' else 'cautious'} overall risk profile."]
                       
        interpretation_box("Risk Summary", summary)
