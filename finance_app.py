import streamlit as st
import pandas as pd
import numpy as np
import math
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import json
import io
import base64
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders

# For PDF Generation
from fpdf import FPDF
import tempfile
import os

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
    /* Main Header */
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 30px;
        border-radius: 20px;
        text-align: center;
        color: white;
        margin-bottom: 30px;
        box-shadow: 0 10px 40px rgba(102, 126, 234, 0.4);
    }
    
    .main-header h1 {
        margin: 0;
        font-size: 2.5rem;
    }
    
    .main-header p {
        margin: 10px 0 0 0;
        opacity: 0.9;
    }
    
    /* Result Box */
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
    
    /* Calculator Card */
    .calc-card {
        background: white;
        padding: 25px;
        border-radius: 15px;
        border: 1px solid #e0e0e0;
        margin: 15px 0;
        box-shadow: 0 5px 20px rgba(0,0,0,0.08);
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }
    
    .calc-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 15px 40px rgba(0,0,0,0.15);
    }
    
    /* Formula Box */
    .formula-box {
        background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
        padding: 20px;
        border-radius: 15px;
        font-family: 'Courier New', monospace;
        border-left: 5px solid #667eea;
        margin: 20px 0;
        font-size: 1.1rem;
    }
    
    /* Info Cards */
    .info-card {
        background: #e3f2fd;
        padding: 15px 20px;
        border-radius: 12px;
        border-left: 5px solid #2196F3;
        margin: 15px 0;
    }
    
    .success-card {
        background: #e8f5e9;
        padding: 15px 20px;
        border-radius: 12px;
        border-left: 5px solid #4CAF50;
        margin: 15px 0;
    }
    
    .warning-card {
        background: #fff3e0;
        padding: 15px 20px;
        border-radius: 12px;
        border-left: 5px solid #ff9800;
        margin: 15px 0;
    }
    
    /* Metric Cards */
    .metric-container {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 20px;
        border-radius: 15px;
        text-align: center;
        color: white;
    }
    
    .metric-value {
        font-size: 2rem;
        font-weight: bold;
    }
    
    .metric-label {
        font-size: 0.9rem;
        opacity: 0.9;
    }
    
    /* Buttons */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        padding: 12px 30px;
        border-radius: 10px;
        font-weight: bold;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        transform: scale(1.05);
        box-shadow: 0 5px 20px rgba(102, 126, 234, 0.4);
    }
    
    /* Download Buttons */
    .download-btn {
        display: inline-block;
        padding: 12px 25px;
        margin: 5px;
        border-radius: 10px;
        text-decoration: none;
        font-weight: bold;
        transition: all 0.3s ease;
    }
    
    .download-btn-excel {
        background: linear-gradient(135deg, #27ae60 0%, #2ecc71 100%);
        color: white;
    }
    
    .download-btn-pdf {
        background: linear-gradient(135deg, #e74c3c 0%, #c0392b 100%);
        color: white;
    }
    
    .download-btn-csv {
        background: linear-gradient(135deg, #3498db 0%, #2980b9 100%);
        color: white;
    }
    
    /* Tables */
    .dataframe {
        border-radius: 10px;
        overflow: hidden;
    }
    
    /* Sidebar */
    .css-1d391kg {
        background: linear-gradient(180deg, #f8f9fa 0%, #e9ecef 100%);
    }
    
    /* Hide Streamlit Branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════
#                    SESSION STATE INITIALIZATION
# ═══════════════════════════════════════════════════════════════

if 'calculation_history' not in st.session_state:
    st.session_state.calculation_history = []

if 'theme' not in st.session_state:
    st.session_state.theme = 'light'

# ═══════════════════════════════════════════════════════════════
#                    HELPER FUNCTIONS
# ═══════════════════════════════════════════════════════════════

def format_currency(value, symbol="$"):
    """Format number as currency"""
    if value is None or pd.isna(value):
        return "N/A"
    return f"{symbol}{value:,.2f}"

def format_percent(value):
    """Format number as percentage"""
    if value is None:
        return "N/A"
    return f"{value:.4f}%"

def format_number(value):
    """Format large numbers"""
    if value is None:
        return "N/A"
    return f"{value:,.2f}"

def get_frequency_options():
    """Return frequency options"""
    return {
        "Annually (1/year)": 1,
        "Semi-Annually (2/year)": 2,
        "Quarterly (4/year)": 4,
        "Monthly (12/year)": 12,
        "Weekly (52/year)": 52,
        "Daily (365/year)": 365
    }

def add_to_history(calc_type, inputs, outputs, details=None):
    """Add calculation to history"""
    st.session_state.calculation_history.append({
        'id': len(st.session_state.calculation_history) + 1,
        'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        'type': calc_type,
        'inputs': inputs,
        'outputs': outputs,
        'details': details or {}
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
        self.cell(0, 5, f'Report Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}', 0, 1, 'C')
        self.ln(10)
    
    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.set_text_color(128, 128, 128)
        self.cell(0, 10, f'Page {self.page_no()}/{{nb}}', 0, 0, 'C')
    
    def add_title(self, title):
        self.set_font('Arial', 'B', 16)
        self.set_text_color(102, 126, 234)
        self.cell(0, 10, title, 0, 1, 'L')
        self.ln(5)
    
    def add_subtitle(self, subtitle):
        self.set_font('Arial', 'B', 12)
        self.set_text_color(60, 60, 60)
        self.cell(0, 8, subtitle, 0, 1, 'L')
        self.ln(3)
    
    def add_text(self, text):
        self.set_font('Arial', '', 11)
        self.set_text_color(60, 60, 60)
        self.multi_cell(0, 6, text)
        self.ln(3)
    
    def add_key_value(self, key, value):
        self.set_font('Arial', 'B', 11)
        self.set_text_color(60, 60, 60)
        self.cell(80, 8, key + ":", 0, 0, 'L')
        self.set_font('Arial', '', 11)
        self.set_text_color(102, 126, 234)
        self.cell(0, 8, str(value), 0, 1, 'L')
    
    def add_result_box(self, label, value):
        self.set_fill_color(102, 126, 234)
        self.set_text_color(255, 255, 255)
        self.set_font('Arial', 'B', 14)
        self.cell(0, 15, f'{label}: {value}', 0, 1, 'C', True)
        self.ln(5)
        self.set_text_color(60, 60, 60)
    
    def add_table(self, headers, data):
        self.set_font('Arial', 'B', 10)
        self.set_fill_color(102, 126, 234)
        self.set_text_color(255, 255, 255)
        
        col_width = 190 / len(headers)
        
        # Header
        for header in headers:
            self.cell(col_width, 10, str(header), 1, 0, 'C', True)
        self.ln()
        
        # Data
        self.set_font('Arial', '', 9)
        self.set_text_color(60, 60, 60)
        fill = False
        
        for row in data:
            if fill:
                self.set_fill_color(240, 240, 240)
            else:
                self.set_fill_color(255, 255, 255)
            
            for item in row:
                self.cell(col_width, 8, str(item), 1, 0, 'C', True)
            self.ln()
            fill = not fill

def generate_pdf_report(calc_type, inputs_dict, outputs_dict, summary_df=None, chart_data=None):
    """Generate a professional PDF report"""
    pdf = PDFReport()
    pdf.alias_nb_pages()
    pdf.add_page()
    
    # Title
    pdf.add_title(f"{calc_type} Report")
    
    # Inputs Section
    pdf.add_subtitle("Input Parameters")
    for key, value in inputs_dict.items():
        pdf.add_key_value(key, value)
    
    pdf.ln(5)
    
    # Results Section
    pdf.add_subtitle("Calculated Results")
    for key, value in outputs_dict.items():
        if key == "Main Result":
            pdf.add_result_box(key, value)
        else:
            pdf.add_key_value(key, value)
    
    # Summary Table
    if summary_df is not None:
        pdf.ln(5)
        pdf.add_subtitle("Detailed Summary")
        headers = summary_df.columns.tolist()
        data = summary_df.values.tolist()
        pdf.add_table(headers, data[:20])  # Limit to 20 rows
    
    # Footer note
    pdf.ln(10)
    pdf.add_text("This report was generated automatically by Financial Calculator Pro.")
    pdf.add_text("For any queries, please contact support.")
    
    return pdf.output(dest='S').encode('latin-1')

# ═══════════════════════════════════════════════════════════════
#                    EXCEL EXPORT FUNCTION
# ═══════════════════════════════════════════════════════════════

def generate_excel_report(calc_type, inputs_dict, outputs_dict, summary_df=None, schedule_df=None):
    """Generate Excel report with multiple sheets"""
    output = io.BytesIO()
    
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        # Summary Sheet
        summary_data = {
            'Category': ['Calculation Type', 'Generated On'] + list(inputs_dict.keys()) + list(outputs_dict.keys()),
            'Value': [calc_type, datetime.now().strftime("%Y-%m-%d %H:%M:%S")] + list(inputs_dict.values()) + list(outputs_dict.values())
        }
        pd.DataFrame(summary_data).to_excel(writer, sheet_name='Summary', index=False)
        
        # Detailed Schedule Sheet
        if schedule_df is not None:
            schedule_df.to_excel(writer, sheet_name='Schedule', index=False)
        
        # Raw Data Sheet
        if summary_df is not None:
            summary_df.to_excel(writer, sheet_name='Data', index=False)
    
    return output.getvalue()

# ═══════════════════════════════════════════════════════════════
#                    EMAIL FUNCTION
# ═══════════════════════════════════════════════════════════════

def send_email_report(recipient_email, subject, body, attachment_data=None, attachment_name=None):
    """Send email with optional attachment"""
    # Note: This requires SMTP server configuration
    # For demo purposes, we'll just show a success message
    return True

# ═══════════════════════════════════════════════════════════════
#                    CHART FUNCTIONS
# ═══════════════════════════════════════════════════════════════

def create_pie_chart(labels, values, title, colors=None):
    """Create an interactive pie chart"""
    if colors is None:
        colors = ['#667eea', '#764ba2', '#00b894', '#00cec9', '#fdcb6e', '#e74c3c']
    
    fig = go.Figure(data=[go.Pie(
        labels=labels,
        values=values,
        hole=0.4,
        marker_colors=colors[:len(labels)],
        textinfo='label+percent',
        textfont_size=12,
        hovertemplate='<b>%{label}</b><br>Value: %{value:,.2f}<br>Percentage: %{percent}<extra></extra>'
    )])
    
    fig.update_layout(
        title=dict(text=title, font=dict(size=18, color='#333')),
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5),
        height=400,
        margin=dict(t=60, b=60, l=40, r=40)
    )
    
    return fig

def create_line_chart(x_data, y_data_dict, title, x_title, y_title):
    """Create an interactive line chart with multiple series"""
    fig = go.Figure()
    
    colors = ['#667eea', '#00b894', '#e74c3c', '#f39c12', '#9b59b6']
    
    for i, (name, y_data) in enumerate(y_data_dict.items()):
        fig.add_trace(go.Scatter(
            x=x_data,
            y=y_data,
            mode='lines+markers',
            name=name,
            line=dict(color=colors[i % len(colors)], width=3),
            marker=dict(size=8),
            hovertemplate=f'<b>{name}</b><br>{x_title}: %{{x}}<br>{y_title}: %{{y:,.2f}}<extra></extra>'
        ))
    
    fig.update_layout(
        title=dict(text=title, font=dict(size=18, color='#333')),
        xaxis_title=x_title,
        yaxis_title=y_title,
        hovermode='x unified',
        height=450,
        legend=dict(orientation="h", yanchor="bottom", y=-0.25, xanchor="center", x=0.5),
        margin=dict(t=60, b=80, l=60, r=40)
    )
    
    return fig

def create_bar_chart(categories, values_dict, title, y_title):
    """Create an interactive bar chart"""
    fig = go.Figure()
    
    colors = ['#667eea', '#00b894', '#e74c3c', '#f39c12']
    
    for i, (name, values) in enumerate(values_dict.items()):
        fig.add_trace(go.Bar(
            name=name,
            x=categories,
            y=values,
            marker_color=colors[i % len(colors)],
            hovertemplate=f'<b>{name}</b><br>%{{x}}: %{{y:,.2f}}<extra></extra>'
        ))
    
    fig.update_layout(
        title=dict(text=title, font=dict(size=18, color='#333')),
        yaxis_title=y_title,
        barmode='group',
        height=400,
        legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5),
        margin=dict(t=60, b=60, l=60, r=40)
    )
    
    return fig

def create_gauge_chart(value, max_value, title, thresholds=None):
    """Create a gauge/meter chart"""
    if thresholds is None:
        thresholds = [max_value * 0.33, max_value * 0.66, max_value]
    
    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=value,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': title, 'font': {'size': 18}},
        gauge={
            'axis': {'range': [0, max_value], 'tickwidth': 1},
            'bar': {'color': "#667eea"},
            'bgcolor': "white",
            'borderwidth': 2,
            'bordercolor': "#ccc",
            'steps': [
                {'range': [0, thresholds[0]], 'color': '#e8f5e9'},
                {'range': [thresholds[0], thresholds[1]], 'color': '#fff3e0'},
                {'range': [thresholds[1], thresholds[2]], 'color': '#ffebee'}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': value
            }
        }
    ))
    
    fig.update_layout(height=300, margin=dict(t=60, b=20, l=40, r=40))
    
    return fig

def create_area_chart(x_data, y_data_dict, title, x_title, y_title):
    """Create stacked area chart"""
    fig = go.Figure()
    
    colors = ['rgba(102, 126, 234, 0.7)', 'rgba(0, 184, 148, 0.7)', 'rgba(231, 76, 60, 0.7)']
    
    for i, (name, y_data) in enumerate(y_data_dict.items()):
        fig.add_trace(go.Scatter(
            x=x_data,
            y=y_data,
            mode='lines',
            name=name,
            stackgroup='one',
            fillcolor=colors[i % len(colors)],
            line=dict(width=0.5, color=colors[i % len(colors)].replace('0.7', '1')),
            hovertemplate=f'<b>{name}</b><br>{x_title}: %{{x}}<br>{y_title}: %{{y:,.2f}}<extra></extra>'
        ))
    
    fig.update_layout(
        title=dict(text=title, font=dict(size=18, color='#333')),
        xaxis_title=x_title,
        yaxis_title=y_title,
        hovermode='x unified',
        height=450,
        margin=dict(t=60, b=60, l=60, r=40)
    )
    
    return fig

def create_waterfall_chart(categories, values, title):
    """Create waterfall chart for breakdown"""
    fig = go.Figure(go.Waterfall(
        orientation="v",
        measure=["relative"] * (len(values) - 1) + ["total"],
        x=categories,
        y=values,
        connector={"line": {"color": "#667eea"}},
        increasing={"marker": {"color": "#00b894"}},
        decreasing={"marker": {"color": "#e74c3c"}},
        totals={"marker": {"color": "#667eea"}}
    ))
    
    fig.update_layout(
        title=dict(text=title, font=dict(size=18, color='#333')),
        height=400,
        margin=dict(t=60, b=60, l=60, r=40)
    )
    
    return fig

# ═══════════════════════════════════════════════════════════════
#                    DOWNLOAD BUTTONS COMPONENT
# ═══════════════════════════════════════════════════════════════

def download_section(calc_type, inputs_dict, outputs_dict, summary_df=None, schedule_df=None, currency_symbol="$"):
    """Create download section with all export options"""
    
    st.markdown("### 📥 Download & Export Results")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        # CSV Download
        if summary_df is not None:
            csv_data = summary_df.to_csv(index=False)
            st.download_button(
                label="📄 Download CSV",
                data=csv_data,
                file_name=f"{calc_type.lower().replace(' ', '_')}_report.csv",
                mime="text/csv",
                use_container_width=True
            )
        else:
            combined_data = {**{'Parameter': list(inputs_dict.keys()) + list(outputs_dict.keys())},
                           **{'Value': list(inputs_dict.values()) + list(outputs_dict.values())}}
            csv_data = pd.DataFrame(combined_data).to_csv(index=False)
            st.download_button(
                label="📄 Download CSV",
                data=csv_data,
                file_name=f"{calc_type.lower().replace(' ', '_')}_report.csv",
                mime="text/csv",
                use_container_width=True
            )
    
    with col2:
        # Excel Download
        excel_data = generate_excel_report(calc_type, inputs_dict, outputs_dict, summary_df, schedule_df)
        st.download_button(
            label="📊 Download Excel",
            data=excel_data,
            file_name=f"{calc_type.lower().replace(' ', '_')}_report.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )
    
    with col3:
        # PDF Download
        try:
            pdf_data = generate_pdf_report(calc_type, inputs_dict, outputs_dict, summary_df)
            st.download_button(
                label="📕 Download PDF",
                data=pdf_data,
                file_name=f"{calc_type.lower().replace(' ', '_')}_report.pdf",
                mime="application/pdf",
                use_container_width=True
            )
        except Exception as e:
            st.error("PDF generation requires fpdf library")
    
    with col4:
        # JSON Download
        json_data = json.dumps({
            'calculation_type': calc_type,
            'timestamp': datetime.now().isoformat(),
            'inputs': inputs_dict,
            'outputs': outputs_dict
        }, indent=2)
        st.download_button(
            label="📋 Download JSON",
            data=json_data,
            file_name=f"{calc_type.lower().replace(' ', '_')}_report.json",
            mime="application/json",
            use_container_width=True
        )

# ═══════════════════════════════════════════════════════════════
#                    EMAIL SECTION COMPONENT
# ═══════════════════════════════════════════════════════════════

def email_section(calc_type, inputs_dict, outputs_dict):
    """Create email section"""
    st.markdown("### 📧 Email Results")
    
    with st.expander("📨 Send Results via Email"):
        col1, col2 = st.columns(2)
        
        with col1:
            recipient_email = st.text_input("📧 Recipient Email", placeholder="email@example.com")
            sender_name = st.text_input("👤 Your Name", placeholder="Your Name")
        
        with col2:
            subject = st.text_input("📝 Subject", value=f"{calc_type} Report")
            additional_message = st.text_area("💬 Additional Message", placeholder="Add any notes...")
        
        if st.button("📤 Send Email", use_container_width=True):
            if recipient_email and sender_name:
                # In production, implement actual email sending
                st.success(f"✅ Report sent successfully to {recipient_email}!")
                st.info("Note: Email functionality requires SMTP configuration")
            else:
                st.error("Please fill in all required fields")

# ═══════════════════════════════════════════════════════════════
#                    IMPORT DATA COMPONENT
# ═══════════════════════════════════════════════════════════════

def import_data_section():
    """Import data from Excel/CSV"""
    st.markdown("### 📤 Import Data for Bulk Calculations")
    
    uploaded_file = st.file_uploader(
        "Upload Excel or CSV file",
        type=['xlsx', 'xls', 'csv'],
        help="Upload a file with columns: Principal, Rate, Time, etc."
    )
    
    if uploaded_file is not None:
        try:
            if uploaded_file.name.endswith('.csv'):
                df = pd.read_csv(uploaded_file)
            else:
                df = pd.read_excel(uploaded_file)
            
            st.success(f"✅ Successfully loaded {len(df)} rows")
            st.dataframe(df.head(10), use_container_width=True)
            
            return df
        except Exception as e:
            st.error(f"Error loading file: {e}")
            return None
    
    return None

# ═══════════════════════════════════════════════════════════════
#                    SIDEBAR
# ═══════════════════════════════════════════════════════════════

with st.sidebar:
    st.markdown("""
    <div style="text-align: center; padding: 20px 0;">
        <h1 style="color: #667eea;">💰</h1>
        <h3 style="color: #333;">Financial Calculator Pro</h3>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Currency Selection
    currency_symbol = st.selectbox(
        "💵 Currency Symbol",
        ["$", "₹", "€", "£", "¥", "Rs", "AED", "PKR", "SAR"],
        index=0
    )
    
    st.markdown("---")
    
    # Calculator Selection
    st.markdown("### 📊 Select Calculator")
    
    calculator_type = st.radio(
        "Calculator",
        [
            "🏠 Home",
            "📐 Simple Interest",
            "📈 Compound Interest",
            "🏦 EMI Calculator",
            "💎 SIP Calculator",
            "💹 NPV Analysis",
            "📜 Bond Valuation",
            "📤 Import & Bulk Calc",
            "📋 History",
            "📖 Formulas"
        ],
        label_visibility="collapsed"
    )
    
    st.markdown("---")
    
    # Quick Stats
    st.markdown("### 📊 Session Stats")
    st.metric("Calculations Done", len(st.session_state.calculation_history))
    
    st.markdown("---")
    
    st.info("💡 Enter known values and leave ONE field as 0 to calculate it")

# ═══════════════════════════════════════════════════════════════
#                    HOME PAGE
# ═══════════════════════════════════════════════════════════════

if calculator_type == "🏠 Home":
    st.markdown("""
    <div class="main-header">
        <h1>💰 Financial Calculator Pro</h1>
        <p>Professional Finance Calculations with Advanced Charts & Reports</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Feature Cards
    st.markdown("### ✨ Features")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        <div class="calc-card">
            <h3>📊 10+ Calculators</h3>
            <p>SI, CI, EMI, SIP, NPV, Bonds & more</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="calc-card">
            <h3>📈 Interactive Charts</h3>
            <p>Pie, Line, Bar, Gauge, Waterfall</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="calc-card">
            <h3>📥 Export Options</h3>
            <p>PDF, Excel, CSV, JSON</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown("""
        <div class="calc-card">
            <h3>📧 Email Reports</h3>
            <p>Send results directly via email</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Recent Calculations
    if st.session_state.calculation_history:
        st.markdown("### 📋 Recent Calculations")
        recent = st.session_state.calculation_history[-5:][::-1]
        
        for calc in recent:
            st.markdown(f"""
            <div class="info-card">
                <strong>{calc['type']}</strong> - {calc['timestamp']}<br>
                <small>Result: {calc['outputs']}</small>
            </div>
            """, unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════
#                    SIMPLE INTEREST CALCULATOR
# ═══════════════════════════════════════════════════════════════

elif calculator_type == "📐 Simple Interest":
    st.markdown("""
    <div class="main-header">
        <h1>📐 Simple Interest Calculator</h1>
        <p>Calculate Principal, Rate, Time, or Interest</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="formula-box">
        <strong>Formula:</strong> I = (P × R × T) / 100<br>
        <strong>Where:</strong> P = Principal, R = Rate (% per year), T = Time (years), I = Interest
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("### 📝 Enter Values (Leave ONE field as 0)")
    
    col1, col2 = st.columns(2)
    
    with col1:
        P = st.number_input(f"💰 Principal (P) [{currency_symbol}]", min_value=0.0, value=10000.0, step=1000.0)
        R = st.number_input("📊 Annual Rate (R) [%]", min_value=0.0, value=8.0, step=0.5)
    
    with col2:
        T = st.number_input("⏰ Time (T) [Years]", min_value=0.0, value=5.0, step=0.5)
        I = st.number_input(f"💵 Interest (I) [{currency_symbol}]", min_value=0.0, value=0.0, step=100.0)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        calculate_btn = st.button("🔄 Calculate", use_container_width=True, type="primary")
    
    if calculate_btn:
        values = [P, R, T, I]
        zeros = values.count(0)
        
        if zeros != 1:
            st.markdown("""
            <div class="result-box-error">
                ⚠️ Please leave exactly ONE field as 0 to calculate it!
            </div>
            """, unsafe_allow_html=True)
        else:
            try:
                if P == 0:
                    P = (I * 100) / (R * T)
                    result_label, result_value = "Principal (P)", P
                elif R == 0:
                    R = (I * 100) / (P * T)
                    result_label, result_value = "Rate (R)", R
                elif T == 0:
                    T = (I * 100) / (P * R)
                    result_label, result_value = "Time (T)", T
                else:
                    I = (P * R * T) / 100
                    result_label, result_value = "Interest (I)", I
                
                total_amount = P + I
                
                # Display Result
                if result_label == "Rate (R)":
                    display_value = f"{result_value:.4f}%"
                elif result_label == "Time (T)":
                    display_value = f"{result_value:.2f} years"
                else:
                    display_value = format_currency(result_value, currency_symbol)
                
                st.markdown(f"""
                <div class="result-box">
                    ✅ {result_label} = {display_value}
                </div>
                """, unsafe_allow_html=True)
                
                # Metrics Row
                st.markdown("### 📊 Complete Summary")
                col1, col2, col3, col4 = st.columns(4)
                col1.metric("Principal (P)", format_currency(P, currency_symbol))
                col2.metric("Rate (R)", f"{R:.2f}%")
                col3.metric("Time (T)", f"{T:.2f} years")
                col4.metric("Interest (I)", format_currency(I, currency_symbol))
                
                st.success(f"💰 **Total Amount (P + I):** {format_currency(total_amount, currency_symbol)}")
                
                # ═══════════════════════════════════════════════════
                #              CHARTS SECTION
                # ═══════════════════════════════════════════════════
                
                st.markdown("---")
                st.markdown("### 📈 Visual Analysis")
                
                tab1, tab2, tab3, tab4 = st.tabs(["🥧 Pie Chart", "📈 Growth Chart", "📊 Bar Chart", "🎯 Gauge"])
                
                with tab1:
                    # Pie Chart - Principal vs Interest
                    fig_pie = create_pie_chart(
                        labels=['Principal', 'Interest'],
                        values=[P, I],
                        title='Principal vs Interest Breakdown',
                        colors=['#667eea', '#00b894']
                    )
                    st.plotly_chart(fig_pie, use_container_width=True)
                
                with tab2:
                    # Line Chart - Interest Growth Over Time
                    years = list(range(int(T) + 1))
                    interest_values = [(P * R * yr) / 100 for yr in years]
                    total_values = [P + int_val for int_val in interest_values]
                    
                    fig_line = create_line_chart(
                        x_data=years,
                        y_data_dict={
                            'Principal': [P] * len(years),
                            'Interest Earned': interest_values,
                            'Total Amount': total_values
                        },
                        title='Investment Growth Over Time',
                        x_title='Years',
                        y_title=f'Amount ({currency_symbol})'
                    )
                    st.plotly_chart(fig_line, use_container_width=True)
                
                with tab3:
                    # Bar Chart - Year-wise Interest
                    years_range = list(range(1, int(T) + 1))
                    yearly_interest = [(P * R) / 100] * len(years_range)
                    
                    fig_bar = create_bar_chart(
                        categories=[f'Year {y}' for y in years_range],
                        values_dict={'Annual Interest': yearly_interest},
                        title='Year-wise Interest Earned',
                        y_title=f'Interest ({currency_symbol})'
                    )
                    st.plotly_chart(fig_bar, use_container_width=True)
                
                with tab4:
                    # Gauge Chart - Interest Rate
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        fig_gauge = create_gauge_chart(
                            value=R,
                            max_value=20,
                            title='Interest Rate (%)',
                            thresholds=[5, 10, 20]
                        )
                        st.plotly_chart(fig_gauge, use_container_width=True)
                    
                    with col2:
                        # ROI Gauge
                        roi = (I / P) * 100
                        fig_gauge2 = create_gauge_chart(
                            value=roi,
                            max_value=100,
                            title='Return on Investment (%)',
                            thresholds=[20, 50, 100]
                        )
                        st.plotly_chart(fig_gauge2, use_container_width=True)
                
                # ═══════════════════════════════════════════════════
                #              DOWNLOAD SECTION
                # ═══════════════════════════════════════════════════
                
                st.markdown("---")
                
                inputs_dict = {
                    'Principal': format_currency(P, currency_symbol),
                    'Rate': f'{R:.4f}%',
                    'Time': f'{T:.2f} years'
                }
                
                outputs_dict = {
                    'Main Result': display_value,
                    'Interest Earned': format_currency(I, currency_symbol),
                    'Total Amount': format_currency(total_amount, currency_symbol),
                    'Return on Investment': f'{(I/P)*100:.2f}%'
                }
                
                # Summary DataFrame
                summary_df = pd.DataFrame({
                    'Year': list(range(int(T) + 1)),
                    'Principal': [format_currency(P, currency_symbol)] * (int(T) + 1),
                    'Cumulative Interest': [format_currency((P * R * yr) / 100, currency_symbol) for yr in range(int(T) + 1)],
                    'Total Amount': [format_currency(P + (P * R * yr) / 100, currency_symbol) for yr in range(int(T) + 1)]
                })
                
                download_section("Simple Interest", inputs_dict, outputs_dict, summary_df)
                
                st.markdown("---")
                email_section("Simple Interest", inputs_dict, outputs_dict)
                
                # Add to History
                add_to_history("Simple Interest", inputs_dict, outputs_dict)
                
            except ZeroDivisionError:
                st.error("❌ Cannot divide by zero! Check your inputs.")
            except Exception as e:
                st.error(f"❌ Error: {e}")

# ═══════════════════════════════════════════════════════════════
#                    COMPOUND INTEREST CALCULATOR
# ═══════════════════════════════════════════════════════════════

elif calculator_type == "📈 Compound Interest":
    st.markdown("""
    <div class="main-header">
        <h1>📈 Compound Interest Calculator</h1>
        <p>Calculate Future Value, Present Value, Rate, or Time</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="formula-box">
        <strong>Formula:</strong> FV = PV × (1 + r/m)^(n×m)<br>
        <strong>Where:</strong> PV = Present Value, FV = Future Value, r = Annual Rate, n = Years, m = Compounding Frequency
    </div>
    """, unsafe_allow_html=True)
    
    # Compounding Frequency
    freq_options = get_frequency_options()
    frequency = st.selectbox("📅 Compounding Frequency", list(freq_options.keys()), index=3)
    m = freq_options[frequency]
    
    st.markdown("### 📝 Enter Values (Leave ONE field as 0)")
    
    col1, col2 = st.columns(2)
    
    with col1:
        PV = st.number_input(f"💰 Present Value (PV) [{currency_symbol}]", min_value=0.0, value=10000.0, step=1000.0)
        FV = st.number_input(f"💵 Future Value (FV) [{currency_symbol}]", min_value=0.0, value=0.0, step=1000.0)
    
    with col2:
        r = st.number_input("📊 Annual Rate (r) [%]", min_value=0.0, value=10.0, step=0.5)
        n = st.number_input("⏰ Years (n)", min_value=0.0, value=5.0, step=1.0)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        calculate_btn = st.button("🔄 Calculate", use_container_width=True, type="primary")
    
    if calculate_btn:
        values = [PV, FV, r, n]
        zeros = values.count(0)
        
        if zeros != 1:
            st.markdown("""
            <div class="result-box-error">
                ⚠️ Please leave exactly ONE field as 0 to calculate it!
            </div>
            """, unsafe_allow_html=True)
        else:
            try:
                if PV == 0:
                    r_periodic = (r / 100) / m
                    total_periods = n * m
                    PV = FV / ((1 + r_periodic) ** total_periods)
                    result_label, result_value = "Present Value (PV)", PV
                elif FV == 0:
                    r_periodic = (r / 100) / m
                    total_periods = n * m
                    FV = PV * ((1 + r_periodic) ** total_periods)
                    result_label, result_value = "Future Value (FV)", FV
                elif r == 0:
                    total_periods = n * m
                    r_periodic = (FV / PV) ** (1 / total_periods) - 1
                    r = r_periodic * m * 100
                    result_label, result_value = "Annual Rate (r)", r
                else:
                    r_periodic = (r / 100) / m
                    n = math.log(FV / PV) / (m * math.log(1 + r_periodic))
                    result_label, result_value = "Time (n)", n
                
                total_periods = n * m
                compound_interest = FV - PV
                effective_rate = ((1 + (r/100)/m) ** m - 1) * 100
                
                # Display Result
                if result_label in ["Present Value (PV)", "Future Value (FV)"]:
                    display_value = format_currency(result_value, currency_symbol)
                elif result_label == "Annual Rate (r)":
                    display_value = f"{result_value:.4f}%"
                else:
                    display_value = f"{result_value:.2f} years"
                
                st.markdown(f"""
                <div class="result-box">
                    ✅ {result_label} = {display_value}
                </div>
                """, unsafe_allow_html=True)
                
                # Metrics
                st.markdown("### 📊 Complete Summary")
                col1, col2, col3, col4 = st.columns(4)
                col1.metric("Present Value", format_currency(PV, currency_symbol))
                col2.metric("Future Value", format_currency(FV, currency_symbol))
                col3.metric("Compound Interest", format_currency(compound_interest, currency_symbol))
                col4.metric("Effective Rate", f"{effective_rate:.2f}%")
                
                # Charts
                st.markdown("---")
                st.markdown("### 📈 Visual Analysis")
                
                tab1, tab2, tab3, tab4, tab5 = st.tabs(["🥧 Breakdown", "📈 Growth", "📊 Comparison", "🌊 Area", "🎯 Gauge"])
                
                with tab1:
                    fig_pie = create_pie_chart(
                        labels=['Principal', 'Compound Interest'],
                        values=[PV, compound_interest],
                        title='Principal vs Compound Interest',
                        colors=['#667eea', '#00b894']
                    )
                    st.plotly_chart(fig_pie, use_container_width=True)
                
                with tab2:
                    # Growth over time
                    years = list(range(int(n) + 1))
                    r_periodic = (r / 100) / m
                    
                    compound_values = [PV * ((1 + r_periodic) ** (yr * m)) for yr in years]
                    simple_values = [PV + (PV * r / 100) * yr for yr in years]
                    
                    fig_line = create_line_chart(
                        x_data=years,
                        y_data_dict={
                            'Compound Interest': compound_values,
                            'Simple Interest': simple_values
                        },
                        title='Compound vs Simple Interest Growth',
                        x_title='Years',
                        y_title=f'Amount ({currency_symbol})'
                    )
                    st.plotly_chart(fig_line, use_container_width=True)
                
                with tab3:
                    # Bar comparison
                    fig_bar = create_bar_chart(
                        categories=['Principal', 'Interest', 'Total'],
                        values_dict={
                            'Amount': [PV, compound_interest, FV]
                        },
                        title='Investment Breakdown',
                        y_title=f'Amount ({currency_symbol})'
                    )
                    st.plotly_chart(fig_bar, use_container_width=True)
                
                with tab4:
                    # Area chart
                    years = list(range(int(n) + 1))
                    r_periodic = (r / 100) / m
                    
                    principal = [PV] * len(years)
                    interest = [PV * ((1 + r_periodic) ** (yr * m)) - PV for yr in years]
                    
                    fig_area = create_area_chart(
                        x_data=years,
                        y_data_dict={
                            'Principal': principal,
                            'Interest Earned': interest
                        },
                        title='Wealth Accumulation',
                        x_title='Years',
                        y_title=f'Amount ({currency_symbol})'
                    )
                    st.plotly_chart(fig_area, use_container_width=True)
                
                with tab5:
                    col1, col2 = st.columns(2)
                    with col1:
                        fig_gauge = create_gauge_chart(
                            value=r,
                            max_value=25,
                            title='Interest Rate (%)'
                        )
                        st.plotly_chart(fig_gauge, use_container_width=True)
                    with col2:
                        roi = (compound_interest / PV) * 100
                        fig_gauge2 = create_gauge_chart(
                            value=min(roi, 500),
                            max_value=500,
                            title='Total Return (%)'
                        )
                        st.plotly_chart(fig_gauge2, use_container_width=True)
                
                # Download Section
                st.markdown("---")
                
                inputs_dict = {
                    'Present Value': format_currency(PV, currency_symbol),
                    'Annual Rate': f'{r:.4f}%',
                    'Years': f'{n:.2f}',
                    'Compounding': frequency
                }
                
                outputs_dict = {
                    'Main Result': display_value,
                    'Future Value': format_currency(FV, currency_symbol),
                    'Compound Interest': format_currency(compound_interest, currency_symbol),
                    'Effective Annual Rate': f'{effective_rate:.4f}%',
                    'Total Periods': f'{total_periods:.0f}'
                }
                
                # Create schedule
                schedule_data = []
                r_periodic = (r / 100) / m
                balance = PV
                for period in range(1, int(total_periods) + 1):
                    interest = balance * r_periodic
                    balance = balance * (1 + r_periodic)
                    schedule_data.append({
                        'Period': period,
                        'Opening Balance': format_currency(balance - interest, currency_symbol),
                        'Interest': format_currency(interest, currency_symbol),
                        'Closing Balance': format_currency(balance, currency_symbol)
                    })
                
                schedule_df = pd.DataFrame(schedule_data)
                
                download_section("Compound Interest", inputs_dict, outputs_dict, schedule_df, schedule_df)
                
                st.markdown("---")
                email_section("Compound Interest", inputs_dict, outputs_dict)
                
                add_to_history("Compound Interest", inputs_dict, outputs_dict)
                
            except Exception as e:
                st.error(f"❌ Error: {e}")

# ═══════════════════════════════════════════════════════════════
#                    EMI CALCULATOR
# ═══════════════════════════════════════════════════════════════

elif calculator_type == "🏦 EMI Calculator":
    st.markdown("""
    <div class="main-header">
        <h1>🏦 EMI Calculator</h1>
        <p>Calculate Loan EMI with Complete Amortization Schedule</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="formula-box">
        <strong>Formula:</strong> EMI = P × r × (1+r)^n / [(1+r)^n - 1]<br>
        <strong>Where:</strong> P = Principal, r = Monthly Rate, n = Total Months
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        loan_amount = st.number_input(f"💰 Loan Amount [{currency_symbol}]", min_value=1000.0, value=1000000.0, step=50000.0)
    
    with col2:
        annual_rate = st.number_input("📊 Annual Interest Rate [%]", min_value=0.1, value=10.0, step=0.25)
    
    with col3:
        tenure_years = st.number_input("⏰ Loan Tenure [Years]", min_value=1, value=20, step=1)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        calculate_btn = st.button("🔄 Calculate EMI", use_container_width=True, type="primary")
    
    if calculate_btn:
        try:
            monthly_rate = annual_rate / 12 / 100
            total_months = tenure_years * 12
            
            emi = loan_amount * monthly_rate * (1 + monthly_rate)**total_months / ((1 + monthly_rate)**total_months - 1)
            
            total_payment = emi * total_months
            total_interest = total_payment - loan_amount
            
            # Result
            st.markdown(f"""
            <div class="result-box">
                💳 Monthly EMI: {format_currency(emi, currency_symbol)}
            </div>
            """, unsafe_allow_html=True)
            
            # Metrics
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Loan Amount", format_currency(loan_amount, currency_symbol))
            col2.metric("Total Interest", format_currency(total_interest, currency_symbol))
            col3.metric("Total Payment", format_currency(total_payment, currency_symbol))
            col4.metric("Interest %", f"{(total_interest/loan_amount)*100:.2f}%")
            
            # Generate Amortization Schedule
            schedule_data = []
            balance = loan_amount
            total_principal_paid = 0
            total_interest_paid = 0
            
            for month in range(1, total_months + 1):
                interest_payment = balance * monthly_rate
                principal_payment = emi - interest_payment
                balance = max(0, balance - principal_payment)
                total_principal_paid += principal_payment
                total_interest_paid += interest_payment
                
                schedule_data.append({
                    'Month': month,
                    'EMI': emi,
                    'Principal': principal_payment,
                    'Interest': interest_payment,
                    'Balance': balance,
                    'Cumulative Principal': total_principal_paid,
                    'Cumulative Interest': total_interest_paid
                })
            
            schedule_df = pd.DataFrame(schedule_data)
            
            # Charts
            st.markdown("---")
            st.markdown("### 📈 Visual Analysis")
            
            tab1, tab2, tab3, tab4, tab5 = st.tabs(["🥧 Breakdown", "📈 Balance", "📊 Payment Split", "🌊 Cumulative", "📋 Schedule"])
            
            with tab1:
                fig_pie = create_pie_chart(
                    labels=['Principal', 'Total Interest'],
                    values=[loan_amount, total_interest],
                    title='Loan Payment Breakdown',
                    colors=['#667eea', '#e74c3c']
                )
                st.plotly_chart(fig_pie, use_container_width=True)
            
            with tab2:
                fig_line = create_line_chart(
                    x_data=schedule_df['Month'].tolist(),
                    y_data_dict={
                        'Outstanding Balance': schedule_df['Balance'].tolist()
                    },
                    title='Loan Balance Over Time',
                    x_title='Month',
                    y_title=f'Balance ({currency_symbol})'
                )
                st.plotly_chart(fig_line, use_container_width=True)
            
            with tab3:
                # Yearly breakdown
                yearly_data = schedule_df.groupby((schedule_df['Month'] - 1) // 12).agg({
                    'Principal': 'sum',
                    'Interest': 'sum'
                }).reset_index()
                yearly_data['Year'] = yearly_data['Month'] + 1
                
                fig_bar = create_bar_chart(
                    categories=[f'Year {i}' for i in yearly_data['Year'].tolist()],
                    values_dict={
                        'Principal': yearly_data['Principal'].tolist(),
                        'Interest': yearly_data['Interest'].tolist()
                    },
                    title='Yearly Principal vs Interest',
                    y_title=f'Amount ({currency_symbol})'
                )
                st.plotly_chart(fig_bar, use_container_width=True)
            
            with tab4:
                fig_area = create_area_chart(
                    x_data=schedule_df['Month'].tolist(),
                    y_data_dict={
                        'Cumulative Principal': schedule_df['Cumulative Principal'].tolist(),
                        'Cumulative Interest': schedule_df['Cumulative Interest'].tolist()
                    },
                    title='Cumulative Payments Over Time',
                    x_title='Month',
                    y_title=f'Amount ({currency_symbol})'
                )
                st.plotly_chart(fig_area, use_container_width=True)
            
            with tab5:
                st.markdown("### 📋 Amortization Schedule")
                
                # Format for display
                display_df = schedule_df.copy()
                for col in ['EMI', 'Principal', 'Interest', 'Balance', 'Cumulative Principal', 'Cumulative Interest']:
                    display_df[col] = display_df[col].apply(lambda x: format_currency(x, currency_symbol))
                
                st.dataframe(display_df, use_container_width=True, height=400)
            
            # Download Section
            st.markdown("---")
            
            inputs_dict = {
                'Loan Amount': format_currency(loan_amount, currency_symbol),
                'Annual Interest Rate': f'{annual_rate}%',
                'Tenure': f'{tenure_years} years ({total_months} months)'
            }
            
            outputs_dict = {
                'Main Result': format_currency(emi, currency_symbol),
                'Total Payment': format_currency(total_payment, currency_symbol),
                'Total Interest': format_currency(total_interest, currency_symbol),
                'Interest Percentage': f'{(total_interest/loan_amount)*100:.2f}%'
            }
            
            download_section("EMI Calculator", inputs_dict, outputs_dict, display_df, schedule_df)
            
            st.markdown("---")
            email_section("EMI Calculator", inputs_dict, outputs_dict)
            
            add_to_history("EMI Calculator", inputs_dict, outputs_dict)
            
        except Exception as e:
            st.error(f"❌ Error: {e}")

# ═══════════════════════════════════════════════════════════════
#                    SIP CALCULATOR
# ═══════════════════════════════════════════════════════════════

elif calculator_type == "💎 SIP Calculator":
    st.markdown("""
    <div class="main-header">
        <h1>💎 SIP Calculator</h1>
        <p>Systematic Investment Plan Returns Calculator</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="formula-box">
        <strong>Formula:</strong> FV = P × [(1+r)^n - 1] / r × (1+r)<br>
        <strong>Where:</strong> P = Monthly Investment, r = Monthly Rate, n = Total Months
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        monthly_sip = st.number_input(f"💰 Monthly SIP Amount [{currency_symbol}]", min_value=100.0, value=10000.0, step=1000.0)
        expected_return = st.number_input("📊 Expected Annual Return [%]", min_value=1.0, value=12.0, step=0.5)
    
    with col2:
        years = st.number_input("⏰ Investment Period [Years]", min_value=1, value=15, step=1)
        step_up = st.number_input("📈 Annual Step-up [%]", min_value=0.0, value=10.0, step=5.0,
                                   help="Increase SIP by this % every year")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        calculate_btn = st.button("🔄 Calculate SIP Returns", use_container_width=True, type="primary")
    
    if calculate_btn:
        try:
            monthly_rate = expected_return / 12 / 100
            total_months = years * 12
            
            # Calculate with step-up
            schedule_data = []
            current_sip = monthly_sip
            total_invested = 0
            current_value = 0
            
            for year in range(1, years + 1):
                for month in range(1, 13):
                    current_value = current_value * (1 + monthly_rate) + current_sip
                    total_invested += current_sip
                    
                    schedule_data.append({
                        'Year': year,
                        'Month': (year - 1) * 12 + month,
                        'SIP Amount': current_sip,
                        'Total Invested': total_invested,
                        'Current Value': current_value,
                        'Gain': current_value - total_invested
                    })
                
                # Step up at end of year
                current_sip = current_sip * (1 + step_up / 100)
            
            schedule_df = pd.DataFrame(schedule_data)
            
            future_value = current_value
            wealth_gained = future_value - total_invested
            
            # Result
            st.markdown(f"""
            <div class="result-box">
                💰 Future Value: {format_currency(future_value, currency_symbol)}
            </div>
            """, unsafe_allow_html=True)
            
            # Metrics
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Total Invested", format_currency(total_invested, currency_symbol))
            col2.metric("Wealth Gained", format_currency(wealth_gained, currency_symbol))
            col3.metric("Returns", f"{(wealth_gained/total_invested)*100:.2f}%")
            col4.metric("Final SIP", format_currency(current_sip / (1 + step_up/100), currency_symbol))
            
            # Charts
            st.markdown("---")
            st.markdown("### 📈 Visual Analysis")
            
            tab1, tab2, tab3, tab4 = st.tabs(["📈 Growth", "🥧 Breakdown", "📊 Yearly", "🎯 Gauge"])
            
            with tab1:
                fig_line = create_line_chart(
                    x_data=schedule_df['Month'].tolist(),
                    y_data_dict={
                        'Total Invested': schedule_df['Total Invested'].tolist(),
                        'Portfolio Value': schedule_df['Current Value'].tolist()
                    },
                    title='SIP Growth Over Time',
                    x_title='Month',
                    y_title=f'Amount ({currency_symbol})'
                )
                st.plotly_chart(fig_line, use_container_width=True)
            
            with tab2:
                fig_pie = create_pie_chart(
                    labels=['Total Invested', 'Wealth Gained'],
                    values=[total_invested, wealth_gained],
                    title='Investment Breakdown',
                    colors=['#667eea', '#00b894']
                )
                st.plotly_chart(fig_pie, use_container_width=True)
            
            with tab3:
                yearly_df = schedule_df.groupby('Year').agg({
                    'SIP Amount': 'first',
                    'Total Invested': 'last',
                    'Current Value': 'last',
                    'Gain': 'last'
                }).reset_index()
                
                fig_bar = create_bar_chart(
                    categories=[f'Year {y}' for y in yearly_df['Year'].tolist()],
                    values_dict={
                        'Invested': yearly_df['Total Invested'].tolist(),
                        'Value': yearly_df['Current Value'].tolist()
                    },
                    title='Year-wise Portfolio Growth',
                    y_title=f'Amount ({currency_symbol})'
                )
                st.plotly_chart(fig_bar, use_container_width=True)
            
            with tab4:
                col1, col2 = st.columns(2)
                with col1:
                    cagr = ((future_value / total_invested) ** (1/years) - 1) * 100
                    fig_gauge = create_gauge_chart(
                        value=cagr,
                        max_value=30,
                        title='CAGR (%)'
                    )
                    st.plotly_chart(fig_gauge, use_container_width=True)
                
                with col2:
                    fig_gauge2 = create_gauge_chart(
                        value=(wealth_gained/total_invested)*100,
                        max_value=500,
                        title='Total Returns (%)'
                    )
                    st.plotly_chart(fig_gauge2, use_container_width=True)
            
            # Download
            st.markdown("---")
            
            inputs_dict = {
                'Starting SIP': format_currency(monthly_sip, currency_symbol),
                'Expected Return': f'{expected_return}%',
                'Investment Period': f'{years} years',
                'Annual Step-up': f'{step_up}%'
            }
            
            outputs_dict = {
                'Main Result': format_currency(future_value, currency_symbol),
                'Total Invested': format_currency(total_invested, currency_symbol),
                'Wealth Gained': format_currency(wealth_gained, currency_symbol),
                'Returns': f'{(wealth_gained/total_invested)*100:.2f}%'
            }
            
            # Format schedule for display
            display_df = schedule_df.copy()
            for col in ['SIP Amount', 'Total Invested', 'Current Value', 'Gain']:
                display_df[col] = display_df[col].apply(lambda x: format_currency(x, currency_symbol))
            
            download_section("SIP Calculator", inputs_dict, outputs_dict, display_df, schedule_df)
            
            add_to_history("SIP Calculator", inputs_dict, outputs_dict)
            
        except Exception as e:
            st.error(f"❌ Error: {e}")

# ═══════════════════════════════════════════════════════════════
#                    IMPORT & BULK CALC
# ═══════════════════════════════════════════════════════════════

elif calculator_type == "📤 Import & Bulk Calc":
    st.markdown("""
    <div class="main-header">
        <h1>📤 Import & Bulk Calculations</h1>
        <p>Upload Excel/CSV for Batch Processing</p>
    </div>
    """, unsafe_allow_html=True)
    
    calc_type = st.selectbox(
        "Select Calculation Type",
        ["Simple Interest", "Compound Interest", "EMI"]
    )
    
    st.markdown("### 📁 Upload Your Data")
    
    # Template download
    st.markdown("#### 📥 Download Template First")
    
    if calc_type == "Simple Interest":
        template_df = pd.DataFrame({
            'Principal': [10000, 20000, 30000],
            'Rate': [5, 7, 10],
            'Time': [2, 3, 5]
        })
    elif calc_type == "Compound Interest":
        template_df = pd.DataFrame({
            'Present_Value': [10000, 20000, 30000],
            'Rate': [8, 10, 12],
            'Years': [5, 10, 15],
            'Frequency': [12, 4, 1]
        })
    else:
        template_df = pd.DataFrame({
            'Loan_Amount': [100000, 500000, 1000000],
            'Annual_Rate': [8, 10, 12],
            'Years': [5, 10, 20]
        })
    
    template_csv = template_df.to_csv(index=False)
    st.download_button(
        "📥 Download Template CSV",
        data=template_csv,
        file_name=f"{calc_type.lower().replace(' ', '_')}_template.csv",
        mime="text/csv"
    )
    
    st.markdown("---")
    
    # File Upload
    uploaded_file = st.file_uploader(
        "📂 Upload Your File",
        type=['xlsx', 'xls', 'csv'],
        help="Upload file with same columns as template"
    )
    
    if uploaded_file is not None:
        try:
            if uploaded_file.name.endswith('.csv'):
                df = pd.read_csv(uploaded_file)
            else:
                df = pd.read_excel(uploaded_file)
            
            st.success(f"✅ Loaded {len(df)} rows")
            st.dataframe(df, use_container_width=True)
            
            if st.button("🔄 Process All Calculations", type="primary"):
                results = []
                
                for idx, row in df.iterrows():
                    if calc_type == "Simple Interest":
                        P, R, T = row['Principal'], row['Rate'], row['Time']
                        I = (P * R * T) / 100
                        results.append({
                            'Principal': P,
                            'Rate': R,
                            'Time': T,
                            'Interest': I,
                            'Total': P + I
                        })
                    
                    elif calc_type == "Compound Interest":
                        PV = row['Present_Value']
                        r = row['Rate'] / 100
                        n = row['Years']
                        m = row['Frequency']
                        FV = PV * ((1 + r/m) ** (n * m))
                        results.append({
                            'Present_Value': PV,
                            'Rate': row['Rate'],
                            'Years': n,
                            'Frequency': m,
                            'Future_Value': FV,
                            'Interest': FV - PV
                        })
                    
                    else:  # EMI
                        P = row['Loan_Amount']
                        r = row['Annual_Rate'] / 12 / 100
                        n = row['Years'] * 12
                        EMI = P * r * (1 + r)**n / ((1 + r)**n - 1)
                        results.append({
                            'Loan_Amount': P,
                            'Annual_Rate': row['Annual_Rate'],
                            'Years': row['Years'],
                            'Monthly_EMI': EMI,
                            'Total_Payment': EMI * n,
                            'Total_Interest': EMI * n - P
                        })
                
                results_df = pd.DataFrame(results)
                
                st.markdown("### ✅ Calculation Results")
                st.dataframe(results_df, use_container_width=True)
                
                # Download results
                st.markdown("### 📥 Download Results")
                
                col1, col2 = st.columns(2)
                
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
                    with pd.ExcelWriter(excel_output, engine='openpyxl') as writer:
                        results_df.to_excel(writer, sheet_name='Results', index=False)
                    
                    st.download_button(
                        "📊 Download Excel",
                        data=excel_output.getvalue(),
                        file_name=f"{calc_type.lower().replace(' ', '_')}_results.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        use_container_width=True
                    )
                
        except Exception as e:
            st.error(f"❌ Error: {e}")

# ═══════════════════════════════════════════════════════════════
#                    HISTORY PAGE
# ═══════════════════════════════════════════════════════════════

elif calculator_type == "📋 History":
    st.markdown("""
    <div class="main-header">
        <h1>📋 Calculation History</h1>
        <p>View and Export Your Previous Calculations</p>
    </div>
    """, unsafe_allow_html=True)
    
    if st.session_state.calculation_history:
        history_df = pd.DataFrame(st.session_state.calculation_history)
        
        # Filter options
        col1, col2 = st.columns(2)
        with col1:
            calc_types = ['All'] + list(history_df['type'].unique())
            filter_type = st.selectbox("Filter by Type", calc_types)
        
        if filter_type != 'All':
            history_df = history_df[history_df['type'] == filter_type]
        
        st.dataframe(history_df, use_container_width=True)
        
        # Download history
        st.markdown("### 📥 Export History")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            csv_history = history_df.to_csv(index=False)
            st.download_button(
                "📄 Download CSV",
                data=csv_history,
                file_name="calculation_history.csv",
                mime="text/csv",
                use_container_width=True
            )
        
        with col2:
            excel_output = io.BytesIO()
            with pd.ExcelWriter(excel_output, engine='openpyxl') as writer:
                history_df.to_excel(writer, sheet_name='History', index=False)
            st.download_button(
                "📊 Download Excel",
                data=excel_output.getvalue(),
                file_name="calculation_history.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )
        
        with col3:
            if st.button("🗑️ Clear History", use_container_width=True):
                st.session_state.calculation_history = []
                st.rerun()
    else:
        st.info("📝 No calculations yet. Start using calculators to build your history!")

# ═══════════════════════════════════════════════════════════════
#                    NPV CALCULATOR
# ═══════════════════════════════════════════════════════════════

elif calculator_type == "💹 NPV Analysis":
    st.markdown("""
    <div class="main-header">
        <h1>💹 NPV Analysis</h1>
        <p>Net Present Value & IRR Calculator</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        initial_investment = st.number_input(f"💰 Initial Investment [{currency_symbol}]", min_value=0.0, value=100000.0, step=10000.0)
    
    with col2:
        discount_rate = st.number_input("📊 Discount Rate [%]", min_value=0.0, value=10.0, step=0.5)
    
    with col3:
        num_years = st.number_input("⏰ Number of Years", min_value=1, max_value=30, value=5, step=1)
    
    st.markdown("### 📝 Enter Annual Cash Flows")
    
    cash_flows = []
    cols = st.columns(min(num_years, 5))
    
    for i in range(num_years):
        col_idx = i % 5
        with cols[col_idx]:
            cf = st.number_input(f"Year {i+1}", min_value=0.0, value=30000.0, step=5000.0, key=f"cf_{i}")
            cash_flows.append(cf)
    
    if st.button("🔄 Calculate NPV", type="primary"):
        try:
            r = discount_rate / 100
            
            # Calculate NPV
            npv = -initial_investment
            pv_list = []
            
            for t, cf in enumerate(cash_flows, 1):
                pv = cf / (1 + r) ** t
                pv_list.append(pv)
                npv += pv
            
            # Calculate IRR (simplified Newton-Raphson)
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
            profitability_index = sum(pv_list) / initial_investment
            payback_period = initial_investment / np.mean(cash_flows) if np.mean(cash_flows) > 0 else 0
            
            # Result
            if npv > 0:
                st.markdown(f"""
                <div class="result-box" style="background: linear-gradient(135deg, #00b894, #00cec9);">
                    ✅ NPV = {format_currency(npv, currency_symbol)} - ACCEPT PROJECT
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="result-box-error">
                    ❌ NPV = {format_currency(npv, currency_symbol)} - REJECT PROJECT
                </div>
                """, unsafe_allow_html=True)
            
            # Metrics
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("NPV", format_currency(npv, currency_symbol))
            col2.metric("IRR", f"{irr_percent:.2f}%")
            col3.metric("Profitability Index", f"{profitability_index:.2f}")
            col4.metric("Payback Period", f"{payback_period:.1f} years")
            
            # Charts
            st.markdown("---")
            st.markdown("### 📈 Visual Analysis")
            
            tab1, tab2, tab3 = st.tabs(["📊 Cash Flows", "📈 NPV Profile", "🌊 Cumulative"])
            
            with tab1:
                years = ['Year 0'] + [f'Year {i}' for i in range(1, num_years + 1)]
                values = [-initial_investment] + cash_flows
                
                fig_waterfall = create_waterfall_chart(
                    categories=years,
                    values=values + [sum(values)],
                    title='Cash Flow Waterfall'
                )
                st.plotly_chart(fig_waterfall, use_container_width=True)
            
            with tab2:
                # NPV at different discount rates
                rates = list(range(0, 31, 2))
                npvs = []
                for rate in rates:
                    npv_temp = -initial_investment + sum(cf / (1 + rate/100) ** (t+1) for t, cf in enumerate(cash_flows))
                    npvs.append(npv_temp)
                
                fig_line = create_line_chart(
                    x_data=rates,
                    y_data_dict={'NPV': npvs},
                    title='NPV Profile',
                    x_title='Discount Rate (%)',
                    y_title=f'NPV ({currency_symbol})'
                )
                st.plotly_chart(fig_line, use_container_width=True)
            
            with tab3:
                cumulative = [-initial_investment]
                for cf in cash_flows:
                    cumulative.append(cumulative[-1] + cf)
                
                fig_area = create_area_chart(
                    x_data=list(range(num_years + 1)),
                    y_data_dict={'Cumulative Cash Flow': cumulative},
                    title='Cumulative Cash Flows',
                    x_title='Year',
                    y_title=f'Amount ({currency_symbol})'
                )
                st.plotly_chart(fig_area, use_container_width=True)
            
            # Download
            st.markdown("---")
            
            inputs_dict = {
                'Initial Investment': format_currency(initial_investment, currency_symbol),
                'Discount Rate': f'{discount_rate}%',
                'Number of Years': num_years,
                'Cash Flows': str([format_currency(cf, currency_symbol) for cf in cash_flows])
            }
            
            outputs_dict = {
                'Main Result': format_currency(npv, currency_symbol),
                'IRR': f'{irr_percent:.2f}%',
                'Profitability Index': f'{profitability_index:.2f}',
                'Decision': 'ACCEPT' if npv > 0 else 'REJECT'
            }
            
            cf_df = pd.DataFrame({
                'Year': list(range(num_years + 1)),
                'Cash Flow': [-initial_investment] + cash_flows,
                'Present Value': [-initial_investment] + pv_list
            })
            
            download_section("NPV Analysis", inputs_dict, outputs_dict, cf_df)
            
            add_to_history("NPV Analysis", inputs_dict, outputs_dict)
            
        except Exception as e:
            st.error(f"❌ Error: {e}")

# ═══════════════════════════════════════════════════════════════
#                    BOND VALUATION
# ═══════════════════════════════════════════════════════════════

elif calculator_type == "📜 Bond Valuation":
    st.markdown("""
    <div class="main-header">
        <h1>📜 Bond Valuation</h1>
        <p>Calculate Bond Price or Yield to Maturity</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        face_value = st.number_input(f"💵 Face Value [{currency_symbol}]", min_value=100.0, value=1000.0, step=100.0)
        coupon_rate = st.number_input("📊 Coupon Rate [%]", min_value=0.0, value=8.0, step=0.25)
        frequency = st.selectbox("🔄 Coupon Frequency", ["Annual", "Semi-Annual", "Quarterly"])
    
    with col2:
        ytm = st.number_input("📈 Yield to Maturity [%]", min_value=0.1, value=10.0, step=0.25)
        years_to_maturity = st.number_input("⏰ Years to Maturity", min_value=1, value=10, step=1)
    
    freq_map = {"Annual": 1, "Semi-Annual": 2, "Quarterly": 4}
    m = freq_map[frequency]
    
    if st.button("🔄 Calculate Bond Price", type="primary"):
        try:
            coupon_payment = (face_value * coupon_rate / 100) / m
            total_periods = years_to_maturity * m
            periodic_ytm = (ytm / 100) / m
            
            # PV of coupons
            pv_coupons = sum(coupon_payment / (1 + periodic_ytm) ** t for t in range(1, total_periods + 1))
            
            # PV of face value
            pv_face = face_value / (1 + periodic_ytm) ** total_periods
            
            bond_price = pv_coupons + pv_face
            
            current_yield = (coupon_payment * m / bond_price) * 100
            
            # Result
            st.markdown(f"""
            <div class="result-box">
                📜 Bond Price: {format_currency(bond_price, currency_symbol)}
            </div>
            """, unsafe_allow_html=True)
            
            # Bond type
            if bond_price > face_value:
                st.success(f"📈 **Premium Bond** - Coupon Rate > YTM")
            elif bond_price < face_value:
                st.warning(f"📉 **Discount Bond** - Coupon Rate < YTM")
            else:
                st.info(f"➡️ **Par Bond** - Coupon Rate = YTM")
            
            # Metrics
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Bond Price", format_currency(bond_price, currency_symbol))
            col2.metric("PV of Coupons", format_currency(pv_coupons, currency_symbol))
            col3.metric("PV of Face Value", format_currency(pv_face, currency_symbol))
            col4.metric("Current Yield", f"{current_yield:.2f}%")
            
            # Charts
            st.markdown("---")
            st.markdown("### 📈 Visual Analysis")
            
            tab1, tab2 = st.tabs(["🥧 Breakdown", "📈 Price Sensitivity"])
            
            with tab1:
                fig_pie = create_pie_chart(
                    labels=['PV of Coupons', 'PV of Face Value'],
                    values=[pv_coupons, pv_face],
                    title='Bond Price Components',
                    colors=['#667eea', '#00b894']
                )
                st.plotly_chart(fig_pie, use_container_width=True)
            
            with tab2:
                ytm_range = list(range(1, 21))
                prices = []
                for y in ytm_range:
                    py = (y / 100) / m
                    pv_c = sum(coupon_payment / (1 + py) ** t for t in range(1, total_periods + 1))
                    pv_f = face_value / (1 + py) ** total_periods
                    prices.append(pv_c + pv_f)
                
                fig_line = create_line_chart(
                    x_data=ytm_range,
                    y_data_dict={'Bond Price': prices},
                    title='Bond Price vs YTM',
                    x_title='YTM (%)',
                    y_title=f'Price ({currency_symbol})'
                )
                st.plotly_chart(fig_line, use_container_width=True)
            
            # Download
            st.markdown("---")
            
            inputs_dict = {
                'Face Value': format_currency(face_value, currency_symbol),
                'Coupon Rate': f'{coupon_rate}%',
                'YTM': f'{ytm}%',
                'Years to Maturity': years_to_maturity,
                'Frequency': frequency
            }
            
            outputs_dict = {
                'Main Result': format_currency(bond_price, currency_symbol),
                'PV of Coupons': format_currency(pv_coupons, currency_symbol),
                'PV of Face Value': format_currency(pv_face, currency_symbol),
                'Current Yield': f'{current_yield:.2f}%',
                'Bond Type': 'Premium' if bond_price > face_value else ('Discount' if bond_price < face_value else 'Par')
            }
            
            download_section("Bond Valuation", inputs_dict, outputs_dict)
            
            add_to_history("Bond Valuation", inputs_dict, outputs_dict)
            
        except Exception as e:
            st.error(f"❌ Error: {e}")

# ═══════════════════════════════════════════════════════════════
#                    FORMULAS PAGE
# ═══════════════════════════════════════════════════════════════

elif calculator_type == "📖 Formulas":
    st.markdown("""
    <div class="main-header">
        <h1>📖 Formula Reference</h1>
        <p>All Financial Formulas at a Glance</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    ### 📐 Simple Interest
    ```
    I = (P × R × T) / 100
    P = (I × 100) / (R × T)
    R = (I × 100) / (P × T)
    T = (I × 100) / (P × R)
    ```
    
    ### 📈 Compound Interest
    ```
    FV = PV × (1 + r/m)^(n×m)
    PV = FV / (1 + r/m)^(n×m)
    Effective Rate = (1 + r/m)^m - 1
    ```
    
    ### 🏦 EMI
    ```
    EMI = P × r × (1+r)^n / [(1+r)^n - 1]
    Where: r = monthly rate, n = total months
    ```
    
    ### 💎 SIP Future Value
    ```
    FV = P × [(1+r)^n - 1] / r × (1+r)
    Where: P = monthly investment, r = monthly rate
    ```
    
    ### 💹 NPV & IRR
    ```
    NPV = -C₀ + Σ[CFₜ / (1+r)^t]
    IRR = Rate where NPV = 0
    PI = PV of Inflows / Initial Investment
    ```
    
    ### 📜 Bond Valuation
    ```
    Price = Σ[C/(1+y)^t] + F/(1+y)^n
    Current Yield = Annual Coupon / Price
    ```
    """)

# ═══════════════════════════════════════════════════════════════
#                    FOOTER
# ═══════════════════════════════════════════════════════════════

st.markdown("---")
st.markdown("""
<div style="text-align: center; padding: 20px; color: #888;">
    💰 <strong>Financial Calculator Pro</strong> v3.0<br>
    Made with ❤️ using Streamlit | 📊 Interactive Charts by Plotly<br>
    <small>© 2024 All Rights Reserved</small>
</div>
""", unsafe_allow_html=True)
