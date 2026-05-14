import streamlit as st
import pandas as pd
import numpy as np
import math
from datetime import datetime, date
import plotly.graph_objects as go
import plotly.express as px
import json
import io
from fpdf import FPDF

# ═══════════════════════════════════════════════════════════════
#                        PAGE CONFIG
# ═══════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="FinCalc Pro | Professional Financial Suite",
    page_icon="💎",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ═══════════════════════════════════════════════════════════════
#                     PROFESSIONAL CSS THEME
# ═══════════════════════════════════════════════════════════════
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

    /* ===== ROOT VARIABLES ===== */
    :root {
        --primary: #0f172a;
        --primary-light: #1e293b;
        --accent: #3b82f6;
        --accent-glow: rgba(59, 130, 246, 0.3);
        --success: #10b981;
        --success-glow: rgba(16, 185, 129, 0.3);
        --danger: #ef4444;
        --warning: #f59e0b;
        --purple: #8b5cf6;
        --cyan: #06b6d4;
        --text-primary: #f8fafc;
        --text-secondary: #94a3b8;
        --text-muted: #64748b;
        --bg-primary: #0f172a;
        --bg-secondary: #1e293b;
        --bg-card: rgba(30, 41, 59, 0.8);
        --border: rgba(148, 163, 184, 0.1);
        --shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.3);
        --shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.4), 0 2px 4px -1px rgba(0, 0, 0, 0.2);
        --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.5), 0 4px 6px -2px rgba(0, 0, 0, 0.3);
        --shadow-glow: 0 0 20px var(--accent-glow);
        --radius: 16px;
        --radius-sm: 12px;
    }

    /* ===== GLOBAL RESET ===== */
    html, body, [class*="css"] {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
    }

    .main .block-container {
        padding: 2rem 3rem;
        max-width: 1400px;
    }

    /* ===== SIDEBAR ===== */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0f172a 0%, #1e293b 100%) !important;
        border-right: 1px solid var(--border);
    }

    [data-testid="stSidebar"] .sidebar-content {
        padding: 1.5rem !important;
    }

    /* ===== HERO HEADER ===== */
    .hero-container {
        background: linear-gradient(135deg, #0f172a 0%, #1e3a5f 50%, #0f172a 100%);
        padding: 3rem 2.5rem;
        border-radius: var(--radius);
        text-align: center;
        margin-bottom: 2.5rem;
        border: 1px solid var(--border);
        box-shadow: var(--shadow-lg), 0 0 40px rgba(59, 130, 246, 0.1);
        position: relative;
        overflow: hidden;
    }

    .hero-container::before {
        content: '';
        position: absolute;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background: radial-gradient(circle, rgba(59, 130, 246, 0.08) 0%, transparent 70%);
        animation: pulse 4s ease-in-out infinite;
    }

    @keyframes pulse {
        0%, 100% { transform: scale(1); opacity: 0.5; }
        50% { transform: scale(1.1); opacity: 0.8; }
    }

    .hero-container h1 {
        margin: 0;
        font-size: 2.8rem;
        font-weight: 800;
        background: linear-gradient(135deg, #60a5fa 0%, #3b82f6 50%, #8b5cf6 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        letter-spacing: -0.02em;
        position: relative;
        z-index: 1;
    }

    .hero-container p {
        margin: 0.75rem 0 0 0;
        color: var(--text-secondary);
        font-size: 1.1rem;
        font-weight: 400;
        position: relative;
        z-index: 1;
    }

    .hero-badge {
        display: inline-block;
        background: rgba(59, 130, 246, 0.15);
        border: 1px solid rgba(59, 130, 246, 0.3);
        color: #60a5fa;
        padding: 0.35rem 1rem;
        border-radius: 9999px;
        font-size: 0.85rem;
        font-weight: 600;
        margin-top: 1rem;
        position: relative;
        z-index: 1;
    }

    /* ===== GLASS CARDS ===== */
    .glass-card {
        background: var(--bg-card);
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        border: 1px solid var(--border);
        border-radius: var(--radius);
        padding: 1.75rem;
        margin: 1rem 0;
        box-shadow: var(--shadow);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }

    .glass-card:hover {
        transform: translateY(-2px);
        box-shadow: var(--shadow-lg), 0 0 30px rgba(59, 130, 246, 0.08);
        border-color: rgba(59, 130, 246, 0.2);
    }

    .glass-card h3 {
        color: var(--text-primary);
        font-size: 1.1rem;
        font-weight: 600;
        margin-bottom: 0.5rem;
    }

    .glass-card p {
        color: var(--text-secondary);
        font-size: 0.9rem;
        line-height: 1.5;
        margin: 0;
    }

    .glass-card small {
        color: var(--text-muted);
        font-size: 0.8rem;
        display: block;
        margin-top: 0.75rem;
        padding-top: 0.75rem;
        border-top: 1px solid var(--border);
    }

    /* ===== RESULT BOXES ===== */
    .result-box {
        background: linear-gradient(135deg, rgba(16, 185, 129, 0.15) 0%, rgba(6, 182, 212, 0.15) 100%);
        border: 1px solid rgba(16, 185, 129, 0.3);
        padding: 2rem 2.5rem;
        border-radius: var(--radius);
        color: #34d399;
        text-align: center;
        font-size: 2rem;
        font-weight: 700;
        margin: 1.5rem 0;
        box-shadow: 0 0 30px rgba(16, 185, 129, 0.15);
        backdrop-filter: blur(10px);
        position: relative;
        overflow: hidden;
    }

    .result-box::after {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.05), transparent);
        animation: shimmer 3s infinite;
    }

    @keyframes shimmer {
        0% { left: -100%; }
        100% { left: 100%; }
    }

    .result-box-reject {
        background: linear-gradient(135deg, rgba(239, 68, 68, 0.15) 0%, rgba(245, 158, 11, 0.15) 100%);
        border: 1px solid rgba(239, 68, 68, 0.3);
        padding: 2rem 2.5rem;
        border-radius: var(--radius);
        color: #f87171;
        text-align: center;
        font-size: 2rem;
        font-weight: 700;
        margin: 1.5rem 0;
        box-shadow: 0 0 30px rgba(239, 68, 68, 0.15);
        backdrop-filter: blur(10px);
    }

    /* ===== FORMULA & WORKING BOXES ===== */
    .formula-box {
        background: linear-gradient(135deg, rgba(59, 130, 246, 0.08) 0%, rgba(139, 92, 246, 0.08) 100%);
        padding: 1.75rem;
        border-radius: var(--radius-sm);
        font-family: 'Courier New', monospace;
        border-left: 4px solid #3b82f6;
        margin: 1.5rem 0;
        border: 1px solid var(--border);
        border-left-width: 4px;
        color: var(--text-secondary);
        font-size: 1rem;
        line-height: 1.8;
    }

    .formula-box strong {
        color: #60a5fa;
    }

    .working-box {
        background: linear-gradient(135deg, rgba(16, 185, 129, 0.05) 0%, rgba(6, 182, 212, 0.05) 100%);
        padding: 1.75rem;
        border-radius: var(--radius-sm);
        font-family: 'Courier New', monospace;
        border-left: 4px solid #10b981;
        margin: 1.5rem 0;
        border: 1px solid var(--border);
        border-left-width: 4px;
        color: var(--text-secondary);
        font-size: 0.95rem;
        line-height: 2;
    }

    .variable-box {
        background: linear-gradient(135deg, rgba(6, 182, 212, 0.08) 0%, rgba(59, 130, 246, 0.08) 100%);
        padding: 1.5rem;
        border-radius: var(--radius-sm);
        border: 1px solid rgba(6, 182, 212, 0.2);
        margin: 1rem 0;
        color: var(--text-secondary);
    }

    /* ===== TIP BOX ===== */
    .tip-box {
        background: linear-gradient(135deg, rgba(245, 158, 11, 0.1) 0%, rgba(245, 158, 11, 0.05) 100%);
        padding: 1.25rem 1.5rem;
        border-radius: var(--radius-sm);
        border: 1px solid rgba(245, 158, 11, 0.2);
        margin: 1.5rem 0;
        color: #fbbf24;
        font-size: 0.95rem;
    }

    .tip-box strong {
        color: #fbbf24;
        font-weight: 600;
    }

    /* ===== DOWNLOAD BOX ===== */
    .download-box {
        background: linear-gradient(135deg, rgba(16, 185, 129, 0.08) 0%, rgba(59, 130, 246, 0.08) 100%);
        padding: 2rem;
        border-radius: var(--radius);
        border: 1px solid rgba(16, 185, 129, 0.2);
        margin: 2rem 0;
        text-align: center;
    }

    .download-box h4 {
        color: #34d399;
        margin-bottom: 1rem;
        font-size: 1.2rem;
        font-weight: 600;
    }

    /* ===== METRIC CARDS ===== */
    .metric-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 1rem;
        margin: 1.5rem 0;
    }

    .metric-card {
        background: var(--bg-card);
        border: 1px solid var(--border);
        border-radius: var(--radius-sm);
        padding: 1.5rem;
        text-align: center;
        transition: all 0.3s ease;
    }

    .metric-card:hover {
        border-color: rgba(59, 130, 246, 0.3);
        transform: translateY(-2px);
    }

    .metric-value {
        font-size: 1.5rem;
        font-weight: 700;
        color: var(--text-primary);
        margin-bottom: 0.25rem;
    }

    .metric-label {
        font-size: 0.85rem;
        color: var(--text-muted);
        font-weight: 500;
    }

    /* ===== SECTION HEADERS ===== */
    .section-header {
        font-size: 1.4rem;
        font-weight: 700;
        color: var(--text-primary);
        margin: 2rem 0 1rem 0;
        padding-bottom: 0.75rem;
        border-bottom: 2px solid var(--border);
        display: flex;
        align-items: center;
        gap: 0.75rem;
    }

    .section-header::after {
        content: '';
        flex: 1;
        height: 2px;
        background: linear-gradient(90deg, var(--border), transparent);
        margin-left: 1rem;
    }

    /* ===== BUTTONS ===== */
    .stButton > button {
        background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: var(--radius-sm) !important;
        padding: 0.75rem 2rem !important;
        font-weight: 600 !important;
        font-size: 1rem !important;
        box-shadow: 0 4px 14px rgba(59, 130, 246, 0.4) !important;
        transition: all 0.3s ease !important;
        text-transform: none !important;
        letter-spacing: 0 !important;
    }

    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 20px rgba(59, 130, 246, 0.6) !important;
        background: linear-gradient(135deg, #60a5fa 0%, #3b82f6 100%) !important;
    }

    .stButton > button:active {
        transform: translateY(0) !important;
    }

    /* ===== INPUT FIELDS ===== */
    .stNumberInput input, .stSelectbox > div > div, .stDateInput input {
        background: var(--bg-secondary) !important;
        border: 1px solid var(--border) !important;
        border-radius: var(--radius-sm) !important;
        color: var(--text-primary) !important;
        font-size: 0.95rem !important;
    }

    .stNumberInput input:focus, .stSelectbox > div > div:focus {
        border-color: #3b82f6 !important;
        box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.2) !important;
    }

    .stRadio > div {
        background: var(--bg-secondary) !important;
        border-radius: var(--radius-sm) !important;
        padding: 0.5rem !important;
    }

    /* ===== DATAFRAMES ===== */
    .stDataFrame {
        border-radius: var(--radius-sm) !important;
        overflow: hidden !important;
    }

    .stDataFrame th {
        background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%) !important;
        color: #60a5fa !important;
        font-weight: 600 !important;
        text-transform: uppercase !important;
        font-size: 0.8rem !important;
        letter-spacing: 0.05em !important;
        padding: 1rem !important;
    }

    .stDataFrame td {
        background: var(--bg-secondary) !important;
        color: var(--text-secondary) !important;
        border-bottom: 1px solid var(--border) !important;
        padding: 0.875rem 1rem !important;
    }

    .stDataFrame tr:hover td {
        background: rgba(59, 130, 246, 0.05) !important;
        color: var(--text-primary) !important;
    }

    /* ===== TABS ===== */
    .stTabs [data-baseweb="tab-list"] {
        background: var(--bg-secondary) !important;
        border-radius: var(--radius-sm) !important;
        padding: 0.5rem !important;
        gap: 0.25rem !important;
        border: 1px solid var(--border) !important;
    }

    .stTabs [data-baseweb="tab"] {
        color: var(--text-muted) !important;
        font-weight: 500 !important;
        border-radius: 8px !important;
        padding: 0.5rem 1rem !important;
    }

    .stTabs [data-baseweb="tab-highlight"] {
        background: linear-gradient(135deg, #3b82f6 0%, #8b5cf6 100%) !important;
        border-radius: 8px !important;
    }

    .stTabs [aria-selected="true"] {
        color: white !important;
        font-weight: 600 !important;
    }

    /* ===== SIDEBAR ITEMS ===== */
    .sidebar-brand {
        text-align: center;
        padding: 1.5rem 1rem;
        margin-bottom: 1rem;
    }

    .sidebar-brand h2 {
        background: linear-gradient(135deg, #60a5fa 0%, #8b5cf6 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800;
        font-size: 1.5rem;
        margin: 0;
    }

    .sidebar-brand p {
        color: var(--text-muted);
        font-size: 0.8rem;
        margin: 0.5rem 0 0 0;
    }

    .sidebar-divider {
        height: 1px;
        background: linear-gradient(90deg, transparent, var(--border), transparent);
        margin: 1rem 0;
    }

    /* ===== FOOTER ===== */
    .footer {
        text-align: center;
        padding: 2.5rem 2rem;
        margin-top: 3rem;
        border-top: 1px solid var(--border);
        color: var(--text-muted);
        font-size: 0.9rem;
    }

    .footer strong {
        color: var(--text-secondary);
        font-weight: 600;
    }

    /* ===== ANIMATIONS ===== */
    @keyframes fadeInUp {
        from {
            opacity: 0;
            transform: translateY(20px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }

    .animate-in {
        animation: fadeInUp 0.6s ease-out forwards;
    }

    .delay-1 { animation-delay: 0.1s; }
    .delay-2 { animation-delay: 0.2s; }
    .delay-3 { animation-delay: 0.3s; }

    /* ===== STATUS INDICATORS ===== */
    .status-accept {
        display: inline-flex;
        align-items: center;
        gap: 0.5rem;
        background: rgba(16, 185, 129, 0.15);
        color: #34d399;
        padding: 0.5rem 1rem;
        border-radius: 9999px;
        font-weight: 600;
        font-size: 0.9rem;
        border: 1px solid rgba(16, 185, 129, 0.3);
    }

    .status-reject {
        display: inline-flex;
        align-items: center;
        gap: 0.5rem;
        background: rgba(239, 68, 68, 0.15);
        color: #f87171;
        padding: 0.5rem 1rem;
        border-radius: 9999px;
        font-weight: 600;
        font-size: 0.9rem;
        border: 1px solid rgba(239, 68, 68, 0.3);
    }

    /* ===== SCROLLBAR ===== */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }

    ::-webkit-scrollbar-track {
        background: var(--bg-primary);
    }

    ::-webkit-scrollbar-thumb {
        background: var(--bg-secondary);
        border-radius: 4px;
        border: 2px solid var(--bg-primary);
    }

    ::-webkit-scrollbar-thumb:hover {
        background: #334155;
    }
</style>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════
#                       SESSION STATE
# ═══════════════════════════════════════════════════════════════
if 'calculation_history' not in st.session_state:
    st.session_state.calculation_history = []

# ═══════════════════════════════════════════════════════════════
#                      HELPER FUNCTIONS
# ═══════════════════════════════════════════════════════════════
def format_currency(value, symbol="$"):
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return "N/A"
    return f"{symbol}{value:,.2f}"

def format_percent(value):
    if value is None:
        return "N/A"
    return f"{value:.4f}%"

def get_frequency_options():
    return {
        "Annually (1/year)": 1,
        "Semi-Annually (2/year)": 2,
        "Quarterly (4/year)": 4,
        "Monthly (12/year)": 12,
    }

def add_to_history(calc_type, inputs, outputs):
    st.session_state.calculation_history.append({
        'id': len(st.session_state.calculation_history) + 1,
        'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        'type': calc_type,
        'inputs': str(inputs),
        'outputs': str(outputs)
    })

# ═══════════════════════════════════════════════════════════════
#              TIME INPUT HELPER (Years/Months/Days/Dates)
# ═══════════════════════════════════════════════════════════════
def get_time_input(key_prefix="time", label="Time Period"):
    st.markdown(f'<div class="section-header">⏰ {label}</div>', unsafe_allow_html=True)
    time_mode = st.selectbox(
        "How do you want to enter time?",
        ["Years", "Months", "Days", "Date Range (Pick two dates)"],
        key=f"{key_prefix}_mode"
    )

    if time_mode == "Years":
        yrs = st.number_input("Enter Years", min_value=0.0, value=0.0, step=0.5, key=f"{key_prefix}_years")
        return yrs, f"{yrs} years"
    elif time_mode == "Months":
        months = st.number_input("Enter Months", min_value=0.0, value=0.0, step=1.0, key=f"{key_prefix}_months")
        yrs = months / 12
        return yrs, f"{months} months = {yrs:.6f} years"
    elif time_mode == "Days":
        days = st.number_input("Enter Days", min_value=0.0, value=0.0, step=1.0, key=f"{key_prefix}_days")
        yrs = days / 365
        return yrs, f"{days} days = {yrs:.6f} years"
    else:
        col_a, col_b = st.columns(2)
        with col_a:
            start_date = st.date_input("Start Date", value=date.today(), key=f"{key_prefix}_start")
        with col_b:
            end_date = st.date_input("End Date", value=date.today(), key=f"{key_prefix}_end")
        delta = (end_date - start_date).days
        if delta < 0:
            st.error("End date must be after start date!")
            return 0.0, "Invalid date range"
        yrs = delta / 365
        return yrs, f"{start_date} to {end_date} = {delta} days = {yrs:.6f} years"

# ═══════════════════════════════════════════════════════════════
#                      PDF GENERATOR
# ═══════════════════════════════════════════════════════════════
class PDFReport(FPDF):
    def __init__(self):
        super().__init__()
        self.set_auto_page_break(auto=True, margin=15)

    def header(self):
        self.set_font('Arial', 'B', 18)
        self.set_text_color(59, 130, 246)
        self.cell(0, 12, 'FinCalc Pro - Financial Report', 0, 1, 'C')
        self.set_font('Arial', 'I', 9)
        self.set_text_color(128, 128, 128)
        self.cell(0, 5, f'Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}', 0, 1, 'C')
        self.ln(8)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')

def generate_pdf_report(title, summary_dict, schedule_df=None):
    pdf = PDFReport()
    pdf.add_page()
    pdf.set_font('Arial', 'B', 14)
    pdf.set_text_color(60, 60, 60)
    pdf.cell(0, 10, title, 0, 1, 'L')
    pdf.ln(5)
    pdf.set_font('Arial', 'B', 11)
    pdf.cell(0, 8, 'Calculation Summary:', 0, 1, 'L')
    pdf.set_font('Arial', '', 10)
    for key, value in summary_dict.items():
        pdf.cell(70, 7, str(key) + ':', 0, 0, 'L')
        pdf.cell(0, 7, str(value), 0, 1, 'L')
    if schedule_df is not None and len(schedule_df) > 0:
        pdf.ln(10)
        pdf.set_font('Arial', 'B', 11)
        pdf.cell(0, 8, 'Detailed Schedule:', 0, 1, 'L')
        pdf.set_font('Arial', 'B', 8)
        pdf.set_fill_color(59, 130, 246)
        pdf.set_text_color(255, 255, 255)
        cols = schedule_df.columns.tolist()
        col_width = 190 / len(cols)
        for col in cols:
            pdf.cell(col_width, 7, str(col)[:12], 1, 0, 'C', True)
        pdf.ln()
        pdf.set_font('Arial', '', 7)
        pdf.set_text_color(60, 60, 60)
        for idx, row in schedule_df.head(30).iterrows():
            for col in cols:
                val = str(row[col])[:12]
                pdf.cell(col_width, 6, val, 1, 0, 'C')
            pdf.ln()
        if len(schedule_df) > 30:
            pdf.set_font('Arial', 'I', 8)
            pdf.cell(0, 8, f'... and {len(schedule_df) - 30} more rows', 0, 1, 'C')
    return pdf.output(dest='S').encode('latin-1')

def generate_excel_report(summary_dict, schedule_df=None):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        summary_data = pd.DataFrame(list(summary_dict.items()), columns=['Parameter', 'Value'])
        summary_data.to_excel(writer, sheet_name='Summary', index=False)
        if schedule_df is not None:
            schedule_df.to_excel(writer, sheet_name='Schedule', index=False)
    return output.getvalue()

# ═══════════════════════════════════════════════════════════════
#                  DOWNLOAD SECTION COMPONENT
# ═══════════════════════════════════════════════════════════════
def render_download_section(calc_name, summary_dict, schedule_df=None, currency_symbol="$"):
    st.markdown("---")
    st.markdown("""
    <div class="download-box">
        <h4>📥 Export Your Analysis</h4>
        <p style="color: #94a3b8; margin-top: 0.5rem;">Download your complete financial report in multiple formats</p>
    </div>
    """, unsafe_allow_html=True)
    file_base = calc_name.lower().replace(" ", "_") + "_" + datetime.now().strftime("%Y%m%d_%H%M%S")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        if schedule_df is not None and len(schedule_df) > 0:
            csv_data = schedule_df.to_csv(index=False)
        else:
            csv_data = pd.DataFrame(list(summary_dict.items()), columns=['Parameter', 'Value']).to_csv(index=False)
        st.download_button(label="📄 CSV", data=csv_data, file_name=f"{file_base}.csv", mime="text/csv", use_container_width=True)
    with col2:
        excel_data = generate_excel_report(summary_dict, schedule_df)
        st.download_button(label="📊 Excel", data=excel_data, file_name=f"{file_base}.xlsx",
                           mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", use_container_width=True)
    with col3:
        try:
            pdf_data = generate_pdf_report(calc_name, summary_dict, schedule_df)
            st.download_button(label="📑 PDF", data=pdf_data, file_name=f"{file_base}.pdf", mime="application/pdf", use_container_width=True)
        except:
            st.button("📑 PDF Error", disabled=True, use_container_width=True)
    with col4:
        json_data = json.dumps({
            "calculation_type": calc_name,
            "timestamp": datetime.now().isoformat(),
            "currency": currency_symbol,
            "summary": summary_dict,
            "schedule": schedule_df.to_dict('records') if schedule_df is not None else None
        }, indent=2, default=str)
        st.download_button(label="🔗 JSON", data=json_data, file_name=f"{file_base}.json", mime="application/json", use_container_width=True)

# ═══════════════════════════════════════════════════════════════
#                      CHART FUNCTIONS
# ═══════════════════════════════════════════════════════════════
def create_pie_chart(labels, values, title):
    colors = ['#3b82f6', '#10b981', '#ef4444', '#f59e0b', '#8b5cf6', '#06b6d4']
    fig = go.Figure(data=[go.Pie(
        labels=labels, 
        values=values, 
        hole=0.55, 
        marker_colors=colors[:len(labels)], 
        textinfo='label+percent',
        textfont=dict(size=13, color='white'),
        hovertemplate='<b>%{label}</b><br>%{value:,.2f}<br>%{percent}<extra></extra>'
    )])
    fig.update_layout(
        title=dict(text=f'<b>{title}</b>', font=dict(size=18, color='#f8fafc')),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(family='Inter, sans-serif', color='#94a3b8'),
        height=420,
        showlegend=True,
        legend=dict(
            orientation='h',
            yanchor='bottom',
            y=-0.1,
            xanchor='center',
            x=0.5,
            font=dict(size=12)
        )
    )
    return fig

def create_line_chart(x_data, y_data_dict, title, x_title, y_title):
    fig = go.Figure()
    colors = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6']
    for i, (name, y_data) in enumerate(y_data_dict.items()):
        fig.add_trace(go.Scatter(
            x=x_data, 
            y=y_data, 
            mode='lines+markers', 
            name=name, 
            line=dict(color=colors[i % len(colors)], width=3),
            marker=dict(size=8, line=dict(width=2, color='rgba(0,0,0,0.3)')),
            fill='tozeroy' if i == 0 else None,
            fillcolor=f'rgba({[59,16,245,239,139][i%5]}, {[130,185,158,68,92][i%5]}, {[246,129,11,68,246][i%5]}, 0.1)'
        ))
    fig.update_layout(
        title=dict(text=f'<b>{title}</b>', font=dict(size=18, color='#f8fafc')),
        xaxis_title=x_title,
        yaxis_title=y_title,
        hovermode='x unified',
        height=420,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(family='Inter, sans-serif', color='#94a3b8'),
        xaxis=dict(
            gridcolor='rgba(148, 163, 184, 0.1)',
            linecolor='rgba(148, 163, 184, 0.2)',
            zerolinecolor='rgba(148, 163, 184, 0.1)'
        ),
        yaxis=dict(
            gridcolor='rgba(148, 163, 184, 0.1)',
            linecolor='rgba(148, 163, 184, 0.2)',
            zerolinecolor='rgba(148, 163, 184, 0.1)'
        ),
        legend=dict(
            orientation='h',
            yanchor='bottom',
            y=-0.15,
            xanchor='center',
            x=0.5,
            bgcolor='rgba(30, 41, 59, 0.8)',
            bordercolor='rgba(148, 163, 184, 0.2)',
            borderwidth=1
        )
    )
    return fig

def create_bar_chart(categories, values_dict, title, y_title):
    fig = go.Figure()
    colors = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444']
    for i, (name, values) in enumerate(values_dict.items()):
        fig.add_trace(go.Bar(
            name=name, 
            x=categories, 
            y=values, 
            marker_color=colors[i % len(colors)],
            marker_line_color='rgba(0,0,0,0.3)',
            marker_line_width=1,
            opacity=0.9
        ))
    fig.update_layout(
        title=dict(text=f'<b>{title}</b>', font=dict(size=18, color='#f8fafc')),
        yaxis_title=y_title,
        barmode='group',
        height=420,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(family='Inter, sans-serif', color='#94a3b8'),
        xaxis=dict(
            gridcolor='rgba(148, 163, 184, 0.1)',
            linecolor='rgba(148, 163, 184, 0.2)'
        ),
        yaxis=dict(
            gridcolor='rgba(148, 163, 184, 0.1)',
            linecolor='rgba(148, 163, 184, 0.2)',
            zerolinecolor='rgba(148, 163, 184, 0.1)'
        ),
        legend=dict(
            orientation='h',
            yanchor='bottom',
            y=-0.15,
            xanchor='center',
            x=0.5,
            bgcolor='rgba(30, 41, 59, 0.8)',
            bordercolor='rgba(148, 163, 184, 0.2)',
            borderwidth=1
        )
    )
    return fig

# ═══════════════════════════════════════════════════════════════
#                         SIDEBAR
# ═══════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("""
    <div class="sidebar-brand">
        <h2>💎 FinCalc Pro</h2>
        <p>Professional Financial Suite</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="sidebar-divider"></div>', unsafe_allow_html=True)

    currency_symbol = st.selectbox("💲 Currency", ["$", "₹", "€", "£", "Rs", "PKR"])

    st.markdown('<div class="sidebar-divider"></div>', unsafe_allow_html=True)

    calculator_type = st.radio(
        "📊 Calculator",
        [
            "🏠 Home",
            "📝 Simple Interest",
            "📈 Compound Interest",
            "🏧 EMI Calculator",
            "💰 SIP Calculator",
            "📉 NPV Calculator",
            "📃 Bond Valuation",
            "🔄 Annuity Calculator",
            "📋 History",
            "📖 Formulas"
        ]
    )

    st.markdown('<div class="sidebar-divider"></div>', unsafe_allow_html=True)

    st.markdown("""
    <div class="tip-box" style="margin-top: 1rem;">
        <strong>💡 How to Use</strong><br><br>
        1. Enter known values<br>
        2. Leave ONE field as 0<br>
        3. Click Calculate<br>
        4. Export results!
    </div>
    """, unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════
#                        HOME PAGE
# ═══════════════════════════════════════════════════════════════
if calculator_type == "🏠 Home":
    st.markdown("""
    <div class="hero-container animate-in">
        <h1>FinCalc Pro</h1>
        <p>Professional Financial Analysis & Computation Suite</p>
        <div class="hero-badge">✨ Smart Auto-Calculate Missing Values</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="glass-card animate-in delay-1">
        <h3>🎯 Smart Calculation Engine</h3>
        <p>Enter any 3 known values and leave 1 field as zero — our intelligent engine will automatically compute the missing variable using precise financial formulas with complete step-by-step working.</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="section-header">📦 Available Calculators</div>', unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("""
        <div class="glass-card animate-in delay-1">
            <h3>📝 Simple Interest</h3>
            <p>Find any one of: Principal, Rate, Time, or Interest</p>
            <small>I = (P × R × T) / 100</small>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("""
        <div class="glass-card animate-in delay-2">
            <h3>🏧 EMI Calculator</h3>
            <p>Calculate monthly EMI with complete amortization schedule</p>
            <small>Full payment breakdown with charts</small>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown("""
        <div class="glass-card animate-in delay-1">
            <h3>📈 Compound Interest</h3>
            <p>Find any one of: PV, FV, Rate, or Time</p>
            <small>Multiple compounding frequencies supported</small>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("""
        <div class="glass-card animate-in delay-2">
            <h3>💰 SIP Calculator</h3>
            <p>Investment returns with annual step-up capability</p>
            <small>Year-wise wealth accumulation schedule</small>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown("""
        <div class="glass-card animate-in delay-1">
            <h3>📉 NPV Calculator</h3>
            <p>Net Present Value & IRR Analysis</p>
            <small>Cash flow analysis with profitability index</small>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("""
        <div class="glass-card animate-in delay-2">
            <h3>🔄 Annuity Calculator</h3>
            <p>Ordinary & Annuity Due calculations</p>
            <small>PV & FV of annuities with schedules</small>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("""
    <div class="glass-card animate-in delay-3" style="margin-top: 1.5rem;">
        <h3>📃 Bond Valuation</h3>
        <p>Calculate bond prices with complete coupon payment schedules and yield analysis</p>
        <small>Price = Σ[C/(1+y)^t] + F/(1+y)^n</small>
    </div>
    """, unsafe_allow_html=True)

    st.info("👈 Select a calculator from the sidebar to begin your financial analysis")

# ═══════════════════════════════════════════════════════════════
#                 SIMPLE INTEREST CALCULATOR
# ═══════════════════════════════════════════════════════════════
elif calculator_type == "📝 Simple Interest":
    st.markdown("""
    <div class="hero-container">
        <h1>📝 Simple Interest</h1>
        <p>Auto-Calculate Any Missing Value</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="formula-box">
        <strong>Formula:</strong> I = (P × R × T) / 100<br><br>
        <strong>Variables:</strong><br>
        • P = Principal (Initial Amount)<br>
        • R = Rate of Interest (% per year)<br>
        • T = Time Period (in years)<br>
        • I = Simple Interest (Earned/Paid)
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="tip-box">
        💡 <strong>Enter 3 values, leave 1 as zero (0)</strong> — that value will be calculated automatically!
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="section-header">📝 Enter Your Values</div>', unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        P = st.number_input(f"🏦 Principal (P) [{currency_symbol}]", min_value=0.0, value=0.0, step=1000.0, help="Enter 0 if you want to calculate this")
        R = st.number_input("📊 Rate (R) [% per year]", min_value=0.0, value=0.0, step=0.5, help="Enter 0 if you want to calculate this")
    with col2:
        T, time_desc = get_time_input(key_prefix="si_time", label="Time (T)")
        I = st.number_input(f"💵 Interest (I) [{currency_symbol}]", min_value=0.0, value=0.0, step=100.0, help="Enter 0 if you want to calculate this")

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        calculate = st.button("🔄 Calculate Missing Value", use_container_width=True, type="primary")

    if calculate:
        values = {'P': P, 'R': R, 'T': T, 'I': I}
        zeros = sum(1 for v in values.values() if v == 0)
        if zeros == 0:
            st.warning("⚠ All values are filled! Leave ONE field as 0 to calculate it.")
        elif zeros > 1:
            st.error(f"❌ You left {zeros} fields as zero. Please fill at least 3 values and leave only 1 as zero.")
        else:
            try:
                working_steps = []
                if P == 0:
                    if R == 0 or T == 0:
                        st.error("❌ Cannot calculate - Rate and Time cannot both be zero!")
                        st.stop()
                    P = (I * 100) / (R * T)
                    calculated_field = "Principal (P)"
                    calculated_value = format_currency(P, currency_symbol)
                    working_steps.append(f"Given: I = {currency_symbol}{I:,.2f}, R = {R}%, T = {T:.6f} years")
                    working_steps.append(f"Formula: P = (I × 100) / (R × T)")
                    working_steps.append(f"P = ({I} × 100) / ({R} × {T:.6f})")
                    working_steps.append(f"P = {I*100} / {R*T:.6f}")
                    working_steps.append(f"P = {currency_symbol}{P:,.2f}")
                elif R == 0:
                    if P == 0 or T == 0:
                        st.error("❌ Cannot calculate - Principal and Time cannot both be zero!")
                        st.stop()
                    R = (I * 100) / (P * T)
                    calculated_field = "Rate (R)"
                    calculated_value = f"{R:.4f}%"
                    working_steps.append(f"Given: P = {currency_symbol}{P:,.2f}, I = {currency_symbol}{I:,.2f}, T = {T:.6f} years")
                    working_steps.append(f"Formula: R = (I × 100) / (P × T)")
                    working_steps.append(f"R = ({I} × 100) / ({P} × {T:.6f})")
                    working_steps.append(f"R = {I*100} / {P*T:.6f}")
                    working_steps.append(f"R = {R:.4f}%")
                elif T == 0:
                    if P == 0 or R == 0:
                        st.error("❌ Cannot calculate - Principal and Rate cannot both be zero!")
                        st.stop()
                    T = (I * 100) / (P * R)
                    calculated_field = "Time (T)"
                    calculated_value = f"{T:.6f} years"
                    working_steps.append(f"Given: P = {currency_symbol}{P:,.2f}, R = {R}%, I = {currency_symbol}{I:,.2f}")
                    working_steps.append(f"Formula: T = (I × 100) / (P × R)")
                    working_steps.append(f"T = ({I} × 100) / ({P} × {R})")
                    working_steps.append(f"T = {I*100} / {P*R:.6f}")
                    working_steps.append(f"T = {T:.6f} years ({T*12:.2f} months, {T*365:.0f} days)")
                else:
                    I = (P * R * T) / 100
                    calculated_field = "Interest (I)"
                    calculated_value = format_currency(I, currency_symbol)
                    working_steps.append(f"Given: P = {currency_symbol}{P:,.2f}, R = {R}%, T = {T:.6f} years")
                    working_steps.append(f"Formula: I = (P × R × T) / 100")
                    working_steps.append(f"I = ({P} × {R} × {T:.6f}) / 100")
                    working_steps.append(f"I = {P*R*T:.6f} / 100")
                    working_steps.append(f"I = {currency_symbol}{I:,.2f}")

                total_amount = P + I
                yearly_interest = (P * R) / 100 if R > 0 else 0

                st.markdown(f"""
                <div class="result-box">
                    ✅ Calculated: {calculated_field} = {calculated_value}
                </div>
                """, unsafe_allow_html=True)

                st.markdown('<div class="section-header">📐 Step-by-Step Working</div>', unsafe_allow_html=True)
                working_html = "<br>".join(working_steps)
                st.markdown(f'<div class="working-box">{working_html}</div>', unsafe_allow_html=True)
                st.markdown(f"**Total Amount (P + I) = {currency_symbol}{P:,.2f} + {currency_symbol}{I:,.2f} = {format_currency(total_amount, currency_symbol)}**")

                st.markdown('<div class="section-header">📊 Complete Summary</div>', unsafe_allow_html=True)

                cols = st.columns(4)
                metrics = [
                    ("Principal (P)", format_currency(P, currency_symbol)),
                    ("Rate (R)", f"{R:.4f}%"),
                    ("Time (T)", f"{T:.4f} years"),
                    ("Interest (I)", format_currency(I, currency_symbol))
                ]
                for col, (label, value) in zip(cols, metrics):
                    with col:
                        st.markdown(f"""
                        <div class="metric-card">
                            <div class="metric-value">{value}</div>
                            <div class="metric-label">{label}</div>
                        </div>
                        """, unsafe_allow_html=True)

                st.success(f"🏦 **Total Amount (P + I):** {format_currency(total_amount, currency_symbol)}")

                # Year-wise Schedule
                st.markdown("---")
                st.markdown('<div class="section-header">📋 Year-wise Interest Schedule</div>', unsafe_allow_html=True)
                schedule_data = []
                num_full_years = int(T) if T >= 1 else 1
                for year in range(1, num_full_years + 1):
                    cumulative_interest = yearly_interest * year
                    schedule_data.append({
                        'Year': year,
                        'Opening Balance': round(P, 2),
                        'Interest This Year': round(yearly_interest, 2),
                        'Cumulative Interest': round(cumulative_interest, 2),
                        'Closing Balance': round(P + cumulative_interest, 2)
                    })
                schedule_df = pd.DataFrame(schedule_data)
                display_df = schedule_df.copy()
                for col in ['Opening Balance', 'Interest This Year', 'Cumulative Interest', 'Closing Balance']:
                    display_df[col] = display_df[col].apply(lambda x: format_currency(x, currency_symbol))
                st.dataframe(display_df, use_container_width=True, hide_index=True)

                # Charts
                st.markdown("---")
                st.markdown('<div class="section-header">📈 Visual Analysis</div>', unsafe_allow_html=True)
                tab1, tab2 = st.tabs(["🥧 Breakdown", "📈 Growth"])
                with tab1:
                    fig = create_pie_chart(['Principal', 'Total Interest'], [P, I], 'Principal vs Interest')
                    st.plotly_chart(fig, use_container_width=True)
                with tab2:
                    if len(schedule_df) > 0:
                        fig = create_line_chart(schedule_df['Year'].tolist(), {'Cumulative Interest': schedule_df['Cumulative Interest'].tolist(), 'Closing Balance': schedule_df['Closing Balance'].tolist()}, 'Growth Over Time', 'Year', f'Amount ({currency_symbol})')
                        st.plotly_chart(fig, use_container_width=True)

                summary_dict = {
                    'Calculation Type': 'Simple Interest',
                    'Calculated Field': calculated_field,
                    'Calculated Value': calculated_value,
                    'Principal (P)': format_currency(P, currency_symbol),
                    'Rate (R)': f'{R:.4f}%',
                    'Time (T)': f'{T:.6f} years',
                    'Time Description': time_desc,
                    'Interest (I)': format_currency(I, currency_symbol),
                    'Total Amount': format_currency(total_amount, currency_symbol),
                    'Yearly Interest': format_currency(yearly_interest, currency_symbol),
                    'Calculation Date': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
                render_download_section("Simple Interest", summary_dict, schedule_df, currency_symbol)
                add_to_history("Simple Interest", {'P': P, 'R': R, 'T': T}, {'I': I, 'Calculated': calculated_field})
            except ZeroDivisionError:
                st.error("❌ Cannot divide by zero! Check your inputs.")
            except Exception as e:
                st.error(f"❌ Error: {e}")

# ═══════════════════════════════════════════════════════════════
#              COMPOUND INTEREST CALCULATOR
# ═══════════════════════════════════════════════════════════════
elif calculator_type == "📈 Compound Interest":
    st.markdown("""
    <div class="hero-container">
        <h1>📈 Compound Interest</h1>
        <p>Auto-Calculate Any Missing Value</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="formula-box">
        <strong>Formula:</strong> FV = PV × (1 + r/m)^(n×m)<br><br>
        <strong>Variables:</strong><br>
        • PV = Present Value (Initial Amount)<br>
        • FV = Future Value (Final Amount)<br>
        • r = Annual Interest Rate (%)<br>
        • n = Time Period (Years)<br>
        • m = Compounding Frequency (per year)
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="tip-box">
        💡 <strong>Enter 3 values, leave 1 as zero (0)</strong> — that value will be calculated automatically!
    </div>
    """, unsafe_allow_html=True)

    freq_options = get_frequency_options()
    frequency = st.selectbox("🔄 Compounding Frequency", list(freq_options.keys()), index=3)
    m = freq_options[frequency]

    st.markdown('<div class="section-header">📝 Enter Your Values</div>', unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        PV = st.number_input(f"🏦 Present Value (PV) [{currency_symbol}]", min_value=0.0, value=0.0, step=10000.0, help="Enter 0 to calculate")
        FV = st.number_input(f"💵 Future Value (FV) [{currency_symbol}]", min_value=0.0, value=0.0, step=10000.0, help="Enter 0 to calculate")
    with col2:
        r = st.number_input("📊 Annual Rate (r) [%]", min_value=0.0, value=0.0, step=0.5, help="Enter 0 to calculate")
        n, time_desc = get_time_input(key_prefix="ci_time", label="Time (n)")

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        calculate = st.button("🔄 Calculate Missing Value", use_container_width=True, type="primary")

    if calculate:
        values = {'PV': PV, 'FV': FV, 'r': r, 'n': n}
        zeros = sum(1 for v in values.values() if v == 0)
        if zeros == 0:
            st.warning("⚠ All values are filled! Leave ONE field as 0.")
        elif zeros > 1:
            st.error(f"❌ You left {zeros} fields as zero. Please fill at least 3 values.")
        else:
            try:
                working_steps = []
                user_rate = r

                if PV == 0:
                    r_periodic = (r / 100) / m
                    total_periods = n * m
                    PV = FV / ((1 + r_periodic) ** total_periods)
                    calculated_field = "Present Value (PV)"
                    calculated_value = format_currency(PV, currency_symbol)
                    working_steps.append(f"Given: FV = {currency_symbol}{FV:,.2f}, r = {r}%, n = {n:.6f} years, m = {m}")
                    working_steps.append(f"Formula: PV = FV / (1 + r/m)^(n×m)")
                    working_steps.append(f"r_periodic = {r}/100/{m} = {r_periodic:.8f}")
                    working_steps.append(f"Total periods = {n:.6f} × {m} = {total_periods:.6f}")
                    working_steps.append(f"PV = {FV} / (1 + {r_periodic:.8f})^{total_periods:.6f}")
                    working_steps.append(f"PV = {FV} / {(1+r_periodic)**total_periods:.8f}")
                    working_steps.append(f"PV = {currency_symbol}{PV:,.2f}")
                elif FV == 0:
                    r_periodic = (r / 100) / m
                    total_periods = n * m
                    FV = PV * ((1 + r_periodic) ** total_periods)
                    calculated_field = "Future Value (FV)"
                    calculated_value = format_currency(FV, currency_symbol)
                    working_steps.append(f"Given: PV = {currency_symbol}{PV:,.2f}, r = {r}%, n = {n:.6f} years, m = {m}")
                    working_steps.append(f"Formula: FV = PV × (1 + r/m)^(n×m)")
                    working_steps.append(f"r_periodic = {r}/100/{m} = {r_periodic:.8f}")
                    working_steps.append(f"Total periods = {n:.6f} × {m} = {total_periods:.6f}")
                    working_steps.append(f"FV = {PV} × (1 + {r_periodic:.8f})^{total_periods:.6f}")
                    working_steps.append(f"FV = {PV} × {(1+r_periodic)**total_periods:.8f}")
                    working_steps.append(f"FV = {currency_symbol}{FV:,.2f}")
                elif r == 0:
                    total_periods = n * m
                    r_periodic = (FV / PV) ** (1 / total_periods) - 1
                    r = r_periodic * m * 100
                    calculated_field = "Annual Rate (r)"
                    calculated_value = f"{r:.4f}%"
                    working_steps.append(f"Given: PV = {currency_symbol}{PV:,.2f}, FV = {currency_symbol}{FV:,.2f}, n = {n:.6f} years, m = {m}")
                    working_steps.append(f"Formula: r = m × [(FV/PV)^(1/(n×m)) - 1] × 100")
                    working_steps.append(f"Total periods = {n:.6f} × {m} = {total_periods:.6f}")
                    working_steps.append(f"r_periodic = ({FV}/{PV})^(1/{total_periods:.6f}) - 1 = {r_periodic:.8f}")
                    working_steps.append(f"r = {r_periodic:.8f} × {m} × 100 = {r:.4f}%")
                else:
                    r_periodic = (r / 100) / m
                    n = math.log(FV / PV) / (m * math.log(1 + r_periodic))
                    calculated_field = "Time (n)"
                    calculated_value = f"{n:.6f} years"
                    working_steps.append(f"Given: PV = {currency_symbol}{PV:,.2f}, FV = {currency_symbol}{FV:,.2f}, r = {r}%, m = {m}")
                    working_steps.append(f"Formula: n = ln(FV/PV) / [m × ln(1 + r/m)]")
                    working_steps.append(f"r_periodic = {r}/100/{m} = {r_periodic:.8f}")
                    working_steps.append(f"n = ln({FV}/{PV}) / [{m} × ln(1 + {r_periodic:.8f})]")
                    working_steps.append(f"n = {math.log(FV/PV):.8f} / {m * math.log(1 + r_periodic):.8f}")
                    working_steps.append(f"n = {n:.6f} years ({n*12:.2f} months)")

                r_periodic = (r / 100) / m
                total_periods = int(n * m)
                compound_interest = FV - PV
                effective_rate = ((1 + (r/100)/m) ** m - 1) * 100

                st.markdown(f"""
                <div class="result-box">
                    ✅ Calculated: {calculated_field} = {calculated_value}
                </div>
                """, unsafe_allow_html=True)

                st.markdown('<div class="section-header">📐 Step-by-Step Working</div>', unsafe_allow_html=True)
                working_html = "<br>".join(working_steps)
                st.markdown(f'<div class="working-box">{working_html}</div>', unsafe_allow_html=True)

                st.markdown('<div class="section-header">📊 Complete Summary</div>', unsafe_allow_html=True)
                cols = st.columns(4)
                metrics = [
                    ("Present Value", format_currency(PV, currency_symbol)),
                    ("Future Value", format_currency(FV, currency_symbol)),
                    ("Interest Earned", format_currency(compound_interest, currency_symbol)),
                    ("Effective Rate", f"{effective_rate:.4f}%")
                ]
                for col, (label, value) in zip(cols, metrics):
                    with col:
                        st.markdown(f"""
                        <div class="metric-card">
                            <div class="metric-value">{value}</div>
                            <div class="metric-label">{label}</div>
                        </div>
                        """, unsafe_allow_html=True)

                # Year-wise Schedule
                st.markdown("---")
                st.markdown('<div class="section-header">📋 Year-wise Compounding Schedule</div>', unsafe_allow_html=True)
                schedule_data = []
                balance = PV
                for year in range(1, int(n) + 1):
                    opening = balance
                    for _ in range(m):
                        balance = balance * (1 + r_periodic)
                    interest = balance - opening
                    schedule_data.append({'Year': year, 'Opening Balance': round(opening, 2), 'Interest Earned': round(interest, 2), 'Closing Balance': round(balance, 2)})
                schedule_df = pd.DataFrame(schedule_data)
                display_df = schedule_df.copy()
                for col in ['Opening Balance', 'Interest Earned', 'Closing Balance']:
                    display_df[col] = display_df[col].apply(lambda x: format_currency(x, currency_symbol))
                st.dataframe(display_df, use_container_width=True, hide_index=True)

                st.markdown("---")
                st.markdown('<div class="section-header">📈 Visual Analysis</div>', unsafe_allow_html=True)
                tab1, tab2 = st.tabs(["🥧 Breakdown", "📈 Growth"])
                with tab1:
                    fig = create_pie_chart(['Principal', 'Compound Interest'], [PV, compound_interest], 'Principal vs Interest')
                    st.plotly_chart(fig, use_container_width=True)
                with tab2:
                    if len(schedule_df) > 0:
                        fig = create_line_chart(schedule_df['Year'].tolist(), {'Balance': schedule_df['Closing Balance'].tolist()}, 'Balance Growth', 'Year', f'Balance ({currency_symbol})')
                        st.plotly_chart(fig, use_container_width=True)

                summary_dict = {
                    'Calculation Type': 'Compound Interest',
                    'Calculated Field': calculated_field,
                    'Calculated Value': calculated_value,
                    'Present Value (PV)': format_currency(PV, currency_symbol),
                    'Future Value (FV)': format_currency(FV, currency_symbol),
                    'Annual Rate (r)': f'{r:.4f}%',
                    'Time (n)': f'{n:.6f} years',
                    'Time Description': time_desc,
                    'Compounding': frequency,
                    'Compound Interest': format_currency(compound_interest, currency_symbol),
                    'Effective Annual Rate': f'{effective_rate:.4f}%',
                    'Calculation Date': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
                render_download_section("Compound Interest", summary_dict, schedule_df, currency_symbol)
                add_to_history("Compound Interest", {'PV': PV, 'r': r, 'n': n, 'm': m}, {'FV': FV, 'Calculated': calculated_field})
            except Exception as e:
                st.error(f"❌ Error: {e}")

# ═══════════════════════════════════════════════════════════════
#                     EMI CALCULATOR
# ═══════════════════════════════════════════════════════════════
elif calculator_type == "🏧 EMI Calculator":
    st.markdown("""
    <div class="hero-container">
        <h1>🏧 EMI Calculator</h1>
        <p>Calculate Loan EMI with Amortization Schedule</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="formula-box">
        <strong>Formula:</strong> EMI = P × r × (1+r)^n / [(1+r)^n - 1]<br><br>
        <strong>Variables:</strong><br>
        • P = Principal Loan Amount<br>
        • r = Monthly Interest Rate (Annual Rate / 12 / 100)<br>
        • n = Total Number of Months
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="section-header">📝 Enter Loan Details</div>', unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        loan_amount = st.number_input(f"🏦 Loan Amount [{currency_symbol}]", min_value=1000.0, value=1000000.0, step=50000.0)
        annual_rate = st.number_input("📊 Annual Interest Rate [%]", min_value=0.1, value=10.0, step=0.25)
    with col2:
        tenure_n, tenure_desc = get_time_input(key_prefix="emi_time", label="Loan Tenure")

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        calculate = st.button("🔄 Calculate EMI", use_container_width=True, type="primary")

    if calculate:
        if tenure_n <= 0:
            st.error("❌ Loan tenure must be greater than zero!")
        else:
            try:
                monthly_rate = annual_rate / 12 / 100
                total_months = int(round(tenure_n * 12))
                if total_months < 1:
                    total_months = 1

                working_steps = []
                working_steps.append(f"Given: P = {currency_symbol}{loan_amount:,.2f}, Annual Rate = {annual_rate}%, Tenure = {tenure_desc}")
                working_steps.append(f"Monthly Rate (r) = {annual_rate} / 12 / 100 = {monthly_rate:.8f}")
                working_steps.append(f"Total Months (n) = {total_months}")

                if monthly_rate > 0:
                    emi = loan_amount * monthly_rate * (1 + monthly_rate)**total_months / ((1 + monthly_rate)**total_months - 1)
                    working_steps.append(f"EMI = P × r × (1+r)^n / [(1+r)^n - 1]")
                    working_steps.append(f"EMI = {loan_amount} × {monthly_rate:.8f} × (1+{monthly_rate:.8f})^{total_months} / [(1+{monthly_rate:.8f})^{total_months} - 1]")
                    factor = (1 + monthly_rate)**total_months
                    working_steps.append(f"(1+r)^n = {factor:.8f}")
                    working_steps.append(f"EMI = {loan_amount} × {monthly_rate:.8f} × {factor:.8f} / [{factor:.8f} - 1]")
                    working_steps.append(f"EMI = {loan_amount * monthly_rate * factor:.2f} / {factor - 1:.8f}")
                    working_steps.append(f"EMI = {currency_symbol}{emi:,.2f}")
                else:
                    emi = loan_amount / total_months
                    working_steps.append(f"Rate = 0, so EMI = P / n = {loan_amount} / {total_months} = {currency_symbol}{emi:,.2f}")

                total_payment = emi * total_months
                total_interest = total_payment - loan_amount
                working_steps.append(f"Total Payment = EMI × n = {currency_symbol}{emi:,.2f} × {total_months} = {currency_symbol}{total_payment:,.2f}")
                working_steps.append(f"Total Interest = Total Payment - P = {currency_symbol}{total_payment:,.2f} - {currency_symbol}{loan_amount:,.2f} = {currency_symbol}{total_interest:,.2f}")

                st.markdown(f"""
                <div class="result-box">
                    📅 Monthly EMI: {format_currency(emi, currency_symbol)}
                </div>
                """, unsafe_allow_html=True)

                st.markdown('<div class="section-header">📐 Step-by-Step Working</div>', unsafe_allow_html=True)
                working_html = "<br>".join(working_steps)
                st.markdown(f'<div class="working-box">{working_html}</div>', unsafe_allow_html=True)

                cols = st.columns(4)
                metrics = [
                    ("Loan Amount", format_currency(loan_amount, currency_symbol)),
                    ("Total Interest", format_currency(total_interest, currency_symbol)),
                    ("Total Payment", format_currency(total_payment, currency_symbol)),
                    ("Interest %", f"{(total_interest/loan_amount)*100:.1f}%")
                ]
                for col, (label, value) in zip(cols, metrics):
                    with col:
                        st.markdown(f"""
                        <div class="metric-card">
                            <div class="metric-value">{value}</div>
                            <div class="metric-label">{label}</div>
                        </div>
                        """, unsafe_allow_html=True)

                st.markdown("---")
                st.markdown('<div class="section-header">📋 Amortization Schedule</div>', unsafe_allow_html=True)
                schedule_data = []
                balance = loan_amount
                for month in range(1, total_months + 1):
                    interest_payment = balance * monthly_rate
                    principal_payment = emi - interest_payment
                    balance = max(0, balance - principal_payment)
                    schedule_data.append({'Month': month, 'EMI': round(emi, 2), 'Principal': round(principal_payment, 2), 'Interest': round(interest_payment, 2), 'Balance': round(balance, 2)})
                schedule_df = pd.DataFrame(schedule_data)
                if len(schedule_df) > 24:
                    st.info(f"📋 Showing first 24 of {len(schedule_df)} months. Download for complete schedule.")
                    display_schedule = schedule_df.head(24).copy()
                else:
                    display_schedule = schedule_df.copy()
                display_df = display_schedule.copy()
                for col in ['EMI', 'Principal', 'Interest', 'Balance']:
                    display_df[col] = display_df[col].apply(lambda x: format_currency(x, currency_symbol))
                st.dataframe(display_df, use_container_width=True, hide_index=True)

                st.markdown("---")
                st.markdown('<div class="section-header">📈 Visual Analysis</div>', unsafe_allow_html=True)
                tab1, tab2 = st.tabs(["🥧 Breakdown", "📈 Balance Over Time"])
                with tab1:
                    fig = create_pie_chart(['Principal', 'Total Interest'], [loan_amount, total_interest], 'Payment Breakdown')
                    st.plotly_chart(fig, use_container_width=True)
                with tab2:
                    sample = schedule_df.iloc[::max(1, len(schedule_df)//50)]
                    fig = create_line_chart(sample['Month'].tolist(), {'Outstanding Balance': sample['Balance'].tolist()}, 'Loan Balance Over Time', 'Month', f'Balance ({currency_symbol})')
                    st.plotly_chart(fig, use_container_width=True)

                summary_dict = {
                    'Calculation Type': 'EMI Calculator',
                    'Loan Amount': format_currency(loan_amount, currency_symbol),
                    'Annual Interest Rate': f'{annual_rate}%',
                    'Loan Tenure': f'{tenure_desc} ({total_months} months)',
                    'Monthly EMI': format_currency(emi, currency_symbol),
                    'Total Payment': format_currency(total_payment, currency_symbol),
                    'Total Interest': format_currency(total_interest, currency_symbol),
                    'Interest as % of Principal': f'{(total_interest/loan_amount)*100:.2f}%',
                    'Calculation Date': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
                render_download_section("EMI Calculator", summary_dict, schedule_df, currency_symbol)
                add_to_history("EMI Calculator", {'Loan': loan_amount, 'Rate': annual_rate, 'Tenure': tenure_desc}, {'EMI': emi, 'Total Interest': total_interest})
            except Exception as e:
                st.error(f"❌ Error: {e}")

# ═══════════════════════════════════════════════════════════════
#                     SIP CALCULATOR
# ═══════════════════════════════════════════════════════════════
elif calculator_type == "💰 SIP Calculator":
    st.markdown("""
    <div class="hero-container">
        <h1>💰 SIP Calculator</h1>
        <p>Systematic Investment Plan with Step-up</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="formula-box">
        <strong>Formula:</strong> FV = P × [(1+r)^n - 1] / r × (1+r)<br><br>
        <strong>Variables:</strong><br>
        • P = Monthly Investment<br>
        • r = Monthly Rate of Return<br>
        • n = Total Number of Months
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="section-header">📝 Enter Investment Details</div>', unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        monthly_sip = st.number_input(f"🏦 Monthly SIP [{currency_symbol}]", min_value=100.0, value=10000.0, step=1000.0)
        expected_return = st.number_input("📊 Expected Annual Return [%]", min_value=1.0, value=12.0, step=0.5)
    with col2:
        investment_years = st.number_input("⏰ Investment Period [Years]", min_value=1, value=10, step=1)
        step_up = st.number_input("📈 Annual Step-up [%]", min_value=0.0, value=10.0, step=5.0, help="Increase SIP by this % every year")

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        calculate = st.button("🔄 Calculate SIP Returns", use_container_width=True, type="primary")

    if calculate:
        try:
            monthly_rate = expected_return / 12 / 100

            working_steps = []
            working_steps.append(f"Given: Monthly SIP = {currency_symbol}{monthly_sip:,.2f}, Expected Return = {expected_return}% p.a., Period = {investment_years} years, Step-up = {step_up}%")
            working_steps.append(f"Monthly Rate = {expected_return} / 12 / 100 = {monthly_rate:.8f}")

            schedule_data = []
            current_sip = monthly_sip
            total_invested = 0
            current_value = 0

            for year in range(1, investment_years + 1):
                year_invested = 0
                for month in range(1, 13):
                    current_value = current_value * (1 + monthly_rate) + current_sip
                    total_invested += current_sip
                    year_invested += current_sip
                schedule_data.append({
                    'Year': year,
                    'Monthly SIP': round(current_sip, 2),
                    'Year Investment': round(year_invested, 2),
                    'Total Invested': round(total_invested, 2),
                    'Portfolio Value': round(current_value, 2),
                    'Total Gain': round(current_value - total_invested, 2)
                })
                current_sip = current_sip * (1 + step_up / 100)

            schedule_df = pd.DataFrame(schedule_data)
            future_value = current_value
            wealth_gained = future_value - total_invested
            absolute_return = (wealth_gained / total_invested) * 100

            working_steps.append(f"Total Invested = {currency_symbol}{total_invested:,.2f}")
            working_steps.append(f"Future Value = {currency_symbol}{future_value:,.2f}")
            working_steps.append(f"Wealth Gained = {currency_symbol}{future_value:,.2f} - {currency_symbol}{total_invested:,.2f} = {currency_symbol}{wealth_gained:,.2f}")
            working_steps.append(f"Absolute Return = ({wealth_gained}/{total_invested}) × 100 = {absolute_return:.2f}%")

            st.markdown(f"""
            <div class="result-box">
                🏦 Future Value: {format_currency(future_value, currency_symbol)}
            </div>
            """, unsafe_allow_html=True)

            st.markdown('<div class="section-header">📐 Step-by-Step Working</div>', unsafe_allow_html=True)
            working_html = "<br>".join(working_steps)
            st.markdown(f'<div class="working-box">{working_html}</div>', unsafe_allow_html=True)

            cols = st.columns(4)
            metrics = [
                ("Total Invested", format_currency(total_invested, currency_symbol)),
                ("Wealth Gained", format_currency(wealth_gained, currency_symbol)),
                ("Absolute Return", f"{absolute_return:.1f}%"),
                ("Final SIP", format_currency(schedule_df['Monthly SIP'].iloc[-1], currency_symbol))
            ]
            for col, (label, value) in zip(cols, metrics):
                with col:
                    st.markdown(f"""
                    <div class="metric-card">
                        <div class="metric-value">{value}</div>
                        <div class="metric-label">{label}</div>
                    </div>
                    """, unsafe_allow_html=True)

            st.markdown("---")
            st.markdown('<div class="section-header">📋 Year-wise Investment Schedule</div>', unsafe_allow_html=True)
            display_df = schedule_df.copy()
            for col in ['Monthly SIP', 'Year Investment', 'Total Invested', 'Portfolio Value', 'Total Gain']:
                display_df[col] = display_df[col].apply(lambda x: format_currency(x, currency_symbol))
            st.dataframe(display_df, use_container_width=True, hide_index=True)

            st.markdown("---")
            st.markdown('<div class="section-header">📈 Visual Analysis</div>', unsafe_allow_html=True)
            tab1, tab2 = st.tabs(["📈 Growth", "🥧 Breakdown"])
            with tab1:
                fig = create_line_chart(schedule_df['Year'].tolist(), {'Total Invested': schedule_df['Total Invested'].tolist(), 'Portfolio Value': schedule_df['Portfolio Value'].tolist()}, 'SIP Growth Over Time', 'Year', f'Amount ({currency_symbol})')
                st.plotly_chart(fig, use_container_width=True)
            with tab2:
                fig = create_pie_chart(['Invested', 'Gains'], [total_invested, wealth_gained], 'Investment Breakdown')
                st.plotly_chart(fig, use_container_width=True)

            summary_dict = {
                'Calculation Type': 'SIP Calculator',
                'Starting Monthly SIP': format_currency(monthly_sip, currency_symbol),
                'Expected Annual Return': f'{expected_return}%',
                'Investment Period': f'{investment_years} years',
                'Annual Step-up': f'{step_up}%',
                'Final Monthly SIP': format_currency(schedule_df['Monthly SIP'].iloc[-1], currency_symbol),
                'Total Invested': format_currency(total_invested, currency_symbol),
                'Future Value': format_currency(future_value, currency_symbol),
                'Wealth Gained': format_currency(wealth_gained, currency_symbol),
                'Absolute Return': f'{absolute_return:.2f}%',
                'Calculation Date': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            render_download_section("SIP Calculator", summary_dict, schedule_df, currency_symbol)
            add_to_history("SIP Calculator", {'SIP': monthly_sip, 'Return': expected_return, 'Years': investment_years}, {'FV': future_value, 'Gain': wealth_gained})
        except Exception as e:
            st.error(f"❌ Error: {e}")

# ═══════════════════════════════════════════════════════════════
#                     NPV CALCULATOR
# ═══════════════════════════════════════════════════════════════
elif calculator_type == "📉 NPV Calculator":
    st.markdown("""
    <div class="hero-container">
        <h1>📉 NPV Calculator</h1>
        <p>Net Present Value & IRR Analysis</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="formula-box">
        <strong>Formula:</strong> NPV = -C₀ + Σ[CFₜ / (1+r)^t]<br><br>
        <strong>Variables:</strong><br>
        • C₀ = Initial Investment<br>
        • CFₜ = Cash Flow at time t<br>
        • r = Discount Rate
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="section-header">📝 Enter Project Details</div>', unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)
    with col1:
        initial_investment = st.number_input(f"🏦 Initial Investment [{currency_symbol}]", min_value=0.0, value=100000.0, step=10000.0)
    with col2:
        discount_rate = st.number_input("📊 Discount Rate [%]", min_value=0.0, value=10.0, step=0.5)
    with col3:
        num_years = st.number_input("⏰ Number of Years", min_value=1, max_value=30, value=5, step=1)

    st.markdown('<div class="section-header">💵 Enter Annual Cash Flows</div>', unsafe_allow_html=True)
    cash_flows = []
    cols = st.columns(min(num_years, 5))
    for i in range(num_years):
        with cols[i % 5]:
            cf = st.number_input(f"Year {i+1}", min_value=0.0, value=30000.0, step=5000.0, key=f"npv_cf_{i}")
            cash_flows.append(cf)

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        calculate = st.button("🔄 Calculate NPV", use_container_width=True, type="primary")

    if calculate:
        try:
            r_dec = discount_rate / 100
            npv = -initial_investment

            working_steps = []
            working_steps.append(f"Given: Initial Investment = {currency_symbol}{initial_investment:,.2f}, Discount Rate = {discount_rate}%")
            working_steps.append(f"NPV = -C₀ + Σ[CFₜ / (1+r)^t]")
            working_steps.append(f"NPV = -{currency_symbol}{initial_investment:,.2f}")

            schedule_data = [{'Year': 0, 'Cash Flow': round(-initial_investment, 2), 'Discount Factor': 1.0, 'Present Value': round(-initial_investment, 2), 'Cumulative PV': round(-initial_investment, 2)}]
            cumulative_pv = -initial_investment

            for t, cf in enumerate(cash_flows, 1):
                discount_factor = 1 / (1 + r_dec) ** t
                pv = cf * discount_factor
                npv += pv
                cumulative_pv += pv
                schedule_data.append({'Year': t, 'Cash Flow': round(cf, 2), 'Discount Factor': round(discount_factor, 6), 'Present Value': round(pv, 2), 'Cumulative PV': round(cumulative_pv, 2)})
                working_steps.append(f"  + {currency_symbol}{cf:,.2f} / (1+{discount_rate/100})^{t} = {currency_symbol}{cf:,.2f} × {discount_factor:.6f} = {currency_symbol}{pv:,.2f}")

            working_steps.append(f"NPV = {currency_symbol}{npv:,.2f}")

            schedule_df = pd.DataFrame(schedule_data)

            # IRR
            irr = 0.1
            for _ in range(1000):
                f = -initial_investment + sum(cf / (1 + irr) ** (t+1) for t, cf in enumerate(cash_flows))
                f_prime = sum(-(t+1) * cf / (1 + irr) ** (t+2) for t, cf in enumerate(cash_flows))
                if abs(f_prime) < 1e-10:
                    break
                irr_new = irr - f / f_prime
                if abs(irr_new - irr) < 1e-10:
                    break
                irr = irr_new
            irr_percent = irr * 100
            profitability_index = sum(s['Present Value'] for s in schedule_data[1:]) / initial_investment
            working_steps.append(f"IRR ≈ {irr_percent:.2f}%")
            working_steps.append(f"Profitability Index = PV of inflows / Investment = {profitability_index:.4f}")

            if npv > 0:
                st.markdown(f'<div class="result-box">✅ NPV = {format_currency(npv, currency_symbol)} — ACCEPT PROJECT</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="result-box-reject">❌ NPV = {format_currency(npv, currency_symbol)} — REJECT PROJECT</div>', unsafe_allow_html=True)

            st.markdown('<div class="section-header">📐 Step-by-Step Working</div>', unsafe_allow_html=True)
            working_html = "<br>".join(working_steps)
            st.markdown(f'<div class="working-box">{working_html}</div>', unsafe_allow_html=True)

            cols = st.columns(4)
            metrics = [
                ("NPV", format_currency(npv, currency_symbol)),
                ("IRR", f"{irr_percent:.2f}%"),
                ("Profitability Index", f"{profitability_index:.2f}"),
                ("Decision", "ACCEPT ✅" if npv > 0 else "REJECT ❌")
            ]
            for col, (label, value) in zip(cols, metrics):
                with col:
                    st.markdown(f"""
                    <div class="metric-card">
                        <div class="metric-value">{value}</div>
                        <div class="metric-label">{label}</div>
                    </div>
                    """, unsafe_allow_html=True)

            st.markdown("---")
            st.markdown('<div class="section-header">📋 Cash Flow Schedule</div>', unsafe_allow_html=True)
            display_df = schedule_df.copy()
            display_df['Cash Flow'] = display_df['Cash Flow'].apply(lambda x: format_currency(x, currency_symbol))
            display_df['Present Value'] = display_df['Present Value'].apply(lambda x: format_currency(x, currency_symbol))
            display_df['Cumulative PV'] = display_df['Cumulative PV'].apply(lambda x: format_currency(x, currency_symbol))
            st.dataframe(display_df, use_container_width=True, hide_index=True)

            st.markdown("---")
            st.markdown('<div class="section-header">📈 Visual Analysis</div>', unsafe_allow_html=True)
            tab1, tab2 = st.tabs(["📊 Cash Flows", "📈 NPV Profile"])
            with tab1:
                fig = create_bar_chart([f'Y{y}' for y in schedule_df['Year'].tolist()], {'Cash Flow': schedule_df['Cash Flow'].tolist(), 'Present Value': schedule_df['Present Value'].tolist()}, 'Cash Flow vs Present Value', f'Amount ({currency_symbol})')
                st.plotly_chart(fig, use_container_width=True)
            with tab2:
                rates = list(range(0, 31, 2))
                npvs = []
                for rate in rates:
                    npv_temp = -initial_investment + sum(cf / (1 + rate/100) ** (t+1) for t, cf in enumerate(cash_flows))
                    npvs.append(npv_temp)
                fig = create_line_chart(rates, {'NPV': npvs}, 'NPV vs Discount Rate', 'Discount Rate (%)', f'NPV ({currency_symbol})')
                st.plotly_chart(fig, use_container_width=True)

            summary_dict = {
                'Calculation Type': 'NPV Calculator',
                'Initial Investment': format_currency(initial_investment, currency_symbol),
                'Discount Rate': f'{discount_rate}%',
                'Number of Years': num_years,
                'Total Cash Inflows': format_currency(sum(cash_flows), currency_symbol),
                'NPV': format_currency(npv, currency_symbol),
                'IRR': f'{irr_percent:.2f}%',
                'Profitability Index': f'{profitability_index:.2f}',
                'Decision': 'ACCEPT' if npv > 0 else 'REJECT',
                'Calculation Date': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            render_download_section("NPV Calculator", summary_dict, schedule_df, currency_symbol)
            add_to_history("NPV Calculator", {'Investment': initial_investment, 'Rate': discount_rate}, {'NPV': npv, 'IRR': irr_percent})
        except Exception as e:
            st.error(f"❌ Error: {e}")

# ═══════════════════════════════════════════════════════════════
#                     BOND VALUATION
# ═══════════════════════════════════════════════════════════════
elif calculator_type == "📃 Bond Valuation":
    st.markdown("""
    <div class="hero-container">
        <h1>📃 Bond Valuation</h1>
        <p>Calculate Bond Price with Coupon Schedule</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="formula-box">
        <strong>Formula:</strong> Price = Σ[C/(1+y)^t] + F/(1+y)^n<br><br>
        <strong>Variables:</strong><br>
        • C = Coupon Payment<br>
        • F = Face Value<br>
        • y = Yield to Maturity (YTM)<br>
        • n = Number of Periods
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="section-header">📝 Enter Bond Details</div>', unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        face_value = st.number_input(f"💵 Face Value [{currency_symbol}]", min_value=100.0, value=1000.0, step=100.0)
        coupon_rate = st.number_input("📊 Coupon Rate [%]", min_value=0.0, value=8.0, step=0.25)
        bond_frequency = st.selectbox("🔄 Coupon Frequency", ["Annual", "Semi-Annual", "Quarterly"])
    with col2:
        ytm = st.number_input("📈 Yield to Maturity [%]", min_value=0.1, value=10.0, step=0.25)
        years_to_maturity = st.number_input("⏰ Years to Maturity", min_value=1, value=10, step=1)

    freq_map = {"Annual": 1, "Semi-Annual": 2, "Quarterly": 4}
    m = freq_map[bond_frequency]

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        calculate = st.button("🔄 Calculate Bond Price", use_container_width=True, type="primary")

    if calculate:
        try:
            coupon_payment = (face_value * coupon_rate / 100) / m
            total_periods = years_to_maturity * m
            periodic_ytm = (ytm / 100) / m

            working_steps = []
            working_steps.append(f"Given: Face Value = {currency_symbol}{face_value:,.2f}, Coupon Rate = {coupon_rate}%, YTM = {ytm}%, Maturity = {years_to_maturity} yrs, Frequency = {bond_frequency}")
            working_steps.append(f"Coupon Payment = ({face_value} × {coupon_rate}/100) / {m} = {currency_symbol}{coupon_payment:,.2f}")
            working_steps.append(f"Total Periods = {years_to_maturity} × {m} = {total_periods}")
            working_steps.append(f"Periodic YTM = {ytm}/100/{m} = {periodic_ytm:.8f}")
            working_steps.append(f"Price = Σ[C/(1+y)^t] + F/(1+y)^n")

            schedule_data = []
            pv_coupons = 0
            for period in range(1, total_periods + 1):
                discount_factor = 1 / (1 + periodic_ytm) ** period
                pv_coupon = coupon_payment * discount_factor
                pv_coupons += pv_coupon
                schedule_data.append({'Period': period, 'Year': round(period / m, 2), 'Coupon Payment': round(coupon_payment, 2), 'Discount Factor': round(discount_factor, 6), 'PV of Coupon': round(pv_coupon, 2)})

            pv_face = face_value / (1 + periodic_ytm) ** total_periods
            bond_price = pv_coupons + pv_face
            current_yield = (coupon_payment * m / bond_price) * 100

            working_steps.append(f"PV of Coupons = {currency_symbol}{pv_coupons:,.2f}")
            working_steps.append(f"PV of Face Value = {face_value} / (1+{periodic_ytm:.8f})^{total_periods} = {currency_symbol}{pv_face:,.2f}")
            working_steps.append(f"Bond Price = {currency_symbol}{pv_coupons:,.2f} + {currency_symbol}{pv_face:,.2f} = {currency_symbol}{bond_price:,.2f}")
            working_steps.append(f"Current Yield = ({coupon_payment * m}/{bond_price:.2f}) × 100 = {current_yield:.2f}%")

            schedule_df = pd.DataFrame(schedule_data)

            st.markdown(f'<div class="result-box">📃 Bond Price: {format_currency(bond_price, currency_symbol)}</div>', unsafe_allow_html=True)

            st.markdown('<div class="section-header">📐 Step-by-Step Working</div>', unsafe_allow_html=True)
            working_html = "<br>".join(working_steps)
            st.markdown(f'<div class="working-box">{working_html}</div>', unsafe_allow_html=True)

            if bond_price > face_value:
                st.success(f"📈 **Premium Bond** — Coupon Rate ({coupon_rate}%) > YTM ({ytm}%)")
            elif bond_price < face_value:
                st.warning(f"📉 **Discount Bond** — Coupon Rate ({coupon_rate}%) < YTM ({ytm}%)")
            else:
                st.info(f"➡ **Par Bond** — Coupon Rate = YTM")

            cols = st.columns(4)
            metrics = [
                ("Bond Price", format_currency(bond_price, currency_symbol)),
                ("PV of Coupons", format_currency(pv_coupons, currency_symbol)),
                ("PV of Face Value", format_currency(pv_face, currency_symbol)),
                ("Current Yield", f"{current_yield:.2f}%")
            ]
            for col, (label, value) in zip(cols, metrics):
                with col:
                    st.markdown(f"""
                    <div class="metric-card">
                        <div class="metric-value">{value}</div>
                        <div class="metric-label">{label}</div>
                    </div>
                    """, unsafe_allow_html=True)

            st.markdown("---")
            st.markdown('<div class="section-header">📋 Coupon Payment Schedule</div>', unsafe_allow_html=True)
            display_df = schedule_df.copy()
            display_df['Coupon Payment'] = display_df['Coupon Payment'].apply(lambda x: format_currency(x, currency_symbol))
            display_df['PV of Coupon'] = display_df['PV of Coupon'].apply(lambda x: format_currency(x, currency_symbol))
            if len(display_df) > 20:
                st.info(f"📋 Showing first 20 of {len(display_df)} periods.")
                st.dataframe(display_df.head(20), use_container_width=True, hide_index=True)
            else:
                st.dataframe(display_df, use_container_width=True, hide_index=True)

            st.markdown("---")
            st.markdown('<div class="section-header">📈 Visual Analysis</div>', unsafe_allow_html=True)
            tab1, tab2 = st.tabs(["🥧 Breakdown", "📈 Price Sensitivity"])
            with tab1:
                fig = create_pie_chart(['PV of Coupons', 'PV of Face Value'], [pv_coupons, pv_face], 'Bond Price Components')
                st.plotly_chart(fig, use_container_width=True)
            with tab2:
                ytm_range = list(range(1, 21))
                prices = []
                for y in ytm_range:
                    py = (y / 100) / m
                    pv_c = sum(coupon_payment / (1 + py) ** t for t in range(1, total_periods + 1))
                    pv_f = face_value / (1 + py) ** total_periods
                    prices.append(pv_c + pv_f)
                fig = create_line_chart(ytm_range, {'Bond Price': prices}, 'Bond Price vs YTM', 'YTM (%)', f'Price ({currency_symbol})')
                st.plotly_chart(fig, use_container_width=True)

            summary_dict = {
                'Calculation Type': 'Bond Valuation',
                'Face Value': format_currency(face_value, currency_symbol),
                'Coupon Rate': f'{coupon_rate}%',
                'Yield to Maturity': f'{ytm}%',
                'Years to Maturity': f'{years_to_maturity} years',
                'Coupon Frequency': bond_frequency,
                'Coupon Payment': format_currency(coupon_payment, currency_symbol),
                'Bond Price': format_currency(bond_price, currency_symbol),
                'PV of Coupons': format_currency(pv_coupons, currency_symbol),
                'PV of Face Value': format_currency(pv_face, currency_symbol),
                'Current Yield': f'{current_yield:.2f}%',
                'Bond Type': 'Premium' if bond_price > face_value else ('Discount' if bond_price < face_value else 'Par'),
                'Calculation Date': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            render_download_section("Bond Valuation", summary_dict, schedule_df, currency_symbol)
            add_to_history("Bond Valuation", {'Face': face_value, 'Coupon': coupon_rate, 'YTM': ytm}, {'Price': bond_price})
        except Exception as e:
            st.error(f"❌ Error: {e}")

# ═══════════════════════════════════════════════════════════════
#                    ANNUITY CALCULATOR
# ═══════════════════════════════════════════════════════════════
elif calculator_type == "🔄 Annuity Calculator":
    st.markdown("""
    <div class="hero-container">
        <h1>🔄 Annuity Calculator</h1>
        <p>Ordinary Annuity & Annuity Due — PV and FV</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="formula-box">
        <strong>Ordinary Annuity (payments at END of period):</strong><br>
        • PV = PMT × [(1 - (1+r)^(-n)) / r]<br>
        • FV = PMT × [((1+r)^n - 1) / r]<br><br>
        <strong>Annuity Due (payments at BEGINNING of period):</strong><br>
        • PV = PMT × [(1 - (1+r)^(-n)) / r] × (1+r)<br>
        • FV = PMT × [((1+r)^n - 1) / r] × (1+r)<br><br>
        <strong>Variables:</strong><br>
        • PMT = Payment per period<br>
        • r = Interest rate per period<br>
        • n = Number of periods
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="tip-box">
        💡 <strong>Enter 3 values, leave 1 as zero (0)</strong> among PMT, r, n, and the value you want to find (PV or FV) — it will be calculated!
    </div>
    """, unsafe_allow_html=True)

    annuity_type = st.radio("Select Annuity Type", ["Ordinary Annuity (End of Period)", "Annuity Due (Beginning of Period)"], horizontal=True)
    is_due = "Due" in annuity_type

    calc_target = st.radio("What do you want to calculate?", ["Future Value (FV)", "Present Value (PV)", "Payment (PMT)", "Interest Rate (r)", "Number of Periods (n)"], horizontal=True)

    freq_options_ann = get_frequency_options()
    ann_frequency = st.selectbox("🔄 Payment Frequency", list(freq_options_ann.keys()), index=3, key="ann_freq")
    m_ann = freq_options_ann[ann_frequency]

    st.markdown('<div class="section-header">📝 Enter Your Values</div>', unsafe_allow_html=True)
    st.markdown("*(Leave the field you want to calculate as 0)*")

    col1, col2 = st.columns(2)
    with col1:
        ann_pmt = st.number_input(f"💵 Payment per period (PMT) [{currency_symbol}]", min_value=0.0, value=0.0, step=1000.0, help="Enter 0 to calculate this")
        ann_rate = st.number_input("📊 Annual Interest Rate [%]", min_value=0.0, value=0.0, step=0.5, help="Enter 0 to calculate this")
    with col2:
        ann_n, ann_time_desc = get_time_input(key_prefix="ann_time", label="Total Time Period")
        ann_value = st.number_input(f"🎯 {'FV' if 'FV' in calc_target else 'PV'} [{currency_symbol}]", min_value=0.0, value=0.0, step=10000.0, help="Enter 0 to calculate this")

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        calculate = st.button("🔄 Calculate Annuity", use_container_width=True, type="primary")

    if calculate:
        try:
            total_periods = ann_n * m_ann
            rate_per_period = (ann_rate / 100) / m_ann if ann_rate > 0 else 0

            working_steps = []
            due_label = "Annuity Due" if is_due else "Ordinary Annuity"
            working_steps.append(f"Type: {due_label}")
            working_steps.append(f"Payment Frequency: {ann_frequency} (m = {m_ann})")
            working_steps.append(f"Time: {ann_time_desc}")
            working_steps.append(f"Total Periods (n) = {ann_n:.6f} × {m_ann} = {total_periods:.4f}")
            if ann_rate > 0:
                working_steps.append(f"Rate per period (r) = {ann_rate}/100/{m_ann} = {rate_per_period:.8f}")

            result_value = 0
            calculated_field = ""
            calculated_value_str = ""

            if "FV" in calc_target:
                if ann_pmt == 0 or ann_rate == 0 or total_periods == 0:
                    if ann_pmt == 0 and ann_rate > 0 and total_periods > 0 and ann_value > 0:
                        st.error("❌ Cannot calculate FV when PMT is 0. Try calculating PMT instead.")
                        st.stop()
                    if total_periods == 0:
                        st.error("❌ Time period must be > 0.")
                        st.stop()
                PMT = ann_pmt
                r = rate_per_period
                n_p = total_periods

                if r == 0:
                    fv = PMT * n_p
                    working_steps.append(f"r = 0, so FV = PMT × n = {PMT} × {n_p:.4f} = {currency_symbol}{fv:,.2f}")
                else:
                    fv = PMT * (((1 + r) ** n_p - 1) / r)
                    working_steps.append(f"FV (Ordinary) = PMT × [((1+r)^n - 1) / r]")
                    working_steps.append(f"FV = {PMT} × [((1+{r:.8f})^{n_p:.4f} - 1) / {r:.8f}]")
                    factor = ((1 + r) ** n_p - 1) / r
                    working_steps.append(f"FV = {PMT} × {factor:.8f} = {currency_symbol}{fv:,.2f}")
                    if is_due:
                        fv = fv * (1 + r)
                        working_steps.append(f"Annuity Due: FV = FV × (1+r) = {currency_symbol}{fv:,.2f}")
                result_value = fv
                calculated_field = "Future Value (FV)"
                calculated_value_str = format_currency(fv, currency_symbol)

            elif "PV" in calc_target:
                PMT = ann_pmt
                r = rate_per_period
                n_p = total_periods

                if r == 0:
                    pv = PMT * n_p
                    working_steps.append(f"r = 0, so PV = PMT × n = {PMT} × {n_p:.4f} = {currency_symbol}{pv:,.2f}")
                else:
                    pv = PMT * ((1 - (1 + r) ** (-n_p)) / r)
                    working_steps.append(f"PV (Ordinary) = PMT × [(1 - (1+r)^(-n)) / r]")
                    working_steps.append(f"PV = {PMT} × [(1 - (1+{r:.8f})^(-{n_p:.4f})) / {r:.8f}]")
                    factor = (1 - (1 + r) ** (-n_p)) / r
                    working_steps.append(f"PV = {PMT} × {factor:.8f} = {currency_symbol}{pv:,.2f}")
                    if is_due:
                        pv = pv * (1 + r)
                        working_steps.append(f"Annuity Due: PV = PV × (1+r) = {currency_symbol}{pv:,.2f}")
                result_value = pv
                calculated_field = "Present Value (PV)"
                calculated_value_str = format_currency(pv, currency_symbol)

            elif "PMT" in calc_target:
                r = rate_per_period
                n_p = total_periods
                target_val = ann_value

                if target_val == 0:
                    st.error("❌ Please enter the PV or FV value to calculate PMT.")
                    st.stop()
                if n_p == 0:
                    st.error("❌ Time period must be > 0.")
                    st.stop()

                working_steps.append(f"Target Value = {currency_symbol}{target_val:,.2f}")
                if r == 0:
                    pmt = target_val / n_p
                    working_steps.append(f"r = 0, PMT = Value / n = {target_val} / {n_p:.4f} = {currency_symbol}{pmt:,.2f}")
                else:
                    fv_factor = ((1 + r) ** n_p - 1) / r
                    if is_due:
                        fv_factor *= (1 + r)
                    pmt = target_val / fv_factor
                    working_steps.append(f"PMT = Value / annuity_factor")
                    working_steps.append(f"Annuity Factor = {fv_factor:.8f}")
                    working_steps.append(f"PMT = {target_val} / {fv_factor:.8f} = {currency_symbol}{pmt:,.2f}")

                result_value = pmt
                calculated_field = "Payment (PMT)"
                calculated_value_str = format_currency(pmt, currency_symbol)

            elif "Rate" in calc_target:
                PMT = ann_pmt
                n_p = total_periods
                target_val = ann_value

                if PMT == 0 or n_p == 0 or target_val == 0:
                    st.error("❌ PMT, time period, and target value must all be > 0 to calculate rate.")
                    st.stop()

                r_guess = 0.01
                for _ in range(1000):
                    if is_due:
                        f_val = PMT * (((1 + r_guess) ** n_p - 1) / r_guess) * (1 + r_guess) - target_val
                    else:
                        f_val = PMT * (((1 + r_guess) ** n_p - 1) / r_guess) - target_val
                    dr = 0.0001
                    if is_due:
                        f_val2 = PMT * (((1 + r_guess + dr) ** n_p - 1) / (r_guess + dr)) * (1 + r_guess + dr) - target_val
                    else:
                        f_val2 = PMT * (((1 + r_guess + dr) ** n_p - 1) / (r_guess + dr)) - target_val
                    f_prime = (f_val2 - f_val) / dr
                    if abs(f_prime) < 1e-15:
                        break
                    r_new = r_guess - f_val / f_prime
                    if r_new <= 0:
                        r_new = r_guess / 2
                    if abs(r_new - r_guess) < 1e-12:
                        break
                    r_guess = r_new

                annual_rate_found = r_guess * m_ann * 100
                working_steps.append(f"Using Newton's method to solve for r...")
                working_steps.append(f"Rate per period = {r_guess:.8f}")
                working_steps.append(f"Annual Rate = {r_guess:.8f} × {m_ann} × 100 = {annual_rate_found:.4f}%")
                result_value = annual_rate_found
                calculated_field = "Annual Interest Rate"
                calculated_value_str = f"{annual_rate_found:.4f}%"

            elif "Periods" in calc_target:
                PMT = ann_pmt
                r = rate_per_period
                target_val = ann_value

                if PMT == 0 or r == 0 or target_val == 0:
                    st.error("❌ PMT, rate, and target value must all be > 0.")
                    st.stop()

                if is_due:
                    adj_target = target_val / (1 + r)
                else:
                    adj_target = target_val
                n_calc = math.log(adj_target * r / PMT + 1) / math.log(1 + r)
                years_calc = n_calc / m_ann
                working_steps.append(f"n = ln(FV×r/PMT + 1) / ln(1+r)")
                working_steps.append(f"n = ln({adj_target}×{r:.8f}/{PMT} + 1) / ln(1+{r:.8f})")
                working_steps.append(f"n = {n_calc:.4f} periods = {years_calc:.4f} years")
                result_value = years_calc
                calculated_field = "Number of Periods"
                calculated_value_str = f"{n_calc:.4f} periods ({years_calc:.4f} years)"

            st.markdown(f'<div class="result-box">✅ {calculated_field} = {calculated_value_str}</div>', unsafe_allow_html=True)

            st.markdown('<div class="section-header">📐 Step-by-Step Working</div>', unsafe_allow_html=True)
            working_html = "<br>".join(working_steps)
            st.markdown(f'<div class="working-box">{working_html}</div>', unsafe_allow_html=True)

            st.markdown("---")
            st.markdown('<div class="section-header">📋 Period-wise Schedule</div>', unsafe_allow_html=True)

            r_sched = rate_per_period if ann_rate > 0 else 0
            pmt_sched = ann_pmt if ann_pmt > 0 else (result_value if "PMT" in calculated_field else 0)
            n_sched = int(total_periods) if total_periods > 0 else (int(result_value * m_ann) if "Periods" in calculated_field else 0)

            if pmt_sched > 0 and n_sched > 0:
                schedule_data = []
                balance_fv = 0
                for period in range(1, min(n_sched + 1, 361)):
                    if is_due:
                        balance_fv += pmt_sched
                        interest = balance_fv * r_sched
                        balance_fv += interest
                    else:
                        interest = balance_fv * r_sched
                        balance_fv += interest + pmt_sched
                    schedule_data.append({
                        'Period': period,
                        'Payment': round(pmt_sched, 2),
                        'Interest': round(interest, 2),
                        'Balance (FV)': round(balance_fv, 2)
                    })
                schedule_df = pd.DataFrame(schedule_data)
                display_df = schedule_df.copy()
                for col in ['Payment', 'Interest', 'Balance (FV)']:
                    display_df[col] = display_df[col].apply(lambda x: format_currency(x, currency_symbol))
                if len(display_df) > 24:
                    st.info(f"Showing first 24 of {len(display_df)} periods.")
                    st.dataframe(display_df.head(24), use_container_width=True, hide_index=True)
                else:
                    st.dataframe(display_df, use_container_width=True, hide_index=True)

                st.markdown("---")
                st.markdown('<div class="section-header">📈 Visual Analysis</div>', unsafe_allow_html=True)
                fig = create_line_chart(schedule_df['Period'].tolist(), {'Balance (FV)': schedule_df['Balance (FV)'].tolist()}, 'Annuity Growth', 'Period', f'Balance ({currency_symbol})')
                st.plotly_chart(fig, use_container_width=True)
            else:
                schedule_df = None

            summary_dict = {
                'Calculation Type': f'Annuity ({due_label})',
                'Calculated Field': calculated_field,
                'Calculated Value': calculated_value_str,
                'Payment (PMT)': format_currency(ann_pmt, currency_symbol) if ann_pmt > 0 else (calculated_value_str if "PMT" in calculated_field else "N/A"),
                'Annual Rate': f'{ann_rate:.4f}%' if ann_rate > 0 else (calculated_value_str if "Rate" in calculated_field else "N/A"),
                'Time': ann_time_desc,
                'Payment Frequency': ann_frequency,
                'Annuity Type': due_label,
                'Calculation Date': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            render_download_section("Annuity Calculator", summary_dict, schedule_df, currency_symbol)
            add_to_history("Annuity Calculator", {'PMT': ann_pmt, 'Rate': ann_rate, 'Time': ann_time_desc, 'Type': due_label}, {'Result': calculated_value_str})
        except Exception as e:
            st.error(f"❌ Error: {e}")

# ═══════════════════════════════════════════════════════════════
#                        HISTORY
# ═══════════════════════════════════════════════════════════════
elif calculator_type == "📋 History":
    st.markdown("""
    <div class="hero-container">
        <h1>📋 Calculation History</h1>
        <p>View and Export Your Past Calculations</p>
    </div>
    """, unsafe_allow_html=True)

    if st.session_state.calculation_history:
        history_df = pd.DataFrame(st.session_state.calculation_history)
        st.markdown(f'<div class="section-header">📊 Total Records: {len(history_df)}</div>', unsafe_allow_html=True)
        st.dataframe(history_df, use_container_width=True, hide_index=True)
        st.markdown("---")
        st.markdown('<div class="section-header">📥 Export History</div>', unsafe_allow_html=True)
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            csv = history_df.to_csv(index=False)
            st.download_button("📄 CSV", data=csv, file_name="history.csv", mime="text/csv", use_container_width=True)
        with col2:
            output = io.BytesIO()
            history_df.to_excel(output, index=False, engine='openpyxl')
            st.download_button("📊 Excel", data=output.getvalue(), file_name="history.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", use_container_width=True)
        with col3:
            json_data = history_df.to_json(orient='records', indent=2)
            st.download_button("🔗 JSON", data=json_data, file_name="history.json", mime="application/json", use_container_width=True)
        with col4:
            if st.button("🗑 Clear All", use_container_width=True):
                st.session_state.calculation_history = []
                st.rerun()
    else:
        st.info("📝 No calculations yet. Use any calculator to build your history!")

# ═══════════════════════════════════════════════════════════════
#                        FORMULAS
# ═══════════════════════════════════════════════════════════════
elif calculator_type == "📖 Formulas":
    st.markdown("""
    <div class="hero-container">
        <h1>📖 Formula Reference</h1>
        <p>Complete Financial Mathematics Library</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="formula-box">
    <h3 style="color:#60a5fa; margin-top:0;">📝 Simple Interest</h3>
    <pre style="color:#94a3b8; font-size:0.95rem; line-height:2;">
I = (P × R × T) / 100
P = (I × 100) / (R × T)
R = (I × 100) / (P × T)
T = (I × 100) / (P × R)
    </pre>
    </div>

    <div class="formula-box">
    <h3 style="color:#60a5fa; margin-top:0;">📈 Compound Interest</h3>
    <pre style="color:#94a3b8; font-size:0.95rem; line-height:2;">
FV = PV × (1 + r/m)^(n×m)
PV = FV / (1 + r/m)^(n×m)
r  = m × [(FV/PV)^(1/(n×m)) - 1]
n  = ln(FV/PV) / [m × ln(1 + r/m)]
Effective Rate = (1 + r/m)^m - 1
    </pre>
    </div>

    <div class="formula-box">
    <h3 style="color:#60a5fa; margin-top:0;">🏧 EMI</h3>
    <pre style="color:#94a3b8; font-size:0.95rem; line-height:2;">
EMI = P × r × (1+r)^n / [(1+r)^n - 1]
Where: r = monthly rate, n = total months
    </pre>
    </div>

    <div class="formula-box">
    <h3 style="color:#60a5fa; margin-top:0;">💰 SIP Future Value</h3>
    <pre style="color:#94a3b8; font-size:0.95rem; line-height:2;">
FV = P × [(1+r)^n - 1] / r × (1+r)
    </pre>
    </div>

    <div class="formula-box">
    <h3 style="color:#60a5fa; margin-top:0;">📉 NPV & IRR</h3>
    <pre style="color:#94a3b8; font-size:0.95rem; line-height:2;">
NPV = -C₀ + Σ[CFₜ / (1+r)^t]
IRR = Rate where NPV = 0
    </pre>
    </div>

    <div class="formula-box">
    <h3 style="color:#60a5fa; margin-top:0;">📃 Bond Valuation</h3>
    <pre style="color:#94a3b8; font-size:0.95rem; line-height:2;">
Price = Σ[C/(1+y)^t] + F/(1+y)^n
    </pre>
    </div>

    <div class="formula-box">
    <h3 style="color:#60a5fa; margin-top:0;">🔄 Annuity — Ordinary</h3>
    <pre style="color:#94a3b8; font-size:0.95rem; line-height:2;">
FV = PMT × [((1+r)^n - 1) / r]
PV = PMT × [(1 - (1+r)^(-n)) / r]
    </pre>
    </div>

    <div class="formula-box">
    <h3 style="color:#60a5fa; margin-top:0;">🔄 Annuity — Due (Beginning of Period)</h3>
    <pre style="color:#94a3b8; font-size:0.95rem; line-height:2;">
FV = PMT × [((1+r)^n - 1) / r] × (1+r)
PV = PMT × [(1 - (1+r)^(-n)) / r] × (1+r)
    </pre>
    </div>
    """)

# ═══════════════════════════════════════════════════════════════
#                         FOOTER
# ═══════════════════════════════════════════════════════════════
st.markdown("""
<div class="footer">
    <strong>💎 FinCalc Pro</strong> | Professional Financial Analysis Suite<br>
    <small style="color: #64748b;">Smart Auto-Calculate • Export in CSV, Excel, PDF, JSON • Precision Financial Mathematics</small>
</div>
""", unsafe_allow_html=True)
