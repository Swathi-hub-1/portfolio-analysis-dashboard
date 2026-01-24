import streamlit as st
import pandas as pd
from utils.charts import bubble_chart, box_chart, bar_chart
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
        return None, None
    start = series.iloc[0]
    end = series.iloc[-1]
    years = len(series) - 1
    if start <= 0 or years <= 0:
        return None, None
    cagr_y = ((end / start) ** (1 / years) - 1) * 100
    return cagr_y, years


def safe_divide(a, b):
    if a is None or b is None or b==0:
        return None
    return a / b


def fundamental_insights(valid_tickers, latest_price):
        st.markdown("<h2 style='text-align:center; color:#7161ef;'>Fundamental Strength & Valuation</h2>", unsafe_allow_html=True)
        st.markdown("<hr style='opacity:0.2;'>", unsafe_allow_html=True)
        
        rows_1 = []
        rows_2 = []
        bs_strength = []
        du_pont = []

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
            
            net_income_series = available_series(income,["Net Income",   
                                                     "Net Income Common Stockholders",
                                                     "Net Income Applicable To Common Shares"])

            revenue_series = available_series(income,["Total Revenue",
                                                  "Operating Revenue"])

            equity_series = available_series(balance,["Total Stockholder Equity",
                                                  "Stockholders Equity",
                                                  "Total Equity",
                                                  "Total Equity Gross Minority Interest"])
            
            total_debt = get_first_available(balance,["Total Debt",
                                                      "Long Term Debt"])
            
            current_asset = get_first_available(balance,["Current Assets",
                                                         "Total Assets"])

            current_liability = get_first_available(balance,["Current Liabilities",
                                                             "Total Liabilities"])
            
            cash = get_first_available(balance, ["Cash And Cash Equivalents",
                                                 "Cash Cash Equivalents And Short Term Investments"])
            
            ebit = get_first_available(income, ["EBIT",
                                                "Operating Income",])

            int_exp = get_first_available(income, ["Interest Expense"])

            total_asset = get_first_available(balance, ["Total Assets"])
            
            total_asset_series = available_series(balance, ["Total Assets"])

            if any(v is None for v in [net_income, revenue, equity, share_outstanding, price]):
                continue
            
            revenue_hist = income.loc["Total Revenue"].dropna().sort_index() if "Total Revenue" in income.index else None
            net_income_hist = income.loc["Net Income"].dropna().sort_index() if "Net Income" in income.index else None

            revenue_yoy = yoy_growth(revenue_hist)
            revenue_cagr, revenue_yrs = cagr(revenue_hist)
            ni_yoy = yoy_growth(net_income_hist)
            ni_cagr, ni_yrs = cagr(net_income_hist)

            market_cap = price * share_outstanding
            eps = safe_divide(net_income, share_outstanding) 
            pe = safe_divide(price, eps)
            book_value_per_share = safe_divide(equity, share_outstanding)
            pb = safe_divide(price, book_value_per_share) 

            cap_employed = equity + (total_debt - cash)
            roe = safe_divide(net_income, equity)
            roce = safe_divide(ebit, cap_employed)
            profit_margin = safe_divide(net_income, revenue)
            roa = safe_divide(net_income, total_asset) 

            debt_equity = safe_divide(total_debt, equity) 
            current_ratio = safe_divide(current_asset, current_liability)
            net_debt = total_debt - cash if cash is not None else total_debt
            interest_coverage = safe_divide(ebit, abs(int_exp))

            rows_1.append({"Symbol": t,
                        "Market Cap Display": format_market_cap(market_cap),
                        "Market Cap": market_cap,
                        "Revenue YOY (%)": round(revenue_yoy, 2),
                        f"Revenue CAGR ({revenue_yrs}Y)": round(revenue_cagr, 2) if revenue_cagr else None,
                        "Net Income YOY (%)": round(ni_yoy, 2),
                        f"Net Income CAGR ({ni_yrs}Y)": round(ni_cagr, 2) if ni_cagr else None,
                        "ROE (%)": round(roe * 100, 2),
                        "Profit Margin (%)": round(profit_margin * 100, 2),
                        "ROA (%)": round(roa * 100, 2),
                        "ROCE (%)": round(roce * 100, 2)})
            
            rows_2.append({"Symbol": t,
                           "EPS (TTM)": round(eps, 2),
                           "P/E Ratio": round(pe, 2) if pe else None,
                           "P/B Ratio": round(pb, 2) if pb else None,
                           "Debt / Equity": round(debt_equity, 2),
                           "Current Ratio": current_ratio,
                           "Interest Coverage": interest_coverage})
            
            bs_strength.append({"Symbol": t,
                                "Net Debt": format_market_cap(net_debt),
                                "Interest Coverage": interest_coverage})
        
            years = (net_income_series.index.intersection(revenue_series.index).intersection(equity_series.index).intersection(total_asset_series.index))

            for yr in sorted(years):
                margin = net_income_series[yr] / revenue_series[yr]
                asset_to = revenue_series[yr] / total_asset_series[yr]
                eq_multiplier = total_asset_series[yr] / equity_series[yr]
                roe_du = profit_margin * asset_to * eq_multiplier
                roa_du = profit_margin * asset_to

                du_pont.append({"Symbol": t,
                                "Year": yr.year,
                                "Net Profit Margin (%)": round(margin * 100, 2),
                                "Asset Turnover Ratio": round(asset_to, 2),
                                "Equity Multplier": round(eq_multiplier, 2),
                                "ROE (%)": round(roe_du * 100, 2),
                                "ROA (%)": round(roa_du * 100, 2)})
  
        business_df = pd.DataFrame(rows_1)
        if business_df.empty:
            st.warning("Insufficient fundamental data")
            return business_df
        
        financial_df = pd.DataFrame(rows_2)
        if financial_df.empty:
            st.warning("Insufficient fundamental data")
            return financial_df
        
        if not business_df.empty:
            avg_roe = business_df["ROE (%)"].dropna().mean()
            avg_margin = business_df["Profit Margin (%)"].dropna().mean()
            median_pe = financial_df["P/E Ratio"].dropna().median()
            median_pb = financial_df["P/B Ratio"].dropna().median()
            avg_de = financial_df["Debt / Equity"].dropna().mean()
            
            metric_row([("Avg ROE (%)", f"{avg_roe:.2f}%", None),
                        ("Avg Profit Margin (%)", f"{avg_margin:.2f}%", None),
                        ("Median P/E", f"{median_pe:.2f}", None),
                        ("Median P/B", f"{median_pb:.2f}", None),
                        ("Avg Debt/Equity", f"{avg_de:.2f}", None),])
            
            st.markdown("<hr style='opacity:0.2;'>", unsafe_allow_html=True)

        st.markdown("<h3 style='color:#7161ef;'>Business Performance & Growth Metrics</h3>", unsafe_allow_html=True)
        display_df = business_df.drop(columns=["Market Cap"])
        display_df = display_df.rename(columns={"Market Cap Display": "Market Cap"})

        st.dataframe(display_df, hide_index=True, width="stretch")
        st.markdown("<hr style='opacity:0.2;'>", unsafe_allow_html=True)

        st.markdown("<h3 style='color:#7161ef;'>DuPont Analysis</h3>", unsafe_allow_html=True)
        dupont_df = pd.DataFrame(du_pont)
        dupont_df = dupont_df.sort_values("Year").reset_index(drop=True)
        view_mode = st.segmented_control("", options=valid_tickers, selection_mode="single", default=valid_tickers[0])
        if view_mode:
            dupont_view = dupont_df[dupont_df["Symbol"] == view_mode]
        else:
            dupont_view = dupont_df
        dupont_view = dupont_view.sort_values("Year").tail(4)
        metrics = ["Net Profit Margin (%)", "Asset Turnover Ratio", "Equity Multplier", "ROE (%)", "ROA (%)"]
        pivot_df = (dupont_view.set_index("Year")[metrics].T.sort_index(axis=1))
        st.dataframe(pivot_df, width="stretch")
        st.markdown("<hr style='opacity:0.2;'>", unsafe_allow_html=True)

        st.markdown("<h3 style='color:#7161ef;'>Valuation & Financial Strength Metrics</h3>", unsafe_allow_html=True)

        st.dataframe(financial_df, hide_index=True, width="stretch")
        st.markdown("<hr style='opacity:0.2;'>", unsafe_allow_html=True)

        st.markdown("<h3 style='color:#7161ef;'>Quality Positioning (ROE vs Profit Margin)</h3>", unsafe_allow_html=True)
        business_df["Quality Bucket"] = pd.cut(business_df["ROE (%)"],
                                                   bins=[-float("inf"), 10, 20, float("inf")],
                                                   labels=["Low ROE", "Moderate ROE", "High ROE"])

        quality_df = business_df.dropna(subset=["ROE (%)", "Profit Margin (%)", "Market Cap", "Quality Bucket"])

        if not quality_df.empty:
            quality_df = quality_df.rename(columns={"Market Cap": "Market Cap"})
            fig_quality = bubble_chart(quality_df,
                                       x="ROE (%)",
                                       y="Profit Margin (%)",
                                       size="Market Cap",
                                       color="Quality Bucket",
                                       hover="Symbol",
                                       reference_line=True, 
                                      title=None)
            
            st.plotly_chart(fig_quality, width="stretch")
        else:
            st.info("Insufficient fundamental data to show quality bubble map.")
        st.markdown("<hr style='opacity:0.2;'>", unsafe_allow_html=True)

        st.markdown("<h3 style='color:#7161ef;'>Net debt & Interest coverage</h3>", unsafe_allow_html=True)
        bs_strength_df = pd.DataFrame(bs_strength)

        fig = bar_chart(bs_strength_df,
                            x="Net Debt",
                            y="Symbol",
                            color="Interest Coverage",
                            orientation="h",
                            show_text=True,
                            hover_col="Symbol",
                            title=None)
        fig.update_traces(texttemplate="",textposition="outside")
        fig.update_layout( xaxis_title="Net Debt (₹)", yaxis_title="", yaxis_tickformat=".1f", xaxis_tickangle=-25)
        st.plotly_chart(fig, width="stretch")

        st.markdown("<h3 style='color:#7161ef;'>Valuation Distribution (P/E & P/B)</h3>", unsafe_allow_html=True)
        val_box_df = financial_df[["Symbol", "P/E Ratio", "P/B Ratio"]].dropna()
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
        return business_df

