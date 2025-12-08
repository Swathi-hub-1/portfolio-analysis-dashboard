import streamlit as st
import pandas as pd
from utils.charts import bubble_chart, box_chart

def metric_row(items):
        cols = st.columns(len(items))
        for col, (label, value, delta) in zip(cols, items):
            if delta is None:
                col.metric(label, value)
            else:
                col.metric(label, value, delta)

def fundamental_insights(valid_tickers, info_dict):
        st.markdown("<h2 style='text-align:center; color:#a2d2ff;'>Fundamental Strength & Valuation</h2>", unsafe_allow_html=True)
        st.markdown("<hr style='opacity:0.2;'>", unsafe_allow_html=True)

        rows = []
        for t in valid_tickers:
            info = info_dict.get(t, {}) or {}
            
            rows.append({"Symbol": t,
                         "Company": info.get("companyName"),
                         "Sector": info.get("sector"),
                         "Market Cap (₹T)": round(info.get("mktCap", 0) / 1e12, 3,) if info.get("marketCap") else None,
                         "P/E Ratio": info.get("priceEarningsRatio"),
                        #  "Forward P/E": info.get("forwardPE"),
                         "P/B Ratio": info.get("priceToBookRatio"),
                         "EPS (TTM)": info.get("eps"),
                         "ROE (%)": round(info.get("returnOnEquityTTM", 0) * 100, 2) if info.get("returnOnEquity") else None,
                         "Profit Margin (%)": round(info.get('profitMargins', 0) * 100, 2) if info.get('profitMargins') else None,})
        fundamentals_df = pd.DataFrame(rows)

        if not fundamentals_df.empty:
            avg_roe = fundamentals_df["ROE (%)"].dropna().mean()
            avg_margin = fundamentals_df["Profit Margin (%)"].dropna().mean()
            median_pe = fundamentals_df["P/E Ratio"].dropna().median()
            median_pb = fundamentals_df["P/B Ratio"].dropna().median()

            metric_row([("Avg ROE (%)", f"{avg_roe:.2f}%", None),
                        ("Avg Profit Margin (%)", f"{avg_margin:.2f}%", None),
                        ("Median P/E", f"{median_pe:.2f}", None),
                        ("Median P/B", f"{median_pb:.2f}", None),])
            
            st.markdown("<hr style='opacity:0.2;'>", unsafe_allow_html=True)
        
        st.subheader("Company Fundamentals")
        st.dataframe(fundamentals_df, hide_index=True, width="stretch")
        st.markdown("<hr style='opacity:0.2;'>", unsafe_allow_html=True)

        quality_df = fundamentals_df.dropna(subset=["ROE (%)", "Profit Margin (%)", "Market Cap (₹T)", "Sector"])

        if not quality_df.empty:
            quality_df = quality_df.rename(columns={"Market Cap (₹T)": "Market Cap"})
            fig_quality = bubble_chart(quality_df,
                                       x="ROE (%)",
                                       y="Profit Margin (%)",
                                       size="Market Cap",
                                       color="Sector",
                                       hover="Symbol",
                                      title="Quality Positioning (ROE vs Profit Margin)")
            
            st.plotly_chart(fig_quality, width="stretch")
        else:
            st.info("Insufficient fundamental data to show quality bubble map.")
        st.markdown("<hr style='opacity:0.2;'>", unsafe_allow_html=True)

        val_box_df = fundamentals_df[["Symbol", "P/E Ratio", "P/B Ratio"]].dropna()
        if not val_box_df.empty:
            melted = val_box_df.melt(id_vars="Symbol",
                                     value_vars=["P/E Ratio", "P/B Ratio"],
                                     var_name="Metric",
                                     value_name="Value")

            fig = box_chart(melted,
                            x_col="Metric",
                            y_col="Value",
                            hover_label_col="Symbol",
                            title="Valuation Distribution (P/E & P/B)")
            st.plotly_chart(fig, width="stretch")
        return fundamentals_df
