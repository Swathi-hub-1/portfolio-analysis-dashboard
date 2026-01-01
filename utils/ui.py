import streamlit as st

ACCENT = '#957fef'
ACCENT_2 = '#7161ef'
TEXT = '#f8f9fa'

def apply_custom_css():
    st.markdown(f"""
                <style>   
                div.stButton > button {{background-color: {ACCENT};
                                        color: {TEXT};
                                        border-radius: 10px;
                                        border: 1px solid {ACCENT_2};
                                        font-weight: 600;
                                        height: 3em;
                                        transition: all 0.3s ease-in-out;}}

                div.stButton > button:hover {{background-color: {ACCENT_2};
                                              color: #f8f9fa;
                                              box-shadow: 0px 0px 12px {ACCENT_2};
                                              transform: translateY(-2px);}}

                div[data-testid="stMetric"] {{border: 1.4px solid {ACCENT_2};
                                              border-radius: 15px;
                                              padding: 12px;
                                              transition: all 0.3s ease;}}

                div[data-testid="stMetric"]:hover {{border-color: {ACCENT};
                                                    transform: translateY(-2px);}}
                
                div[data-testid="stDataFrame"] thead th {{background-color: {ACCENT_2} !important;
                                                          color: {TEXT} !important;
                                                          font-weight: 600 !important;
                                                          text-align: center !important;
                                                          border-bottom: 1px solid {ACCENT};}}

                details{{border-radius: 10px !important;
                        border: 1px solid {ACCENT_2}33 !important;
                        background: rgba(76, 201, 240, 0.06) !important;
                        margin-bottom: 8px !important;
                        transition: 0.25s ease-in-out !important;
                        padding: 4px !important;}}

                summary {{color: {ACCENT} !important;
                         font-weight: 600 !important;
                         padding: 6px !important;
                         cursor: pointer !important;}}

                details:hover {{transform: scale(1.01);
                                border-color: {ACCENT_2};
                                box-shadow: 0 0 12px {ACCENT_2};}}

                .stTabs [data-baseweb="tab"]{{color: {ACCENT_2};
                                              transition: all 0.25s ease !important;
                                              padding: 12px 22px !important;  
                                              font-size: 10px;
                                              font-weight: 900 !important;
                                              opacity: 0.9;}}

                .stTabs [data-baseweb="tab"]:hover {{opacity: 1.9;
                                                     font-size: 20px;
                                                     transform: translateY(-2px);}}

                .stTabs [data-baseweb="tab"][aria-selected="true"] {{color: {ACCENT_2} !important;
                                                                     font-weight: 900 !important;
                                                                     opacity: 1.9;
                                                                     transform: translateY(-1px);}}    
                </style>""", unsafe_allow_html=True)

def header():
    st.markdown(f"<h1 style='text-align:center; color:{ACCENT_2};'>Portfolio Analysis Dashboard</h1>", unsafe_allow_html=True)
    st.markdown(f"<hr style='border:0.5px solid {ACCENT}; opacity:0.8;'>", unsafe_allow_html=True)


def sidebar_config():
    st.sidebar.markdown(f"<h1 style='color:{ACCENT_2}; text-align: center; width: 100%;'>Portfolio Input Panel</h1><hr style='border:0.5px solid {ACCENT};'>", unsafe_allow_html=True)
    

def home_page():
    st.markdown(f"""
                <div style='background:rgba(149,127,239,0.1); border:1px solid rgba(149,127,239,0.3); border-radius:12px; padding:25px 30px; margin-top:40px;'>
                    <h4 style='font-size:20px; font-weight:700; margin-top:25px; margin-bottom:10px'>
                        About This Dashboard
                    </h4>
                     <p style="font-size:15px; line-height:1.6; margin-top:10px;">
                        This dashboard is built to make equity analysis easy to understand, even for beginners, 
                        while still offering the depth needed for serious portfolio evaluation. It takes real stock 
                        market data and converts it into clean, visual insights — helping you track your 
                        portfolio’s performance, understand risk, explore fundamental ratios, and review 
                        dividend growth in a structured, intuitive layout.
                        <br><br>
                        By combining simplicity with analytical strength, the dashboard supports both learning 
                        and professional-style analysis. Whether you’re exploring how markets work or 
                        reviewing your investments with more detail, the interface adapts to your pace and 
                        gives you clarity through charts, summaries, and real-time data.
                    </p>
                    <h4 style='font-size:20px; font-weight:700; margin-top:25px; margin-bottom:10px;'>
                        How to use
                    </h4>
                    <ul style="font-size:15px; line-height:1.7; padding-left:20px; margin-top:15px;">
                        Use the sidebar on the left to begin.
                        <li><b>Add Tickers</b> : Search and select the stocks you own.</li>
                        <li><b>Select Date Range</b> – Choose the period during which you held each stock.</li>
                        <li><b>Enter Shares</b> – Specify how many units you hold for each stock.</li>
                        <li><b>Click Generate Analysis</b> – View performance, risk, fundamentals & dividends.</li>
                    </ul>
                    <h4 style='font-size:20px; font-weight:700; margin-top:25px; margin-bottom:10px;'>
                        What You Can Explore
                    </h4>
                    <ul style="font-size:15px; line-height:1.7; padding-left:20px; margin-top:15px;">
                        <li><b>Portfolio Performance</b> – Track returns, allocation, cost basis, and price movement trends.</li>
                        <li><b>Risk Analysis</b> – Understand volatility, drawdowns, beta, Sharpe ratio, and other risk metrics.</li>
                        <li><b>Fundamental Strength</b> – Explore valuation ratios, profitability metrics, quality factors, and sector comparisons.</li>
                        <li><b>Dividend Insights</b> – Review yield, payout patterns, 5-year CAGR, stability, and income projections.</li>
                        <li><b>Automation Ready</b> – Export your analysis to a professional Excel report or QuantStats report in seconds.</li>
                    </ul>
                </div>""",unsafe_allow_html=True)
    
    st.markdown(f"""
                <div style='text-align:center; margin-top:50px; padding:18px 0; opacity:1.1; color:{ACCENT}; font-size:13px; border-top:1px solid rgba(0,180,216,0.18);'>
                    2025 • Portfolio Analytics Dashboard  
                    <br>
                    Built for learning, research, and informed investing.
                </div>""", unsafe_allow_html=True)
    

def interpretation_box(title, points):
    st.markdown(f"""
        <div style="background: rgba(149,127,239,0.1); border: 1px solid rgba(149,127,239,0.3); border-radius: 14px; padding: 20px 24px; margin-top: 25px;">
            <h4 style="color:{ACCENT_2}; margin-bottom:12px;">{title}</h4>
            <ul style="line-height:1.75; font-size:15px; padding-left: 18px; margin: 0;">
                {''.join([f'<li style="margin-bottom: 10px;">{p}</li>' for p in points])}
            </ul>
        </div>""",unsafe_allow_html=True)
    
   
def color_rsi_category(cat):
    if isinstance(cat, str):
        if cat.lower() == "overbought":
            return "color: #f44336; font-weight:600;"
        elif cat.lower() == "oversold":
            return "color: #4caf50; font-weight:600;"
        elif cat.lower() == "neutral":
            return "color: #9e9e9e; font-weight:600;"
    return ""


def color_gain_loss(val):
    try:
        v = float(val)
        if v > 0:
            return "color: #4caf50; font-weight:600;"
        elif v < 0:
            return "color: #f44336; font-weight:600;"
    except:
        pass
    return ""


def color_trend_class(val):
    try:
        v = str(val).lower()

        if "strong bullish" in v:
            return "color: #38b000; font-weight:600;"
        if "bullish" in v and "strong" not in v:
            return "color: #aad576; font-weight:600;"
        if "weak bullish" in v:
            return "color:#9ef01a; font-weight:600;"
        if "range" in v:
            return "color: #9e9e9e; font-weight:600;"
        if "weak bearish" in v:
            return "color: #ef9a9a; font-weight:600;"
        if "bearish" in v and "strong" not in v:
            return "color: #f44336; font-weight:600;"
        if "strong bearish" in v:
            return "color: #b71c1c; font-weight:600;"
    except:
        pass
    return ""


def beta_color(beta: float):
    if beta == 1.0:
        return "color: #2563eb; font-weight:600;"
    elif beta > 1.0:
        return "color: #f44336; font-weight:600;"  
    elif beta < 1.0:
        return "color: #4caf50; font-weight:600;"  
 
