import streamlit as st
import pandas as pd
from utils.helper import metric_row, safe_float, safe_divide, safe_round, safe_margin
from utils.charts import line_chart, pie_chart, bar_chart
from utils.ui import interpretation_box


def dividend_income(valid_tickers, div_dict, date_ranges, buy_price, latest_price, shares):
        st.markdown("<h2 style='text-align:center; color:#7161ef;'>Dividend Income & Yield Analytics</h2>", unsafe_allow_html=True)
        st.markdown("<hr style='opacity:0.2;'>", unsafe_allow_html=True)

        div_rows = []
        share_values = {t: safe_float(latest_price.get(t)) * float(shares.get(t, 0)) for t in valid_tickers}
        total_value = float(sum(share_values.values())) if share_values else 0.0
        pf_income = 0
        total_projected_annual_income = 0
        
        for t in valid_tickers:
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
                try:
                    div_since_buy = divs.loc[divs.index >= start_dt].sum()
                except Exception:
                    try:
                        divs_naive = divs.copy()
                        divs_naive.index = divs_naive.index.tz_localize(None)
                        start_dt_naive = pd.to_datetime(start_dt).tz_localize(None) if getattr(start_dt, "tzinfo", None) is not None else pd.to_datetime(start_dt)
                        div_since_buy = divs_naive.loc[divs_naive.index >= start_dt_naive].sum()
                    except Exception:
                        div_since_buy = 0.0
            else:
                div_since_buy = 0.0

            if not divs.empty:

                try:
                    one_year_ago = pd.Timestamp.now(tz=divs.index.tz) - pd.DateOffset(years=1) if getattr(divs.index, "tz", None) is not None else pd.Timestamp.now() - pd.DateOffset(years=1)
                    last_year_div = divs.loc[divs.index >= one_year_ago].sum()
                except Exception:
                    last_year_div = 0.0
            else:
                last_year_div = 0.0

            try:
                last_ex_dividend = divs.index[-1].date() if divs is not None and not divs.empty else None
            except:
                last_ex_dividend = None

            if not divs.empty:
                try:
                    divs_cagr = divs.loc[divs.index >= start_dt]
                    annual_div = divs_cagr.resample("YE").sum()
                    if len(annual_div) > 1 and annual_div.iloc[0] > 0:
                        periods = len(annual_div) - 1
                        div_cagr = ((annual_div.iloc[-1] / annual_div.iloc[0]) ** (1 / periods) - 1) * 100
                    else:
                        div_cagr = None
                except:
                    div_cagr = None
            else:
                div_cagr = None
            
            buy_p = buy_price.get(t) or 0.0
            yoc = safe_margin(last_year_div, buy_p)
            current_yield = safe_margin(last_year_div, latest_price.get(t))

            stk_income = float(div_since_buy) * float(shares.get(t, 0))
            pf_income += stk_income

            projected_annual_income = last_year_div * shares.get(t, 0)
            total_projected_annual_income += projected_annual_income
            
            forward_portfolio_yield = safe_divide(total_projected_annual_income, total_value)
            actual_current_yield = safe_divide(pf_income, total_value)
            
            dividend_payers = sum(1 for t in valid_tickers if not div_dict.get(t).empty)
            coverage = f"{dividend_payers} / {len(valid_tickers)}"

            div_rows.append({"Ticker": t,
                             "Shares": shares.get(t, 0),
                             "Ex-Date": last_ex_dividend.strftime("%b %d, %Y") if last_ex_dividend else "-",
                             "Last 12M Div (₹)": float(last_year_div),
                             "Dividend Income(₹)": safe_round(stk_income),
                             "YOC (%)": yoc,
                             "Current Yield (%)": current_yield,
                             "Projected Div (₹)": safe_round(projected_annual_income),
                             "Dividend CAGR (%)": safe_round(div_cagr),})
        div_df = pd.DataFrame(div_rows)

        metric_row([("Total Dividend Income", f"₹{pf_income:,.2f}", None),
                    ("Portfolio Yield", f"{actual_current_yield:.2%}", None),
                    ("Forward Portfolio Yield", f"{forward_portfolio_yield:.2%}", None),
                    ("Dividend Coverage", f"{coverage}", None)])
        st.markdown("<hr style='opacity:0.2;'>", unsafe_allow_html=True)

        st.markdown("<h3 style='color:#7161ef;'>Dividend Income Summary</h3>", unsafe_allow_html=True)
        st.dataframe(div_df, hide_index=True, width="stretch")
        st.markdown("<hr style='opacity:0.2;'>", unsafe_allow_html=True)

        st.markdown("<h3 style='color:#7161ef;'>Dividend Contribution by Stock</h3>", unsafe_allow_html=True)
        if not div_df.empty and div_df["Dividend Income(₹)"].sum() > 0:
            fig_income = pie_chart(div_df["Ticker"].tolist(), div_df["Dividend Income(₹)"].tolist(), title=None)
            st.plotly_chart(fig_income, width="stretch")
        else:
            st.info("No dividend income to visualize for the selected holdings/date ranges.")
        st.markdown("<hr style='opacity:0.2;'>", unsafe_allow_html=True)

        st.markdown("<h3 style='color:#7161ef;'>Cumulative Dividend Income Trend</h3>", unsafe_allow_html=True)
        combined = []
        for t in valid_tickers:
            divs = div_dict.get(t)
            if divs is not None and not divs.empty:
                df_temp = pd.DataFrame({"Date": divs.index,
                                        "Dividend (₹)": divs.cumsum(),
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

        st.markdown("<h3 style='color:#7161ef;'>Dividend Metrics: DPS vs Yield vs Growth</h3>", unsafe_allow_html=True)
        fig_bar = bar_chart(div_df,
                            x="Ticker",
                            y="Last 12M Div (₹)",
                            color="Dividend CAGR (%)",
                            show_text=True,
                            hover_col="Ticker",
                            title=None)
        fig_bar.update_layout(yaxis_tickformat=".1f", xaxis_tickangle=-25)
        st.plotly_chart(fig_bar, width="stretch")
        st.markdown("<hr style='opacity:0.2;'>", unsafe_allow_html=True)
        
        if not div_df.empty:
            avg_cagr = div_df["Dividend CAGR (%)"].dropna().mean() if not div_df["Dividend CAGR (%)"].isna().all() else 0
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

        summary = [f"The portfolio generates an estimated annual dividend income of ₹{total_projected_annual_income:,.2f}, making it -low/moderate/strong- from an income perspective. with a current portfolio yield of {actual_current_yield:.2%}.",
                   
                   f"Dividend growth trends indicate {trend_label} income, suggesting the portfolio is {orientation_label} and prioritizes {'yield' if orientation_label == 'income-oriented' else 'total return'}."]
        
        interpretation_box("Income Summary", summary)
        return div_df
