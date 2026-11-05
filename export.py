"""Builds the downloadable Excel workbook (OpenPyXL engine)."""
import io
import pandas as pd
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.utils import get_column_letter
from .dataset import NOT_REPORTED, SOURCES
from .metrics import METRIC_LABELS


def _statement(df, labels, keys):
    t = df[[k for k in keys if k in df.columns]].T
    t.insert(0, "Line item", [labels.get(k, k) for k in t.index])
    return t.reset_index(drop=True)


def build_workbook(df, labels, m, recon, insights, years, basis):
    from .dataset import INCOME, BALANCE, CASHFLOW
    buf = io.BytesIO()
    met = m.loc[years, [c for c in METRIC_LABELS if c in m.columns]].T.round(4)
    met.insert(0, "Metric", [METRIC_LABELS[k] for k in met.index])
    ins = pd.DataFrame([(cat, t, x) for cat, items in insights.items() for t, x in items], columns=["Category", "Title", "Insight"])
    notes = pd.DataFrame([("Basis for return/turnover ratios", "Average of opening and closing balances" if basis == "average" else "Year-end balances"),
                          ("Units", "INR crore unless stated"), ("Scope", "Consolidated Ind AS statements only")]
                         + [(k, v) for k, v in NOT_REPORTED.items()] + [(y, SOURCES[y]) for y in years], columns=["Item", "Note"])
    with pd.ExcelWriter(buf, engine="openpyxl") as xw:
        for name, rows in (("Income Statement", INCOME), ("Balance Sheet", BALANCE), ("Cash Flow", CASHFLOW)):
            _statement(df.loc[years], labels, rows.keys()).to_excel(xw, sheet_name=name, index=False)
        met.reset_index(drop=True).to_excel(xw, sheet_name="Ratios & Metrics", index=False)
        recon.to_excel(xw, sheet_name="Data Checks", index=False)
        ins.to_excel(xw, sheet_name="Insights", index=False)
        notes.to_excel(xw, sheet_name="Notes", index=False)
        for ws in xw.book.worksheets:
            for c in ws[1]:
                c.font = Font(bold=True, color="FFFFFF"); c.fill = PatternFill("solid", fgColor="0B2A5B")
                c.alignment = Alignment(horizontal="center", wrap_text=True)
            for i, col in enumerate(ws.columns, 1):
                width = max(len(str(c.value)) if c.value is not None else 0 for c in col)
                ws.column_dimensions[get_column_letter(i)].width = min(max(12, width + 2), 70 if i <= 3 else 22)
            ws.freeze_panes = "B2"
    return buf.getvalue()
