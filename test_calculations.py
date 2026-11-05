"""Independent verification of data integrity, formulas and export. Needs only pandas/numpy/openpyxl.
Run:  python tests/test_calculations.py   (or: pytest tests)"""
import io, pathlib, sys
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
import numpy as np
from openpyxl import load_workbook
from tcs_fin.loader import load_statements, reconcile
from tcs_fin.metrics import compute_metrics, RATIOS
from tcs_fin.insights import build_insights, overall_assessment
from tcs_fin.export import build_workbook
from tcs_fin.fmt import indian

DATA = pathlib.Path(__file__).resolve().parents[1] / "data" / "tcs_consolidated_financials.xlsx"
df, labels, _ = load_statements(DATA)
Y = ["FY2022", "FY2023", "FY2024", "FY2025", "FY2026"]


def test_no_missing_and_reconciles():
    assert df.isna().sum().sum() == 0
    r = reconcile(df)
    assert (r.Status == "PASS").all(), r[r.Status == "FAIL"]


def test_hand_calculated_fy2026():
    m = compute_metrics(df, "closing")
    # computed by hand from the FY2025-26 statements
    assert m.op_profit["FY2026"] == 267021 - (154994 + 4399 + 5560 + 35230) == 66838
    assert abs(m.op_margin["FY2026"] - 66838 / 267021 * 100) < 1e-9
    assert abs(m.net_margin["FY2026"] - 49210 / 267021 * 100) < 1e-9
    assert abs(m.current_ratio["FY2026"] - 135705 / 60914) < 1e-9
    assert m.total_liabilities["FY2026"] == 182372 - 108478 == 73894
    assert abs(m.roe["FY2026"] - 49210 / 107240 * 100) < 1e-9
    assert abs(m.roce["FY2026"] - (70013 + 1227) / (182372 - 60914) * 100) < 1e-9
    assert m.fcf["FY2026"] == 52094 - (3670 + 367 + 109)
    assert abs(m.rev_growth["FY2026"] - (267021 / 255324 - 1) * 100) < 1e-9
    assert m.total_debt["FY2026"] == 9453 + 1830 + 126


def test_average_basis_and_base_year():
    m = compute_metrics(df, "average")
    assert abs(m.roe["FY2026"] - 49210 / ((107240 + 94756) / 2) * 100) < 1e-9
    assert np.isnan(m.roe["FY2021"])             # no prior year -> not fabricated
    assert not np.isnan(m.rev_growth["FY2022"])  # FY2022 growth uses FY2021 base


def test_gross_margin_not_fabricated():
    assert compute_metrics(df)["gross_margin"].isna().all()


def test_insights_and_assessment_run():
    m = compute_metrics(df)
    ins = build_insights(df, m, Y)
    assert ins["Potential concerns"] and ins["Positive trends"]
    table, text = overall_assessment(df, m, Y)
    assert len(table) == 6 and "₹" in text
    import re; bad = re.compile(r"\bnan\b", re.I)
    assert not bad.search(text) and not any(bad.search(t) for v in ins.values() for _, t in v)


def test_excel_export_roundtrip():
    m = compute_metrics(df)
    b = build_workbook(df, labels, m, reconcile(df), build_insights(df, m, Y), Y, "average")
    wb = load_workbook(io.BytesIO(b))
    assert wb.sheetnames == ["Income Statement", "Balance Sheet", "Cash Flow", "Ratios & Metrics", "Data Checks", "Insights", "Notes"]
    ws = wb["Income Statement"]
    assert [c.value for c in ws[1]] == ["Line item"] + Y
    assert ws["A2"].value == "Revenue from operations" and ws["F2"].value == 267021


def test_indian_format():
    assert indian(267021) == "2,67,021" and indian(1234567) == "12,34,567" and indian(-9108) == "-9,108" and indian(999) == "999"


if __name__ == "__main__":
    for n, f in list(globals().items()):
        if n.startswith("test_"):
            f(); print("PASS", n)
