import streamlit as st
import pandas as pd
import numpy as np
import math
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go
import io
import json
from fpdf import FPDF

# ═══════════════════════════════════════════════════════════════
#                    PAGE CONFIGURATION
# ═══════════════════════════════════════════════════════════════

st.set_page_config(
    page_title="Financial Calculator Pro",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ═══════════════════════════════════════════════════════════════
#                    CUSTOM CSS
# ═══════════════════════════════════════════════════════════════

st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 30px;
        border-radius: 20px;
        text-align: center;
        color: white;
        margin-bottom: 30px;
    }
    .result-box {
        background: linear-gradient(135deg, #00b894 0%, #00cec9 100%);
        padding: 20px;
        border-radius: 15px;
        color: white;
        text-align: center;
        font-size: 1.5rem;
        font-weight: bold;
        margin: 20px 0;
    }
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        height: 3em;
        width: 100%;
        border-radius: 10px;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════
#                    HELPER FUNCTIONS
# ═══════════════════════════════════════════════════════════════

def format_currency(value, symbol="$"):
    if value is None or pd.isna(value): return "N/A"
    return f"{symbol}{value:,.2f}"

# ═══════════════════════════════════════════════════════════════
#                    PDF CLASS
# ═══════════════════════════════════════════════════════════════

class PDFReport(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 16)
        self.cell(0, 10, 'Financial Calculator Pro - Report', 0, 1, 'C')
        self.ln(10)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')

def generate_pdf_report(calc_type, inputs, results, df=None):
    pdf = PDFReport()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    
    # Title
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(200, 10, txt=f"Calculation: {calc_type}", ln=True, align='L')
    pdf.ln(5)
    
    # Inputs
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(200, 10, txt="Inputs:", ln=True)
    pdf.set_font("Arial", size=11)
    for k, v in inputs.items():
        pdf.cell(200, 8, txt=f"{k}: {v}", ln=True)
    pdf.ln(5)
    
    # Results
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(200, 10, txt="Results:", ln=True)
    pdf.set_font("Arial", size=11)
    for k, v in results.items():
        pdf.cell(200, 8, txt=f"{k}: {v}", ln=True)
        
    return pdf.output(dest='S').encode('latin-1')

def download_section(calc_type, inputs, results, df=None):
    st.markdown("---")
    st.subheader("📥 Downloads")
    c1, c2, c3 = st.columns(3)
    
    # CSV
    if df is not None:
        c1.download_button("📄 Download Schedule (CSV)", df.to_csv(index=False), f"{calc_type}_schedule.csv", "text/csv")
    
    # PDF (Generated only when needed logic applies, but Streamlit requires pre-computation)
    # We wrap it in try-except to prevent crashes
    try:
        pdf_data = generate_pdf_report(calc_type, inputs, results, df)
        c2.download_button("📕 Download Report (PDF)", pdf_data, f"{calc_type}_report.pdf", "application/pdf")
    except Exception as e:
        c2.error("PDF Error")

    # JSON
    json_str = json.dumps({**inputs, **results}, indent=2)
    c3.download_button("📋 Download Data (JSON)", json_str, f"{calc_type}.json", "application/json")

# ═══════════════════════════════════════════════════════════════
#                    SIDEBAR
# ═══════════════════════════════════════════════════════════════

with st.sidebar:
    st.title("💰 Finance Pro")
    currency = st.selectbox("Currency", ["$", "Rs", "₹", "€", "£", "AED"])
    choice = st.radio("Navigate", ["Simple Interest", "Compound Interest", "EMI Calculator", "SIP Calculator", "NPV Analysis"])

# ═══════════════════════════════════════════════════════════════
#                    1. SIMPLE INTEREST
# ═══════════════════════════════════════════════════════════════

if choice == "Simple Interest":
    st.markdown(f"<div class='main-header'><h1>📐 Simple Interest Calculator</h1></div>", unsafe_allow_html=True)
    
    c1, c2 = st.columns(2)
    P = c1.number_input("Principal (P)", value=10000.0)
    R = c1.number_input("Rate (R %)", value=10.0)
    T = c2.number_input("Time (Years)", value=5.0)
    
    if st.button("Calculate"):
        I = (P * R * T) / 100
        Total = P + I
        
        st.markdown(f"<div class='result-box'>Total Interest: {format_currency(I, currency)}<br>Total Amount: {format_currency(Total, currency)}</div>", unsafe_allow_html=True)
        
        # --- NEW: SCHEDULE TABLE ---
        st.subheader("📊 Yearly Schedule")
        schedule_data = []
        accumulated_interest = 0
        for year in range(1, int(T) + 1):
            yearly_int = (P * R) / 100
            accumulated_interest += yearly_int
            schedule_data.append({
                "Year": year,
                "Principal": format_currency(P, currency),
                "Interest Earned": format_currency(yearly_int, currency),
                "Total Interest": format_currency(accumulated_interest, currency),
                "Balance": format_currency(P + accumulated_interest, currency)
            })
        
        df = pd.DataFrame(schedule_data)
        st.dataframe(df, use_container_width=True)
        
        download_section("Simple Interest", {"P":P, "R":R, "T":T}, {"Interest":I, "Total":Total}, df)

# ═══════════════════════════════════════════════════════════════
#                    2. COMPOUND INTEREST
# ═══════════════════════════════════════════════════════════════

elif choice == "Compound Interest":
    st.markdown(f"<div class='main-header'><h1>📈 Compound Interest Calculator</h1></div>", unsafe_allow_html=True)
    
    c1, c2 = st.columns(2)
    P = c1.number_input("Principal (P)", value=10000.0)
    R = c1.number_input("Rate (R %)", value=10.0)
    T = c2.number_input("Time (Years)", value=5.0)
    freq_map = {"Annually": 1, "Semi-Annually": 2, "Quarterly": 4, "Monthly": 12}
    freq = c2.selectbox("Compounding", list(freq_map.keys()))
    
    if st.button("Calculate"):
        n = freq_map[freq]
        Amount = P * (1 + (R/100)/n)**(n*T)
        CI = Amount - P
        
        st.markdown(f"<div class='result-box'>Total Amount: {format_currency(Amount, currency)}<br>Compound Interest: {format_currency(CI, currency)}</div>", unsafe_allow_html=True)
        
        # --- NEW: SCHEDULE TABLE ---
        st.subheader("📊 Detailed Schedule")
        schedule_data = []
        current_amt = P
        for year in range(1, int(T) + 1):
            new_amt = P * (1 + (R/100)/n)**(n*year)
            interest_earned = new_amt - current_amt
            schedule_data.append({
                "Year": year,
                "Opening Balance": format_currency(current_amt, currency),
                "Interest Earned": format_currency(interest_earned, currency),
                "Closing Balance": format_currency(new_amt, currency)
            })
            current_amt = new_amt
            
        df = pd.DataFrame(schedule_data)
        st.dataframe(df, use_container_width=True)
        
        # Charts
        chart_data = pd.DataFrame({"Category": ["Principal", "Interest"], "Value": [P, CI]})
        st.plotly_chart(px.pie(chart_data, values="Value", names="Category", title="Breakdown"))
        
        download_section("Compound Interest", {"P":P, "R":R, "T":T}, {"Amount":Amount}, df)

# ═══════════════════════════════════════════════════════════════
#                    3. EMI CALCULATOR (Already had schedule, kept it)
# ═══════════════════════════════════════════════════════════════

elif choice == "EMI Calculator":
    st.markdown(f"<div class='main-header'><h1>🏦 EMI Calculator</h1></div>", unsafe_allow_html=True)
    
    c1, c2, c3 = st.columns(3)
    loan = c1.number_input("Loan Amount", value=100000.0)
    rate = c2.number_input("Interest Rate (%)", value=10.0)
    tenure = c3.number_input("Tenure (Years)", value=5.0)
    
    if st.button("Calculate EMI"):
        r = rate / (12 * 100)
        n = tenure * 12
        emi = (loan * r * (1 + r)**n) / ((1 + r)**n - 1)
        total_pay = emi * n
        total_int = total_pay - loan
        
        st.markdown(f"<div class='result-box'>Monthly EMI: {format_currency(emi, currency)}<br>Total Interest: {format_currency(total_int, currency)}</div>", unsafe_allow_html=True)
        
        # Schedule
        st.subheader("📊 Amortization Schedule")
        schedule = []
        balance = loan
        for m in range(1, int(n)+1):
            inte = balance * r
            princ = emi - inte
            balance -= princ
            schedule.append({
                "Month": m,
                "Principal": format_currency(princ, currency),
                "Interest": format_currency(inte, currency),
                "Balance": format_currency(max(0, balance), currency)
            })
            
        df = pd.DataFrame(schedule)
        with st.expander("View Full Schedule", expanded=True):
            st.dataframe(df, use_container_width=True)
            
        download_section("EMI", {"Loan":loan, "Rate":rate}, {"EMI":emi}, df)

# ═══════════════════════════════════════════════════════════════
#                    4. SIP CALCULATOR
# ═══════════════════════════════════════════════════════════════

elif choice == "SIP Calculator":
    st.markdown(f"<div class='main-header'><h1>💎 SIP Calculator</h1></div>", unsafe_allow_html=True)
    
    c1, c2 = st.columns(2)
    monthly = c1.number_input("Monthly Investment", value=5000.0)
    rate = c1.number_input("Expected Return (%)", value=12.0)
    years = c2.number_input("Time Period (Years)", value=10.0)
    
    if st.button("Calculate"):
        i = rate / (12 * 100)
        n = years * 12
        FV = monthly * (((1 + i)**n - 1) / i) * (1 + i)
        invested = monthly * n
        gain = FV - invested
        
        st.markdown(f"<div class='result-box'>Future Value: {format_currency(FV, currency)}<br>Wealth Gained: {format_currency(gain, currency)}</div>", unsafe_allow_html=True)
        
        # --- NEW: SCHEDULE TABLE ---
        st.subheader("📊 Investment Schedule")
        schedule = []
        curr_val = 0
        total_inv = 0
        for y in range(1, int(years)+1):
            # Simplified yearly view
            for m in range(12):
                curr_val = (curr_val + monthly) * (1 + i)
                total_inv += monthly
            
            schedule.append({
                "Year": y,
                "Total Invested": format_currency(total_inv, currency),
                "Portfolio Value": format_currency(curr_val, currency),
                "Profit": format_currency(curr_val - total_inv, currency)
            })
            
        df = pd.DataFrame(schedule)
        st.dataframe(df, use_container_width=True)
        
        download_section("SIP", {"Inv":monthly, "Rate":rate}, {"FV":FV}, df)

# ═══════════════════════════════════════════════════════════════
#                    5. NPV ANALYSIS
# ═══════════════════════════════════════════════════════════════

elif choice == "NPV Analysis":
    st.markdown(f"<div class='main-header'><h1>💹 NPV & Cash Flow Analysis</h1></div>", unsafe_allow_html=True)
    
    initial = st.number_input("Initial Investment", value=100000.0)
    rate = st.number_input("Discount Rate (%)", value=10.0)
    years = st.number_input("Number of Years", value=5, step=1)
    
    st.subheader("Cash Flows")
    cols = st.columns(min(int(years), 5))
    cash_flows = []
    for i in range(int(years)):
        with cols[i % 5]:
            cf = st.number_input(f"Year {i+1}", value=30000.0, key=f"cf{i}")
            cash_flows.append(cf)
            
    if st.button("Calculate NPV"):
        npv_val = -initial
        schedule = []
        
        # Year 0
        schedule.append({"Year": 0, "Cash Flow": format_currency(-initial, currency), "PV Factor": "1.000", "Present Value": format_currency(-initial, currency)})
        
        for t, cf in enumerate(cash_flows, 1):
            pv = cf / (1 + rate/100)**t
            npv_val += pv
            schedule.append({
                "Year": t,
                "Cash Flow": format_currency(cf, currency),
                "PV Factor": f"{1/(1+rate/100)**t:.4f}",
                "Present Value": format_currency(pv, currency)
            })
            
        st.markdown(f"<div class='result-box'>NPV: {format_currency(npv_val, currency)}</div>", unsafe_allow_html=True)
        
        # --- NEW: SCHEDULE TABLE ---
        st.subheader("📊 Cash Flow Schedule")
        df = pd.DataFrame(schedule)
        st.dataframe(df, use_container_width=True)
        
        download_section("NPV", {"Initial":initial}, {"NPV":npv_val}, df)
