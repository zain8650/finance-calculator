Professional Financial Analysis & Computation Suite
A premium dark-themed financial calculator built with Streamlit, featuring auto-calculation of missing values, complete amortization schedules, and professional export capabilities.
🚀 Features
📝 Simple Interest — Auto-calculate P, R, T, or I
📈 Compound Interest — Multi-frequency compounding
🏧 EMI Calculator — Full amortization schedule
💰 SIP Calculator — With annual step-up
📉 NPV Calculator — IRR & Profitability Index
📃 Bond Valuation — Premium/Discount/Par analysis
🔄 Annuity Calculator — Ordinary & Due
📋 Calculation History — Exportable records
📖 Formula Reference — Complete math library
📦 Installation
bash
Copy
pip install -r requirements.txt
🖥️ Run Locally
bash
Copy
streamlit run fincalc_pro.py
📁 File Structure
plain
Copy
.
├── fincalc_pro.py      # Main application
├── requirements.txt    # Dependencies
└── README.md           # This file
🛠️ Tech Stack
Frontend: Streamlit + Custom CSS (Glassmorphism)
Visualization: Plotly (dark theme charts)
Data Export: CSV, Excel (openpyxl), PDF (fpdf2), JSON
Math Engine: NumPy + Python standard library
📸 Screenshots
Dark premium UI with animated headers, glass cards, and interactive charts
📄 Exports
Every calculator supports downloading results in:
📄 CSV
📊 Excel
📑 PDF Report
🔗 JSON
⚠️ Note
fpdf2 is the maintained fork of fpdf. Please use fpdf2, not the old fpdf.
xlrd is not required since we only write Excel files (.xlsx) using openpyxl.
📝 License
MIT License — Free for personal and commercial use.
