import streamlit as st
import pandas as pd
from utils.data_fetch import fetch_fundamentals
from utils.helper import get_first_available, available_series, yoy_growth, cagr, safe_divide, safe_round, safe_subtract, metric_row, format_market_cap
from utils.charts import bubble_chart, box_chart, bar_chart
from utils.ui import interpretation_box


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
            income_q = fs.get("income_q")
            balance = fs.get("balance")
            shares_outstanding = fs.get("s_o")
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

            net_income_series = available_series(income,["Net Income",   
                                                         "Net Income Common Stockholders",
                                                         "Net Income Applicable To Common Shares"])

            revenue_series = available_series(income,["Total Revenue",
                                                      "Operating Revenue"])

            equity_series = available_series(balance,["Total Stockholder Equity",
                                                      "Stockholders Equity",
                                                      "Total Equity",
                                                      "Total Equity Gross Minority Interest"])
            
            total_asset_series = available_series(balance, ["Total Assets"])

            net_income_series_q = available_series(income_q,["Net Income"])

            if any(v is None for v in [net_income, revenue, equity, shares_outstanding, price]):
                continue
                        
            revenue_hist = income.loc["Total Revenue"].dropna().sort_index() if "Total Revenue" in income.index else None
            net_income_hist = income.loc["Net Income"].dropna().sort_index() if "Net Income" in income.index else None
            ni_q = net_income_series_q.sort_index().dropna().tail(4)
            ni_sum = ni_q.sum()
            sh_os = shares_outstanding.sort_index()
            sh_os.index = sh_os.index.tz_localize(None)
            sh_os = sh_os.to_frame(name="shares")
            start_d = ni_q.index.min()
            end_d = ni_q.index.max()

            share = sh_os.loc[start_d:end_d]

            if len(share) == 1:
                weighted_avg_shares = share.iloc[0, 0]
            else:
                share["next_date"] = share.index.to_series().shift(-1)
                share.iloc[-1, share.columns.get_loc("next_date")] = end_d

                share["days"] = (share["next_date"] - share.index).dt.days

                weighted_avg_shares = (share["shares"] * share["days"]).sum() / share["days"].sum()

            shares = shares_outstanding[-1] if shares_outstanding is not None and not shares_outstanding.empty else None
            
            revenue_yoy = yoy_growth(revenue_hist)
            revenue_cagr, revenue_yrs = cagr(revenue_hist)
            ni_yoy = yoy_growth(net_income_hist)
            ni_cagr, ni_yrs = cagr(net_income_hist)

            market_cap = price * shares
            eps = safe_divide(ni_sum, weighted_avg_shares) 
            pe = safe_divide(price, eps)
            book_value_per_share = safe_divide(equity, shares)
            pb = safe_divide(price, book_value_per_share) 

            cap_employed = safe_subtract(total_asset, current_liability)
            roe = safe_divide(net_income, equity)
            roce = safe_divide(ebit, cap_employed)
            profit_margin = safe_divide(net_income, revenue)
            roa = safe_divide(net_income, total_asset) 

            debt_equity = safe_divide(total_debt, equity) 
            current_ratio = safe_divide(current_asset, current_liability)
            net_debt = safe_subtract(total_debt, cash)            
            interest_coverage = safe_divide(ebit, abs(int_exp))

            rows_1.append({"Symbol": t,
                        "Market Cap Display": format_market_cap(market_cap),
                        "Market Cap": market_cap,
                        "Revenue YOY (%)": safe_round(revenue_yoy),
                        f"Revenue CAGR ({revenue_yrs}Y)": safe_round(revenue_cagr) if revenue_cagr else None,
                        "Net Income YOY (%)": safe_round(ni_yoy),
                        f"Net Income CAGR ({ni_yrs}Y)": safe_round(ni_cagr) if ni_cagr else None,
                        "ROE (%)": safe_round(roe, 100),
                        "Profit Margin (%)": safe_round(profit_margin, 100),
                        "ROA (%)": safe_round(roa, 100),
                        "ROCE (%)": safe_round(roce, 100)})
            
            rows_2.append({"Symbol": t,
                           "EPS (TTM)": safe_round(eps),
                           "P/E Ratio": safe_round(pe) if pe else None,
                           "P/B Ratio": safe_round(pb) if pb else None,
                           "Debt / Equity": safe_round(debt_equity),
                           "Current Ratio": safe_round(current_ratio),
                           "Interest Coverage": safe_round(interest_coverage)})
            
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
                                "Net Profit Margin (%)": safe_round(margin, 100),
                                "Asset Turnover Ratio": safe_round(asset_to),
                                "Equity Multplier": safe_round(eq_multiplier),
                                "ROE (%)": safe_round(roe_du, 100),
                                "ROA (%)": safe_round(roa_du, 100)})
  
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

