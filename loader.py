"""Reads the Excel workbook (OpenPyXL via pandas) and reconciles the statements."""
import pandas as pd
import numpy as np

SHEETS = ["Income Statement", "Balance Sheet", "Cash Flow"]


def load_statements(path):
    """Return (wide DataFrame indexed by FY, label dict, raw sheets)."""
    raw = pd.read_excel(path, sheet_name=None, engine="openpyxl")
    frames, labels = [], {}
    for s in SHEETS:
        t = raw[s].copy()
        labels.update(dict(zip(t["Key"], t.iloc[:, 1])))
        frames.append(t.drop(columns=t.columns[1]).set_index("Key").T)
    df = pd.concat(frames, axis=1).apply(pd.to_numeric, errors="coerce")
    df.index.name = "Year"
    return df, labels, raw


def reconcile(df):
    """Arithmetic tie-outs. Returns DataFrame: Check, Year, Reported, Recomputed, Difference, Status."""
    c = lambda *k: df[list(k)].sum(axis=1)
    checks = {
        "Total income = revenue + other income": (df.total_income, c("revenue", "other_income"), 0),
        "Total expenses = sum of expense lines": (df.total_expenses, c("employee_cost", "equipment_cost", "finance_cost", "depreciation", "other_expenses"), 0),
        "PBE = total income - total expenses": (df.pbe, df.total_income - df.total_expenses, 0),
        "PBT = PBE - exceptional items": (df.pbt, df.pbe - df.exceptional, 0),
        "Total tax = current + deferred": (df.total_tax, c("current_tax", "deferred_tax"), 0),
        "Profit = PBT - tax": (df.pat, df.pbt - df.total_tax, 0),
        "Profit = shareholders + NCI": (df.pat, c("pat_sh", "pat_nci"), 0),
        "EPS = shareholder profit / weighted shares": (df.eps, df.pat_sh / df.shares_cr, 0.02),
        "Total non-current assets = sum": (df.total_nca, c("ppe", "cwip", "rou", "goodwill", "intangibles", "nca_investments", "nca_receivables", "nca_loans", "nca_other_fin", "dta", "nca_tax_assets", "nca_other"), 0),
        "Total current assets = sum": (df.total_ca, c("inventories", "ca_investments", "ca_receivables", "cash", "other_bank", "ca_loans", "ca_other_fin", "ca_tax_assets", "ca_other"), 0),
        "Total assets = NCA + CA": (df.total_assets, c("total_nca", "total_ca"), 0),
        "Shareholder equity = capital + other equity": (df.equity_sh, c("share_capital", "other_equity"), 0),
        "Total equity = shareholders + NCI": (df.total_equity, c("equity_sh", "nci"), 0),
        "Total non-current liabilities = sum": (df.total_ncl, c("ccps", "lease_nc", "other_fin_nc", "emp_nc", "dtl", "unearned_nc"), 0),
        "Total current liabilities = sum": (df.total_cl, c("lease_c", "trade_payables", "other_fin_c", "unearned_c", "other_liab_c", "provisions", "emp_c", "tax_liab"), 0),
        "Balance sheet balances (A = E + L)": (df.total_assets, c("total_equity", "total_ncl", "total_cl"), 0),
        "Cash flow: opening + net change + FX = closing": (df.cash_end, c("cash_begin", "net_change_cash", "fx_effect"), 0),
        "Cash flow: CFO + CFI + CFF = net change": (df.net_change_cash, c("cfo", "cfi", "cff"), 0),
        "Cash flow closing cash = balance sheet cash": (df.cash_end, df.cash, 0),
    }
    rows = []
    for name, (rep, calc, tol) in checks.items():
        for y in df.index:
            diff = float(rep[y] - calc[y])
            ok = abs(diff) <= tol
            rows.append([name, y, float(rep[y]), float(calc[y]), diff, "PASS" if ok else "FAIL"])
    return pd.DataFrame(rows, columns=["Check", "Year", "Reported", "Recomputed", "Difference", "Status"])
