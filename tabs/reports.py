import streamlit as st
import pandas as pd
import os
import io

def report(pf_summary_table, fundamentals_df, div_df, pf_returns):
        st.markdown("<h2 style='text-align:center; color:#a2d2ff;'>Export Portfolio Reports</h2>", unsafe_allow_html=True)
        st.markdown("<p style='text-align:center; color:#90e0ef;'>Download detailed portfolio analytics in Excel or QuantStats report formats.</p>", unsafe_allow_html=True)

        try:
            buffer = io.BytesIO()
            with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
                if not pf_summary_table.empty:
                    pf_summary_table.to_excel(writer, index=False, sheet_name="Portfolio_Summary")
                if "fundamentals_df" in locals() and not fundamentals_df.empty:
                    fundamentals_df.to_excel(writer, index=False, sheet_name="Fundamentals")
                if not div_df.empty:
                    div_df.to_excel(writer, index=False, sheet_name="Dividends")
            buffer.seek(0)
            st.download_button("📘 Download Excel Summary", data=buffer.getvalue(), file_name="Portfolio_Summary.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        except Exception as e:
            st.warning(f"Could not export Excel: {e}")

        if not pf_returns.empty:
            try:
                import quantstats as qs
                import tempfile
                tmpdir = tempfile.TemporaryDirectory()
                report_path = os.path.join(tmpdir.name, "portfolio_report.html")
                qs.reports.html(pf_returns, output=report_path, title="Portfolio Performance Report")
                with open(report_path, "r", encoding="utf-8") as f:
                    html_data = f.read()
                st.download_button("📊 Download QuantStats Performance Report", data=html_data, file_name="Portfolio_Report.html", mime="text/html")
                tmpdir.cleanup()
            except Exception as e:
                st.warning(f"Could not generate QuantStats report: {e}")

