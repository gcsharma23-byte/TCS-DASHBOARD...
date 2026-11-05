# TCS Financial Analytics Dashboard (Python · Streamlit · Plotly)

Interactive dashboard on Tata Consultancy Services' **consolidated** Ind AS financials, FY2022–FY2026
(FY2021 is held only as a base year for FY2022 growth and average-balance ratios). Amounts in ₹ crore.

## Run locally
```bash
cd tcs_dashboard
python -m venv .venv && source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py                                    # opens http://localhost:8501
```

## Project layout
```
app.py                       Streamlit app (7 pages, sidebar navigation + filters)
requirements.txt
.streamlit/config.toml       Navy/blue/white Streamlit theme
data/tcs_consolidated_financials.xlsx   Extracted statements (read with OpenPyXL)
tcs_fin/dataset.py           Extracted figures + source mapping + "not reported" notes
tcs_fin/loader.py            Excel loader + 19 reconciliation checks per year
tcs_fin/metrics.py           Margins, returns, liquidity, efficiency, solvency, cash-flow metrics
tcs_fin/insights.py          Automated, figure-backed insights and overall assessment
tcs_fin/charts.py            Plotly Express / Graph Objects figure builders
tcs_fin/export.py            Excel export of analysed data
scripts/build_dataset.py     Rebuilds the Excel file from dataset.py
tests/test_calculations.py   Independent formula / data / export tests (no Streamlit needed)
tests/smoke_test_stubbed.py  Runs app.py through every page & filter using stand-ins (see note)
```

## Pages and filters
Executive Summary (12 KPI cards with YoY deltas) · Revenue & Profitability · Balance Sheet · Ratio Analysis ·
Cash Flow · Financial Insights (incl. "Overall Financial Performance Assessment of TCS") · Data & Downloads.
Sidebar: financial-year dropdown, multi-year comparison, compare-against year, ratio basis (average / year-end),
currency unit (₹ crore / ₹ billion), per-page metric selectors, **Reset filters**, Excel/CSV download.

## Definitions (also shown in the app)
* **Operating profit** = revenue − employee − equipment & licence − depreciation − other expenses (excludes other income, finance cost, exceptional items).
* **Net profit** = profit attributable to shareholders. **ROCE** = (PBT before exceptionals + finance cost) / (total assets − current liabilities).
* **Debt** = lease liabilities (+ FY2026 Class B preference shares ₹126 cr); TCS reports no borrowings.
* **Free cash flow** = operating cash flow − (PPE + intangibles + ROU advances); acquisitions excluded.

## Not calculable (never fabricated)
Gross profit margin (TCS reports expenses by nature); classic debt-to-equity (no borrowings);
inventory turnover is computed but not meaningful (inventories ≈ 0.02% of assets); no US$ figures (no FX data supplied).

## Data provenance
FY2026/FY2025 from the FY2025-26 report; FY2024/FY2023 from FY2023-24; FY2022/FY2021 from FY2021-22 (consolidated only).
The FY2024-25 PDF's text layer drops digits, so FY2025 is taken from the clean comparative column in the FY2025-26 report.

## Tests
```bash
python tests/test_calculations.py
```
