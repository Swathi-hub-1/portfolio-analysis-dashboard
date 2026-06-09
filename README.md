# 📊 Portfolio Analysis Dashboard

> **Live equity analytics platform** — institutional-grade risk metrics, fundamental screening, and dividend analysis on real-time market data.

🚀 **[Open Live App](https://portfolio-analysis-dashboard.streamlit.app/)** &nbsp;|&nbsp; 🐍 Python &nbsp;|&nbsp; 📈 Finance &nbsp;|&nbsp; ☁️ Deployed on Streamlit Cloud

---

## What This Does

Most retail portfolio tools show you returns. This one shows you *why* — decomposing performance into risk-adjusted metrics, fundamental quality signals, and income attribution the way institutional research desks do.

Built by combining an MBA in Finance with Python to recreate the kind of analysis typically locked behind Bloomberg terminals or equity research platforms — and making it accessible for any portfolio.

---

## Live Demo

Upload your holdings (ticker, quantity, buy date) and the dashboard instantly generates:

| Analysis Module | Key Outputs |
|---|---|
| **Portfolio Overview** | Cumulative return, CAGR, unrealized P&L, position health scoring |
| **Risk Analysis** | Sharpe, Sortino, Beta, VaR, CVaR, drawdown, rolling volatility |
| **Fundamentals** | P/E, P/B, ROE, margins, DuPont decomposition, sector breakdown |
| **Dividend & Income** | Dividend CAGR, yield on cost, cumulative income timeline |
| **Export** | One-click Excel report + QuantStats HTML performance report |

---

## Why These Metrics Matter

**Value at Risk (VaR) & CVaR** — quantifies the downside tail risk of the portfolio, not just average volatility. CVaR captures what happens *beyond* the VaR threshold — the expected loss in worst-case scenarios.

**DuPont Decomposition** — breaks ROE into net margin × asset turnover × leverage, revealing *why* a company is profitable or deteriorating. A rising ROE driven by leverage is a red flag; driven by margins, it's a quality signal.

**Sortino Ratio** — unlike Sharpe, only penalises downside volatility. More relevant for evaluating asymmetric return profiles common in concentrated equity portfolios.

**Yield on Cost** — dividend income as a percentage of your *original* purchase price, not current market value. A long-held position yielding 8% on cost may show only 2% current yield — this metric surfaces that compounding effect.

---

## Tech Stack

```
Data Layer      yfinance (live market data with intelligent caching)
Processing      Python · Pandas · NumPy
Risk Engine     Custom-built: VaR, CVaR, Beta, Drawdown, Rolling metrics
Visualisation   Plotly (interactive charts) · QuantStats (performance reports)
UI              Streamlit (modular tab architecture)
Export          OpenPyXL (Excel) · QuantStats HTML
Deployment      Streamlit Community Cloud
```

---

## Project Structure

```
portfolio-analysis-dashboard/
│
├── app.py                  # Entry point — routing and session state
│
├── tabs/                   # One file per analysis module
│   ├── overview.py         # Portfolio summary and position health
│   ├── risk.py             # VaR, CVaR, Sharpe, drawdown analysis
│   ├── fundamentals.py     # DuPont, valuation ratios, sector view
│   └── dividends.py        # Income analysis and dividend CAGR
│   └── reports.py          # Excel and QuantStats report generation
│
├── utils/                  # Shared logic
│   ├── data_fetch.py       # yfinance wrapper with caching
│   ├── analytics.py        # Risk and return computation engine
│   └── charts.py           # Charts framework
│   └── ui.py               # UI framework 
│   └── helpers.py          # Conditional formatting
│
├── Tickers.xlsx            # Sample input file format
└── requirements.txt
```

---

## Getting Started

### Run Locally

```bash
# Clone the repository
git clone https://github.com/Swathi-hub-1/portfolio-analysis-dashboard.git
cd portfolio-analysis-dashboard

# Create virtual environment
python -m venv venv
source venv/bin/activate        # macOS/Linux
venv\Scripts\activate           # Windows

# Install dependencies
pip install -r requirements.txt

# Launch
streamlit run app.py
```

### Input Format

Prepare an Excel file with stock tickers:

| Ticker | Shares | Buy Date |
|--------|--------|----------|
| RELIANCE.NS | 50 | 2022-03-15 |
| INFY.NS | 100 | 2021-08-10 |

> Use `.NS` suffix for NSE-listed stocks, `.BO` for BSE. Any Yahoo Finance-supported ticker works.

---

## What I'd Build Next

- DCF valuation module with customisable growth and discount rate assumptions
- Peer comparison: plot your holdings against sector benchmarks
- Portfolio optimisation using mean-variance (Markowitz efficient frontier)
- News sentiment overlay using financial news APIs

---

## About

Built by **Swathi Sri C.R.T** — MBA Finance & Operations (University of Madras), NISM-certified in Equity Research.

This project started as a personal need: most free portfolio trackers show returns but not *risk-adjusted* performance or fundamental quality. The goal was to build something that thinks the way a buy-side analyst would — combining quantitative rigour with accessible output.

📬 [swathisri.mba@outlook.com](mailto:swathisri.mba@outlook.com) &nbsp;|&nbsp; [LinkedIn](https://www.linkedin.com/in/swathi-sri-4b48602a0)

---

*Built with Python · Deployed on Streamlit Cloud · Data via Yahoo Finance*
