import streamlit as st
import pandas as pd
from utils.data_fetch import fetch_fundamentals
from utils.helper import metric_row, safe_float, safe_divide, safe_round, safe_margin, cagr, safe_subtract, safe_multiple
from utils.charts import line_chart, pie_chart, bubble_chart
from utils.ui import interpretation_box


def dividend_income(valid_tickers, div_dict, date_ranges, buy_price, latest_price, shares):
        st.markdown("<h2 style='text-align:center; color:#7161ef;'>Dividend & Income Analysis</h2>", unsafe_allow_html=True)
        st.markdown("<hr style='opacity:0.2;'>", unsafe_allow_html=True)

        div_rows = []
        share_values = {t: safe_float(latest_price.get(t)) * float(shares.get(t, 0)) for t in valid_tickers}
        total_value = float(sum(share_values.values())) if share_values else 0.0
        pf_income = 0
        total_projected_annual_income = 0
        dividend_payers = 0
        
        for t in valid_tickers:
            fs = fetch_fundamentals(t)
            income = fs.get("income")
            shares_outstanding = fs.get("s_o")
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
                div_since_buy = divs.loc[divs.index >= start_dt].sum()
                one_year_ago = pd.Timestamp.now(tz=divs.index.tz) - pd.DateOffset(years=1) if div_index_tz is not None else pd.Timestamp.now() - pd.DateOffset(years=1)
                last_year_div = divs.loc[divs.index >= one_year_ago].sum()
                
                div_annual = divs.resample("YE").sum()
                div_annual.index = div_annual.index.year
                div_hist = div_annual.tail(6)
                div_cagr, div_yr = cagr(div_hist)

                div_df = divs.to_frame("Dividend")
                div_df["FY"] = div_df.index.to_period("Y-MAR")
                fy_div = div_df.groupby("FY")["Dividend"].sum()
                fy_div = fy_div.iloc[-2]
            
            else:
                div_since_buy = 0.0
                last_year_div = 0.0
                div_cagr = 0.0
                fy_div = None
            
            # div_df = divs.to_frame("Dividend")
            # div_df["FY"] = div_df.index.to_period("Y-MAR")
            # fy_div = div_df.groupby("FY")["Dividend"].sum()

            # fy_div = fy_div.iloc[-2]
            s_o = shares_outstanding[-1] if shares_outstanding is not None and not shares_outstanding.empty else None
            div_paid = safe_multiple(fy_div, s_o)

            net_income = income.loc["Net Income"].dropna().sort_index()
            fy_ni = net_income.iloc[-1]

            payout = safe_divide(div_paid, fy_ni)
            retention = safe_subtract(1, payout)

            last_ex_dividend = divs.index[-1].date() if divs is not None and not divs.empty else None
                
            buy_p = buy_price.get(t) or 0.0
            yoc = safe_margin(last_year_div, buy_p)
            div_yield = safe_margin(last_year_div, latest_price.get(t))

            stk_income = float(div_since_buy) * float(shares.get(t, 0))
            pf_income += stk_income
            
            projected_annual_income = last_year_div * shares.get(t, 0)
            total_projected_annual_income += projected_annual_income
            
            forward_portfolio_yield = safe_divide(total_projected_annual_income, total_value)
            actual_current_yield = safe_divide(pf_income, total_value)
            
            if div_since_buy > 0:
                dividend_payers += 1
            coverage = f"{dividend_payers} / {len(valid_tickers)}"

            div_rows.append({"Ticker": t,
                             "Shares": shares.get(t, 0),
                             "Ex-Date": last_ex_dividend.strftime("%b %d, %Y") if last_ex_dividend else "-",
                             "Last 12M Div (₹)": float(last_year_div),
                             "Dividend Income(₹)": safe_round(stk_income),
                             "YOC (%)": yoc,
                             "Dividend Yield (%)": div_yield,
                             "Payout Ratio (%)": safe_round(payout, 100) if payout else "-",
                             "Retention Ratio (%)": safe_round(retention, 100) if retention else "-",
                             f"Dividend CAGR ({div_yr}Y)": safe_round(div_cagr) ,})
        div_df = pd.DataFrame(div_rows)

        metric_row([("Total Dividend Income", f"₹{pf_income:,.2f}", None),
                    ("Portfolio Yield", f"{actual_current_yield:.2%}", None),
                    ("Forward Portfolio Yield", f"{forward_portfolio_yield:.2%}", None),
                    ("Income-Generating Holdings", f"{coverage}", None)])
        st.markdown("<hr style='opacity:0.2;'>", unsafe_allow_html=True)

        st.markdown("<h3 style='color:#7161ef;'>Dividend Income Summary</h3>", unsafe_allow_html=True)
        st.dataframe(div_df, hide_index=True, width="stretch")
        st.markdown("<hr style='opacity:0.2;'>", unsafe_allow_html=True)

        st.markdown("<h3 style='color:#7161ef;'>Dividend Contribution by Stock</h3>", unsafe_allow_html=True)
        if not div_df.empty and div_df["Dividend Income(₹)"].sum() > 0:
            pie_df = div_df.sort_values("Dividend Income(₹)", ascending=False)
            fig_income = pie_chart(pie_df["Ticker"].tolist(), pie_df["Dividend Income(₹)"].tolist(), title=None)
            st.plotly_chart(fig_income, width="stretch")
        else:
            st.info("No dividend income to visualize for the selected holdings/date ranges.")
        st.markdown("<hr style='opacity:0.2;'>", unsafe_allow_html=True)

        st.markdown("<h3 style='color:#7161ef;'>Dividend Payment History</h3>", unsafe_allow_html=True)
        combined = []
        for t in valid_tickers:
            divs = div_dict.get(t)
            if divs is not None and not divs.empty:
                df_temp = pd.DataFrame({"Date": divs.index,
                                        "Dividend (₹)": divs,
                                        "Ticker": t})
                combined.append(df_temp)
        if combined:
            cum_div_df = pd.concat(combined, ignore_index=True)
            fig_cum = line_chart(cum_div_df,
                                 x="Date",
                                 y="Dividend (₹)",
                                 color="Ticker",
                                 markers=True,
                                 title=None,
                                 labels={"Date": "Date", "Dividend (₹)": "Cumulative Dividend (₹)"})
            st.plotly_chart(fig_cum, width="stretch")

            st.markdown("<hr style='opacity:0.2;'>", unsafe_allow_html=True)

        st.markdown("<h3 style='color:#7161ef;'>Dividend Yield vs Growth — Portfolio Map</h3>", unsafe_allow_html=True)
        fig = bubble_chart(df=div_df,
                            x="Dividend Yield (%)",
                            y=f"Dividend CAGR ({div_yr}Y)",
                            size="Dividend Income(₹)",
                            color="Ticker", 
                            hover="Ticker",
                            title="",
                            reference_line=True)
        st.plotly_chart(fig, width="stretch")
        st.markdown("<hr style='opacity:0.2;'>", unsafe_allow_html=True)

        
        if not div_df.empty:
            avg_cagr = div_df[f"Dividend CAGR ({div_yr}Y)"].dropna().mean() if not div_df[f"Dividend CAGR ({div_yr}Y)"].isna().all() else 0
            if avg_cagr > 10:
                trend_label = "rapidly growing"
            elif avg_cagr > 2:
                trend_label = "stable and growing"
            else:
                trend_label = "uneven or stagnant"

            yield_pct = actual_current_yield * 100
            if yield_pct > 4:
                orientation_label = "income-oriented"
            elif yield_pct > 1.5:
                orientation_label = "blended"
            else:
                orientation_label = "growth-focused"

        top_contributor = div_df.sort_values("Dividend Income(₹)", ascending=False).iloc[0]

        summary = [f"The portfolio has generated ₹{pf_income:,.2f} in dividend income so far, with an estimated annual income of "
                    f"₹{total_projected_annual_income:,.2f}. The current portfolio yield of {actual_current_yield:.2%} reflects a "
                    f"{orientation_label} dividend profile.",

                    f"{top_contributor['Ticker']} is the largest dividend contributor, making it a key income driver for the portfolio. "
                    f"Changes in its dividend policy will have a meaningful impact on overall income stability.",

                    f"The payout ratio highlights how much earnings are returned to shareholders, while the retention ratio indicates "
                    f"the portion reinvested for future growth. A balanced mix of both supports income sustainability over time.",

                    f"The Dividend Yield vs Growth map distinguishes high-yield income stocks from dividend-growth-oriented stocks, "
                    f"helping assess whether returns are driven by current cash flow or future income potential."]
        
        interpretation_box("Income Summary", summary)
        return div_df
