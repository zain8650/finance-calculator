import streamlit as st
import pandas as pd
import numpy as np
import math
from datetime import datetime
import plotly.graph_objects as go
import json
import io

# PDF Generation
from fpdf import FPDF

# ═══════════════════════════════════════════════════════════════
#                    PAGE CONFIG
# ═══════════════════════════════════════════════════════════════

st.set_page_config(
    page_title="Financial Calculator Pro",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ═══════════════════════════════════════════════════════════════
#                    CSS STYLES
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
    
    .result-box-reject {
        background: linear-gradient(135deg, #e74c3c 0%, #c0392b 100%);
        padding: 30px;
        border-radius: 20px;
        color: white;
        text-align: center;
        font-size: 1.8rem;
        font-weight: bold;
        margin: 25px 0;
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
    
    .variable-box {
        background: linear-gradient(135deg, #e8f4f8 0%, #d1ecf1 100%);
        padding: 20px;
        border-radius: 15px;
        border: 2px solid #17a2b8;
        margin: 15px 0;
    }
    
    .download-box {
        background: linear-gradient(135deg, #d4edda 0%, #c3e6cb 100%);
        padding: 25px;
        border-radius: 15px;
        border: 2px solid #28a745;
        margin: 30px 0;
    }
    
    .download-box h4 {
        color: #28a745;
        margin-bottom: 15px;
        text-align: center;
    }
    
    .calc-card {
        background: white;
        padding: 20px;
        border-radius: 15px;
        border: 1px solid #e0e0e0;
        margin: 10px 0;
        box-shadow: 0 5px 15px rgba(0,0,0,0.08);
    }
    
    .tip-box {
        background: linear-gradient(135deg, #fff3cd 0%, #ffeeba 100%);
        padding: 15px;
        border-radius: 10px;
        border-left: 5px solid #ffc107;
        margin: 15px 0;
    }
</style>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════
#                    SESSION STATE
# ═══════════════════════════════════════════════════════════════

if 'calculation_history' not in st.session_state:
    st.session_state.calculation_history = []

# ═══════════════════════════════════════════════════════════════
#                    HELPER FUNCTIONS
# ═══════════════════════════════════════════════════════════════

def format_currency(value, symbol="$"):
    """Format value as currency"""
    if value is None or pd.isna(value):
        return "N/A"
    return f"{symbol}{value:,.2f}"

def format_percent(value):
    """Format value as percentage"""
    if value is None:
        return "N/A"
    return f"{value:.4f}%"

def is_empty_or_zero(value):
    """Check if value is empty, None, or zero"""
    if value is None:
        return True
    if isinstance(value, str) and value.strip() == "":
        return True
    try:
        return float(value) == 0
    except:
        return True

def get_float_value(value, default=0.0):
    """Safely convert to float"""
    if value is None or value == "":
        return 0.0
    try:
        return float(value)
    except:
        return default

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
#                    PDF GENERATOR
# ═══════════════════════════════════════════════════════════════

class PDFReport(FPDF):
    def __init__(self):
        super().__init__()
        self.set_auto_page_break(auto=True, margin=15)
    
    def header(self):
        self.set_font('Arial', 'B', 18)
        self.set_text_color(102, 126, 234)
        self.cell(0, 12, 'Financial Calculator Pro', 0, 1, 'C')
        self.set_font('Arial', 'I', 9)
        self.set_text_color(128, 128, 128)
        self.cell(0, 5, f'Report: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}', 0, 1, 'C')
        self.ln(8)
    
    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')

def generate_pdf_report(title, summary_dict, schedule_df=None):
    pdf = PDFReport()
    pdf.add_page()
    
    # Title
    pdf.set_font('Arial', 'B', 14)
    pdf.set_text_color(60, 60, 60)
    pdf.cell(0, 10, title, 0, 1, 'L')
    pdf.ln(5)
    
    # Summary
    pdf.set_font('Arial', 'B', 11)
    pdf.cell(0, 8, 'Calculation Summary:', 0, 1, 'L')
    pdf.set_font('Arial', '', 10)
    
    for key, value in summary_dict.items():
        pdf.cell(70, 7, str(key) + ':', 0, 0, 'L')
        pdf.cell(0, 7, str(value), 0, 1, 'L')
    
    # Schedule Table
    if schedule_df is not None and len(schedule_df) > 0:
        pdf.ln(10)
        pdf.set_font('Arial', 'B', 11)
        pdf.cell(0, 8, 'Detailed Schedule:', 0, 1, 'L')
        
        pdf.set_font('Arial', 'B', 8)
        pdf.set_fill_color(102, 126, 234)
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
#                    DOWNLOAD SECTION COMPONENT
# ═══════════════════════════════════════════════════════════════

def render_download_section(calc_name, summary_dict, schedule_df=None, currency_symbol="$"):
    """Render download section with all export options"""
    
    st.markdown("---")
    
    st.markdown("""
    <div class="download-box">
        <h4>📥 Download Your Results</h4>
        <p style="text-align: center; color: #155724;">Click any button below to download this calculation</p>
    </div>
    """, unsafe_allow_html=True)
    
    file_base = calc_name.lower().replace(" ", "_") + "_" + datetime.now().strftime("%Y%m%d_%H%M%S")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if schedule_df is not None and len(schedule_df) > 0:
            csv_data = schedule_df.to_csv(index=False)
        else:
            csv_data = pd.DataFrame(list(summary_dict.items()), columns=['Parameter', 'Value']).to_csv(index=False)
        
        st.download_button(
            label="📄 Download CSV",
            data=csv_data,
            file_name=f"{file_base}.csv",
            mime="text/csv",
            use_container_width=True
        )
    
    with col2:
        excel_data = generate_excel_report(summary_dict, schedule_df)
        st.download_button(
            label="📊 Download Excel",
            data=excel_data,
            file_name=f"{file_base}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )
    
    with col3:
        try:
            pdf_data = generate_pdf_report(calc_name, summary_dict, schedule_df)
            st.download_button(
                label="📕 Download PDF",
                data=pdf_data,
                file_name=f"{file_base}.pdf",
                mime="application/pdf",
                use_container_width=True
            )
        except:
            st.button("📕 PDF Error", disabled=True, use_container_width=True)
    
    with col4:
        json_data = json.dumps({
            "calculation_type": calc_name,
            "timestamp": datetime.now().isoformat(),
            "currency": currency_symbol,
            "summary": summary_dict,
            "schedule": schedule_df.to_dict('records') if schedule_df is not None else None
        }, indent=2, default=str)
        
        st.download_button(
            label="📋 Download JSON",
            data=json_data,
            file_name=f"{file_base}.json",
            mime="application/json",
            use_container_width=True
        )

# ═══════════════════════════════════════════════════════════════
#                    CHART FUNCTIONS
# ═══════════════════════════════════════════════════════════════

def create_pie_chart(labels, values, title):
    colors = ['#667eea', '#00b894', '#e74c3c', '#f39c12']
    fig = go.Figure(data=[go.Pie(
        labels=labels, values=values, hole=0.4,
        marker_colors=colors[:len(labels)],
        textinfo='label+percent'
    )])
    fig.update_layout(title=dict(text=title, font=dict(size=16)), height=400)
    return fig

def create_line_chart(x_data, y_data_dict, title, x_title, y_title):
    fig = go.Figure()
    colors = ['#667eea', '#00b894', '#e74c3c']
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

# ═══════════════════════════════════════════════════════════════
#                    SIDEBAR
# ═══════════════════════════════════════════════════════════════

with st.sidebar:
    st.markdown("""
    <div style="text-align: center; padding: 15px;">
        <h1 style="color: #667eea; margin: 0;">💰</h1>
        <h3 style="margin: 5px 0;">Financial Calculator</h3>
        <p style="color: #888; font-size: 0.8rem;">Smart Auto-Calculate</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    currency_symbol = st.selectbox("💵 Currency", ["$", "₹", "€", "£", "Rs", "PKR"])
    
    st.markdown("---")
    
    calculator_type = st.radio(
        "📊 Calculator",
        [
            "🏠 Home",
            "📐 Simple Interest",
            "📈 Compound Interest",
            "🏦 EMI Calculator",
            "💎 SIP Calculator",
            "💹 NPV Calculator",
            "📜 Bond Valuation",
            "📋 History",
            "📖 Formulas"
        ]
    )
    
    st.markdown("---")
    
    st.markdown("""
    <div class="tip-box">
        <strong>💡 How to Use:</strong><br>
        1. Enter known values<br>
        2. Leave ONE field as 0 or blank<br>
        3. Click Calculate<br>
        4. Download results!
    </div>
    """, unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════
#                    HOME PAGE
# ═══════════════════════════════════════════════════════════════

if calculator_type == "🏠 Home":
    st.markdown("""
    <div class="main-header">
        <h1>💰 Financial Calculator Pro</h1>
        <p>Smart Auto-Calculate Missing Values</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="tip-box">
        <h4>🎯 How It Works:</h4>
        <ul>
            <li><strong>Enter</strong> all values you know</li>
            <li><strong>Leave ONE field as 0</strong> (or blank) that you want to calculate</li>
            <li><strong>Click Calculate</strong> - the missing value will be computed automatically!</li>
            <li><strong>Download</strong> your results in CSV, Excel, PDF, or JSON</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("### 🧮 Available Calculators")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="calc-card">
            <h4>📐 Simple Interest</h4>
            <p>Find any one of: P, R, T, or I</p>
            <small>Formula: I = (P × R × T) / 100</small>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="calc-card">
            <h4>🏦 EMI Calculator</h4>
            <p>Calculate monthly EMI</p>
            <small>With complete amortization schedule</small>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="calc-card">
            <h4>📈 Compound Interest</h4>
            <p>Find any one of: PV, FV, r, or n</p>
            <small>Multiple compounding frequencies</small>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="calc-card">
            <h4>💎 SIP Calculator</h4>
            <p>Investment returns with step-up</p>
            <small>Year-wise wealth schedule</small>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="calc-card">
            <h4>💹 NPV Calculator</h4>
            <p>Net Present Value & IRR</p>
            <small>Cash flow analysis</small>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="calc-card">
            <h4>📜 Bond Valuation</h4>
            <p>Bond price calculation</p>
            <small>Coupon payment schedule</small>
        </div>
        """, unsafe_allow_html=True)
    
    st.info("👈 Select a calculator from the sidebar to get started!")

# ═══════════════════════════════════════════════════════════════
#                    SIMPLE INTEREST CALCULATOR
# ═══════════════════════════════════════════════════════════════

elif calculator_type == "📐 Simple Interest":
    st.markdown("""
    <div class="main-header">
        <h1>📐 Simple Interest Calculator</h1>
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
        💡 <strong>Enter 3 values, leave 1 as zero (0)</strong> - that value will be calculated!
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("### 📝 Enter Your Values")
    
    col1, col2 = st.columns(2)
    
    with col1:
        P = st.number_input(
            f"💰 Principal (P) [{currency_symbol}]",
            min_value=0.0, value=0.0, step=1000.0,
            help="Enter 0 if you want to calculate this"
        )
        R = st.number_input(
            "📊 Rate (R) [% per year]",
            min_value=0.0, value=0.0, step=0.5,
            help="Enter 0 if you want to calculate this"
        )
    
    with col2:
        T = st.number_input(
            "⏰ Time (T) [Years]",
            min_value=0.0, value=0.0, step=1.0,
            help="Enter 0 if you want to calculate this"
        )
        I = st.number_input(
            f"💵 Interest (I) [{currency_symbol}]",
            min_value=0.0, value=0.0, step=100.0,
            help="Enter 0 if you want to calculate this"
        )
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        calculate = st.button("🔄 Calculate Missing Value", use_container_width=True, type="primary")
    
    if calculate:
        # Count zeros (missing values)
        values = {'P': P, 'R': R, 'T': T, 'I': I}
        zeros = sum(1 for v in values.values() if v == 0)
        
        if zeros == 0:
            st.warning("⚠️ All values are filled! Leave ONE field as 0 to calculate it.")
        elif zeros > 1:
            st.error(f"❌ You left {zeros} fields as zero. Please fill at least 3 values and leave only 1 as zero.")
        else:
            try:
                # Find and calculate the missing value
                if P == 0:
                    if R == 0 or T == 0:
                        st.error("❌ Cannot calculate - Rate and Time cannot both be zero!")
                    else:
                        P = (I * 100) / (R * T)
                        calculated_field = "Principal (P)"
                        calculated_value = format_currency(P, currency_symbol)
                elif R == 0:
                    if P == 0 or T == 0:
                        st.error("❌ Cannot calculate - Principal and Time cannot both be zero!")
                    else:
                        R = (I * 100) / (P * T)
                        calculated_field = "Rate (R)"
                        calculated_value = f"{R:.4f}%"
                elif T == 0:
                    if P == 0 or R == 0:
                        st.error("❌ Cannot calculate - Principal and Rate cannot both be zero!")
                    else:
                        T = (I * 100) / (P * R)
                        calculated_field = "Time (T)"
                        calculated_value = f"{T:.2f} years"
                else:  # I == 0
                    I = (P * R * T) / 100
                    calculated_field = "Interest (I)"
                    calculated_value = format_currency(I, currency_symbol)
                
                total_amount = P + I
                yearly_interest = (P * R) / 100 if R > 0 else 0
                
                # Show Result
                st.markdown(f"""
                <div class="result-box">
                    ✅ Calculated: {calculated_field} = {calculated_value}
                </div>
                """, unsafe_allow_html=True)
                
                # Show all values
                st.markdown("### 📊 Complete Summary")
                
                col1, col2, col3, col4 = st.columns(4)
                col1.metric("Principal (P)", format_currency(P, currency_symbol))
                col2.metric("Rate (R)", f"{R:.2f}%")
                col3.metric("Time (T)", f"{T:.2f} years")
                col4.metric("Interest (I)", format_currency(I, currency_symbol))
                
                st.success(f"💰 **Total Amount (P + I):** {format_currency(total_amount, currency_symbol)}")
                
                # Year-wise Schedule
                st.markdown("---")
                st.markdown("### 📋 Year-wise Interest Schedule")
                
                schedule_data = []
                for year in range(1, int(T) + 1):
                    cumulative_interest = yearly_interest * year
                    schedule_data.append({
                        'Year': year,
                        'Opening Balance': round(P, 2),
                        'Interest This Year': round(yearly_interest, 2),
                        'Cumulative Interest': round(cumulative_interest, 2),
                        'Closing Balance': round(P + cumulative_interest, 2)
                    })
                
                schedule_df = pd.DataFrame(schedule_data)
                
                # Display formatted
                display_df = schedule_df.copy()
                for col in ['Opening Balance', 'Interest This Year', 'Cumulative Interest', 'Closing Balance']:
                    display_df[col] = display_df[col].apply(lambda x: format_currency(x, currency_symbol))
                
                st.dataframe(display_df, use_container_width=True, hide_index=True)
                
                # Charts
                st.markdown("---")
                st.markdown("### 📈 Visual Analysis")
                
                tab1, tab2 = st.tabs(["🥧 Breakdown", "📈 Growth"])
                
                with tab1:
                    fig = create_pie_chart(['Principal', 'Total Interest'], [P, I], 'Principal vs Interest')
                    st.plotly_chart(fig, use_container_width=True)
                
                with tab2:
                    fig = create_line_chart(
                        schedule_df['Year'].tolist(),
                        {'Cumulative Interest': schedule_df['Cumulative Interest'].tolist(),
                         'Closing Balance': schedule_df['Closing Balance'].tolist()},
                        'Growth Over Time', 'Year', f'Amount ({currency_symbol})'
                    )
                    st.plotly_chart(fig, use_container_width=True)
                
                # Summary for download
                summary_dict = {
                    'Calculation Type': 'Simple Interest',
                    'Calculated Field': calculated_field,
                    'Calculated Value': calculated_value,
                    'Principal (P)': format_currency(P, currency_symbol),
                    'Rate (R)': f'{R:.4f}%',
                    'Time (T)': f'{T:.2f} years',
                    'Interest (I)': format_currency(I, currency_symbol),
                    'Total Amount': format_currency(total_amount, currency_symbol),
                    'Yearly Interest': format_currency(yearly_interest, currency_symbol),
                    'Calculation Date': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
                
                # Download Section
                render_download_section("Simple Interest", summary_dict, schedule_df, currency_symbol)
                
                add_to_history("Simple Interest", 
                              {'P': P, 'R': R, 'T': T}, 
                              {'I': I, 'Calculated': calculated_field})
                
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
        💡 <strong>Enter 3 values, leave 1 as zero (0)</strong> - that value will be calculated!
    </div>
    """, unsafe_allow_html=True)
    
    # Compounding Frequency
    freq_options = get_frequency_options()
    frequency = st.selectbox("📅 Compounding Frequency", list(freq_options.keys()), index=3)
    m = freq_options[frequency]
    
    st.markdown("### 📝 Enter Your Values")
    
    col1, col2 = st.columns(2)
    
    with col1:
        PV = st.number_input(
            f"💰 Present Value (PV) [{currency_symbol}]",
            min_value=0.0, value=0.0, step=10000.0,
            help="Enter 0 if you want to calculate this"
        )
        FV = st.number_input(
            f"💵 Future Value (FV) [{currency_symbol}]",
            min_value=0.0, value=0.0, step=10000.0,
            help="Enter 0 if you want to calculate this"
        )
    
    with col2:
        r = st.number_input(
            "📊 Annual Rate (r) [%]",
            min_value=0.0, value=0.0, step=0.5,
            help="Enter 0 if you want to calculate this"
        )
        n = st.number_input(
            "⏰ Time (n) [Years]",
            min_value=0.0, value=0.0, step=1.0,
            help="Enter 0 if you want to calculate this"
        )
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        calculate = st.button("🔄 Calculate Missing Value", use_container_width=True, type="primary")
    
    if calculate:
        values = {'PV': PV, 'FV': FV, 'r': r, 'n': n}
        zeros = sum(1 for v in values.values() if v == 0)
        
        if zeros == 0:
            st.warning("⚠️ All values are filled! Leave ONE field as 0 to calculate it.")
        elif zeros > 1:
            st.error(f"❌ You left {zeros} fields as zero. Please fill at least 3 values.")
        else:
            try:
                if PV == 0:
                    r_periodic = (r / 100) / m
                    total_periods = n * m
                    PV = FV / ((1 + r_periodic) ** total_periods)
                    calculated_field = "Present Value (PV)"
                    calculated_value = format_currency(PV, currency_symbol)
                elif FV == 0:
                    r_periodic = (r / 100) / m
                    total_periods = n * m
                    FV = PV * ((1 + r_periodic) ** total_periods)
                    calculated_field = "Future Value (FV)"
                    calculated_value = format_currency(FV, currency_symbol)
                elif r == 0:
                    total_periods = n * m
                    r_periodic = (FV / PV) ** (1 / total_periods) - 1
                    r = r_periodic * m * 100
                    calculated_field = "Annual Rate (r)"
                    calculated_value = f"{r:.4f}%"
                else:  # n == 0
                    r_periodic = (r / 100) / m
                    n = math.log(FV / PV) / (m * math.log(1 + r_periodic))
                    calculated_field = "Time (n)"
                    calculated_value = f"{n:.2f} years"
                
                # Recalculate values
                r_periodic = (r / 100) / m
                total_periods = int(n * m)
                compound_interest = FV - PV
                effective_rate = ((1 + (r/100)/m) ** m - 1) * 100
                
                # Show Result
                st.markdown(f"""
                <div class="result-box">
                    ✅ Calculated: {calculated_field} = {calculated_value}
                </div>
                """, unsafe_allow_html=True)
                
                st.markdown("### 📊 Complete Summary")
                
                col1, col2, col3, col4 = st.columns(4)
                col1.metric("Present Value", format_currency(PV, currency_symbol))
                col2.metric("Future Value", format_currency(FV, currency_symbol))
                col3.metric("Interest Earned", format_currency(compound_interest, currency_symbol))
                col4.metric("Effective Rate", f"{effective_rate:.2f}%")
                
                # Year-wise Schedule
                st.markdown("---")
                st.markdown("### 📋 Year-wise Compounding Schedule")
                
                schedule_data = []
                balance = PV
                
                for year in range(1, int(n) + 1):
                    opening = balance
                    for _ in range(m):
                        balance = balance * (1 + r_periodic)
                    interest = balance - opening
                    
                    schedule_data.append({
                        'Year': year,
                        'Opening Balance': round(opening, 2),
                        'Interest Earned': round(interest, 2),
                        'Closing Balance': round(balance, 2)
                    })
                
                schedule_df = pd.DataFrame(schedule_data)
                
                display_df = schedule_df.copy()
                for col in ['Opening Balance', 'Interest Earned', 'Closing Balance']:
                    display_df[col] = display_df[col].apply(lambda x: format_currency(x, currency_symbol))
                
                st.dataframe(display_df, use_container_width=True, hide_index=True)
                
                # Charts
                st.markdown("---")
                tab1, tab2 = st.tabs(["🥧 Breakdown", "📈 Growth"])
                
                with tab1:
                    fig = create_pie_chart(['Principal', 'Compound Interest'], [PV, compound_interest], 'Principal vs Interest')
                    st.plotly_chart(fig, use_container_width=True)
                
                with tab2:
                    fig = create_line_chart(
                        schedule_df['Year'].tolist(),
                        {'Balance': schedule_df['Closing Balance'].tolist()},
                        'Balance Growth', 'Year', f'Balance ({currency_symbol})'
                    )
                    st.plotly_chart(fig, use_container_width=True)
                
                # Summary for download
                summary_dict = {
                    'Calculation Type': 'Compound Interest',
                    'Calculated Field': calculated_field,
                    'Calculated Value': calculated_value,
                    'Present Value (PV)': format_currency(PV, currency_symbol),
                    'Future Value (FV)': format_currency(FV, currency_symbol),
                    'Annual Rate (r)': f'{r:.4f}%',
                    'Time (n)': f'{n:.2f} years',
                    'Compounding': frequency,
                    'Compound Interest': format_currency(compound_interest, currency_symbol),
                    'Effective Annual Rate': f'{effective_rate:.4f}%',
                    'Calculation Date': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
                
                render_download_section("Compound Interest", summary_dict, schedule_df, currency_symbol)
                
                add_to_history("Compound Interest", 
                              {'PV': PV, 'r': r, 'n': n, 'm': m}, 
                              {'FV': FV, 'Calculated': calculated_field})
                
            except Exception as e:
                st.error(f"❌ Error: {e}")

# ═══════════════════════════════════════════════════════════════
#                    EMI CALCULATOR
# ═══════════════════════════════════════════════════════════════

elif calculator_type == "🏦 EMI Calculator":
    st.markdown("""
    <div class="main-header">
        <h1>🏦 EMI Calculator</h1>
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
    
    st.markdown("### 📝 Enter Loan Details")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        loan_amount = st.number_input(f"💰 Loan Amount [{currency_symbol}]", min_value=1000.0, value=1000000.0, step=50000.0)
    with col2:
        annual_rate = st.number_input("📊 Annual Interest Rate [%]", min_value=0.1, value=10.0, step=0.25)
    with col3:
        tenure_years = st.number_input("⏰ Loan Tenure [Years]", min_value=1, value=20, step=1)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        calculate = st.button("🔄 Calculate EMI", use_container_width=True, type="primary")
    
    if calculate:
        try:
            monthly_rate = annual_rate / 12 / 100
            total_months = tenure_years * 12
            
            if monthly_rate > 0:
                emi = loan_amount * monthly_rate * (1 + monthly_rate)**total_months / ((1 + monthly_rate)**total_months - 1)
            else:
                emi = loan_amount / total_months
            
            total_payment = emi * total_months
            total_interest = total_payment - loan_amount
            
            st.markdown(f"""
            <div class="result-box">
                💳 Monthly EMI: {format_currency(emi, currency_symbol)}
            </div>
            """, unsafe_allow_html=True)
            
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Loan Amount", format_currency(loan_amount, currency_symbol))
            col2.metric("Total Interest", format_currency(total_interest, currency_symbol))
            col3.metric("Total Payment", format_currency(total_payment, currency_symbol))
            col4.metric("Interest %", f"{(total_interest/loan_amount)*100:.1f}%")
            
            # Amortization Schedule
            st.markdown("---")
            st.markdown("### 📋 Amortization Schedule")
            
            schedule_data = []
            balance = loan_amount
            
            for month in range(1, total_months + 1):
                interest_payment = balance * monthly_rate
                principal_payment = emi - interest_payment
                balance = max(0, balance - principal_payment)
                
                schedule_data.append({
                    'Month': month,
                    'EMI': round(emi, 2),
                    'Principal': round(principal_payment, 2),
                    'Interest': round(interest_payment, 2),
                    'Balance': round(balance, 2)
                })
            
            schedule_df = pd.DataFrame(schedule_data)
            
            # Show limited rows
            if len(schedule_df) > 24:
                st.info(f"📋 Showing first 24 of {len(schedule_df)} months. Download for complete schedule.")
                display_schedule = schedule_df.head(24).copy()
            else:
                display_schedule = schedule_df.copy()
            
            display_df = display_schedule.copy()
            for col in ['EMI', 'Principal', 'Interest', 'Balance']:
                display_df[col] = display_df[col].apply(lambda x: format_currency(x, currency_symbol))
            
            st.dataframe(display_df, use_container_width=True, hide_index=True)
            
            # Charts
            st.markdown("---")
            tab1, tab2 = st.tabs(["🥧 Breakdown", "📈 Balance Over Time"])
            
            with tab1:
                fig = create_pie_chart(['Principal', 'Total Interest'], [loan_amount, total_interest], 'Payment Breakdown')
                st.plotly_chart(fig, use_container_width=True)
            
            with tab2:
                sample = schedule_df.iloc[::max(1, len(schedule_df)//50)]
                fig = create_line_chart(
                    sample['Month'].tolist(),
                    {'Outstanding Balance': sample['Balance'].tolist()},
                    'Loan Balance Over Time', 'Month', f'Balance ({currency_symbol})'
                )
                st.plotly_chart(fig, use_container_width=True)
            
            summary_dict = {
                'Calculation Type': 'EMI Calculator',
                'Loan Amount': format_currency(loan_amount, currency_symbol),
                'Annual Interest Rate': f'{annual_rate}%',
                'Loan Tenure': f'{tenure_years} years ({total_months} months)',
                'Monthly EMI': format_currency(emi, currency_symbol),
                'Total Payment': format_currency(total_payment, currency_symbol),
                'Total Interest': format_currency(total_interest, currency_symbol),
                'Interest as % of Principal': f'{(total_interest/loan_amount)*100:.2f}%',
                'Calculation Date': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            
            render_download_section("EMI Calculator", summary_dict, schedule_df, currency_symbol)
            
            add_to_history("EMI Calculator", 
                          {'Loan': loan_amount, 'Rate': annual_rate, 'Years': tenure_years}, 
                          {'EMI': emi, 'Total Interest': total_interest})
            
        except Exception as e:
            st.error(f"❌ Error: {e}")

# ═══════════════════════════════════════════════════════════════
#                    SIP CALCULATOR
# ═══════════════════════════════════════════════════════════════

elif calculator_type == "💎 SIP Calculator":
    st.markdown("""
    <div class="main-header">
        <h1>💎 SIP Calculator</h1>
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
    
    st.markdown("### 📝 Enter Investment Details")
    
    col1, col2 = st.columns(2)
    
    with col1:
        monthly_sip = st.number_input(f"💰 Monthly SIP [{currency_symbol}]", min_value=100.0, value=10000.0, step=1000.0)
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
            
            st.markdown(f"""
            <div class="result-box">
                💰 Future Value: {format_currency(future_value, currency_symbol)}
            </div>
            """, unsafe_allow_html=True)
            
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Total Invested", format_currency(total_invested, currency_symbol))
            col2.metric("Wealth Gained", format_currency(wealth_gained, currency_symbol))
            col3.metric("Absolute Return", f"{absolute_return:.1f}%")
            col4.metric("Final SIP", format_currency(schedule_df['Monthly SIP'].iloc[-1], currency_symbol))
            
            st.markdown("---")
            st.markdown("### 📋 Year-wise Investment Schedule")
            
            display_df = schedule_df.copy()
            for col in ['Monthly SIP', 'Year Investment', 'Total Invested', 'Portfolio Value', 'Total Gain']:
                display_df[col] = display_df[col].apply(lambda x: format_currency(x, currency_symbol))
            
            st.dataframe(display_df, use_container_width=True, hide_index=True)
            
            # Charts
            st.markdown("---")
            tab1, tab2 = st.tabs(["📈 Growth", "🥧 Breakdown"])
            
            with tab1:
                fig = create_line_chart(
                    schedule_df['Year'].tolist(),
                    {'Total Invested': schedule_df['Total Invested'].tolist(),
                     'Portfolio Value': schedule_df['Portfolio Value'].tolist()},
                    'SIP Growth Over Time', 'Year', f'Amount ({currency_symbol})'
                )
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
            
            add_to_history("SIP Calculator", 
                          {'SIP': monthly_sip, 'Return': expected_return, 'Years': investment_years}, 
                          {'FV': future_value, 'Gain': wealth_gained})
            
        except Exception as e:
            st.error(f"❌ Error: {e}")

# ═══════════════════════════════════════════════════════════════
#                    NPV CALCULATOR
# ═══════════════════════════════════════════════════════════════

elif calculator_type == "💹 NPV Calculator":
    st.markdown("""
    <div class="main-header">
        <h1>💹 NPV Calculator</h1>
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
    
    st.markdown("### 📝 Enter Project Details")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        initial_investment = st.number_input(f"💰 Initial Investment [{currency_symbol}]", min_value=0.0, value=100000.0, step=10000.0)
    with col2:
        discount_rate = st.number_input("📊 Discount Rate [%]", min_value=0.0, value=10.0, step=0.5)
    with col3:
        num_years = st.number_input("⏰ Number of Years", min_value=1, max_value=30, value=5, step=1)
    
    st.markdown("### 💵 Enter Annual Cash Flows")
    
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
            r = discount_rate / 100
            
            npv = -initial_investment
            
            schedule_data = [{
                'Year': 0,
                'Cash Flow': round(-initial_investment, 2),
                'Discount Factor': 1.0,
                'Present Value': round(-initial_investment, 2),
                'Cumulative PV': round(-initial_investment, 2)
            }]
            
            cumulative_pv = -initial_investment
            
            for t, cf in enumerate(cash_flows, 1):
                discount_factor = 1 / (1 + r) ** t
                pv = cf * discount_factor
                npv += pv
                cumulative_pv += pv
                
                schedule_data.append({
                    'Year': t,
                    'Cash Flow': round(cf, 2),
                    'Discount Factor': round(discount_factor, 4),
                    'Present Value': round(pv, 2),
                    'Cumulative PV': round(cumulative_pv, 2)
                })
            
            schedule_df = pd.DataFrame(schedule_data)
            
            # Calculate IRR
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
            
            if npv > 0:
                st.markdown(f"""
                <div class="result-box">
                    ✅ NPV = {format_currency(npv, currency_symbol)} — ACCEPT PROJECT
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="result-box-reject">
                    ❌ NPV = {format_currency(npv, currency_symbol)} — REJECT PROJECT
                </div>
                """, unsafe_allow_html=True)
            
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("NPV", format_currency(npv, currency_symbol))
            col2.metric("IRR", f"{irr_percent:.2f}%")
            col3.metric("Profitability Index", f"{profitability_index:.2f}")
            col4.metric("Decision", "ACCEPT ✅" if npv > 0 else "REJECT ❌")
            
            st.markdown("---")
            st.markdown("### 📋 Cash Flow Schedule")
            
            display_df = schedule_df.copy()
            display_df['Cash Flow'] = display_df['Cash Flow'].apply(lambda x: format_currency(x, currency_symbol))
            display_df['Present Value'] = display_df['Present Value'].apply(lambda x: format_currency(x, currency_symbol))
            display_df['Cumulative PV'] = display_df['Cumulative PV'].apply(lambda x: format_currency(x, currency_symbol))
            
            st.dataframe(display_df, use_container_width=True, hide_index=True)
            
            # Charts
            st.markdown("---")
            tab1, tab2 = st.tabs(["📊 Cash Flows", "📈 NPV Profile"])
            
            with tab1:
                fig = create_bar_chart(
                    [f'Y{y}' for y in schedule_df['Year'].tolist()],
                    {'Cash Flow': schedule_df['Cash Flow'].tolist(),
                     'Present Value': schedule_df['Present Value'].tolist()},
                    'Cash Flow vs Present Value', f'Amount ({currency_symbol})'
                )
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
            
            add_to_history("NPV Calculator", 
                          {'Investment': initial_investment, 'Rate': discount_rate}, 
                          {'NPV': npv, 'IRR': irr_percent})
            
        except Exception as e:
            st.error(f"❌ Error: {e}")

# ═══════════════════════════════════════════════════════════════
#                    BOND VALUATION
# ═══════════════════════════════════════════════════════════════

elif calculator_type == "📜 Bond Valuation":
    st.markdown("""
    <div class="main-header">
        <h1>📜 Bond Valuation</h1>
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
    
    st.markdown("### 📝 Enter Bond Details")
    
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
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        calculate = st.button("🔄 Calculate Bond Price", use_container_width=True, type="primary")
    
    if calculate:
        try:
            coupon_payment = (face_value * coupon_rate / 100) / m
            total_periods = years_to_maturity * m
            periodic_ytm = (ytm / 100) / m
            
            schedule_data = []
            pv_coupons = 0
            
            for period in range(1, total_periods + 1):
                discount_factor = 1 / (1 + periodic_ytm) ** period
                pv_coupon = coupon_payment * discount_factor
                pv_coupons += pv_coupon
                
                schedule_data.append({
                    'Period': period,
                    'Year': round(period / m, 2),
                    'Coupon Payment': round(coupon_payment, 2),
                    'Discount Factor': round(discount_factor, 4),
                    'PV of Coupon': round(pv_coupon, 2)
                })
            
            pv_face = face_value / (1 + periodic_ytm) ** total_periods
            bond_price = pv_coupons + pv_face
            current_yield = (coupon_payment * m / bond_price) * 100
            
            schedule_df = pd.DataFrame(schedule_data)
            
            st.markdown(f"""
            <div class="result-box">
                📜 Bond Price: {format_currency(bond_price, currency_symbol)}
            </div>
            """, unsafe_allow_html=True)
            
            if bond_price > face_value:
                st.success(f"📈 **Premium Bond** — Coupon Rate ({coupon_rate}%) > YTM ({ytm}%)")
            elif bond_price < face_value:
                st.warning(f"📉 **Discount Bond** — Coupon Rate ({coupon_rate}%) < YTM ({ytm}%)")
            else:
                st.info(f"➡️ **Par Bond** — Coupon Rate = YTM")
            
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Bond Price", format_currency(bond_price, currency_symbol))
            col2.metric("PV of Coupons", format_currency(pv_coupons, currency_symbol))
            col3.metric("PV of Face Value", format_currency(pv_face, currency_symbol))
            col4.metric("Current Yield", f"{current_yield:.2f}%")
            
            st.markdown("---")
            st.markdown("### 📋 Coupon Payment Schedule")
            
            display_df = schedule_df.copy()
            display_df['Coupon Payment'] = display_df['Coupon Payment'].apply(lambda x: format_currency(x, currency_symbol))
            display_df['PV of Coupon'] = display_df['PV of Coupon'].apply(lambda x: format_currency(x, currency_symbol))
            
            if len(display_df) > 20:
                st.info(f"📋 Showing first 20 of {len(display_df)} periods. Download for complete schedule.")
                st.dataframe(display_df.head(20), use_container_width=True, hide_index=True)
            else:
                st.dataframe(display_df, use_container_width=True, hide_index=True)
            
            # Charts
            st.markdown("---")
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
                'Coupon Frequency': frequency,
                'Coupon Payment': format_currency(coupon_payment, currency_symbol),
                'Bond Price': format_currency(bond_price, currency_symbol),
                'PV of Coupons': format_currency(pv_coupons, currency_symbol),
                'PV of Face Value': format_currency(pv_face, currency_symbol),
                'Current Yield': f'{current_yield:.2f}%',
                'Bond Type': 'Premium' if bond_price > face_value else ('Discount' if bond_price < face_value else 'Par'),
                'Calculation Date': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            
            render_download_section("Bond Valuation", summary_dict, schedule_df, currency_symbol)
            
            add_to_history("Bond Valuation", 
                          {'Face': face_value, 'Coupon': coupon_rate, 'YTM': ytm}, 
                          {'Price': bond_price})
            
        except Exception as e:
            st.error(f"❌ Error: {e}")

# ═══════════════════════════════════════════════════════════════
#                    HISTORY
# ═══════════════════════════════════════════════════════════════

elif calculator_type == "📋 History":
    st.markdown("""
    <div class="main-header">
        <h1>📋 Calculation History</h1>
        <p>View and Export Your Past Calculations</p>
    </div>
    """, unsafe_allow_html=True)
    
    if st.session_state.calculation_history:
        history_df = pd.DataFrame(st.session_state.calculation_history)
        
        st.markdown(f"### 📊 Total Records: {len(history_df)}")
        st.dataframe(history_df, use_container_width=True, hide_index=True)
        
        st.markdown("---")
        st.markdown("### 📥 Export History")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            csv = history_df.to_csv(index=False)
            st.download_button("📄 CSV", data=csv, file_name="history.csv", mime="text/csv", use_container_width=True)
        
        with col2:
            output = io.BytesIO()
            history_df.to_excel(output, index=False, engine='openpyxl')
            st.download_button("📊 Excel", data=output.getvalue(), file_name="history.xlsx", 
                             mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", use_container_width=True)
        
        with col3:
            json_data = history_df.to_json(orient='records', indent=2)
            st.download_button("📋 JSON", data=json_data, file_name="history.json", mime="application/json", use_container_width=True)
        
        with col4:
            if st.button("🗑️ Clear All", use_container_width=True):
                st.session_state.calculation_history = []
                st.rerun()
    else:
        st.info("📝 No calculations yet. Use any calculator to build your history!")

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
    P = (I × 100) / (R × T)
    R = (I × 100) / (P × T)
    T = (I × 100) / (P × R)
    ```
    
    ### 📈 Compound Interest
    ```
    FV = PV × (1 + r/m)^(n×m)
    PV = FV / (1 + r/m)^(n×m)
    r = m × [(FV/PV)^(1/(n×m)) - 1]
    n = ln(FV/PV) / [m × ln(1 + r/m)]
    ```
    
    ### 🏦 EMI
    ```
    EMI = P × r × (1+r)^n / [(1+r)^n - 1]
    Where: r = monthly rate, n = total months
    ```
    
    ### 💎 SIP Future Value
    ```
    FV = P × [(1+r)^n - 1] / r × (1+r)
    ```
    
    ### 💹 NPV & IRR
    ```
    NPV = -C₀ + Σ[CFₜ / (1+r)^t]
    IRR = Rate where NPV = 0
    ```
    
    ### 📜 Bond Valuation
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
    💰 Financial Calculator Pro | Smart Auto-Calculate<br>
    <small>Leave any field as 0 to calculate it • Download in CSV, Excel, PDF, JSON</small>
</div>
""", unsafe_allow_html=True)
