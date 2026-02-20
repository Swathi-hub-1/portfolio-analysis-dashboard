import streamlit as st
import pandas as pd
import numpy as np
from utils.data_fetch import fetch_fundamentals
from utils.helper import get_first_available, available_series, yoy_growth, cagr, safe_divide, safe_round, safe_subtract, metric_row, format_market_cap, safe_margin
from utils.charts import bubble_chart, box_chart, bar_chart
from utils.ui import interpretation_box


def fundamental_insights(valid_tickers, latest_price):
        st.markdown("<h2 style='text-align:center; color:#7161ef;'>Fundamental Strength & Valuation</h2>", unsafe_allow_html=True)
        st.markdown("<hr style='opacity:0.2;'>", unsafe_allow_html=True)
        
        rows_1 = []
        rows_2 = []
        bs_strength = []
        du_pont = []
        summary = {}


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
                                                  "Total Equity"])
            
            total_debt = get_first_available(balance,["Total Debt",
                                                      "Long Term Debt"])
            
            total_asset = get_first_available(balance,["Total Assets"])
            
            current_asset = get_first_available(balance,["Current Assets"])

            current_liability = get_first_available(balance,["Current Liabilities"])
            
            cash = get_first_available(balance,["Cash And Cash Equivalents",
                                                "Cash Cash Equivalents And Short Term Investments"])
            
            ebit = get_first_available(income,["EBIT",
                                               "Operating Income",])

            int_exp = get_first_available(income,["Interest Expense"])

            net_income_series = available_series(income,["Net Income",   
                                                         "Net Income Common Stockholders",
                                                         "Net Income Applicable To Common Shares"])

            revenue_series = available_series(income,["Total Revenue",
                                                      "Operating Revenue"])

            equity_series = available_series(balance,["Total Stockholder Equity",
                                                      "Stockholders Equity",
                                                      "Total Equity",
                                                      "Total Equity Gross Minority Interest"])
            
            total_asset_series = available_series(balance,["Total Assets"])

            net_income_series_q = available_series(income_q,["Net Income"])

            if any(v is None for v in [net_income, revenue, equity, shares_outstanding, price]):
                continue
                        
            revenue_hist = income.loc["Total Revenue"].dropna().sort_index() if "Total Revenue" in income.index else None
            net_income_hist = income.loc["Net Income"].dropna().sort_index() if "Net Income" in income.index else None
            
            sh_os = shares_outstanding.sort_index()
            sh_os.index = sh_os.index.tz_localize(None)
            sh_os = sh_os.to_frame(name="shares")

            ni_q = None
            ni_sum = None
            ni_q_sh = None
            if net_income_series_q is not None and not net_income_series_q.empty:
                ni_q = net_income_series_q.sort_index().dropna().rolling(4) 
                ni_q_sh = net_income_series_q.sort_index().dropna().tail(4)
                ni_sum = ni_q.sum() 

            if ni_q_sh is not None and len(ni_q_sh) > 0:
                start_d = ni_q_sh.index.min()
                end_d = ni_q_sh.index.max()
            else:
                start_d = None
                end_d = None

            share = sh_os.loc[start_d:end_d]

            if share.empty:
                weighted_avg_shares = None
            elif len(share) == 1:
                weighted_avg_shares = share.iloc[0, 0]
            else:
                share = share.copy()
                share["next_date"] = share.index.to_series().shift(-1)
                share.iloc[-1, share.columns.get_loc("next_date")] = end_d

                share["days"] = (share["next_date"] - share.index).dt.days

                if share["days"].sum() > 0:
                    weighted_avg_shares = (share["shares"] * share["days"]).sum() / share["days"].sum()
                else:
                    weighted_avg_shares = None
                    
            shares = shares_outstanding[-1] if shares_outstanding is not None and not shares_outstanding.empty else None
            
            revenue_yoy = yoy_growth(revenue_hist)
            revenue_cagr, revenue_yrs = cagr(revenue_hist)
            ni_yoy = yoy_growth(net_income_hist)
            ni_cagr, ni_yrs = cagr(net_income_hist)

            market_cap = price * shares
            
            if ni_sum is not None and not ni_sum.empty and weighted_avg_shares:
                eps = safe_divide(ni_sum.iloc[-1], weighted_avg_shares)
                eps_series = safe_divide(ni_sum, weighted_avg_shares)
            else:
                eps = None
                eps_series = None
            eps_yoy = yoy_growth(eps_series)

            pe = safe_divide(price, eps)
            book_value_per_share = safe_divide(equity, shares)
            pb = safe_divide(price, book_value_per_share) 

            cap_employed = safe_subtract(total_asset, current_liability)
            roe = safe_margin(net_income, equity)
            roce = safe_margin(ebit, cap_employed)
            roa = safe_margin(net_income, total_asset)
            profit_margin = safe_margin(net_income, revenue)
            op_margin = safe_margin(ebit, revenue) 

            debt_equity = safe_divide(total_debt, equity) 
            current_ratio = safe_divide(current_asset, current_liability)
            net_debt = safe_subtract(total_debt, cash)            
            interest_coverage = safe_divide(ebit, abs(int_exp)) if int_exp else None

            if revenue_yoy is not None:
                if revenue_yoy > 10:
                    growth_strength = "strong"
                elif revenue_yoy > 0:
                    growth_strength = "moderate"
                else:
                    growth_strength = "weak"
            else:
                growth_strength = "data unavailable"

            if revenue_yoy is not None and ni_yoy is not None:
                ni_relation = "effectively translating into" if ni_yoy >= revenue_yoy else "partially translating into"
            else: 
                ni_relation = "inconclusive"

            if eps_yoy is not None and ni_yoy is not None:
                eps_relation = "sustained" if eps_yoy >= ni_yoy else "diluted"
            else:
                eps_relation = "inconclusive"

            if eps_yoy is not None and ni_yoy is not None and revenue_yoy is not None:
                if revenue_yoy > 0 and ni_yoy > 0 and eps_yoy > 0:
                    growth_quality = "high-quality and scalable growth"
                elif revenue_yoy > 0:
                    growth_quality = "top-line-led growth with profitability pressure"
                else:
                    growth_quality = "constrained growth momentum"
            else:
                growth_quality = "inconclusive"

            if profit_margin is not None and roe is not None:
                if profit_margin > 15 and roe > 15:
                    profit_strength = "strong"
                elif profit_margin > 0:
                    profit_strength = "moderate"
                else:
                    profit_strength = "weak"
            else:
                profit_strength = "data unavailable"

            if roa is not None and roe is not None:
                if roe > roa * 2:
                    profit_quality = "efficient shareholder-level profitability supported by asset leverage"
                elif roe > roa:
                    profit_quality = "balanced earnings conversion with effective asset utilization"
                else:
                    profit_quality = "subdued returns despite positive earnings"
            else:
                profit_quality = "inconclusive"

            if roce is not None:
                if roce > 15:
                    efficiency_strength = "strong"
                elif roce > 8:
                    efficiency_strength = "moderate"
                else:
                    efficiency_strength = "weak"
            else:
                efficiency_strength = "data unavailable"

            if roce is not None and roe is not None:
                if abs(roce - roe) <= 3:
                    driver = "operational performance rather than financial leverage"
                elif roe > roce:
                    driver = "equity leverage amplification over operating efficiency"
                else:
                    driver = "efficient operating capital deployment"
            else: 
                driver = "inconclusive"

            if debt_equity is not None and interest_coverage is not None:
                if debt_equity < 0.5 and interest_coverage > 5:
                    profile = "conservative"
                elif debt_equity < 1.5 and interest_coverage > 2:
                    profile = "manageable"
                else:
                    profile = "elevated"
            else:
                profile = "data unavailable"

            if current_ratio is not None:
                if current_ratio >= 1.5:
                    liquidity = "adequate"
                elif current_ratio >= 1:
                    liquidity = "tight but manageable"
                else:
                    liquidity = "constrained"
            else:
                liquidity = "inconclusive"

            if pe is not None and roe is not None:           
                if pe < 15 and roe > 15:
                    view = "attractive"
                elif pe <= 25 and roe >= 12:
                    view = "reasonable"
                elif pe > 25 and roe < 12:
                    view = "demanding"
                else:
                    view = "fair but execution-dependent"
            else: view = "data unavailable"
            
            rows_1.append({"Symbol": t,
                           "Market Cap Display": format_market_cap(market_cap),
                           "Market Cap": market_cap,
                           "Revenue YOY (%)": safe_round(revenue_yoy),
                          f"Revenue CAGR ({revenue_yrs}Y)": safe_round(revenue_cagr),
                           "Net Income YOY (%)": safe_round(ni_yoy),
                          f"Net Income CAGR ({ni_yrs}Y)": safe_round(ni_cagr),
                           "ROE (%)": roe,
                           "Profit Margin (%)": profit_margin,
                           "ROA (%)": roa,
                           "ROCE (%)": roce})
            
            rows_2.append({"Symbol": t,
                           "EPS (TTM)": safe_round(eps),
                           "P/E Ratio": safe_round(pe) if pe else None,
                           "P/B Ratio": safe_round(pb) if pb else None,
                           "Debt / Equity": safe_round(debt_equity),
                           "Current Ratio": safe_round(current_ratio),
                           "Interest Coverage": safe_round(interest_coverage)})
            
            bs_strength.append({"Symbol": t,
                                "Net Debt": format_market_cap(net_debt),
                                "Debt / Equity": safe_round(debt_equity),
                                "Interest Coverage": interest_coverage})
            
            pe_display = f"{pe:.2f}x" if pe is not None else "-"
            pb_display = f"{pb:.2f}x" if pb is not None else "-"

            
            summary[t] = [f"{t} exhibits {growth_strength} business expansion, with revenue growth of {safe_round(revenue_yoy)}% {ni_relation} net income growth "
                          f"of {safe_round(ni_yoy)}% and {eps_relation} EPS growth of {safe_round(eps_yoy)}%, indicating {growth_quality}.",
                                
                          f"Profitability remains {profit_strength}, with operating and net margins at {op_margin}% and {profit_margin}%, "
                          f"while returns of {roe}% ROE and {roa}% ROA indicate {profit_quality}.",
                                
                          f"Capital efficiency is {efficiency_strength}, with ROCE at {roce}% relative to ROE of {roe}%, indicating that "
                          f"shareholder returns are primarily driven by {driver} rather than margin or leverage effects.",

                          f"The balance sheet reflects {profile} leverage, with a debt-to-equity ratio of {safe_round(debt_equity)}x and interest coverage of "
                          f"{safe_round(interest_coverage)}x, while a current ratio of {safe_round(current_ratio)}x indicates {liquidity} financial flexibility.",
                                
                          f"At current levels, the stock trades at {pe_display} earnings and {pb_display} book value, "
                          f"which appears {view} given its return profile, as reflected by an ROE of {roe}%."]
        
            years = (net_income_series.index.intersection(revenue_series.index).intersection(equity_series.index).intersection(total_asset_series.index))

            for yr in sorted(years):
                margin = net_income_series[yr] / revenue_series[yr]
                asset_to = revenue_series[yr] / total_asset_series[yr]
                eq_multiplier = total_asset_series[yr] / equity_series[yr]
                if None in (profit_margin, asset_to, eq_multiplier):
                    roe_du = None
                    roa_du = None
                else:
                    roe_du = profit_margin * asset_to * eq_multiplier
                    roa_du = profit_margin * asset_to

                du_pont.append({"Symbol": t,
                                "Year": yr.year,
                                "Net Profit Margin (%)": safe_round(margin, 100),
                                "Asset Turnover Ratio": safe_round(asset_to),
                                "Equity Multplier": safe_round(eq_multiplier),
                                "ROE (%)": safe_round(roe_du),
                                "ROA (%)": safe_round(roa_du)})
  
        business_df = pd.DataFrame(rows_1)        
        financial_df = pd.DataFrame(rows_2)
        fundamental_df = business_df.merge(financial_df, on="Symbol", how="inner")

        if fundamental_df.empty :
            st.warning("Insufficient fundamental data")
            return fundamental_df
        
        if not business_df.empty:
            avg_roe = business_df["ROE (%)"].dropna().mean()
            avg_margin = business_df["Profit Margin (%)"].dropna().mean()
            avg_roce = business_df["ROCE (%)"].dropna().mean()
            median_pe = financial_df["P/E Ratio"].dropna().median()
            median_pb = financial_df["P/B Ratio"].dropna().median()
            avg_de = financial_df["Debt / Equity"].dropna().mean()
            
            metric_row([("Portfolio Avg ROE", f"{avg_roe:.2f}%", None),
                        ("Portfolio Avg Margin", f"{avg_margin:.2f}%", None),
                        ("Avg ROCE", f"{avg_roce:.2f}%", None),
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
        view_mode = st.segmented_control("Select stock", options=valid_tickers, selection_mode="single", default=valid_tickers[0], label_visibility="collapsed", key="view_mode")
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
        quality_df = business_df.dropna(subset=["ROE (%)", "Profit Margin (%)", "Market Cap"])

        if len(quality_df) < 2:
            quality_df["Quality Bucket"] = "Single Holding"
        else:
            roe_median = quality_df["ROE (%)"].median()
            roe_q75 = quality_df["ROE (%)"].quantile(0.75)

            quality_df["Quality Bucket"] = pd.cut(quality_df["ROE (%)"],
                                              bins=[-float("inf"), roe_median, roe_q75, float("inf")],
                                              labels=["Below Avg ROE", "Strong ROE", "High ROE"])
        
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

        st.markdown("<h3 style='color:#7161ef;'>Debt / Equity & Interest coverage</h3>", unsafe_allow_html=True)
        bs_strength_df = pd.DataFrame(bs_strength)

        fig = bar_chart(bs_strength_df,
                            x="Debt / Equity",
                            y="Symbol",
                            color="Interest Coverage",
                            orientation="h",
                            show_text=True,
                            hover_col="Symbol",
                            title=None)
        fig.update_traces(texttemplate="",textposition="outside")
        fig.update_layout( xaxis_title="Debt / Equity", yaxis_title="", yaxis_tickformat=".1f", xaxis_tickangle=-25)
        st.plotly_chart(fig, width="stretch")
        st.markdown("<hr style='opacity:0.2;'>", unsafe_allow_html=True)

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
  
        view_mode_summary = st.segmented_control("Select stock for summary", options=valid_tickers, selection_mode="single", default=valid_tickers[0], label_visibility="collapsed", key="view_mode_summary")
        summary = summary.get(view_mode_summary, [])
            
        interpretation_box(f"Fundamental Strength Summary - {view_mode_summary}", summary)
        
        return fundamental_df

