Portfolio Analysis Dashboard

A fully interactive equity portfolio analytics dashboard built with Streamlit, providing insights across performance, risk, fundamentals, and dividends.
The tool converts raw market data into easy-to-understand visual analytics suitable for beginners and advanced users alike.


About the Project

Portfolio Analysis Dashboard is a comprehensive tool designed to help users understand and analyze stock portfolios with the depth typically seen in institutional research platforms.

The application integrates:
    Live market data from Yahoo Finance.
    Analytics & performance metrics using Pandas, NumPy, and QuantStats.
    Interactive visualizations using Plotly.
    A clean, responsive Streamlit UI.

This makes the dashboard suitable for retail investors, finance students, and analysts who need a lightweight, customizable analytics environment.


Key Features

1. Portfolio Overview

Cumulative return, CAGR and active performance metrics

Best and worst performing holdings

Allocation breakdown and unrealized P/L

Position health classification (trend, RSI, 52-week zone, momentum)

2. Risk Analysis

Annualized volatility, Sharpe ratio, Sortino ratio

Beta, Value-at-Risk (VaR), Conditional VaR (CVaR)

Drawdown analysis

Correlation heatmap

Rolling volatility and rolling Sharpe

Risk vs. return scatter plot

3. Fundamentals

Market cap, sector, valuation ratios (P/E, P/B), and EPS

Profitability metrics such as ROE and margins

Company quality visualized through bubble charts

Valuation distribution using box plots

4. Dividend Analysis

Total dividends received since purchase

Dividend yield, yield on cost, and dividend CAGR

Cumulative dividend timeline

Income contribution by stock

5. Reporting Tools

Export complete Excel report

Generate a QuantStats HTML performance report

Intelligent caching for faster repeated analyses


Why This Dashboard Is Useful

Combines performance, risk, fundamentals, and dividends into one unified interface

Provides professional-grade metrics normally found in equity research

Beginner-friendly design with meaningful, well-structured insights

Customizable date ranges, share quantities, and portfolio configuration

Fast, efficient, and export-ready for academic or practical use


Tech Stack

Streamlit	                            Application UI
yfinance	                            Market data 
Pandas, NumPy	                        Data processing and calculations
Plotly	                                Interactive visualizations
QuantStats	                            Performance and risk reporting
OpenPyXL	                            Excel export functionality


Installation & Setup

1. Clone the Repository
git clone https://github.com/yourusername/portfolio-analysis-dashboard.git
cd portfolio-analysis-dashboard

2. Create & Activate a Virtual Environment
python -m venv venv
source venv/bin/activate  -> macOS/Linux
venv\Scripts\activate     -> Windows

3. Install Dependencies
pip install -r requirements.txt

4. Run the Dashboard
streamlit run app.py


Requirements (requirements.txt)

streamlit
yfinance
pandas
numpy
plotly
quantstats
openpyxl
python-dotenv
requests


Author

Built by Swathi, combining finance knowledge with Python-based analytics to create tools for learning, research, and investment insights.