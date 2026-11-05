"""Writes data/tcs_consolidated_financials.xlsx from tcs_fin/dataset.py (run from project root)."""
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.utils import get_column_letter
from tcs_fin import dataset as d

OUT = pathlib.Path(__file__).resolve().parents[1] / "data" / "tcs_consolidated_financials.xlsx"

wb = Workbook(); wb.remove(wb.active)
for sheet, rows in d.all_statements().items():
    ws = wb.create_sheet(sheet)
    ws.append(["Key", "Line item (INR crore unless stated)"] + d.YEARS)
    for key, (label, vals) in rows.items():
        ws.append([key, label] + vals)
    for c in ws[1]:
        c.font = Font(bold=True, color="FFFFFF"); c.fill = PatternFill("solid", fgColor="0B2A5B")
        c.alignment = Alignment(horizontal="center")
    ws.column_dimensions["A"].width = 18; ws.column_dimensions["B"].width = 58
    for i in range(3, 3 + len(d.YEARS)):
        ws.column_dimensions[get_column_letter(i)].width = 13
        for cell in ws[get_column_letter(i)][1:]:
            cell.number_format = "#,##0.00" if ws.cell(cell.row, 1).value in ("eps", "shares_cr") else "#,##0"
    ws.freeze_panes = "C2"

ws = wb.create_sheet("Sources & Notes")
ws.append(["Year", "Source"])
for y in d.YEARS: ws.append([y, d.SOURCES[y]])
ws.append([]); ws.append(["Metric", "Availability note"])
for k, v in d.NOT_REPORTED.items(): ws.append([k, v])
ws.column_dimensions["A"].width = 38; ws.column_dimensions["B"].width = 140
wb.save(OUT); print("written", OUT)
