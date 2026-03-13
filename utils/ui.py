import streamlit as st

PRIMARY = "#7161ef"
SECONDARY = "#957fef"
TEXT = "var(--text-color)"

def apply_custom_css():
    st.markdown(f"""
                <style>   
                div.stButton > button {{background-color: {SECONDARY};
                                        color: {TEXT};
                                        border-radius: 10px;
                                        border: 1px solid {PRIMARY};
                                        font-weight: 600;
                                        height: 3em;
                                        transition: all 0.3s ease-in-out;}}

                div.stButton > button:hover {{background-color: {PRIMARY};
                                              color: #f8f9fa;
                                              box-shadow: 0px 0px 12px {PRIMARY};
                                              transform: translateY(-2px);}}

                div[data-testid="stMetric"] {{border: 1.4px solid {PRIMARY};
                                              border-radius: 15px;
                                              padding: 12px;
                                              transition: all 0.3s ease;}}

                div[data-testid="stMetric"]:hover {{background: rgba(149,127,239,0.1);
                                                    border-color: {SECONDARY};
                                                    transform: translateY(-2px);}}
                
                div[data-testid="stDataFrame"] thead th {{background-color: {PRIMARY} !important;
                                                          color: {TEXT} !important;
                                                          font-weight: 600 !important;
                                                          text-align: center !important;
                                                          border-bottom: 1px solid {SECONDARY};}}

                details{{border-radius: 10px !important;
                        border: 1px solid {PRIMARY}33 !important;
                        background: rgba(76, 201, 240, 0.06) !important;
                        margin-bottom: 8px !important;
                        transition: 0.25s ease-in-out !important;
                        padding: 4px !important;}}

                summary {{color: {SECONDARY} !important;
                         font-weight: 600 !important;
                         padding: 6px !important;
                         cursor: pointer !important;}}

                details:hover {{transform: scale(1.01);
                                border-color: {PRIMARY};
                                box-shadow: 0 0 12px {PRIMARY};}}

                .stTabs [data-baseweb="tab"]{{color: {PRIMARY};
                                              transition: all 0.25s ease !important;
                                              padding: 12px 22px !important;  
                                              font-size: 10px;
                                              font-weight: 900 !important;
                                              opacity: 0.9;}}

                .stTabs [data-baseweb="tab"]:hover {{opacity: 1.9;
                                                     font-size: 20px;
                                                     transform: translateY(-2px);}}

                .stTabs [data-baseweb="tab"][aria-selected="true"] {{color: {PRIMARY} !important;
                                                                     font-weight: 900 !important;
                                                                     opacity: 1.9;
                                                                     transform: translateY(-1px);}}    
                </style>""", unsafe_allow_html=True)

def header():
    st.markdown(f"<h1 style='text-align:center; color:{PRIMARY};'>Portfolio Analysis Dashboard</h1>", unsafe_allow_html=True)
    st.markdown(f"<hr style='border:0.5px solid {SECONDARY}; opacity:0.8;'>", unsafe_allow_html=True)


def sidebar_config():
    st.sidebar.markdown(f"<h1 style='color:{PRIMARY}; text-align: center; width: 100%;'>Portfolio Input Panel</h1><hr style='border:0.5px solid {SECONDARY};'>", unsafe_allow_html=True)


def home_page():
    st.markdown(f"""
                <div style='background:linear-gradient(135deg, rgba(113,97,239,0.12), rgba(149,127,239,0.05)); border:1px solid rgba(149,127,239,0.35); border-radius:22px; padding:55px 50px; margin-top:35px;'>
                    <h2 style='text-align:center; color:{PRIMARY}; font-weight:800; margin-bottom:8px'>
                        Analyze Your Portfolio Like a Professional
                    </h2>
                     <p style='text-align:center; font-size:16px; opacity:0.9; max-width:900px; margin:auto;'>
                        An education-focused equity portfolio analytics dashboard designed to support learning and research.
                        It helps users understand how publicly available market data is translated into portfolio performance,
                        risk indicators, and fundamental metrics through structured analysis and clear visualizations.
                    </p>
                    <hr style='margin:40px 0; border-color:rgba(149,127,239,0.3);' />
                    <div style="display:grid; grid-template-columns:repeat(auto-fit, minmax(260px,1fr)); gap:22px;">
                        <div style="background:rgba(255,255,255,0.04); border:1px solid rgba(149,127,239,0.25); border-radius:16px; padding:22px;">
                            <h3>📈 Portfolio Performance</h3>
                            <p>Track returns, CAGR, allocation, and cost basis.</p>
                            <p style="opacity:0.7;">Understand how your portfolio truly performs over time.</p>
                        </div>
                        <div style="background:rgba(255,255,255,0.04); border:1px solid rgba(149,127,239,0.25);
                                    border-radius:16px; padding:22px;">
                            <h3>⚠️ Risk Intelligence</h3>
                            <p>Volatility, Beta, Sharpe, Drawdowns.</p>
                            <p style="opacity:0.7;">Measure risk before risk measures you.</p>
                        </div>
                        <div style="background:rgba(255,255,255,0.04); border:1px solid rgba(149,127,239,0.25);
                                    border-radius:16px; padding:22px;">
                            <h3>🏦 Fundamental Analysis</h3>
                            <p>Valuation, ROE, ROCE, margins & growth.</p>
                            <p style="opacity:0.7;">Go beyond price. Understand business strength.</p>
                        </div>
                        <div style="background:rgba(255,255,255,0.04); border:1px solid rgba(149,127,239,0.25);
                                    border-radius:16px; padding:22px;">
                            <h3>💸 Dividend Tracking</h3>
                            <p>Yield, income, historical dividend trends.</p>
                            <p style="opacity:0.7;">Track passive income generation clearly.</p>
                        </div>
                    </div>
                    <hr style='margin:45px 0; border-color:rgba(149,127,239,0.3);' />
                    <h2 style='text-align:center; color:{PRIMARY}; margin-bottom:25px;'>
                        How to Get Started
                    </h2>
                    <div style="display:flex; justify-content:space-around; flex-wrap:wrap; gap:30px; text-align:center;">
                        <div>
                            <h3 style="color:{SECONDARY};">1️⃣ Add Stocks</h3>
                            <p>Search and add the stocks you want to analyze from the sidebar</p>
                        </div>
                        <div>
                            <h3 style="color:{SECONDARY};">2️⃣ Configure Holdings</h3>
                            <p>Set the holding period and quantity for each selected stock.</p>
                        </div>
                        <div>
                            <h3 style="color:{SECONDARY};">3️⃣ Generate Analysis</h3>
                            <p>Click <b>Generate Analysis</b> to view portfolio insights and performance metrics.</p>
                        </div>
                    </div>
                    <hr style="margin:45px 0; border-color:rgba(149,127,239,0.25);" />
                    <p style="text-align:center; font-size:13.5px; line-height:1.6; opacity:0.85;">
                        Built using Python • Financial Metrics • Real Market Data • Educational Purpose
                    </p>
                    <p style="text-align:center; font-size:12px; opacity:0.6; margin-top:12px;">
                        <b>Data Source:</b> Yahoo Finance (via yfinance and yahooquery libraries)
                    </p>
                    <p style="text-align:center; font-size:12px; opacity:0.6; margin-top:12px;">
                        <b>Disclaimer:</b> Data may be delayed or differ from official exchange data. 
                        This dashboard is for educational and analytical purposes only and does not constitute investment advice.
                    </p>
                </div>""",unsafe_allow_html=True)
    
    st.markdown(f"""
                <div style='text-align:center; margin-top:45px; padding:18px 0; opacity:1.1; color:{SECONDARY}; font-size:13px; border-top:1px solid rgba(149,127,239,0.25);'>
                    2026 • Portfolio Analytics Dashboard  
                    <br>
                    Designed for learning, analysis, and professional growth.
                </div>""", unsafe_allow_html=True)
    

def interpretation_box(title, points):
    st.markdown(f"""
        <div style="background: rgba(149,127,239,0.1); border: 1px solid rgba(149,127,239,0.3); border-radius: 14px; padding: 20px 24px; margin-top: 25px;">
            <h4 style="color:{PRIMARY}; margin-bottom:12px;">{title}</h4>
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
 
