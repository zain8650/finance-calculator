import streamlit as st
import pandas as pd
import numpy as np
import math
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go
import json
import io
import base64

# For PDF Generation
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
        box-shadow: 0 10px 40px rgba(102, 126, 234, 0.4);
    }
    
    .main-header h1 { margin: 0; font-size: 2.5rem; }
    .main-header p { margin: 10px 0 0 0; opacity: 0.9; }
    
    .result-box {
        background: linear-gradient(135deg, #00b894 0%, #00cec9 100%);
        padding: 30px;
        border-radius: 20px;
        color: white;
        text-align: center;
        font-size: 1.8rem;
        font-weight: bold;
        margin: 25px 0;
        box-shadow: 0 10px 40px rgba(0, 184, 148, 0.4);
    }
    
    .result-box-error {
        background: linear-gradient(135deg, #e74c3c 0%, #c0392b 100%);
        padding: 30px;
        border-radius: 20px;
        color: white;
        text-align: center;
        font-size: 1.5rem;
        margin: 25px 0;
    }
    
    .calc-card {
        background: white;
        padding: 25px;
        border-radius: 15px;
        border: 1px solid #e0e0e0;
        margin: 15px 0;
        box-shadow: 0 5px 20px rgba(0,0,0,0.08);
    }
    
    .formula-box {
        background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
        padding: 20px;
        border-radius: 15px;
        font-family: 'Courier New', monospace;
        border-left: 5px solid #667eea;
        margin: 20px 0;
        font-size: 1.1rem;
    }
    
    .upload-section {
        background: linear-gradient(135deg, #e8f5e9 0%, #c8e6c9 100%);
        padding: 30px;
        border-radius: 20px;
        border: 3px dashed #4CAF50;
        text-align: center;
        margin: 20px 0;
    }
    
    .download-section {
        background: #f8f9fa;
        padding: 20px;
        border-radius: 15px;
        border: 2px dashed #667eea;
        margin: 20px 0;
    }
    
    .filter-section {
        background: linear-gradient(135deg, #fff3e0 0%, #ffe0b2 100%);
        padding: 15px;
        border-radius: 10px;
        margin: 15px 0;
    }
    
    .template-card {
        background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%);
        padding: 20px;
        border-radius: 15px;
        margin: 10px 0;
        border-left: 5px solid #2196F3;
    }
    
    .success-banner {
        background: linear-gradient(135deg, #4CAF50 0%, #8BC34A 100%);
        padding: 15px;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin: 15px 0;
    }
</style>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════
#                    SESSION STATE
# ═══════════════════════════════════════════════════════════════

if 'calculation_history' not in st.session_state:
    st.session_state.calculation_history = []

if 'show_downloads' not in st.session_state:
    st.session_state.show_downloads = False

if 'bulk_results' not in st.session_state:
    st.session_state.bulk_results = None

# ═══════════════════════════════════════════════════════════════
#                    HELPER FUNCTIONS
# ═══════════════════════════════════════════════════════════════

def format_currency(value, symbol="$"):
    if value is None or pd.isna(value):
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
        "Daily (365/year)": 365
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
#                    PDF GENERATION CLASS
# ═══════════════════════════════════════════════════════════════

class PDFReport(FPDF):
    def __init__(self):
        super().__init__()
        self.set_auto_page_break(auto=True, margin=15)
    
    def header(self):
        self.set_font('Arial', 'B', 20)
        self.set_text_color(102, 126, 234)
        self.cell(0, 15, 'Financial Calculator Pro', 0, 1, 'C')
        self.set_font('Arial', 'I', 10)
        self.set_text_color(128, 128, 128)
        self.cell(0, 5, f'Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}', 0, 1, 'C')
        self.ln(10)
    
    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.set_text_color(128, 128, 128)
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')
    
    def add_title(self, title):
        self.set_font('Arial', 'B', 16)
        self.set_text_color(102, 126, 234)
        self.cell(0, 10, title, 0, 1, 'L')
        self.ln(5)
    
    def add_key_value(self, key, value):
        self.set_font('Arial', 'B', 11)
        self.set_text_color(60, 60, 60)
        self.cell(70, 8, str(key) + ":", 0, 0, 'L')
        self.set_font('Arial', '', 11)
        self.cell(0, 8, str(value), 0, 1, 'L')
    
    def add_table(self, df, max_rows=50):
        self.set_font('Arial', 'B', 9)
        self.set_fill_color(102, 126, 234)
        self.set_text_color(255, 255, 255)
        
        cols = df.columns.tolist()
        col_width = 190 / len(cols)
        
        # Header
        for col in cols:
            self.cell(col_width, 8, str(col)[:15], 1, 0, 'C', True)
        self.ln()
        
        # Data
        self.set_font('Arial', '', 8)
        self.set_text_color(60, 60, 60)
        
        for idx, row in df.head(max_rows).iterrows():
            for col in cols:
                val = str(row[col])[:15]
                self.cell(col_width, 6, val, 1, 0, 'C')
            self.ln()

def generate_pdf(title, data_dict, df=None):
    pdf = PDFReport()
    pdf.add_page()
    pdf.add_title(title)
    
    for key, value in data_dict.items():
        pdf.add_key_value(key, value)
    
    if df is not None:
        pdf.ln(10)
        pdf.add_title("Detailed Data")
        pdf.add_table(df)
    
    return pdf.output(dest='S').encode('latin-1')

def generate_excel(data_dict, df=None, sheet_name="Data"):
    output = io.BytesIO()
    
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        # Summary Sheet
        summary_df = pd.DataFrame(list(data_dict.items()), columns=['Parameter', 'Value'])
        summary_df.to_excel(writer, sheet_name='Summary', index=False)
        
        # Data Sheet
        if df is not None:
            df.to_excel(writer, sheet_name=sheet_name, index=False)
    
    return output.getvalue()

# ═══════════════════════════════════════════════════════════════
#                    DOWNLOAD SECTION COMPONENT
# ═══════════════════════════════════════════════════════════════

def show_download_section(calc_type, summary_dict, schedule_df=None, currency_symbol="$"):
    st.markdown("---")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("📥 Click to Download Results", use_container_width=True, type="primary", key=f"dl_{calc_type}"):
            st.session_state.show_downloads = True
    
    if st.session_state.show_downloads:
        st.markdown("""
        <div class="download-section">
            <h4 style="text-align: center; color: #667eea;">📥 Select Download Format</h4>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            if schedule_df is not None:
                csv_data = schedule_df.to_csv(index=False)
            else:
                csv_data = pd.DataFrame(list(summary_dict.items()), columns=['Parameter', 'Value']).to_csv(index=False)
            
            st.download_button(
                "📄 Download CSV",
                data=csv_data,
                file_name=f"{calc_type.lower().replace(' ', '_')}.csv",
                mime="text/csv",
                use_container_width=True
            )
        
        with col2:
            excel_data = generate_excel(summary_dict, schedule_df)
            st.download_button(
                "📊 Download Excel",
                data=excel_data,
                file_name=f"{calc_type.lower().replace(' ', '_')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )
        
        with col3:
            try:
                pdf_data = generate_pdf(calc_type, summary_dict, schedule_df)
                st.download_button(
                    "📕 Download PDF",
                    data=pdf_data,
                    file_name=f"{calc_type.lower().replace(' ', '_')}.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )
            except Exception as e:
                st.button("📕 PDF (Error)", disabled=True, use_container_width=True)
        
        with col4:
            json_data = json.dumps({
                'type': calc_type,
                'timestamp': datetime.now().isoformat(),
                'summary': summary_dict
            }, indent=2)
            st.download_button(
                "📋 Download JSON",
                data=json_data,
                file_name=f"{calc_type.lower().replace(' ', '_')}.json",
                mime="application/json",
                use_container_width=True
            )
        
        if st.button("❌ Close Download Options", use_container_width=True):
            st.session_state.show_downloads = False
            st.rerun()

# ═══════════════════════════════════════════════════════════════
#                    CHART FUNCTIONS
# ═══════════════════════════════════════════════════════════════

def create_pie_chart(labels, values, title, colors=None):
    if colors is None:
        colors = ['#667eea', '#00b894', '#e74c3c', '#f39c12']
    
    fig = go.Figure(data=[go.Pie(
        labels=labels,
        values=values,
        hole=0.4,
        marker_colors=colors[:len(labels)],
        textinfo='label+percent'
    )])
    fig.update_layout(title=dict(text=title, font=dict(size=16)), height=400)
    return fig

def create_line_chart(x_data, y_data_dict, title, x_title, y_title):
    fig = go.Figure()
    colors = ['#667eea', '#00b894', '#e74c3c', '#f39c12']
    
    for i, (name, y_data) in enumerate(y_data_dict.items()):
        fig.add_trace(go.Scatter(
            x=x_data, y=y_data, mode='lines+markers', name=name,
            line=dict(color=colors[i % len(colors)], width=3)
        ))
    
    fig.update_layout(
        title=dict(text=title, font=dict(size=16)),
        xaxis_title=x_title, yaxis_title=y_title,
        hovermode='x unified', height=400
    )
    return fig

def create_bar_chart(categories, values_dict, title, y_title):
    fig = go.Figure()
    colors = ['#667eea', '#00b894', '#e74c3c']
    
    for i, (name, values) in enumerate(values_dict.items()):
        fig.add_trace(go.Bar(name=name, x=categories, y=values, marker_color=colors[i % len(colors)]))
    
    fig.update_layout(
        title=dict(text=title, font=dict(size=16)),
        yaxis_title=y_title, barmode='group', height=400
    )
    return fig

def create_gauge_chart(value, max_value, title):
    fig = go.Figure(go.Indicator(
        mode="gauge+number", value=value,
        title={'text': title, 'font': {'size': 16}},
        gauge={
            'axis': {'range': [0, max_value]},
            'bar': {'color': "#667eea"},
            'steps': [
                {'range': [0, max_value*0.33], 'color': '#e8f5e9'},
                {'range': [max_value*0.33, max_value*0.66], 'color': '#fff3e0'},
                {'range': [max_value*0.66, max_value], 'color': '#ffebee'}
            ]
        }
    ))
    fig.update_layout(height=300)
    return fig

def create_area_chart(x_data, y_data_dict, title, x_title, y_title):
    fig = go.Figure()
    colors = ['rgba(102, 126, 234, 0.7)', 'rgba(0, 184, 148, 0.7)', 'rgba(231, 76, 60, 0.7)']
    
    for i, (name, y_data) in enumerate(y_data_dict.items()):
        fig.add_trace(go.Scatter(
            x=x_data, y=y_data, mode='lines', name=name,
            stackgroup='one', fillcolor=colors[i % len(colors)]
        ))
    
    fig.update_layout(
        title=dict(text=title, font=dict(size=16)),
        xaxis_title=x_title, yaxis_title=y_title, height=400
    )
    return fig

# ═══════════════════════════════════════════════════════════════
#                    BULK CALCULATION FUNCTIONS
# ═══════════════════════════════════════════════════════════════

def calculate_simple_interest_bulk(df):
    """Calculate SI for multiple rows"""
    results = []
    for _, row in df.iterrows():
        try:
            P = float(row.get('Principal', 0))
            R = float(row.get('Rate', 0))
            T = float(row.get('Time', 0))
            
            I = (P * R * T) / 100
            total = P + I
            
            results.append({
                'Principal': P,
                'Rate (%)': R,
                'Time (Years)': T,
                'Interest': round(I, 2),
                'Total Amount': round(total, 2),
                'Status': '✅ Success'
            })
        except Exception as e:
            results.append({
                'Principal': row.get('Principal', 'N/A'),
                'Rate (%)': row.get('Rate', 'N/A'),
                'Time (Years)': row.get('Time', 'N/A'),
                'Interest': 'Error',
                'Total Amount': 'Error',
                'Status': f'❌ {str(e)}'
            })
    
    return pd.DataFrame(results)

def calculate_compound_interest_bulk(df):
    """Calculate CI for multiple rows"""
    results = []
    for _, row in df.iterrows():
        try:
            PV = float(row.get('Present_Value', row.get('Principal', 0)))
            R = float(row.get('Rate', 0))
            N = float(row.get('Years', row.get('Time', 0)))
            M = int(row.get('Frequency', 12))
            
            r_periodic = (R / 100) / M
            total_periods = N * M
            FV = PV * ((1 + r_periodic) ** total_periods)
            interest = FV - PV
            
            results.append({
                'Present Value': PV,
                'Rate (%)': R,
                'Years': N,
                'Frequency': M,
                'Future Value': round(FV, 2),
                'Interest Earned': round(interest, 2),
                'Status': '✅ Success'
            })
        except Exception as e:
            results.append({
                'Present Value': row.get('Present_Value', 'N/A'),
                'Rate (%)': row.get('Rate', 'N/A'),
                'Years': row.get('Years', 'N/A'),
                'Frequency': row.get('Frequency', 'N/A'),
                'Future Value': 'Error',
                'Interest Earned': 'Error',
                'Status': f'❌ {str(e)}'
            })
    
    return pd.DataFrame(results)

def calculate_emi_bulk(df):
    """Calculate EMI for multiple rows"""
    results = []
    for _, row in df.iterrows():
        try:
            P = float(row.get('Loan_Amount', row.get('Principal', 0)))
            R = float(row.get('Annual_Rate', row.get('Rate', 0)))
            N = float(row.get('Years', row.get('Tenure', 0)))
            
            monthly_rate = R / 12 / 100
            total_months = int(N * 12)
            
            if monthly_rate > 0:
                EMI = P * monthly_rate * (1 + monthly_rate)**total_months / ((1 + monthly_rate)**total_months - 1)
            else:
                EMI = P / total_months
            
            total_payment = EMI * total_months
            total_interest = total_payment - P
            
            results.append({
                'Loan Amount': P,
                'Annual Rate (%)': R,
                'Tenure (Years)': N,
                'Monthly EMI': round(EMI, 2),
                'Total Payment': round(total_payment, 2),
                'Total Interest': round(total_interest, 2),
                'Status': '✅ Success'
            })
        except Exception as e:
            results.append({
                'Loan Amount': row.get('Loan_Amount', 'N/A'),
                'Annual Rate (%)': row.get('Annual_Rate', 'N/A'),
                'Tenure (Years)': row.get('Years', 'N/A'),
                'Monthly EMI': 'Error',
                'Total Payment': 'Error',
                'Total Interest': 'Error',
                'Status': f'❌ {str(e)}'
            })
    
    return pd.DataFrame(results)

def calculate_sip_bulk(df):
    """Calculate SIP for multiple rows"""
    results = []
    for _, row in df.iterrows():
        try:
            monthly_sip = float(row.get('Monthly_SIP', row.get('SIP', 0)))
            expected_return = float(row.get('Expected_Return', row.get('Rate', 12)))
            years = float(row.get('Years', row.get('Period', 0)))
            step_up = float(row.get('Step_Up', 0))
            
            monthly_rate = expected_return / 12 / 100
            current_sip = monthly_sip
            total_invested = 0
            current_value = 0
            
            for year in range(int(years)):
                for month in range(12):
                    current_value = current_value * (1 + monthly_rate) + current_sip
                    total_invested += current_sip
                current_sip = current_sip * (1 + step_up / 100)
            
            wealth_gained = current_value - total_invested
            
            results.append({
                'Monthly SIP': monthly_sip,
                'Expected Return (%)': expected_return,
                'Years': years,
                'Step Up (%)': step_up,
                'Total Invested': round(total_invested, 2),
                'Future Value': round(current_value, 2),
                'Wealth Gained': round(wealth_gained, 2),
                'Status': '✅ Success'
            })
        except Exception as e:
            results.append({
                'Monthly SIP': row.get('Monthly_SIP', 'N/A'),
                'Expected Return (%)': row.get('Expected_Return', 'N/A'),
                'Years': row.get('Years', 'N/A'),
                'Step Up (%)': row.get('Step_Up', 'N/A'),
                'Total Invested': 'Error',
                'Future Value': 'Error',
                'Wealth Gained': 'Error',
                'Status': f'❌ {str(e)}'
            })
    
    return pd.DataFrame(results)

# ═══════════════════════════════════════════════════════════════
#                    SIDEBAR
# ═══════════════════════════════════════════════════════════════

with st.sidebar:
    st.markdown("""
    <div style="text-align: center; padding: 20px 0;">
        <h1 style="color: #667eea;">💰</h1>
        <h3>Financial Calculator Pro</h3>
        <p style="color: #888; font-size: 0.9rem;">v3.0 - Full Features</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    currency_symbol = st.selectbox("💵 Currency", ["$", "₹", "€", "£", "Rs", "PKR", "AED"])
    
    st.markdown("---")
    
    calculator_type = st.radio(
        "📊 Select Option",
        [
            "🏠 Home",
            "📐 Simple Interest",
            "📈 Compound Interest",
            "🏦 EMI Calculator",
            "💎 SIP Calculator",
            "💹 NPV Calculator",
            "📜 Bond Valuation",
            "📤 Import & Bulk Calc",
            "📋 History & Export",
            "📖 Formulas"
        ]
    )
    
    st.markdown("---")
    
    # Session Stats
    st.markdown("### 📊 Session Stats")
    col1, col2 = st.columns(2)
    col1.metric("Calculations", len(st.session_state.calculation_history))
    col2.metric("Calculators", "7")
    
    st.markdown("---")
    st.info("💡 Leave ONE field as 0 to calculate it")

# ═══════════════════════════════════════════════════════════════
#                    HOME PAGE
# ═══════════════════════════════════════════════════════════════

if calculator_type == "🏠 Home":
    st.markdown("""
    <div class="main-header">
        <h1>💰 Financial Calculator Pro</h1>
        <p>Complete Financial Calculations with Import, Export & Charts</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Features Overview
    st.markdown("### ✨ Key Features")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        <div class="calc-card">
            <h4>🧮 7 Calculators</h4>
            <p>SI, CI, EMI, SIP, NPV, Bond & more</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="calc-card">
            <h4>📤 Import Data</h4>
            <p>CSV & Excel upload for bulk calculations</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="calc-card">
            <h4>📥 Export Results</h4>
            <p>Download CSV, Excel, PDF, JSON</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown("""
        <div class="calc-card">
            <h4>📊 Charts</h4>
            <p>Interactive Pie, Line, Bar, Gauge</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Quick Start
    st.markdown("### 🚀 Quick Start")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        **📊 Single Calculation:**
        1. Select calculator from sidebar
        2. Enter known values
        3. Leave ONE field as 0
        4. Click Calculate
        5. Download results
        """)
    
    with col2:
        st.markdown("""
        **📤 Bulk Calculation:**
        1. Go to "Import & Bulk Calc"
        2. Download template
        3. Fill your data
        4. Upload CSV/Excel
        5. Get all results at once!
        """)
    
    st.success("👈 Select an option from sidebar to get started!")

# ═══════════════════════════════════════════════════════════════
#                    IMPORT & BULK CALCULATIONS
# ═══════════════════════════════════════════════════════════════

elif calculator_type == "📤 Import & Bulk Calc":
    st.markdown("""
    <div class="main-header">
        <h1>📤 Import & Bulk Calculations</h1>
        <p>Upload CSV or Excel file for multiple calculations at once</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Step 1: Select Calculation Type
    st.markdown("### Step 1: Select Calculation Type")
    
    calc_type = st.selectbox(
        "Choose calculation type:",
        ["Simple Interest", "Compound Interest", "EMI Calculator", "SIP Calculator"],
        key="bulk_calc_type"
    )
    
    # Step 2: Download Template
    st.markdown("### Step 2: Download Template")
    
    st.markdown("""
    <div class="template-card">
        <h4>📋 Template Required Columns</h4>
    </div>
    """, unsafe_allow_html=True)
    
    # Create templates based on calculation type
    if calc_type == "Simple Interest":
        template_df = pd.DataFrame({
            'Principal': [10000, 25000, 50000, 100000],
            'Rate': [5.0, 7.5, 10.0, 12.0],
            'Time': [1, 2, 3, 5]
        })
        st.info("**Required columns:** Principal, Rate, Time")
        
    elif calc_type == "Compound Interest":
        template_df = pd.DataFrame({
            'Present_Value': [10000, 25000, 50000, 100000],
            'Rate': [8.0, 10.0, 12.0, 15.0],
            'Years': [5, 10, 15, 20],
            'Frequency': [12, 4, 2, 1]
        })
        st.info("**Required columns:** Present_Value, Rate, Years, Frequency (1=Annual, 2=Semi, 4=Quarterly, 12=Monthly)")
        
    elif calc_type == "EMI Calculator":
        template_df = pd.DataFrame({
            'Loan_Amount': [100000, 500000, 1000000, 2500000],
            'Annual_Rate': [8.5, 9.0, 10.5, 12.0],
            'Years': [5, 10, 15, 20]
        })
        st.info("**Required columns:** Loan_Amount, Annual_Rate, Years")
        
    else:  # SIP Calculator
        template_df = pd.DataFrame({
            'Monthly_SIP': [5000, 10000, 15000, 25000],
            'Expected_Return': [12.0, 12.0, 15.0, 12.0],
            'Years': [10, 15, 20, 25],
            'Step_Up': [0, 10, 10, 5]
        })
        st.info("**Required columns:** Monthly_SIP, Expected_Return, Years, Step_Up")
    
    # Show template preview
    st.markdown("**Template Preview:**")
    st.dataframe(template_df, use_container_width=True, hide_index=True)
    
    # Download template buttons
    col1, col2 = st.columns(2)
    
    with col1:
        csv_template = template_df.to_csv(index=False)
        st.download_button(
            "📄 Download CSV Template",
            data=csv_template,
            file_name=f"{calc_type.lower().replace(' ', '_')}_template.csv",
            mime="text/csv",
            use_container_width=True
        )
    
    with col2:
        excel_output = io.BytesIO()
        template_df.to_excel(excel_output, index=False, engine='openpyxl')
        st.download_button(
            "📊 Download Excel Template",
            data=excel_output.getvalue(),
            file_name=f"{calc_type.lower().replace(' ', '_')}_template.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )
    
    st.markdown("---")
    
    # Step 3: Upload File
    st.markdown("### Step 3: Upload Your Data")
    
    st.markdown("""
    <div class="upload-section">
        <h4>📁 Drag and drop or click to upload</h4>
        <p>Supported formats: CSV, XLS, XLSX</p>
    </div>
    """, unsafe_allow_html=True)
    
    uploaded_file = st.file_uploader(
        "Upload your file",
        type=['csv', 'xls', 'xlsx'],
        key="bulk_upload",
        label_visibility="collapsed"
    )
    
    if uploaded_file is not None:
        try:
            # Read file
            if uploaded_file.name.endswith('.csv'):
                df = pd.read_csv(uploaded_file)
            else:
                df = pd.read_excel(uploaded_file)
            
            st.markdown(f"""
            <div class="success-banner">
                ✅ Successfully loaded {len(df)} rows from {uploaded_file.name}
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("**Uploaded Data Preview:**")
            st.dataframe(df.head(10), use_container_width=True, hide_index=True)
            
            if len(df) > 10:
                st.info(f"Showing first 10 of {len(df)} rows")
            
            # Step 4: Calculate
            st.markdown("---")
            st.markdown("### Step 4: Run Calculations")
            
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                if st.button("🔄 Calculate All Rows", use_container_width=True, type="primary"):
                    with st.spinner(f"Processing {len(df)} calculations..."):
                        # Run calculations based on type
                        if calc_type == "Simple Interest":
                            results_df = calculate_simple_interest_bulk(df)
                        elif calc_type == "Compound Interest":
                            results_df = calculate_compound_interest_bulk(df)
                        elif calc_type == "EMI Calculator":
                            results_df = calculate_emi_bulk(df)
                        else:
                            results_df = calculate_sip_bulk(df)
                        
                        st.session_state.bulk_results = results_df
                    
                    st.success("✅ Calculations completed!")
            
            # Show Results
            if st.session_state.bulk_results is not None:
                st.markdown("---")
                st.markdown("### 📊 Calculation Results")
                
                results_df = st.session_state.bulk_results
                
                # Stats
                success_count = len(results_df[results_df['Status'].str.contains('Success', na=False)])
                error_count = len(results_df) - success_count
                
                col1, col2, col3 = st.columns(3)
                col1.metric("Total Rows", len(results_df))
                col2.metric("Successful", success_count, delta=None)
                col3.metric("Errors", error_count, delta=None, delta_color="inverse")
                
                # Display results
                st.dataframe(results_df, use_container_width=True, hide_index=True)
                
                # Download Results
                st.markdown("---")
                st.markdown("### 📥 Download Results")
                
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    csv_results = results_df.to_csv(index=False)
                    st.download_button(
                        "📄 Download CSV",
                        data=csv_results,
                        file_name=f"{calc_type.lower().replace(' ', '_')}_results.csv",
                        mime="text/csv",
                        use_container_width=True
                    )
                
                with col2:
                    excel_output = io.BytesIO()
                    results_df.to_excel(excel_output, index=False, engine='openpyxl')
                    st.download_button(
                        "📊 Download Excel",
                        data=excel_output.getvalue(),
                        file_name=f"{calc_type.lower().replace(' ', '_')}_results.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        use_container_width=True
                    )
                
                with col3:
                    try:
                        summary_dict = {
                            'Calculation Type': calc_type,
                            'Total Rows': len(results_df),
                            'Successful': success_count,
                            'Errors': error_count,
                            'Generated': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        }
                        pdf_data = generate_pdf(f"Bulk {calc_type} Results", summary_dict, results_df)
                        st.download_button(
                            "📕 Download PDF",
                            data=pdf_data,
                            file_name=f"{calc_type.lower().replace(' ', '_')}_results.pdf",
                            mime="application/pdf",
                            use_container_width=True
                        )
                    except:
                        st.button("📕 PDF (Error)", disabled=True, use_container_width=True)
                
                with col4:
                    json_results = results_df.to_json(orient='records', indent=2)
                    st.download_button(
                        "📋 Download JSON",
                        data=json_results,
                        file_name=f"{calc_type.lower().replace(' ', '_')}_results.json",
                        mime="application/json",
                        use_container_width=True
                    )
                
                # Add to history
                add_to_history(
                    f"Bulk {calc_type}",
                    {'Rows': len(df), 'File': uploaded_file.name},
                    {'Success': success_count, 'Errors': error_count}
                )
                
        except Exception as e:
            st.error(f"❌ Error reading file: {e}")
            st.info("Please make sure your file has the correct columns as shown in the template.")

# ═══════════════════════════════════════════════════════════════
#                    HISTORY & EXPORT PAGE
# ═══════════════════════════════════════════════════════════════

elif calculator_type == "📋 History & Export":
    st.markdown("""
    <div class="main-header">
        <h1>📋 Calculation History</h1>
        <p>View, Filter & Export Your Calculation History</p>
    </div>
    """, unsafe_allow_html=True)
    
    if st.session_state.calculation_history:
        history_df = pd.DataFrame(st.session_state.calculation_history)
        
        # Filter Section
        st.markdown("""
        <div class="filter-section">
            <h4>🔍 Filter History</h4>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            # Filter by calculation type
            calc_types = ['All Types'] + list(history_df['type'].unique())
            filter_type = st.selectbox("📊 Calculation Type", calc_types)
        
        with col2:
            # Filter by date
            date_options = ['All Time', 'Today', 'Last 7 Days', 'Last 30 Days']
            filter_date = st.selectbox("📅 Date Range", date_options)
        
        with col3:
            # Search
            search_term = st.text_input("🔍 Search", placeholder="Search in inputs/outputs...")
        
        # Apply filters
        filtered_df = history_df.copy()
        
        if filter_type != 'All Types':
            filtered_df = filtered_df[filtered_df['type'] == filter_type]
        
        if filter_date != 'All Time':
            today = datetime.now().date()
            if filter_date == 'Today':
                filtered_df = filtered_df[pd.to_datetime(filtered_df['timestamp']).dt.date == today]
            elif filter_date == 'Last 7 Days':
                week_ago = today - pd.Timedelta(days=7)
                filtered_df = filtered_df[pd.to_datetime(filtered_df['timestamp']).dt.date >= week_ago]
            elif filter_date == 'Last 30 Days':
                month_ago = today - pd.Timedelta(days=30)
                filtered_df = filtered_df[pd.to_datetime(filtered_df['timestamp']).dt.date >= month_ago]
        
        if search_term:
            mask = (
                filtered_df['inputs'].str.contains(search_term, case=False, na=False) |
                filtered_df['outputs'].str.contains(search_term, case=False, na=False)
            )
            filtered_df = filtered_df[mask]
        
        # Display stats
        st.markdown("---")
        
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Total Records", len(history_df))
        col2.metric("Filtered Records", len(filtered_df))
        col3.metric("Unique Types", history_df['type'].nunique())
        col4.metric("Today's Calcs", len(history_df[pd.to_datetime(history_df['timestamp']).dt.date == datetime.now().date()]))
        
        # Display filtered history
        st.markdown("---")
        st.markdown("### 📋 History Records")
        
        st.dataframe(filtered_df, use_container_width=True, hide_index=True)
        
        # Export History Section
        st.markdown("---")
        st.markdown("### 📥 Export History")
        
        st.markdown("""
        <div class="download-section">
            <h4 style="text-align: center; color: #667eea;">Download Your Calculation History</h4>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            # CSV Export
            csv_history = filtered_df.to_csv(index=False)
            st.download_button(
                "📄 Export as CSV",
                data=csv_history,
                file_name=f"calculation_history_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv",
                use_container_width=True
            )
        
        with col2:
            # Excel Export
            excel_output = io.BytesIO()
            with pd.ExcelWriter(excel_output, engine='openpyxl') as writer:
                filtered_df.to_excel(writer, sheet_name='History', index=False)
                
                # Summary sheet
                summary_data = {
                    'Metric': ['Total Records', 'Unique Types', 'Export Date'],
                    'Value': [len(filtered_df), filtered_df['type'].nunique(), datetime.now().strftime('%Y-%m-%d %H:%M')]
                }
                pd.DataFrame(summary_data).to_excel(writer, sheet_name='Summary', index=False)
            
            st.download_button(
                "📊 Export as Excel",
                data=excel_output.getvalue(),
                file_name=f"calculation_history_{datetime.now().strftime('%Y%m%d')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )
        
        with col3:
            # PDF Export
            try:
                summary_dict = {
                    'Total Records': len(filtered_df),
                    'Unique Types': filtered_df['type'].nunique(),
                    'Date Range': f"{filtered_df['timestamp'].min()} to {filtered_df['timestamp'].max()}",
                    'Export Date': datetime.now().strftime('%Y-%m-%d %H:%M')
                }
                pdf_data = generate_pdf("Calculation History Report", summary_dict, filtered_df)
                st.download_button(
                    "📕 Export as PDF",
                    data=pdf_data,
                    file_name=f"calculation_history_{datetime.now().strftime('%Y%m%d')}.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )
            except:
                st.button("📕 PDF (Error)", disabled=True, use_container_width=True)
        
        with col4:
            # JSON Export
            json_history = filtered_df.to_json(orient='records', indent=2)
            st.download_button(
                "📋 Export as JSON",
                data=json_history,
                file_name=f"calculation_history_{datetime.now().strftime('%Y%m%d')}.json",
                mime="application/json",
                use_container_width=True
            )
        
        # Clear History
        st.markdown("---")
        st.markdown("### ⚠️ Danger Zone")
        
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            if st.button("🗑️ Clear All History", use_container_width=True, type="secondary"):
                st.session_state.calculation_history = []
                st.success("History cleared!")
                st.rerun()
    
    else:
        st.info("📝 No calculation history yet. Start using calculators to build your history!")
        
        st.markdown("""
        <div class="calc-card">
            <h4>💡 How to build history:</h4>
            <ul>
                <li>Use any calculator from the sidebar</li>
                <li>Complete a calculation</li>
                <li>It will automatically be saved here</li>
                <li>Export anytime in CSV, Excel, PDF, or JSON</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════
#                    SIMPLE INTEREST
# ═══════════════════════════════════════════════════════════════

elif calculator_type == "📐 Simple Interest":
    st.markdown("""
    <div class="main-header">
        <h1>📐 Simple Interest Calculator</h1>
        <p>With Year-wise Interest Schedule</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="formula-box">
        <strong>Formula:</strong> I = (P × R × T) / 100
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        P = st.number_input(f"💰 Principal (P) [{currency_symbol}]", min_value=0.0, value=100000.0, step=10000.0)
        R = st.number_input("📊 Rate (R) [% per year]", min_value=0.0, value=10.0, step=0.5)
    
    with col2:
        T = st.number_input("⏰ Time (T) [Years]", min_value=0.0, value=5.0, step=1.0)
        I = st.number_input(f"💵 Interest (I) [{currency_symbol}]", min_value=0.0, value=0.0, step=1000.0)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        calculate_btn = st.button("🔄 Calculate", use_container_width=True, type="primary")
    
    if calculate_btn:
        st.session_state.show_downloads = False
        
        values = [P, R, T, I]
        zeros = values.count(0)
        
        if zeros != 1:
            st.error("⚠️ Please leave exactly ONE field as 0!")
        else:
            try:
                if P == 0:
                    P = (I * 100) / (R * T)
                    result_label, result_value = "Principal (P)", format_currency(P, currency_symbol)
                elif R == 0:
                    R = (I * 100) / (P * T)
                    result_label, result_value = "Rate (R)", f"{R:.4f}%"
                elif T == 0:
                    T = (I * 100) / (P * R)
                    result_label, result_value = "Time (T)", f"{T:.2f} years"
                else:
                    I = (P * R * T) / 100
                    result_label, result_value = "Interest (I)", format_currency(I, currency_symbol)
                
                total_amount = P + I
                
                st.markdown(f"""
                <div class="result-box">
                    ✅ {result_label} = {result_value}
                </div>
                """, unsafe_allow_html=True)
                
                col1, col2, col3, col4 = st.columns(4)
                col1.metric("Principal", format_currency(P, currency_symbol))
                col2.metric("Rate", f"{R:.2f}%")
                col3.metric("Time", f"{T:.0f} years")
                col4.metric("Interest", format_currency(I, currency_symbol))
                
                st.success(f"💰 **Total Amount:** {format_currency(total_amount, currency_symbol)}")
                
                # Schedule
                st.markdown("---")
                st.markdown("### 📋 Year-wise Schedule")
                
                schedule_data = []
                yearly_interest = (P * R) / 100
                
                for year in range(1, int(T) + 1):
                    schedule_data.append({
                        'Year': year,
                        'Opening Balance': P,
                        'Interest': yearly_interest,
                        'Cumulative Interest': yearly_interest * year,
                        'Total Value': P + (yearly_interest * year)
                    })
                
                schedule_df = pd.DataFrame(schedule_data)
                
                display_df = schedule_df.copy()
                for col in ['Opening Balance', 'Interest', 'Cumulative Interest', 'Total Value']:
                    display_df[col] = display_df[col].apply(lambda x: format_currency(x, currency_symbol))
                
                st.dataframe(display_df, use_container_width=True, hide_index=True)
                
                # Charts
                st.markdown("---")
                st.markdown("### 📈 Charts")
                
                tab1, tab2 = st.tabs(["🥧 Pie Chart", "📈 Growth"])
                
                with tab1:
                    fig = create_pie_chart(['Principal', 'Interest'], [P, I], 'Principal vs Interest')
                    st.plotly_chart(fig, use_container_width=True)
                
                with tab2:
                    fig = create_line_chart(
                        schedule_df['Year'].tolist(),
                        {'Total Value': schedule_df['Total Value'].tolist()},
                        'Growth Over Time', 'Year', f'Value ({currency_symbol})'
                    )
                    st.plotly_chart(fig, use_container_width=True)
                
                # Download
                summary_dict = {
                    'Principal': format_currency(P, currency_symbol),
                    'Rate': f'{R:.4f}%',
                    'Time': f'{T:.2f} years',
                    'Interest': format_currency(I, currency_symbol),
                    'Total Amount': format_currency(total_amount, currency_symbol)
                }
                
                show_download_section("Simple Interest", summary_dict, schedule_df, currency_symbol)
                add_to_history("Simple Interest", summary_dict, {'Result': result_value})
                
            except Exception as e:
                st.error(f"❌ Error: {e}")

# ═══════════════════════════════════════════════════════════════
#                    COMPOUND INTEREST
# ═══════════════════════════════════════════════════════════════

elif calculator_type == "📈 Compound Interest":
    st.markdown("""
    <div class="main-header">
        <h1>📈 Compound Interest Calculator</h1>
        <p>With Period-wise Schedule</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="formula-box">
        <strong>Formula:</strong> FV = PV × (1 + r/m)^(n×m)
    </div>
    """, unsafe_allow_html=True)
    
    freq_options = get_frequency_options()
    frequency = st.selectbox("📅 Compounding Frequency", list(freq_options.keys()), index=3)
    m = freq_options[frequency]
    
    col1, col2 = st.columns(2)
    
    with col1:
        PV = st.number_input(f"💰 Present Value [{currency_symbol}]", min_value=0.0, value=100000.0, step=10000.0)
        FV = st.number_input(f"💵 Future Value [{currency_symbol}]", min_value=0.0, value=0.0, step=10000.0)
    
    with col2:
        r = st.number_input("📊 Annual Rate [%]", min_value=0.0, value=10.0, step=0.5)
        n = st.number_input("⏰ Years", min_value=0.0, value=5.0, step=1.0)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        calculate_btn = st.button("🔄 Calculate", use_container_width=True, type="primary")
    
    if calculate_btn:
        st.session_state.show_downloads = False
        values = [PV, FV, r, n]
        zeros = values.count(0)
        
        if zeros != 1:
            st.error("⚠️ Please leave exactly ONE field as 0!")
        else:
            try:
                if PV == 0:
                    r_periodic = (r / 100) / m
                    total_periods = n * m
                    PV = FV / ((1 + r_periodic) ** total_periods)
                    result_label, result_value = "Present Value", format_currency(PV, currency_symbol)
                elif FV == 0:
                    r_periodic = (r / 100) / m
                    total_periods = n * m
                    FV = PV * ((1 + r_periodic) ** total_periods)
                    result_label, result_value = "Future Value", format_currency(FV, currency_symbol)
                elif r == 0:
                    total_periods = n * m
                    r_periodic = (FV / PV) ** (1 / total_periods) - 1
                    r = r_periodic * m * 100
                    result_label, result_value = "Annual Rate", f"{r:.4f}%"
                else:
                    r_periodic = (r / 100) / m
                    n = math.log(FV / PV) / (m * math.log(1 + r_periodic))
                    result_label, result_value = "Years", f"{n:.2f}"
                
                compound_interest = FV - PV
                
                st.markdown(f"""
                <div class="result-box">
                    ✅ {result_label} = {result_value}
                </div>
                """, unsafe_allow_html=True)
                
                col1, col2, col3, col4 = st.columns(4)
                col1.metric("Present Value", format_currency(PV, currency_symbol))
                col2.metric("Future Value", format_currency(FV, currency_symbol))
                col3.metric("Interest", format_currency(compound_interest, currency_symbol))
                col4.metric("Years", f"{n:.2f}")
                
                # Schedule
                st.markdown("---")
                st.markdown("### 📋 Year-wise Schedule")
                
                r_periodic = (r / 100) / m
                schedule_data = []
                balance = PV
                
                for year in range(1, int(n) + 1):
                    opening = balance
                    for _ in range(m):
                        balance = balance * (1 + r_periodic)
                    interest = balance - opening
                    
                    schedule_data.append({
                        'Year': year,
                        'Opening': opening,
                        'Interest': interest,
                        'Closing': balance
                    })
                
                schedule_df = pd.DataFrame(schedule_data)
                
                display_df = schedule_df.copy()
                for col in ['Opening', 'Interest', 'Closing']:
                    display_df[col] = display_df[col].apply(lambda x: format_currency(x, currency_symbol))
                
                st.dataframe(display_df, use_container_width=True, hide_index=True)
                
                # Charts
                st.markdown("---")
                tab1, tab2 = st.tabs(["🥧 Breakdown", "📈 Growth"])
                
                with tab1:
                    fig = create_pie_chart(['Principal', 'Interest'], [PV, compound_interest], 'Breakdown')
                    st.plotly_chart(fig, use_container_width=True)
                
                with tab2:
                    fig = create_line_chart(
                        schedule_df['Year'].tolist(),
                        {'Balance': schedule_df['Closing'].tolist()},
                        'Growth Over Time', 'Year', f'Value ({currency_symbol})'
                    )
                    st.plotly_chart(fig, use_container_width=True)
                
                summary_dict = {
                    'Present Value': format_currency(PV, currency_symbol),
                    'Future Value': format_currency(FV, currency_symbol),
                    'Rate': f'{r:.4f}%',
                    'Years': f'{n:.2f}',
                    'Compounding': frequency,
                    'Interest': format_currency(compound_interest, currency_symbol)
                }
                
                show_download_section("Compound Interest", summary_dict, schedule_df, currency_symbol)
                add_to_history("Compound Interest", summary_dict, {'Result': result_value})
                
            except Exception as e:
                st.error(f"❌ Error: {e}")

# ═══════════════════════════════════════════════════════════════
#                    EMI CALCULATOR
# ═══════════════════════════════════════════════════════════════

elif calculator_type == "🏦 EMI Calculator":
    st.markdown("""
    <div class="main-header">
        <h1>🏦 EMI Calculator</h1>
        <p>With Amortization Schedule</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        loan = st.number_input(f"💰 Loan Amount [{currency_symbol}]", min_value=1000.0, value=1000000.0, step=50000.0)
    with col2:
        rate = st.number_input("📊 Annual Rate [%]", min_value=0.1, value=10.0, step=0.25)
    with col3:
        tenure = st.number_input("⏰ Tenure [Years]", min_value=1, value=20, step=1)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🔄 Calculate EMI", use_container_width=True, type="primary"):
            st.session_state.show_downloads = False
            
            monthly_rate = rate / 12 / 100
            months = tenure * 12
            emi = loan * monthly_rate * (1 + monthly_rate)**months / ((1 + monthly_rate)**months - 1)
            total = emi * months
            interest = total - loan
            
            st.markdown(f"""
            <div class="result-box">
                💳 Monthly EMI: {format_currency(emi, currency_symbol)}
            </div>
            """, unsafe_allow_html=True)
            
            col1, col2, col3 = st.columns(3)
            col1.metric("Total Payment", format_currency(total, currency_symbol))
            col2.metric("Total Interest", format_currency(interest, currency_symbol))
            col3.metric("Interest %", f"{(interest/loan)*100:.1f}%")
            
            # Schedule
            st.markdown("---")
            st.markdown("### 📋 Amortization Schedule")
            
            schedule = []
            balance = loan
            for month in range(1, months + 1):
                int_pay = balance * monthly_rate
                prin_pay = emi - int_pay
                balance = max(0, balance - prin_pay)
                schedule.append({'Month': month, 'EMI': emi, 'Principal': prin_pay, 'Interest': int_pay, 'Balance': balance})
            
            schedule_df = pd.DataFrame(schedule)
            
            display_df = schedule_df.head(24).copy() if len(schedule_df) > 24 else schedule_df.copy()
            for col in ['EMI', 'Principal', 'Interest', 'Balance']:
                display_df[col] = display_df[col].apply(lambda x: format_currency(x, currency_symbol))
            
            st.dataframe(display_df, use_container_width=True, hide_index=True)
            if len(schedule_df) > 24:
                st.info(f"Showing first 24 of {len(schedule_df)} months. Download for full schedule.")
            
            # Charts
            st.markdown("---")
            tab1, tab2 = st.tabs(["🥧 Breakdown", "📈 Balance"])
            
            with tab1:
                fig = create_pie_chart(['Principal', 'Interest'], [loan, interest], 'Payment Breakdown')
                st.plotly_chart(fig, use_container_width=True)
            
            with tab2:
                fig = create_line_chart(
                    schedule_df['Month'].tolist()[::max(1, len(schedule_df)//50)],
                    {'Balance': schedule_df['Balance'].tolist()[::max(1, len(schedule_df)//50)]},
                    'Loan Balance', 'Month', f'Balance ({currency_symbol})'
                )
                st.plotly_chart(fig, use_container_width=True)
            
            summary_dict = {
                'Loan': format_currency(loan, currency_symbol),
                'Rate': f'{rate}%',
                'Tenure': f'{tenure} years',
                'EMI': format_currency(emi, currency_symbol),
                'Total Payment': format_currency(total, currency_symbol),
                'Total Interest': format_currency(interest, currency_symbol)
            }
            
            show_download_section("EMI Calculator", summary_dict, schedule_df, currency_symbol)
            add_to_history("EMI Calculator", summary_dict, {'EMI': format_currency(emi, currency_symbol)})

# ═══════════════════════════════════════════════════════════════
#                    SIP CALCULATOR
# ═══════════════════════════════════════════════════════════════

elif calculator_type == "💎 SIP Calculator":
    st.markdown("""
    <div class="main-header">
        <h1>💎 SIP Calculator</h1>
        <p>With Year-wise Schedule</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        sip = st.number_input(f"💰 Monthly SIP [{currency_symbol}]", min_value=100.0, value=10000.0, step=1000.0)
        ret = st.number_input("📊 Expected Return [%]", min_value=1.0, value=12.0, step=0.5)
    with col2:
        years = st.number_input("⏰ Years", min_value=1, value=10, step=1)
        step_up = st.number_input("📈 Step-up [%]", min_value=0.0, value=10.0, step=5.0)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🔄 Calculate SIP", use_container_width=True, type="primary"):
            st.session_state.show_downloads = False
            
            monthly_rate = ret / 12 / 100
            current_sip = sip
            invested = 0
            value = 0
            
            schedule = []
            for year in range(1, years + 1):
                for _ in range(12):
                    value = value * (1 + monthly_rate) + current_sip
                    invested += current_sip
                
                schedule.append({
                    'Year': year,
                    'SIP': current_sip,
                    'Invested': invested,
                    'Value': value,
                    'Gain': value - invested
                })
                current_sip = current_sip * (1 + step_up / 100)
            
            schedule_df = pd.DataFrame(schedule)
            wealth = value - invested
            
            st.markdown(f"""
            <div class="result-box">
                💰 Future Value: {format_currency(value, currency_symbol)}
            </div>
            """, unsafe_allow_html=True)
            
            col1, col2, col3 = st.columns(3)
            col1.metric("Invested", format_currency(invested, currency_symbol))
            col2.metric("Wealth Gained", format_currency(wealth, currency_symbol))
            col3.metric("Returns", f"{(wealth/invested)*100:.1f}%")
            
            # Schedule
            st.markdown("---")
            st.markdown("### 📋 Year-wise Schedule")
            
            display_df = schedule_df.copy()
            for col in ['SIP', 'Invested', 'Value', 'Gain']:
                display_df[col] = display_df[col].apply(lambda x: format_currency(x, currency_symbol))
            
            st.dataframe(display_df, use_container_width=True, hide_index=True)
            
            # Charts
            st.markdown("---")
            tab1, tab2 = st.tabs(["📈 Growth", "🥧 Breakdown"])
            
            with tab1:
                fig = create_line_chart(
                    schedule_df['Year'].tolist(),
                    {'Invested': schedule_df['Invested'].tolist(), 'Value': schedule_df['Value'].tolist()},
                    'SIP Growth', 'Year', f'Amount ({currency_symbol})'
                )
                st.plotly_chart(fig, use_container_width=True)
            
            with tab2:
                fig = create_pie_chart(['Invested', 'Gains'], [invested, wealth], 'Breakdown')
                st.plotly_chart(fig, use_container_width=True)
            
            summary_dict = {
                'Starting SIP': format_currency(sip, currency_symbol),
                'Return': f'{ret}%',
                'Years': years,
                'Step-up': f'{step_up}%',
                'Invested': format_currency(invested, currency_symbol),
                'Future Value': format_currency(value, currency_symbol),
                'Wealth': format_currency(wealth, currency_symbol)
            }
            
            show_download_section("SIP Calculator", summary_dict, schedule_df, currency_symbol)
            add_to_history("SIP Calculator", summary_dict, {'Value': format_currency(value, currency_symbol)})

# ═══════════════════════════════════════════════════════════════
#                    NPV CALCULATOR
# ═══════════════════════════════════════════════════════════════

elif calculator_type == "💹 NPV Calculator":
    st.markdown("""
    <div class="main-header">
        <h1>💹 NPV Calculator</h1>
        <p>With Cash Flow Schedule</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        initial = st.number_input(f"💰 Initial Investment [{currency_symbol}]", min_value=0.0, value=100000.0, step=10000.0)
    with col2:
        rate = st.number_input("📊 Discount Rate [%]", min_value=0.0, value=10.0, step=0.5)
    with col3:
        num_years = st.number_input("⏰ Years", min_value=1, max_value=20, value=5)
    
    st.markdown("### Cash Flows")
    cash_flows = []
    cols = st.columns(min(num_years, 5))
    for i in range(num_years):
        with cols[i % 5]:
            cf = st.number_input(f"Year {i+1}", min_value=0.0, value=30000.0, step=5000.0, key=f"cf{i}")
            cash_flows.append(cf)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🔄 Calculate NPV", use_container_width=True, type="primary"):
            st.session_state.show_downloads = False
            
            r = rate / 100
            npv = -initial
            
            schedule = [{'Year': 0, 'Cash Flow': -initial, 'PV': -initial, 'Cumulative': -initial}]
            cumulative = -initial
            
            for t, cf in enumerate(cash_flows, 1):
                pv = cf / (1 + r) ** t
                npv += pv
                cumulative += pv
                schedule.append({'Year': t, 'Cash Flow': cf, 'PV': pv, 'Cumulative': cumulative})
            
            schedule_df = pd.DataFrame(schedule)
            
            color = "00b894" if npv > 0 else "e74c3c"
            decision = "ACCEPT" if npv > 0 else "REJECT"
            
            st.markdown(f"""
            <div class="result-box" style="background: linear-gradient(135deg, #{color}, #{color}dd);">
                NPV = {format_currency(npv, currency_symbol)} - {decision}
            </div>
            """, unsafe_allow_html=True)
            
            # Schedule
            st.markdown("---")
            st.markdown("### 📋 Cash Flow Schedule")
            
            display_df = schedule_df.copy()
            for col in ['Cash Flow', 'PV', 'Cumulative']:
                display_df[col] = display_df[col].apply(lambda x: format_currency(x, currency_symbol))
            
            st.dataframe(display_df, use_container_width=True, hide_index=True)
            
            # Chart
            fig = create_bar_chart(
                [f'Y{y}' for y in schedule_df['Year'].tolist()],
                {'Cash Flow': schedule_df['Cash Flow'].tolist(), 'PV': schedule_df['PV'].tolist()},
                'Cash Flows', f'Amount ({currency_symbol})'
            )
            st.plotly_chart(fig, use_container_width=True)
            
            summary_dict = {
                'Initial': format_currency(initial, currency_symbol),
                'Rate': f'{rate}%',
                'Years': num_years,
                'NPV': format_currency(npv, currency_symbol),
                'Decision': decision
            }
            
            show_download_section("NPV Calculator", summary_dict, schedule_df, currency_symbol)
            add_to_history("NPV Calculator", summary_dict, {'NPV': format_currency(npv, currency_symbol)})

# ═══════════════════════════════════════════════════════════════
#                    BOND VALUATION
# ═══════════════════════════════════════════════════════════════

elif calculator_type == "📜 Bond Valuation":
    st.markdown("""
    <div class="main-header">
        <h1>📜 Bond Valuation</h1>
        <p>With Coupon Schedule</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        face = st.number_input(f"💵 Face Value [{currency_symbol}]", min_value=100.0, value=1000.0, step=100.0)
        coupon = st.number_input("📊 Coupon Rate [%]", min_value=0.0, value=8.0, step=0.25)
        freq = st.selectbox("🔄 Frequency", ["Annual", "Semi-Annual", "Quarterly"])
    with col2:
        ytm = st.number_input("📈 YTM [%]", min_value=0.1, value=10.0, step=0.25)
        maturity = st.number_input("⏰ Years", min_value=1, value=10)
    
    freq_map = {"Annual": 1, "Semi-Annual": 2, "Quarterly": 4}
    m = freq_map[freq]
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🔄 Calculate Price", use_container_width=True, type="primary"):
            st.session_state.show_downloads = False
            
            coupon_pay = (face * coupon / 100) / m
            periods = maturity * m
            y = (ytm / 100) / m
            
            pv_coupons = sum(coupon_pay / (1 + y) ** t for t in range(1, periods + 1))
            pv_face = face / (1 + y) ** periods
            price = pv_coupons + pv_face
            
            st.markdown(f"""
            <div class="result-box">
                📜 Bond Price: {format_currency(price, currency_symbol)}
            </div>
            """, unsafe_allow_html=True)
            
            if price > face:
                st.success("📈 Premium Bond")
            elif price < face:
                st.warning("📉 Discount Bond")
            else:
                st.info("➡️ Par Bond")
            
            col1, col2, col3 = st.columns(3)
            col1.metric("Bond Price", format_currency(price, currency_symbol))
            col2.metric("PV Coupons", format_currency(pv_coupons, currency_symbol))
            col3.metric("PV Face", format_currency(pv_face, currency_symbol))
            
            # Schedule
            schedule = []
            for t in range(1, periods + 1):
                pv = coupon_pay / (1 + y) ** t
                schedule.append({'Period': t, 'Coupon': coupon_pay, 'PV': pv})
            
            schedule_df = pd.DataFrame(schedule)
            
            st.markdown("---")
            st.markdown("### 📋 Coupon Schedule")
            
            display_df = schedule_df.copy()
            for col in ['Coupon', 'PV']:
                display_df[col] = display_df[col].apply(lambda x: format_currency(x, currency_symbol))
            
            st.dataframe(display_df.head(20), use_container_width=True, hide_index=True)
            
            summary_dict = {
                'Face': format_currency(face, currency_symbol),
                'Coupon': f'{coupon}%',
                'YTM': f'{ytm}%',
                'Years': maturity,
                'Price': format_currency(price, currency_symbol)
            }
            
            show_download_section("Bond Valuation", summary_dict, schedule_df, currency_symbol)
            add_to_history("Bond Valuation", summary_dict, {'Price': format_currency(price, currency_symbol)})

# ═══════════════════════════════════════════════════════════════
#                    FORMULAS
# ═══════════════════════════════════════════════════════════════

elif calculator_type == "📖 Formulas":
    st.markdown("""
    <div class="main-header">
        <h1>📖 Formula Reference</h1>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    ### 📐 Simple Interest
    ```
    I = (P × R × T) / 100
    ```
    
    ### 📈 Compound Interest
    ```
    FV = PV × (1 + r/m)^(n×m)
    ```
    
    ### 🏦 EMI
    ```
    EMI = P × r × (1+r)^n / [(1+r)^n - 1]
    ```
    
    ### 💎 SIP
    ```
    FV = P × [(1+r)^n - 1] / r × (1+r)
    ```
    
    ### 💹 NPV
    ```
    NPV = -C₀ + Σ[CFₜ / (1+r)^t]
    ```
    
    ### 📜 Bond
    ```
    Price = Σ[C/(1+y)^t] + F/(1+y)^n
    ```
    """)

# ═══════════════════════════════════════════════════════════════
#                    FOOTER
# ═══════════════════════════════════════════════════════════════

st.markdown("---")
st.markdown("""
<div style="text-align: center; padding: 20px; color: #888;">
    💰 Financial Calculator Pro v3.0 | Made with ❤️
</div>
""", unsafe_allow_html=True)
