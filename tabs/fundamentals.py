import streamlit as st
import pandas as pd
from utils.charts import bubble_chart, box_chart
from utils.data_fetch import fetch_fundamentals
from utils.ui import interpretation_box

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


def fundamental_insights(valid_tickers, latest_price):
        st.markdown("<h2 style='text-align:center; color:#7161ef;'>Fundamental Strength & Valuation</h2>", unsafe_allow_html=True)
        st.markdown("<hr style='opacity:0.2;'>", unsafe_allow_html=True)

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
            
            total_debt = get_first_available(balance,["Total Debt",
                                                      "Long Term Debt"])
            
            if any(v is None for v in [net_income, revenue, equity, share_outstanding, price]):
                continue

            eps = net_income / share_outstanding if share_outstanding else None
            pe = price / eps if eps and eps !=0 else None

            book_value_per_share = equity / share_outstanding
            pb = price / book_value_per_share if book_value_per_share else None

            roe = net_income / equity
            profit_margin = net_income / revenue
            debt_equity = total_debt / equity if total_debt else 0

            market_cap = price * share_outstanding

            rows.append({"Symbol": t,
                        "Market Cap Display": format_market_cap(market_cap),
                        "Market Cap": market_cap,
                        "ROE (%)": round(roe * 100, 2),
                        "Profit Margin (%)": round(profit_margin * 100, 2),
                        "Debt / Equity": round(debt_equity, 2),
                        "EPS (TTM)": round(eps, 2),
                        "P/E Ratio": round(pe, 2) if pe else None,
                        "P/B Ratio": round(pb, 2) if pb else None,})
                        
       
        fundamentals_df = pd.DataFrame(rows)

        if not fundamentals_df.empty:
            avg_roe = fundamentals_df["ROE (%)"].dropna().mean()
            avg_margin = fundamentals_df["Profit Margin (%)"].dropna().mean()
            median_pe = fundamentals_df["P/E Ratio"].dropna().median()
            median_pb = fundamentals_df["P/B Ratio"].dropna().median()
            avg_de = fundamentals_df["Debt / Equity"].dropna().mean()

            metric_row([("Avg ROE (%)", f"{avg_roe:.2f}%", None),
                        ("Avg Profit Margin (%)", f"{avg_margin:.2f}%", None),
                        ("Median P/E", f"{median_pe:.2f}", None),
                        ("Median P/B", f"{median_pb:.2f}", None),
                        ("Avg Debt/Equity", f"{avg_de:.2f}", None),])
            
            st.markdown("<hr style='opacity:0.2;'>", unsafe_allow_html=True)
        
        st.markdown("<h3 style=color:#7161ef;'>Company Fundamentals</h3>", unsafe_allow_html=True)
        display_df = fundamentals_df.drop(columns=["Market Cap"])
        display_df = display_df.rename(columns={"Market Cap Display": "Market Cap"})

        st.dataframe(display_df, hide_index=True, width="stretch")
        st.markdown("<hr style='opacity:0.2;'>", unsafe_allow_html=True)

        st.markdown("<h3 style=color:#7161ef;'>Quality Positioning (ROE vs Profit Margin)</h3>", unsafe_allow_html=True)
        fundamentals_df["Quality Bucket"] = pd.cut(fundamentals_df["ROE (%)"],
                                                   bins=[-float("inf"), 10, 20, float("inf")],
                                                   labels=["Low ROE", "Moderate ROE", "High ROE"])

        quality_df = fundamentals_df.dropna(subset=["ROE (%)", "Profit Margin (%)", "Market Cap", "Quality Bucket"])

        if not quality_df.empty:
            quality_df = quality_df.rename(columns={"Market Cap": "Market Cap"})
            fig_quality = bubble_chart(quality_df,
                                       x="ROE (%)",
                                       y="Profit Margin (%)",
                                       size="Market Cap",
                                       color="Quality Bucket",
                                       hover="Symbol",
                                      title=None)
            
            st.plotly_chart(fig_quality, width="stretch")
        else:
            st.info("Insufficient fundamental data to show quality bubble map.")
        st.markdown("<hr style='opacity:0.2;'>", unsafe_allow_html=True)

        st.markdown("<h3 style=color:#7161ef;'>Valuation Distribution (P/E & P/B)</h3>", unsafe_allow_html=True)
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
                            title=None)
            st.plotly_chart(fig, width="stretch")
            st.markdown("<hr style='opacity:0.2;'>", unsafe_allow_html=True)

            quality_label = "strong" if avg_roe > 15 else "moderate"
            valuation_label = "expensive" if median_pe > 25 else "reasonable"

            if median_pe < 15:
                style_label = "value"
            elif median_pe > 30:
                style_label = "growth/quality"
            else:
                style_label = "blend"

            summary =[f"On average, the portfolio companies generate an ROE of {avg_roe:.2f}% with healthy profit margins of {avg_margin:.2f}%, indicating {quality_label} business quality.", 
                      
                      f"Valuation multiples remain {valuation_label}, with a median P/E of {median_pe:.2f}, suggesting the portfolio is tilted toward {style_label} stocks."]
            
            interpretation_box("Fundamental Strength Summary", summary)
        return fundamentals_df
