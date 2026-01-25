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
    
    .main-header h1 {
        margin: 0;
        font-size: 2.5rem;
    }
    
    .main-header p {
        margin: 10px 0 0 0;
        opacity: 0.9;
    }
    
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
    
    .schedule-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 15px;
        border-radius: 10px 10px 0 0;
        text-align: center;
        font-weight: bold;
    }
    
    .download-section {
        background: #f8f9fa;
        padding: 20px;
        border-radius: 15px;
        border: 2px dashed #667eea;
        margin: 20px 0;
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
#                    PDF GENERATION
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
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')

def generate_pdf(calc_type, data_dict, schedule_df=None):
    pdf = PDFReport()
    pdf.add_page()
    
    pdf.set_font('Arial', 'B', 16)
    pdf.set_text_color(60, 60, 60)
    pdf.cell(0, 10, calc_type, 0, 1, 'L')
    pdf.ln(5)
    
    pdf.set_font('Arial', '', 11)
    for key, value in data_dict.items():
        pdf.cell(80, 8, f'{key}:', 0, 0, 'L')
        pdf.cell(0, 8, str(value), 0, 1, 'L')
    
    return pdf.output(dest='S').encode('latin-1')

# ═══════════════════════════════════════════════════════════════
#                    EXCEL GENERATION
# ═══════════════════════════════════════════════════════════════

def generate_excel(summary_dict, schedule_df=None):
    output = io.BytesIO()
    
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        # Summary Sheet
        summary_df = pd.DataFrame(list(summary_dict.items()), columns=['Parameter', 'Value'])
        summary_df.to_excel(writer, sheet_name='Summary', index=False)
        
        # Schedule Sheet
        if schedule_df is not None:
            schedule_df.to_excel(writer, sheet_name='Schedule', index=False)
    
    return output.getvalue()

# ═══════════════════════════════════════════════════════════════
#                    DOWNLOAD SECTION COMPONENT
# ═══════════════════════════════════════════════════════════════

def show_download_section(calc_type, summary_dict, schedule_df=None, currency_symbol="$"):
    """Show downloads only when user clicks button"""
    
    st.markdown("---")
    
    # Download Button
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("📥 Download Results", use_container_width=True, type="primary", key=f"download_btn_{calc_type}"):
            st.session_state.show_downloads = True
    
    # Show download options only after button click
    if st.session_state.show_downloads:
        st.markdown("""
        <div class="download-section">
            <h4 style="text-align: center; color: #667eea;">📥 Select Download Format</h4>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            # CSV
            if schedule_df is not None:
                csv_data = schedule_df.to_csv(index=False)
            else:
                csv_data = pd.DataFrame(list(summary_dict.items()), columns=['Parameter', 'Value']).to_csv(index=False)
            
            st.download_button(
                label="📄 CSV",
                data=csv_data,
                file_name=f"{calc_type.lower().replace(' ', '_')}.csv",
                mime="text/csv",
                use_container_width=True
            )
        
        with col2:
            # Excel
            excel_data = generate_excel(summary_dict, schedule_df)
            st.download_button(
                label="📊 Excel",
                data=excel_data,
                file_name=f"{calc_type.lower().replace(' ', '_')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )
        
        with col3:
            # PDF
            try:
                pdf_data = generate_pdf(calc_type, summary_dict, schedule_df)
                st.download_button(
                    label="📕 PDF",
                    data=pdf_data,
                    file_name=f"{calc_type.lower().replace(' ', '_')}.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )
            except:
                st.button("📕 PDF", disabled=True, use_container_width=True)
        
        with col4:
            # JSON
            json_data = json.dumps(summary_dict, indent=2)
            st.download_button(
                label="📋 JSON",
                data=json_data,
                file_name=f"{calc_type.lower().replace(' ', '_')}.json",
                mime="application/json",
                use_container_width=True
            )
        
        # Close button
        if st.button("✖️ Close Downloads", use_container_width=True):
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
        textinfo='label+percent',
        hovertemplate='<b>%{label}</b><br>Value: %{value:,.2f}<br>Percentage: %{percent}<extra></extra>'
    )])
    
    fig.update_layout(
        title=dict(text=title, font=dict(size=16)),
        height=400,
        margin=dict(t=60, b=60, l=40, r=40)
    )
    
    return fig

def create_line_chart(x_data, y_data_dict, title, x_title, y_title):
    fig = go.Figure()
    
    colors = ['#667eea', '#00b894', '#e74c3c', '#f39c12']
    
    for i, (name, y_data) in enumerate(y_data_dict.items()):
        fig.add_trace(go.Scatter(
            x=x_data,
            y=y_data,
            mode='lines+markers',
            name=name,
            line=dict(color=colors[i % len(colors)], width=3),
            marker=dict(size=6)
        ))
    
    fig.update_layout(
        title=dict(text=title, font=dict(size=16)),
        xaxis_title=x_title,
        yaxis_title=y_title,
        hovermode='x unified',
        height=400
    )
    
    return fig

def create_bar_chart(categories, values_dict, title, y_title):
    fig = go.Figure()
    
    colors = ['#667eea', '#00b894', '#e74c3c']
    
    for i, (name, values) in enumerate(values_dict.items()):
        fig.add_trace(go.Bar(
            name=name,
            x=categories,
            y=values,
            marker_color=colors[i % len(colors)]
        ))
    
    fig.update_layout(
        title=dict(text=title, font=dict(size=16)),
        yaxis_title=y_title,
        barmode='group',
        height=400
    )
    
    return fig

def create_gauge_chart(value, max_value, title):
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=value,
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
    
    fig.update_layout(height=300, margin=dict(t=60, b=20, l=40, r=40))
    
    return fig

def create_area_chart(x_data, y_data_dict, title, x_title, y_title):
    fig = go.Figure()
    
    colors = ['rgba(102, 126, 234, 0.7)', 'rgba(0, 184, 148, 0.7)', 'rgba(231, 76, 60, 0.7)']
    
    for i, (name, y_data) in enumerate(y_data_dict.items()):
        fig.add_trace(go.Scatter(
            x=x_data,
            y=y_data,
            mode='lines',
            name=name,
            stackgroup='one',
            fillcolor=colors[i % len(colors)]
        ))
    
    fig.update_layout(
        title=dict(text=title, font=dict(size=16)),
        xaxis_title=x_title,
        yaxis_title=y_title,
        height=400
    )
    
    return fig

# ═══════════════════════════════════════════════════════════════
#                    SIDEBAR
# ═══════════════════════════════════════════════════════════════

with st.sidebar:
    st.markdown("""
    <div style="text-align: center; padding: 20px 0;">
        <h1 style="color: #667eea;">💰</h1>
        <h3>Financial Calculator Pro</h3>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    currency_symbol = st.selectbox("💵 Currency", ["$", "₹", "€", "£", "Rs", "PKR"])
    
    st.markdown("---")
    
    calculator_type = st.radio(
        "📊 Select Calculator",
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
    st.info("💡 Leave ONE field as 0 to calculate it")

# ═══════════════════════════════════════════════════════════════
#                    HOME PAGE
# ═══════════════════════════════════════════════════════════════

if calculator_type == "🏠 Home":
    st.markdown("""
    <div class="main-header">
        <h1>💰 Financial Calculator Pro</h1>
        <p>Professional Finance Calculations with Charts & Reports</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="calc-card">
            <h4>📐 Simple Interest</h4>
            <p>Calculate P, R, T, or I with detailed year-wise schedule</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="calc-card">
            <h4>🏦 EMI Calculator</h4>
            <p>Loan EMI with complete amortization schedule</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="calc-card">
            <h4>📈 Compound Interest</h4>
            <p>FV, PV, Rate with period-wise growth schedule</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="calc-card">
            <h4>💎 SIP Calculator</h4>
            <p>Monthly investment with year-wise wealth schedule</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="calc-card">
            <h4>💹 NPV Analysis</h4>
            <p>NPV, IRR with cash flow schedule</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="calc-card">
            <h4>📜 Bond Valuation</h4>
            <p>Bond price with coupon payment schedule</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    st.success("👈 Select a calculator from sidebar to get started!")

# ═══════════════════════════════════════════════════════════════
#                    SIMPLE INTEREST WITH SCHEDULE
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
        # Reset download state
        st.session_state.show_downloads = False
        
        values = [P, R, T, I]
        zeros = values.count(0)
        
        if zeros != 1:
            st.error("⚠️ Please leave exactly ONE field as 0 to calculate it!")
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
                
                # Result Box
                st.markdown(f"""
                <div class="result-box">
                    ✅ {result_label} = {result_value}
                </div>
                """, unsafe_allow_html=True)
                
                # Metrics
                col1, col2, col3, col4 = st.columns(4)
                col1.metric("Principal", format_currency(P, currency_symbol))
                col2.metric("Rate", f"{R:.2f}%")
                col3.metric("Time", f"{T:.0f} years")
                col4.metric("Interest", format_currency(I, currency_symbol))
                
                st.success(f"💰 **Total Amount:** {format_currency(total_amount, currency_symbol)}")
                
                # ═══════════════════════════════════════
                #         YEAR-WISE SCHEDULE
                # ═══════════════════════════════════════
                
                st.markdown("---")
                st.markdown("### 📋 Year-wise Interest Schedule")
                
                schedule_data = []
                yearly_interest = (P * R) / 100
                
                for year in range(1, int(T) + 1):
                    cumulative_interest = yearly_interest * year
                    schedule_data.append({
                        'Year': year,
                        'Opening Balance': P,
                        'Interest This Year': yearly_interest,
                        'Cumulative Interest': cumulative_interest,
                        'Closing Balance': P + cumulative_interest
                    })
                
                schedule_df = pd.DataFrame(schedule_data)
                
                # Display Schedule
                display_df = schedule_df.copy()
                display_df['Opening Balance'] = display_df['Opening Balance'].apply(lambda x: format_currency(x, currency_symbol))
                display_df['Interest This Year'] = display_df['Interest This Year'].apply(lambda x: format_currency(x, currency_symbol))
                display_df['Cumulative Interest'] = display_df['Cumulative Interest'].apply(lambda x: format_currency(x, currency_symbol))
                display_df['Closing Balance'] = display_df['Closing Balance'].apply(lambda x: format_currency(x, currency_symbol))
                
                st.dataframe(display_df, use_container_width=True, hide_index=True)
                
                # ═══════════════════════════════════════
                #              CHARTS
                # ═══════════════════════════════════════
                
                st.markdown("---")
                st.markdown("### 📈 Visual Analysis")
                
                tab1, tab2, tab3 = st.tabs(["🥧 Pie Chart", "📈 Growth Chart", "📊 Bar Chart"])
                
                with tab1:
                    fig = create_pie_chart(
                        ['Principal', 'Interest'],
                        [P, I],
                        'Principal vs Interest'
                    )
                    st.plotly_chart(fig, use_container_width=True)
                
                with tab2:
                    fig = create_line_chart(
                        schedule_df['Year'].tolist(),
                        {
                            'Cumulative Interest': schedule_df['Cumulative Interest'].tolist(),
                            'Closing Balance': schedule_df['Closing Balance'].tolist()
                        },
                        'Interest Growth Over Time',
                        'Year',
                        f'Amount ({currency_symbol})'
                    )
                    st.plotly_chart(fig, use_container_width=True)
                
                with tab3:
                    fig = create_bar_chart(
                        [f'Year {y}' for y in schedule_df['Year'].tolist()],
                        {'Interest': schedule_df['Interest This Year'].tolist()},
                        'Year-wise Interest',
                        f'Interest ({currency_symbol})'
                    )
                    st.plotly_chart(fig, use_container_width=True)
                
                # ═══════════════════════════════════════
                #           DOWNLOAD SECTION
                # ═══════════════════════════════════════
                
                summary_dict = {
                    'Principal': format_currency(P, currency_symbol),
                    'Rate': f'{R:.4f}%',
                    'Time': f'{T:.2f} years',
                    'Total Interest': format_currency(I, currency_symbol),
                    'Total Amount': format_currency(total_amount, currency_symbol),
                    'Yearly Interest': format_currency(yearly_interest, currency_symbol)
                }
                
                show_download_section("Simple Interest", summary_dict, schedule_df, currency_symbol)
                
                # Add to history
                add_to_history("Simple Interest", summary_dict, {'Result': result_value})
                
            except ZeroDivisionError:
                st.error("❌ Cannot divide by zero!")
            except Exception as e:
                st.error(f"❌ Error: {e}")

# ═══════════════════════════════════════════════════════════════
#                    COMPOUND INTEREST WITH SCHEDULE
# ═══════════════════════════════════════════════════════════════

elif calculator_type == "📈 Compound Interest":
    st.markdown("""
    <div class="main-header">
        <h1>📈 Compound Interest Calculator</h1>
        <p>With Period-wise Compounding Schedule</p>
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
                
                total_periods = int(n * m)
                compound_interest = FV - PV
                effective_rate = ((1 + (r/100)/m) ** m - 1) * 100
                r_periodic = (r / 100) / m
                
                # Result
                st.markdown(f"""
                <div class="result-box">
                    ✅ {result_label} = {result_value}
                </div>
                """, unsafe_allow_html=True)
                
                col1, col2, col3, col4 = st.columns(4)
                col1.metric("Present Value", format_currency(PV, currency_symbol))
                col2.metric("Future Value", format_currency(FV, currency_symbol))
                col3.metric("Interest Earned", format_currency(compound_interest, currency_symbol))
                col4.metric("Effective Rate", f"{effective_rate:.2f}%")
                
                # ═══════════════════════════════════════
                #         PERIOD-WISE SCHEDULE
                # ═══════════════════════════════════════
                
                st.markdown("---")
                st.markdown("### 📋 Period-wise Compounding Schedule")
                
                schedule_data = []
                balance = PV
                
                for period in range(1, total_periods + 1):
                    opening = balance
                    interest = balance * r_periodic
                    balance = balance + interest
                    
                    schedule_data.append({
                        'Period': period,
                        'Year': (period - 1) // m + 1,
                        'Opening Balance': opening,
                        'Interest Earned': interest,
                        'Closing Balance': balance
                    })
                
                schedule_df = pd.DataFrame(schedule_data)
                
                # Show first 24 and last 12 periods if too many
                if len(schedule_df) > 36:
                    display_schedule = pd.concat([schedule_df.head(24), schedule_df.tail(12)])
                    st.info(f"📋 Showing first 24 and last 12 of {len(schedule_df)} periods")
                else:
                    display_schedule = schedule_df
                
                display_df = display_schedule.copy()
                for col in ['Opening Balance', 'Interest Earned', 'Closing Balance']:
                    display_df[col] = display_df[col].apply(lambda x: format_currency(x, currency_symbol))
                
                st.dataframe(display_df, use_container_width=True, hide_index=True)
                
                # Charts
                st.markdown("---")
                st.markdown("### 📈 Visual Analysis")
                
                tab1, tab2, tab3 = st.tabs(["🥧 Breakdown", "📈 Growth", "🎯 Gauge"])
                
                with tab1:
                    fig = create_pie_chart(
                        ['Principal', 'Compound Interest'],
                        [PV, compound_interest],
                        'Principal vs Interest'
                    )
                    st.plotly_chart(fig, use_container_width=True)
                
                with tab2:
                    # Year-wise for chart
                    yearly = schedule_df.groupby('Year').last().reset_index()
                    fig = create_line_chart(
                        yearly['Year'].tolist(),
                        {'Balance': yearly['Closing Balance'].tolist()},
                        'Balance Growth Over Years',
                        'Year',
                        f'Balance ({currency_symbol})'
                    )
                    st.plotly_chart(fig, use_container_width=True)
                
                with tab3:
                    col1, col2 = st.columns(2)
                    with col1:
                        fig = create_gauge_chart(r, 25, 'Interest Rate (%)')
                        st.plotly_chart(fig, use_container_width=True)
                    with col2:
                        fig = create_gauge_chart(min((compound_interest/PV)*100, 500), 500, 'Total Return (%)')
                        st.plotly_chart(fig, use_container_width=True)
                
                # Download
                summary_dict = {
                    'Present Value': format_currency(PV, currency_symbol),
                    'Future Value': format_currency(FV, currency_symbol),
                    'Annual Rate': f'{r:.4f}%',
                    'Years': f'{n:.2f}',
                    'Compounding': frequency,
                    'Total Periods': total_periods,
                    'Compound Interest': format_currency(compound_interest, currency_symbol),
                    'Effective Annual Rate': f'{effective_rate:.4f}%'
                }
                
                show_download_section("Compound Interest", summary_dict, schedule_df, currency_symbol)
                
                add_to_history("Compound Interest", summary_dict, {'Result': result_value})
                
            except Exception as e:
                st.error(f"❌ Error: {e}")

# ═══════════════════════════════════════════════════════════════
#                    EMI CALCULATOR WITH SCHEDULE
# ═══════════════════════════════════════════════════════════════

elif calculator_type == "🏦 EMI Calculator":
    st.markdown("""
    <div class="main-header">
        <h1>🏦 EMI Calculator</h1>
        <p>With Complete Amortization Schedule</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="formula-box">
        <strong>Formula:</strong> EMI = P × r × (1+r)^n / [(1+r)^n - 1]
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
        st.session_state.show_downloads = False
        
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
            
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Loan Amount", format_currency(loan_amount, currency_symbol))
            col2.metric("Total Interest", format_currency(total_interest, currency_symbol))
            col3.metric("Total Payment", format_currency(total_payment, currency_symbol))
            col4.metric("Interest %", f"{(total_interest/loan_amount)*100:.1f}%")
            
            # ═══════════════════════════════════════
            #         AMORTIZATION SCHEDULE
            # ═══════════════════════════════════════
            
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
                    'Year': (month - 1) // 12 + 1,
                    'EMI': emi,
                    'Principal': principal_payment,
                    'Interest': interest_payment,
                    'Balance': balance
                })
            
            schedule_df = pd.DataFrame(schedule_data)
            
            # Show limited rows
            if len(schedule_df) > 36:
                display_schedule = pd.concat([schedule_df.head(24), schedule_df.tail(12)])
                st.info(f"📋 Showing first 24 and last 12 of {len(schedule_df)} months. Download for full schedule.")
            else:
                display_schedule = schedule_df
            
            display_df = display_schedule.copy()
            for col in ['EMI', 'Principal', 'Interest', 'Balance']:
                display_df[col] = display_df[col].apply(lambda x: format_currency(x, currency_symbol))
            
            st.dataframe(display_df, use_container_width=True, hide_index=True)
            
            # Yearly Summary
            st.markdown("### 📊 Year-wise Summary")
            
            yearly_df = schedule_df.groupby('Year').agg({
                'Principal': 'sum',
                'Interest': 'sum',
                'Balance': 'last'
            }).reset_index()
            
            yearly_display = yearly_df.copy()
            yearly_display['Principal'] = yearly_display['Principal'].apply(lambda x: format_currency(x, currency_symbol))
            yearly_display['Interest'] = yearly_display['Interest'].apply(lambda x: format_currency(x, currency_symbol))
            yearly_display['Balance'] = yearly_display['Balance'].apply(lambda x: format_currency(x, currency_symbol))
            
            st.dataframe(yearly_display, use_container_width=True, hide_index=True)
            
            # Charts
            st.markdown("---")
            st.markdown("### 📈 Visual Analysis")
            
            tab1, tab2, tab3, tab4 = st.tabs(["🥧 Breakdown", "📈 Balance", "📊 Yearly Split", "🌊 Cumulative"])
            
            with tab1:
                fig = create_pie_chart(
                    ['Principal', 'Total Interest'],
                    [loan_amount, total_interest],
                    'Payment Breakdown'
                )
                st.plotly_chart(fig, use_container_width=True)
            
            with tab2:
                fig = create_line_chart(
                    schedule_df['Month'].tolist()[::max(1, len(schedule_df)//50)],
                    {'Outstanding Balance': schedule_df['Balance'].tolist()[::max(1, len(schedule_df)//50)]},
                    'Loan Balance Over Time',
                    'Month',
                    f'Balance ({currency_symbol})'
                )
                st.plotly_chart(fig, use_container_width=True)
            
            with tab3:
                fig = create_bar_chart(
                    [f'Y{y}' for y in yearly_df['Year'].tolist()[:20]],
                    {
                        'Principal': yearly_df['Principal'].tolist()[:20],
                        'Interest': yearly_df['Interest'].tolist()[:20]
                    },
                    'Yearly Principal vs Interest',
                    f'Amount ({currency_symbol})'
                )
                st.plotly_chart(fig, use_container_width=True)
            
            with tab4:
                cumulative_principal = schedule_df['Principal'].cumsum().tolist()
                cumulative_interest = schedule_df['Interest'].cumsum().tolist()
                
                fig = create_area_chart(
                    schedule_df['Month'].tolist()[::max(1, len(schedule_df)//50)],
                    {
                        'Cumulative Principal': cumulative_principal[::max(1, len(schedule_df)//50)],
                        'Cumulative Interest': cumulative_interest[::max(1, len(schedule_df)//50)]
                    },
                    'Cumulative Payments',
                    'Month',
                    f'Amount ({currency_symbol})'
                )
                st.plotly_chart(fig, use_container_width=True)
            
            # Download
            summary_dict = {
                'Loan Amount': format_currency(loan_amount, currency_symbol),
                'Annual Rate': f'{annual_rate}%',
                'Tenure': f'{tenure_years} years ({total_months} months)',
                'Monthly EMI': format_currency(emi, currency_symbol),
                'Total Payment': format_currency(total_payment, currency_symbol),
                'Total Interest': format_currency(total_interest, currency_symbol),
                'Interest Percentage': f'{(total_interest/loan_amount)*100:.2f}%'
            }
            
            show_download_section("EMI Calculator", summary_dict, schedule_df, currency_symbol)
            
            add_to_history("EMI Calculator", summary_dict, {'EMI': format_currency(emi, currency_symbol)})
            
        except Exception as e:
            st.error(f"❌ Error: {e}")

# ═══════════════════════════════════════════════════════════════
#                    SIP CALCULATOR WITH SCHEDULE
# ═══════════════════════════════════════════════════════════════

elif calculator_type == "💎 SIP Calculator":
    st.markdown("""
    <div class="main-header">
        <h1>💎 SIP Calculator</h1>
        <p>With Month-wise Investment Schedule</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="formula-box">
        <strong>Formula:</strong> FV = P × [(1+r)^n - 1] / r × (1+r)
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        monthly_sip = st.number_input(f"💰 Monthly SIP [{currency_symbol}]", min_value=100.0, value=10000.0, step=1000.0)
        expected_return = st.number_input("📊 Expected Return [% per year]", min_value=1.0, value=12.0, step=0.5)
    
    with col2:
        years = st.number_input("⏰ Investment Period [Years]", min_value=1, value=10, step=1)
        step_up = st.number_input("📈 Annual Step-up [%]", min_value=0.0, value=10.0, step=5.0)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        calculate_btn = st.button("🔄 Calculate SIP", use_container_width=True, type="primary")
    
    if calculate_btn:
        st.session_state.show_downloads = False
        
        try:
            monthly_rate = expected_return / 12 / 100
            total_months = years * 12
            
            # Calculate with step-up
            schedule_data = []
            current_sip = monthly_sip
            total_invested = 0
            current_value = 0
            
            for year in range(1, years + 1):
                year_start_value = current_value
                year_invested = 0
                
                for month in range(1, 13):
                    month_num = (year - 1) * 12 + month
                    current_value = current_value * (1 + monthly_rate) + current_sip
                    total_invested += current_sip
                    year_invested += current_sip
                    
                    schedule_data.append({
                        'Month': month_num,
                        'Year': year,
                        'SIP Amount': current_sip,
                        'Total Invested': total_invested,
                        'Portfolio Value': current_value,
                        'Gain': current_value - total_invested
                    })
                
                # Step up at year end
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
            
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Total Invested", format_currency(total_invested, currency_symbol))
            col2.metric("Wealth Gained", format_currency(wealth_gained, currency_symbol))
            col3.metric("Returns", f"{(wealth_gained/total_invested)*100:.1f}%")
            col4.metric("CAGR", f"{((future_value/total_invested)**(1/years)-1)*100:.1f}%")
            
            # ═══════════════════════════════════════
            #         YEARLY SCHEDULE
            # ═══════════════════════════════════════
            
            st.markdown("---")
            st.markdown("### 📋 Year-wise Investment Schedule")
            
            yearly_df = schedule_df.groupby('Year').agg({
                'SIP Amount': 'first',
                'Total Invested': 'last',
                'Portfolio Value': 'last',
                'Gain': 'last'
            }).reset_index()
            
            yearly_df['Year Return'] = yearly_df['Portfolio Value'].pct_change().fillna(0) * 100
            
            yearly_display = yearly_df.copy()
            yearly_display['SIP Amount'] = yearly_display['SIP Amount'].apply(lambda x: format_currency(x, currency_symbol))
            yearly_display['Total Invested'] = yearly_display['Total Invested'].apply(lambda x: format_currency(x, currency_symbol))
            yearly_display['Portfolio Value'] = yearly_display['Portfolio Value'].apply(lambda x: format_currency(x, currency_symbol))
            yearly_display['Gain'] = yearly_display['Gain'].apply(lambda x: format_currency(x, currency_symbol))
            yearly_display['Year Return'] = yearly_display['Year Return'].apply(lambda x: f"{x:.1f}%")
            
            st.dataframe(yearly_display, use_container_width=True, hide_index=True)
            
            # Charts
            st.markdown("---")
            st.markdown("### 📈 Visual Analysis")
            
            tab1, tab2, tab3 = st.tabs(["📈 Growth", "🥧 Breakdown", "📊 Yearly"])
            
            with tab1:
                fig = create_line_chart(
                    yearly_df['Year'].tolist(),
                    {
                        'Total Invested': yearly_df['Total Invested'].tolist(),
                        'Portfolio Value': yearly_df['Portfolio Value'].tolist()
                    },
                    'SIP Growth Over Years',
                    'Year',
                    f'Amount ({currency_symbol})'
                )
                st.plotly_chart(fig, use_container_width=True)
            
            with tab2:
                fig = create_pie_chart(
                    ['Invested', 'Gains'],
                    [total_invested, wealth_gained],
                    'Investment Breakdown'
                )
                st.plotly_chart(fig, use_container_width=True)
            
            with tab3:
                fig = create_bar_chart(
                    [f'Y{y}' for y in yearly_df['Year'].tolist()],
                    {
                        'Invested': yearly_df['Total Invested'].tolist(),
                        'Value': yearly_df['Portfolio Value'].tolist()
                    },
                    'Year-wise Growth',
                    f'Amount ({currency_symbol})'
                )
                st.plotly_chart(fig, use_container_width=True)
            
            # Download
            summary_dict = {
                'Starting SIP': format_currency(monthly_sip, currency_symbol),
                'Expected Return': f'{expected_return}%',
                'Period': f'{years} years',
                'Step-up': f'{step_up}%',
                'Total Invested': format_currency(total_invested, currency_symbol),
                'Future Value': format_currency(future_value, currency_symbol),
                'Wealth Gained': format_currency(wealth_gained, currency_symbol),
                'Total Returns': f'{(wealth_gained/total_invested)*100:.2f}%'
            }
            
            show_download_section("SIP Calculator", summary_dict, schedule_df, currency_symbol)
            
            add_to_history("SIP Calculator", summary_dict, {'Future Value': format_currency(future_value, currency_symbol)})
            
        except Exception as e:
            st.error(f"❌ Error: {e}")

# ═══════════════════════════════════════════════════════════════
#                    NPV CALCULATOR WITH SCHEDULE
# ═══════════════════════════════════════════════════════════════

elif calculator_type == "💹 NPV Calculator":
    st.markdown("""
    <div class="main-header">
        <h1>💹 NPV Calculator</h1>
        <p>With Detailed Cash Flow Schedule</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="formula-box">
        <strong>Formula:</strong> NPV = -C₀ + Σ[CFₜ / (1+r)^t]
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
        with cols[i % 5]:
            cf = st.number_input(f"Year {i+1}", min_value=0.0, value=30000.0, step=5000.0, key=f"cf_{i}")
            cash_flows.append(cf)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        calculate_btn = st.button("🔄 Calculate NPV", use_container_width=True, type="primary")
    
    if calculate_btn:
        st.session_state.show_downloads = False
        
        try:
            r = discount_rate / 100
            
            # Calculate NPV
            npv = -initial_investment
            
            schedule_data = []
            schedule_data.append({
                'Year': 0,
                'Cash Flow': -initial_investment,
                'Discount Factor': 1.0,
                'Present Value': -initial_investment,
                'Cumulative PV': -initial_investment
            })
            
            cumulative_pv = -initial_investment
            
            for t, cf in enumerate(cash_flows, 1):
                discount_factor = 1 / (1 + r) ** t
                pv = cf * discount_factor
                npv += pv
                cumulative_pv += pv
                
                schedule_data.append({
                    'Year': t,
                    'Cash Flow': cf,
                    'Discount Factor': discount_factor,
                    'Present Value': pv,
                    'Cumulative PV': cumulative_pv
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
            
            profitability_index = (npv + initial_investment) / initial_investment
            payback = initial_investment / np.mean(cash_flows) if np.mean(cash_flows) > 0 else 0
            
            # Result
            if npv > 0:
                st.markdown(f"""
                <div class="result-box">
                    ✅ NPV = {format_currency(npv, currency_symbol)} - ACCEPT PROJECT
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="result-box-error">
                    ❌ NPV = {format_currency(npv, currency_symbol)} - REJECT PROJECT
                </div>
                """, unsafe_allow_html=True)
            
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("NPV", format_currency(npv, currency_symbol))
            col2.metric("IRR", f"{irr*100:.2f}%")
            col3.metric("Profitability Index", f"{profitability_index:.2f}")
            col4.metric("Payback Period", f"{payback:.1f} yrs")
            
            # ═══════════════════════════════════════
            #         CASH FLOW SCHEDULE
            # ═══════════════════════════════════════
            
            st.markdown("---")
            st.markdown("### 📋 Discounted Cash Flow Schedule")
            
            display_df = schedule_df.copy()
            display_df['Cash Flow'] = display_df['Cash Flow'].apply(lambda x: format_currency(x, currency_symbol))
            display_df['Discount Factor'] = display_df['Discount Factor'].apply(lambda x: f"{x:.4f}")
            display_df['Present Value'] = display_df['Present Value'].apply(lambda x: format_currency(x, currency_symbol))
            display_df['Cumulative PV'] = display_df['Cumulative PV'].apply(lambda x: format_currency(x, currency_symbol))
            
            st.dataframe(display_df, use_container_width=True, hide_index=True)
            
            # Charts
            st.markdown("---")
            st.markdown("### 📈 Visual Analysis")
            
            tab1, tab2, tab3 = st.tabs(["📊 Cash Flows", "📈 NPV Profile", "🥧 Breakdown"])
            
            with tab1:
                fig = create_bar_chart(
                    [f'Y{y}' for y in schedule_df['Year'].tolist()],
                    {
                        'Cash Flow': schedule_df['Cash Flow'].tolist(),
                        'Present Value': schedule_df['Present Value'].tolist()
                    },
                    'Cash Flow vs Present Value',
                    f'Amount ({currency_symbol})'
                )
                st.plotly_chart(fig, use_container_width=True)
            
            with tab2:
                rates = list(range(0, 31, 2))
                npvs = []
                for rate in rates:
                    npv_temp = -initial_investment + sum(cf / (1 + rate/100) ** (t+1) for t, cf in enumerate(cash_flows))
                    npvs.append(npv_temp)
                
                fig = create_line_chart(
                    rates,
                    {'NPV': npvs},
                    'NPV Profile (NPV vs Discount Rate)',
                    'Discount Rate (%)',
                    f'NPV ({currency_symbol})'
                )
                st.plotly_chart(fig, use_container_width=True)
            
            with tab3:
                total_inflows = sum(cash_flows)
                fig = create_pie_chart(
                    ['Initial Investment', 'Present Value of Inflows'],
                    [initial_investment, npv + initial_investment],
                    'Investment Analysis'
                )
                st.plotly_chart(fig, use_container_width=True)
            
            # Download
            summary_dict = {
                'Initial Investment': format_currency(initial_investment, currency_symbol),
                'Discount Rate': f'{discount_rate}%',
                'Number of Years': num_years,
                'NPV': format_currency(npv, currency_symbol),
                'IRR': f'{irr*100:.2f}%',
                'Profitability Index': f'{profitability_index:.2f}',
                'Decision': 'ACCEPT' if npv > 0 else 'REJECT'
            }
            
            show_download_section("NPV Calculator", summary_dict, schedule_df, currency_symbol)
            
            add_to_history("NPV Calculator", summary_dict, {'NPV': format_currency(npv, currency_symbol)})
            
        except Exception as e:
            st.error(f"❌ Error: {e}")

# ═══════════════════════════════════════════════════════════════
#                    BOND VALUATION WITH SCHEDULE
# ═══════════════════════════════════════════════════════════════

elif calculator_type == "📜 Bond Valuation":
    st.markdown("""
    <div class="main-header">
        <h1>📜 Bond Valuation</h1>
        <p>With Coupon Payment Schedule</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="formula-box">
        <strong>Formula:</strong> Price = Σ[C/(1+y)^t] + F/(1+y)^n
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
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        calculate_btn = st.button("🔄 Calculate Bond Price", use_container_width=True, type="primary")
    
    if calculate_btn:
        st.session_state.show_downloads = False
        
        try:
            coupon_payment = (face_value * coupon_rate / 100) / m
            total_periods = years_to_maturity * m
            periodic_ytm = (ytm / 100) / m
            
            # Calculate with schedule
            schedule_data = []
            pv_coupons = 0
            
            for period in range(1, total_periods + 1):
                discount_factor = 1 / (1 + periodic_ytm) ** period
                pv_coupon = coupon_payment * discount_factor
                pv_coupons += pv_coupon
                
                year = (period - 1) / m + (1/m)
                
                schedule_data.append({
                    'Period': period,
                    'Year': round(year, 2),
                    'Coupon Payment': coupon_payment,
                    'Discount Factor': discount_factor,
                    'PV of Coupon': pv_coupon,
                    'Cumulative PV': pv_coupons
                })
            
            # Add face value
            pv_face = face_value / (1 + periodic_ytm) ** total_periods
            
            schedule_data.append({
                'Period': total_periods,
                'Year': years_to_maturity,
                'Coupon Payment': face_value,
                'Discount Factor': 1 / (1 + periodic_ytm) ** total_periods,
                'PV of Coupon': pv_face,
                'Cumulative PV': pv_coupons + pv_face
            })
            
            schedule_df = pd.DataFrame(schedule_data)
            
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
                st.success(f"📈 **Premium Bond** - Coupon Rate ({coupon_rate}%) > YTM ({ytm}%)")
            elif bond_price < face_value:
                st.warning(f"📉 **Discount Bond** - Coupon Rate ({coupon_rate}%) < YTM ({ytm}%)")
            else:
                st.info(f"➡️ **Par Bond** - Coupon Rate = YTM")
            
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Bond Price", format_currency(bond_price, currency_symbol))
            col2.metric("PV of Coupons", format_currency(pv_coupons, currency_symbol))
            col3.metric("PV of Face Value", format_currency(pv_face, currency_symbol))
            col4.metric("Current Yield", f"{current_yield:.2f}%")
            
            # ═══════════════════════════════════════
            #         COUPON SCHEDULE
            # ═══════════════════════════════════════
            
            st.markdown("---")
            st.markdown("### 📋 Coupon Payment Schedule")
            
            display_df = schedule_df.copy()
            display_df['Coupon Payment'] = display_df['Coupon Payment'].apply(lambda x: format_currency(x, currency_symbol))
            display_df['Discount Factor'] = display_df['Discount Factor'].apply(lambda x: f"{x:.4f}")
            display_df['PV of Coupon'] = display_df['PV of Coupon'].apply(lambda x: format_currency(x, currency_symbol))
            display_df['Cumulative PV'] = display_df['Cumulative PV'].apply(lambda x: format_currency(x, currency_symbol))
            
            st.dataframe(display_df, use_container_width=True, hide_index=True)
            
            # Charts
            st.markdown("---")
            st.markdown("### 📈 Visual Analysis")
            
            tab1, tab2, tab3 = st.tabs(["🥧 Breakdown", "📈 Price Sensitivity", "📊 Payments"])
            
            with tab1:
                fig = create_pie_chart(
                    ['PV of Coupons', 'PV of Face Value'],
                    [pv_coupons, pv_face],
                    'Bond Price Components'
                )
                st.plotly_chart(fig, use_container_width=True)
            
            with tab2:
                ytm_range = list(range(1, 21))
                prices = []
                for y in ytm_range:
                    py = (y / 100) / m
                    pv_c = sum(coupon_payment / (1 + py) ** t for t in range(1, total_periods + 1))
                    pv_f = face_value / (1 + py) ** total_periods
                    prices.append(pv_c + pv_f)
                
                fig = create_line_chart(
                    ytm_range,
                    {'Bond Price': prices},
                    'Bond Price vs YTM',
                    'YTM (%)',
                    f'Price ({currency_symbol})'
                )
                st.plotly_chart(fig, use_container_width=True)
            
            with tab3:
                fig = create_bar_chart(
                    [f'P{p}' for p in schedule_df['Period'].tolist()[:-1]],
                    {'PV of Coupons': schedule_df['PV of Coupon'].tolist()[:-1]},
                    'Present Value of Each Coupon',
                    f'PV ({currency_symbol})'
                )
                st.plotly_chart(fig, use_container_width=True)
            
            # Download
            summary_dict = {
                'Face Value': format_currency(face_value, currency_symbol),
                'Coupon Rate': f'{coupon_rate}%',
                'YTM': f'{ytm}%',
                'Years to Maturity': years_to_maturity,
                'Frequency': frequency,
                'Bond Price': format_currency(bond_price, currency_symbol),
                'PV of Coupons': format_currency(pv_coupons, currency_symbol),
                'PV of Face Value': format_currency(pv_face, currency_symbol),
                'Current Yield': f'{current_yield:.2f}%',
                'Bond Type': 'Premium' if bond_price > face_value else ('Discount' if bond_price < face_value else 'Par')
            }
            
            show_download_section("Bond Valuation", summary_dict, schedule_df, currency_symbol)
            
            add_to_history("Bond Valuation", summary_dict, {'Price': format_currency(bond_price, currency_symbol)})
            
        except Exception as e:
            st.error(f"❌ Error: {e}")

# ═══════════════════════════════════════════════════════════════
#                    HISTORY PAGE
# ═══════════════════════════════════════════════════════════════

elif calculator_type == "📋 History":
    st.markdown("""
    <div class="main-header">
        <h1>📋 Calculation History</h1>
    </div>
    """, unsafe_allow_html=True)
    
    if st.session_state.calculation_history:
        history_df = pd.DataFrame(st.session_state.calculation_history)
        st.dataframe(history_df, use_container_width=True, hide_index=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            csv = history_df.to_csv(index=False)
            st.download_button("📥 Download History", data=csv, file_name="history.csv", mime="text/csv", use_container_width=True)
        
        with col2:
            if st.button("🗑️ Clear History", use_container_width=True):
                st.session_state.calculation_history = []
                st.rerun()
    else:
        st.info("📝 No calculations yet!")

# ═══════════════════════════════════════════════════════════════
#                    FORMULAS PAGE
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
    Effective Rate = (1 + r/m)^m - 1
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
    IRR = Rate where NPV = 0
    ```
    
    ### 📜 Bond
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
    💰 Financial Calculator Pro | Made with ❤️ using Streamlit
</div>
""", unsafe_allow_html=True)
