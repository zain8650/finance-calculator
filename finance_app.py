import streamlit as st
import math
import pandas as pd

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
#                    CUSTOM CSS STYLING
# ═══════════════════════════════════════════════════════════════

st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        color: #1E88E5;
        margin-bottom: 2rem;
    }
    
    .sub-header {
        font-size: 1.5rem;
        color: #424242;
        text-align: center;
        margin-bottom: 2rem;
    }
    
    .result-box {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 20px;
        border-radius: 15px;
        color: white;
        text-align: center;
        font-size: 1.5rem;
        margin: 20px 0;
    }
    
    .formula-box {
        background-color: #f5f5f5;
        padding: 15px;
        border-radius: 10px;
        border-left: 5px solid #1E88E5;
        font-family: monospace;
        margin: 10px 0;
    }
    
    .info-box {
        background-color: #e3f2fd;
        padding: 15px;
        border-radius: 10px;
        margin: 10px 0;
    }
    
    .success-box {
        background-color: #c8e6c9;
        padding: 15px;
        border-radius: 10px;
        margin: 10px 0;
    }
    
    .warning-box {
        background-color: #fff3e0;
        padding: 15px;
        border-radius: 10px;
        margin: 10px 0;
    }
    
    .stMetric {
        background-color: #f8f9fa;
        padding: 15px;
        border-radius: 10px;
    }
</style>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════
#                    HELPER FUNCTIONS
# ═══════════════════════════════════════════════════════════════

def format_currency(value, symbol="$"):
    """Format number as currency"""
    if value is None:
        return "?"
    return f"{symbol}{value:,.2f}"

def format_percent(value):
    """Format number as percentage"""
    if value is None:
        return "?"
    return f"{value:.4f}%"

def get_frequency_options():
    """Return frequency options"""
    return {
        "Annually (1/year)": 1,
        "Semi-Annually (2/year)": 2,
        "Quarterly (4/year)": 4,
        "Monthly (12/year)": 12,
        "Daily (365/year)": 365
    }

# ═══════════════════════════════════════════════════════════════
#                    SIDEBAR NAVIGATION
# ═══════════════════════════════════════════════════════════════

st.sidebar.markdown("## 💰 Financial Calculator")
st.sidebar.markdown("---")

calculator_type = st.sidebar.selectbox(
    "📊 Select Calculator",
    [
        "🏠 Home",
        "📐 Simple Interest",
        "📈 Compound Interest",
        "🏦 EMI / Loan Calculator",
        "💎 Annuity Calculator",
        "💹 NPV Calculator",
        "📜 Bond Valuation",
        "📋 Formula Reference"
    ]
)

st.sidebar.markdown("---")
currency_symbol = st.sidebar.selectbox("💵 Currency", ["$", "₹", "€", "£", "¥"])
st.sidebar.markdown("---")
st.sidebar.info("💡 Enter known values, leave unknown field as 0 or empty to calculate it.")

# ═══════════════════════════════════════════════════════════════
#                    HOME PAGE
# ═══════════════════════════════════════════════════════════════

if calculator_type == "🏠 Home":
    st.markdown('<h1 class="main-header">💰 Financial Calculator Pro</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Professional Finance Calculations Made Easy</p>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        ### 📐 Simple Interest
        - Calculate Interest
        - Find Principal
        - Determine Rate
        - Calculate Time
        """)
        
        st.markdown("""
        ### 🏦 EMI Calculator
        - Loan EMI
        - Amortization Schedule
        - Multiple Frequencies
        """)
    
    with col2:
        st.markdown("""
        ### 📈 Compound Interest
        - Future Value
        - Present Value
        - Interest Rate
        - Time Period
        """)
        
        st.markdown("""
        ### 💎 Annuity
        - Present Value
        - Future Value
        - Ordinary & Due
        """)
    
    with col3:
        st.markdown("""
        ### 💹 NPV Analysis
        - Net Present Value
        - IRR Calculation
        - Profitability Index
        """)
        
        st.markdown("""
        ### 📜 Bond Valuation
        - Bond Price
        - Yield to Maturity
        - Premium/Discount
        """)
    
    st.markdown("---")
    st.success("👈 Select a calculator from the sidebar to get started!")

# ═══════════════════════════════════════════════════════════════
#                    SIMPLE INTEREST
# ═══════════════════════════════════════════════════════════════

elif calculator_type == "📐 Simple Interest":
    st.markdown("## 📐 Simple Interest Calculator")
    
    st.markdown("""
    <div class="formula-box">
        <strong>Formula:</strong> I = (P × R × T) / 100
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("### Enter Known Values (Leave ONE field as 0 to calculate)")
    
    col1, col2 = st.columns(2)
    
    with col1:
        P = st.number_input(f"💰 Principal (P) [{currency_symbol}]", min_value=0.0, value=0.0, step=100.0)
        R = st.number_input("📊 Rate (R) [%]", min_value=0.0, value=0.0, step=0.1)
    
    with col2:
        T = st.number_input("⏰ Time (T) [Years]", min_value=0.0, value=0.0, step=0.5)
        I = st.number_input(f"💵 Interest (I) [{currency_symbol}]", min_value=0.0, value=0.0, step=100.0)
    
    if st.button("🔄 Calculate", key="si_calc"):
        values = [P, R, T, I]
        zeros = values.count(0)
        
        if zeros == 0:
            st.warning("⚠️ All values provided! Leave ONE field as 0 to calculate it.")
        elif zeros > 1:
            st.error(f"❌ {zeros} fields are empty! Fill at least 3 values.")
        else:
            try:
                if P == 0:
                    P = (I * 100) / (R * T)
                    result_label = "Principal (P)"
                    result_value = P
                elif R == 0:
                    R = (I * 100) / (P * T)
                    result_label = "Rate (R)"
                    result_value = R
                    result_value_display = f"{R:.4f}%"
                elif T == 0:
                    T = (I * 100) / (P * R)
                    result_label = "Time (T)"
                    result_value = T
                elif I == 0:
                    I = (P * R * T) / 100
                    result_label = "Interest (I)"
                    result_value = I
                
                # Display Result
                st.markdown(f"""
                <div class="result-box">
                    ✅ Calculated {result_label} = {format_currency(result_value, currency_symbol) if result_label != "Rate (R)" and result_label != "Time (T)" else (f"{result_value:.4f}%" if result_label == "Rate (R)" else f"{result_value:.2f} years")}
                </div>
                """, unsafe_allow_html=True)
                
                # Summary Table
                st.markdown("### 📋 Complete Summary")
                summary_df = pd.DataFrame({
                    "Variable": ["Principal (P)", "Rate (R)", "Time (T)", "Interest (I)", "Total Amount (P+I)"],
                    "Value": [
                        format_currency(P, currency_symbol),
                        f"{R:.4f}%",
                        f"{T:.2f} years",
                        format_currency(I, currency_symbol),
                        format_currency(P + I, currency_symbol)
                    ]
                })
                st.table(summary_df)
                
            except ZeroDivisionError:
                st.error("❌ Cannot divide by zero! Check your inputs.")
            except Exception as e:
                st.error(f"❌ Error: {e}")

# ═══════════════════════════════════════════════════════════════
#                    COMPOUND INTEREST
# ═══════════════════════════════════════════════════════════════

elif calculator_type == "📈 Compound Interest":
    st.markdown("## 📈 Compound Interest Calculator")
    
    st.markdown("""
    <div class="formula-box">
        <strong>Formula:</strong> FV = PV × (1 + r/m)^(n×m)
    </div>
    """, unsafe_allow_html=True)
    
    # Frequency Selection
    freq_options = get_frequency_options()
    frequency = st.selectbox("📅 Compounding Frequency", list(freq_options.keys()))
    m = freq_options[frequency]
    
    st.markdown("### Enter Known Values (Leave ONE field as 0 to calculate)")
    
    col1, col2 = st.columns(2)
    
    with col1:
        PV = st.number_input(f"💰 Present Value (PV) [{currency_symbol}]", min_value=0.0, value=0.0, step=100.0)
        FV = st.number_input(f"💵 Future Value (FV) [{currency_symbol}]", min_value=0.0, value=0.0, step=100.0)
    
    with col2:
        r = st.number_input("📊 Annual Rate (r) [%]", min_value=0.0, value=0.0, step=0.1)
        n = st.number_input("⏰ Years (n)", min_value=0.0, value=0.0, step=0.5)
    
    if st.button("🔄 Calculate", key="ci_calc"):
        values = [PV, FV, r, n]
        zeros = values.count(0)
        
        if zeros == 0:
            st.warning("⚠️ All values provided! Leave ONE field as 0.")
        elif zeros > 1:
            st.error(f"❌ Fill at least 3 values!")
        else:
            try:
                if PV == 0:
                    r_periodic = (r / 100) / m
                    total_periods = n * m
                    PV = FV / ((1 + r_periodic) ** total_periods)
                    result_label = "Present Value (PV)"
                    result_value = PV
                    
                elif FV == 0:
                    r_periodic = (r / 100) / m
                    total_periods = n * m
                    FV = PV * ((1 + r_periodic) ** total_periods)
                    result_label = "Future Value (FV)"
                    result_value = FV
                    
                elif r == 0:
                    total_periods = n * m
                    r_periodic = (FV / PV) ** (1 / total_periods) - 1
                    r = r_periodic * m * 100
                    result_label = "Annual Rate (r)"
                    result_value = r
                    
                elif n == 0:
                    r_periodic = (r / 100) / m
                    n = math.log(FV / PV) / (m * math.log(1 + r_periodic))
                    result_label = "Years (n)"
                    result_value = n
                
                # Calculate additional metrics
                total_periods = n * m
                compound_interest = FV - PV
                effective_rate = ((1 + (r/100)/m) ** m - 1) * 100
                
                # Result Display
                if result_label in ["Present Value (PV)", "Future Value (FV)"]:
                    display_val = format_currency(result_value, currency_symbol)
                elif result_label == "Annual Rate (r)":
                    display_val = f"{result_value:.4f}%"
                else:
                    display_val = f"{result_value:.2f} years"
                
                st.markdown(f"""
                <div class="result-box">
                    ✅ Calculated {result_label} = {display_val}
                </div>
                """, unsafe_allow_html=True)
                
                # Metrics
                col1, col2, col3, col4 = st.columns(4)
                col1.metric("Present Value", format_currency(PV, currency_symbol))
                col2.metric("Future Value", format_currency(FV, currency_symbol))
                col3.metric("Compound Interest", format_currency(compound_interest, currency_symbol))
                col4.metric("Effective Rate", f"{effective_rate:.2f}%")
                
                # Summary Table
                st.markdown("### 📋 Complete Summary")
                summary_df = pd.DataFrame({
                    "Variable": [
                        "Present Value (PV)", "Future Value (FV)", 
                        "Annual Rate (r)", "Years (n)",
                        "Compounding", "Total Periods",
                        "Periodic Rate", "Compound Interest",
                        "Effective Annual Rate"
                    ],
                    "Value": [
                        format_currency(PV, currency_symbol),
                        format_currency(FV, currency_symbol),
                        f"{r:.4f}%",
                        f"{n:.2f} years",
                        frequency,
                        f"{total_periods:.0f} periods",
                        f"{r/m:.4f}%",
                        format_currency(compound_interest, currency_symbol),
                        f"{effective_rate:.4f}%"
                    ]
                })
                st.table(summary_df)
                
                # Growth Chart
                if n > 0 and n <= 50:
                    st.markdown("### 📊 Growth Over Time")
                    r_periodic = (r / 100) / m
                    periods = list(range(int(total_periods) + 1))
                    values = [PV * (1 + r_periodic) ** p for p in periods]
                    
                    chart_df = pd.DataFrame({
                        "Period": periods,
                        "Value": values
                    })
                    st.line_chart(chart_df.set_index("Period"))
                
            except Exception as e:
                st.error(f"❌ Error: {e}")

# ═══════════════════════════════════════════════════════════════
#                    EMI CALCULATOR
# ═══════════════════════════════════════════════════════════════

elif calculator_type == "🏦 EMI / Loan Calculator":
    st.markdown("## 🏦 EMI / Loan Calculator")
    
    st.markdown("""
    <div class="formula-box">
        <strong>Formula:</strong> EMI = P × r × (1+r)^n / [(1+r)^n - 1]
    </div>
    """, unsafe_allow_html=True)
    
    # Payment Frequency
    freq_options = {
        "Monthly (12/year)": 12,
        "Quarterly (4/year)": 4,
        "Semi-Annually (2/year)": 2,
        "Annually (1/year)": 1
    }
    frequency = st.selectbox("📅 Payment Frequency", list(freq_options.keys()))
    m = freq_options[frequency]
    
    st.markdown("### Enter Loan Details")
    
    col1, col2 = st.columns(2)
    
    with col1:
        P = st.number_input(f"💰 Loan Amount [{currency_symbol}]", min_value=0.0, value=100000.0, step=1000.0)
        R = st.number_input("📊 Annual Interest Rate [%]", min_value=0.0, value=10.0, step=0.1)
    
    with col2:
        T = st.number_input("⏰ Loan Tenure [Years]", min_value=0.1, value=5.0, step=0.5)
        
    if st.button("🔄 Calculate EMI", key="emi_calc"):
        try:
            n_periods = int(T * m)
            r_periodic = (R / 100) / m
            
            if r_periodic == 0:
                EMI = P / n_periods
            else:
                EMI = P * r_periodic * (1 + r_periodic)**n_periods / ((1 + r_periodic)**n_periods - 1)
            
            total_payment = EMI * n_periods
            total_interest = total_payment - P
            
            # Result Display
            st.markdown(f"""
            <div class="result-box">
                💳 Your {frequency.split()[0]} Payment: {format_currency(EMI, currency_symbol)}
            </div>
            """, unsafe_allow_html=True)
            
            # Metrics
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("EMI", format_currency(EMI, currency_symbol))
            col2.metric("Total Payment", format_currency(total_payment, currency_symbol))
            col3.metric("Total Interest", format_currency(total_interest, currency_symbol))
            col4.metric("Interest %", f"{(total_interest/P)*100:.2f}%")
            
            # Pie Chart
            st.markdown("### 📊 Payment Breakdown")
            pie_df = pd.DataFrame({
                "Component": ["Principal", "Interest"],
                "Amount": [P, total_interest]
            })
            
            col1, col2 = st.columns(2)
            with col1:
                st.bar_chart(pie_df.set_index("Component"))
            
            with col2:
                st.markdown(f"""
                **Loan Summary:**
                - Principal: {format_currency(P, currency_symbol)}
                - Total Interest: {format_currency(total_interest, currency_symbol)}
                - Total Payment: {format_currency(total_payment, currency_symbol)}
                - Number of Payments: {n_periods}
                """)
            
            # Amortization Schedule
            st.markdown("### 📋 Amortization Schedule")
            
            schedule_data = []
            balance = P
            
            for period in range(1, n_periods + 1):
                interest_payment = balance * r_periodic
                principal_payment = EMI - interest_payment
                balance = max(0, balance - principal_payment)
                
                schedule_data.append({
                    "Period": period,
                    "Payment": EMI,
                    "Principal": principal_payment,
                    "Interest": interest_payment,
                    "Balance": balance
                })
            
            schedule_df = pd.DataFrame(schedule_data)
            schedule_df["Payment"] = schedule_df["Payment"].apply(lambda x: format_currency(x, currency_symbol))
            schedule_df["Principal"] = schedule_df["Principal"].apply(lambda x: format_currency(x, currency_symbol))
            schedule_df["Interest"] = schedule_df["Interest"].apply(lambda x: format_currency(x, currency_symbol))
            schedule_df["Balance"] = schedule_df["Balance"].apply(lambda x: format_currency(x, currency_symbol))
            
            st.dataframe(schedule_df, use_container_width=True)
            
            # Download Button
            csv = schedule_df.to_csv(index=False)
            st.download_button(
                label="📥 Download Amortization Schedule",
                data=csv,
                file_name="amortization_schedule.csv",
                mime="text/csv"
            )
            
        except Exception as e:
            st.error(f"❌ Error: {e}")

# ═══════════════════════════════════════════════════════════════
#                    ANNUITY CALCULATOR
# ═══════════════════════════════════════════════════════════════

elif calculator_type == "💎 Annuity Calculator":
    st.markdown("## 💎 Annuity Calculator")
    
    st.markdown("""
    <div class="formula-box">
        <strong>PV Formula:</strong> PV = PMT × [1 - (1+r)^-n] / r<br>
        <strong>FV Formula:</strong> FV = PMT × [(1+r)^n - 1] / r
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        annuity_type = st.radio("Annuity Type", ["Ordinary Annuity (End)", "Annuity Due (Beginning)"])
        is_due = "Due" in annuity_type
    
    with col2:
        freq_options = get_frequency_options()
        frequency = st.selectbox("📅 Payment Frequency", list(freq_options.keys()))
        m = freq_options[frequency]
    
    st.markdown("### Enter Known Values")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        PMT = st.number_input(f"💵 Payment (PMT) [{currency_symbol}]", min_value=0.0, value=1000.0, step=100.0)
        r = st.number_input("📊 Annual Rate [%]", min_value=0.0, value=8.0, step=0.1)
    
    with col2:
        T = st.number_input("⏰ Years", min_value=0.1, value=10.0, step=0.5)
    
    calc_type = st.radio("What to Calculate?", ["Present Value (PV)", "Future Value (FV)", "Payment (PMT)"])
    
    if st.button("🔄 Calculate", key="annuity_calc"):
        try:
            r_periodic = (r / 100) / m
            n_periods = T * m
            
            if calc_type == "Present Value (PV)":
                if r_periodic == 0:
                    PV = PMT * n_periods
                else:
                    PV = PMT * (1 - (1 + r_periodic)**(-n_periods)) / r_periodic
                    if is_due:
                        PV *= (1 + r_periodic)
                
                st.markdown(f"""
                <div class="result-box">
                    ✅ Present Value = {format_currency(PV, currency_symbol)}
                </div>
                """, unsafe_allow_html=True)
                
            elif calc_type == "Future Value (FV)":
                if r_periodic == 0:
                    FV = PMT * n_periods
                else:
                    FV = PMT * ((1 + r_periodic)**n_periods - 1) / r_periodic
                    if is_due:
                        FV *= (1 + r_periodic)
                
                st.markdown(f"""
                <div class="result-box">
                    ✅ Future Value = {format_currency(FV, currency_symbol)}
                </div>
                """, unsafe_allow_html=True)
            
            # Summary
            total_payments = PMT * n_periods
            st.metric("Total Payments", format_currency(total_payments, currency_symbol))
            
        except Exception as e:
            st.error(f"❌ Error: {e}")

# ═══════════════════════════════════════════════════════════════
#                    NPV CALCULATOR
# ═══════════════════════════════════════════════════════════════

elif calculator_type == "💹 NPV Calculator":
    st.markdown("## 💹 NPV Calculator")
    
    st.markdown("""
    <div class="formula-box">
        <strong>Formula:</strong> NPV = -C₀ + Σ [CFₜ / (1 + r)^t]
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        initial = st.number_input(f"💰 Initial Investment [{currency_symbol}]", min_value=0.0, value=100000.0, step=1000.0)
    
    with col2:
        rate = st.number_input("📊 Discount Rate [%]", min_value=0.0, value=10.0, step=0.5)
    
    with col3:
        years = st.number_input("⏰ Number of Years", min_value=1, value=5, step=1)
    
    st.markdown("### Enter Annual Cash Flows")
    
    cash_flows = []
    cols = st.columns(min(years, 5))
    
    for i in range(years):
        col_index = i % 5
        with cols[col_index]:
            cf = st.number_input(f"Year {i+1}", min_value=0.0, value=30000.0, step=1000.0, key=f"cf_{i}")
            cash_flows.append(cf)
    
    if st.button("🔄 Calculate NPV", key="npv_calc"):
        try:
            r = rate / 100
            npv = -initial
            pv_list = []
            
            for t, cf in enumerate(cash_flows, 1):
                pv = cf / (1 + r) ** t
                pv_list.append(pv)
                npv += pv
            
            # NPV Result
            if npv > 0:
                st.markdown(f"""
                <div class="result-box" style="background: linear-gradient(135deg, #4CAF50, #8BC34A);">
                    ✅ NPV = {format_currency(npv, currency_symbol)} - ACCEPT PROJECT
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="result-box" style="background: linear-gradient(135deg, #f44336, #ff5722);">
                    ❌ NPV = {format_currency(npv, currency_symbol)} - REJECT PROJECT
                </div>
                """, unsafe_allow_html=True)
            
            # Cash Flow Table
            cf_df = pd.DataFrame({
                "Year": [0] + list(range(1, years + 1)),
                "Cash Flow": [f"-{format_currency(initial, currency_symbol)}"] + [format_currency(cf, currency_symbol) for cf in cash_flows],
                "Present Value": [f"-{format_currency(initial, currency_symbol)}"] + [format_currency(pv, currency_symbol) for pv in pv_list]
            })
            
            st.dataframe(cf_df, use_container_width=True)
            
            # Metrics
            col1, col2, col3 = st.columns(3)
            col1.metric("Total Cash Inflows", format_currency(sum(cash_flows), currency_symbol))
            col2.metric("Total PV of Inflows", format_currency(sum(pv_list), currency_symbol))
            col3.metric("Profitability Index", f"{sum(pv_list)/initial:.4f}")
            
        except Exception as e:
            st.error(f"❌ Error: {e}")

# ═══════════════════════════════════════════════════════════════
#                    BOND CALCULATOR
# ═══════════════════════════════════════════════════════════════

elif calculator_type == "📜 Bond Valuation":
    st.markdown("## 📜 Bond Valuation Calculator")
    
    st.markdown("""
    <div class="formula-box">
        <strong>Formula:</strong> Price = Σ[C/(1+y)^t] + F/(1+y)^n
    </div>
    """, unsafe_allow_html=True)
    
    freq_options = {
        "Annual (1/year)": 1,
        "Semi-Annual (2/year)": 2,
        "Quarterly (4/year)": 4
    }
    frequency = st.selectbox("📅 Coupon Frequency", list(freq_options.keys()))
    m = freq_options[frequency]
    
    col1, col2 = st.columns(2)
    
    with col1:
        F = st.number_input(f"💵 Face Value [{currency_symbol}]", min_value=0.0, value=1000.0, step=100.0)
        C = st.number_input("📊 Coupon Rate [%]", min_value=0.0, value=8.0, step=0.1)
    
    with col2:
        Y = st.number_input("📈 Yield to Maturity [%]", min_value=0.0, value=10.0, step=0.1)
        T = st.number_input("⏰ Years to Maturity", min_value=0.1, value=10.0, step=0.5)
    
    if st.button("🔄 Calculate Bond Price", key="bond_calc"):
        try:
            n_periods = int(T * m)
            coupon_payment = (F * (C / 100)) / m
            y_periodic = (Y / 100) / m
            
            # PV of coupons
            pv_coupons = sum(coupon_payment / (1 + y_periodic)**t for t in range(1, n_periods + 1))
            
            # PV of face value
            pv_face = F / (1 + y_periodic) ** n_periods
            
            # Bond Price
            bond_price = pv_coupons + pv_face
            
            # Result
            st.markdown(f"""
            <div class="result-box">
                📜 Bond Price = {format_currency(bond_price, currency_symbol)}
            </div>
            """, unsafe_allow_html=True)
            
            # Bond Type
            if bond_price > F:
                st.success(f"📈 **Premium Bond** - Price ({format_currency(bond_price, currency_symbol)}) > Face Value ({format_currency(F, currency_symbol)})")
            elif bond_price < F:
                st.warning(f"📉 **Discount Bond** - Price ({format_currency(bond_price, currency_symbol)}) < Face Value ({format_currency(F, currency_symbol)})")
            else:
                st.info(f"➡️ **Par Bond** - Price = Face Value")
            
            # Metrics
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Bond Price", format_currency(bond_price, currency_symbol))
            col2.metric("PV of Coupons", format_currency(pv_coupons, currency_symbol))
            col3.metric("PV of Face Value", format_currency(pv_face, currency_symbol))
            col4.metric("Current Yield", f"{(coupon_payment * m / bond_price) * 100:.2f}%")
            
        except Exception as e:
            st.error(f"❌ Error: {e}")

# ═══════════════════════════════════════════════════════════════
#                    FORMULA REFERENCE
# ═══════════════════════════════════════════════════════════════

elif calculator_type == "📋 Formula Reference":
    st.markdown("## 📋 Formula Reference Sheet")
    
    st.markdown("""
    ### 📐 Simple Interest
    ```
    I = (P × R × T) / 100
    Where: P = Principal, R = Rate(%), T = Time(years)
    ```
    
    ### 📈 Compound Interest
    ```
    FV = PV × (1 + r/m)^(n×m)
    Effective Rate = (1 + r/m)^m - 1
    Where: m = compounding frequency per year
    ```
    
    ### 🏦 EMI Formula
    ```
    EMI = P × r × (1+r)^n / [(1+r)^n - 1]
    Where: r = periodic rate, n = total periods
    ```
    
    ### 💎 Annuity
    ```
    PV = PMT × [1 - (1+r)^-n] / r    (Ordinary)
    FV = PMT × [(1+r)^n - 1] / r     (Ordinary)
    For Annuity Due: Multiply by (1+r)
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
    
    st.markdown("### 📅 Compounding Frequencies")
    freq_df = pd.DataFrame({
        "Frequency": ["Annual", "Semi-Annual", "Quarterly", "Monthly", "Daily"],
        "Per Year (m)": [1, 2, 4, 12, 365],
        "Periodic Rate": ["r/1", "r/2", "r/4", "r/12", "r/365"]
    })
    st.table(freq_df)

# ═══════════════════════════════════════════════════════════════
#                    FOOTER
# ═══════════════════════════════════════════════════════════════

st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #888;">
    💰 Financial Calculator Pro | Made with ❤️ using Streamlit
</div>
""", unsafe_allow_html=True)