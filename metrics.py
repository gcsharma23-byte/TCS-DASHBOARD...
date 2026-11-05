"""Financial metric and ratio calculations (pandas / NumPy). All money in INR crore."""
import numpy as np
import pandas as pd


def _bal(s, basis):
    """Balance used as denominator: average of opening+closing, or closing only."""
    return (s + s.shift(1)) / 2 if basis == "average" else s


def compute_metrics(df, basis="average"):
    """df: wide statements frame indexed by FY (incl. base year). Returns metrics frame, same index.
    The base year has NaN for anything needing a prior year."""
    m = pd.DataFrame(index=df.index)
    rev = df.revenue

    # ---- derived profit measures -------------------------------------------------
    m["revenue"] = rev
    m["op_profit"] = rev - (df.employee_cost + df.equipment_cost + df.depreciation + df.other_expenses)
    m["ebitda"] = m.op_profit + df.depreciation
    m["pbe"] = df.pbe
    m["pbt"] = df.pbt
    m["net_profit"] = df.pat_sh               # attributable to shareholders (basis for EPS/ROE)
    m["profit_for_year"] = df.pat
    m["eps"] = df.eps
    m["ebit_incl_other_income"] = df.pbe + df.finance_cost

    # ---- structure ---------------------------------------------------------------
    m["total_assets"] = df.total_assets
    m["total_liabilities"] = df.total_ncl + df.total_cl
    m["equity"] = df.equity_sh
    m["total_equity"] = df.total_equity
    m["current_assets"] = df.total_ca
    m["current_liabilities"] = df.total_cl
    m["cash"] = df.cash
    m["cash_liquid"] = df.cash + df.other_bank + df.ca_investments
    m["lease_liabilities"] = df.lease_nc + df.lease_c
    m["total_debt"] = m.lease_liabilities + df.ccps      # no borrowings are reported
    m["net_cash"] = m.cash_liquid - m.total_debt
    m["capital_employed"] = df.total_assets - df.total_cl

    # ---- growth ------------------------------------------------------------------
    for k, s in {"rev": rev, "op": m.op_profit, "np": m.net_profit, "eps": df.eps, "ta": df.total_assets}.items():
        m[f"{k}_growth"] = s.pct_change() * 100

    # ---- profitability -----------------------------------------------------------
    m["op_margin"] = m.op_profit / rev * 100
    m["ebitda_margin"] = m.ebitda / rev * 100
    m["net_margin"] = m.net_profit / rev * 100
    m["pbt_margin"] = df.pbt / rev * 100
    m["gross_margin"] = np.nan                            # not reported by TCS
    m["contribution_margin_proxy"] = (rev - df.employee_cost - df.equipment_cost) / rev * 100
    m["roa"] = m.net_profit / _bal(df.total_assets, basis) * 100
    m["roe"] = m.net_profit / _bal(df.equity_sh, basis) * 100
    m["roce"] = m.ebit_incl_other_income / _bal(m.capital_employed, basis) * 100
    m["tax_rate"] = df.total_tax / df.pbt * 100

    # ---- liquidity ---------------------------------------------------------------
    quick_assets = df.total_ca - df.inventories - df.ca_other - df.ca_tax_assets
    m["current_ratio"] = df.total_ca / df.total_cl
    m["quick_ratio"] = quick_assets / df.total_cl
    m["cash_ratio"] = m.cash_liquid / df.total_cl

    # ---- efficiency --------------------------------------------------------------
    m["asset_turnover"] = rev / _bal(df.total_assets, basis)
    m["inventory_turnover"] = df.equipment_cost / _bal(df.inventories, basis)
    m["dso"] = df.ca_receivables / rev * 365

    # ---- solvency ----------------------------------------------------------------
    m["debt_equity"] = m.total_debt / df.total_equity
    m["liabilities_equity"] = m.total_liabilities / df.total_equity
    m["equity_ratio"] = df.total_equity / df.total_assets * 100
    m["interest_coverage"] = m.op_profit / df.finance_cost

    # ---- cash flow ---------------------------------------------------------------
    m["cfo"], m["cfi"], m["cff"] = df.cfo, df.cfi, df.cff
    m["capex"] = df.capex_ppe + df.capex_intang + df.capex_rou
    m["fcf"] = df.cfo - m.capex
    m["fcf_after_leases"] = m.fcf - df.lease_repay
    m["cfo_to_np"] = df.cfo / m.net_profit * 100
    m["fcf_to_np"] = m.fcf / m.net_profit * 100
    m["payout"] = df.dividend_sh / m.net_profit * 100
    m["shareholder_returns"] = df.dividend_sh + df.buyback
    return m


# metadata used by the UI: key -> (label, unit-kind, higher_is_better, group)
RATIOS = {
    "gross_margin":        ("Gross Profit Margin", "%", True, "Profitability"),
    "op_margin":           ("Operating Profit Margin", "%", True, "Profitability"),
    "net_margin":          ("Net Profit Margin", "%", True, "Profitability"),
    "roa":                 ("Return on Assets (ROA)", "%", True, "Profitability"),
    "roe":                 ("Return on Equity (ROE)", "%", True, "Profitability"),
    "roce":                ("Return on Capital Employed (ROCE)", "%", True, "Profitability"),
    "current_ratio":       ("Current Ratio", "x", True, "Liquidity"),
    "quick_ratio":         ("Quick Ratio", "x", True, "Liquidity"),
    "asset_turnover":      ("Total Asset Turnover", "x", True, "Efficiency"),
    "inventory_turnover":  ("Inventory Turnover", "x", True, "Efficiency"),
    "dso":                 ("Receivable Days (DSO)", "days", False, "Efficiency"),
    "debt_equity":         ("Debt-to-Equity (incl. leases)", "x", False, "Solvency"),
    "interest_coverage":   ("Interest Coverage (EBIT / finance cost)", "x", True, "Solvency"),
}

FORMULAS = {
    "gross_margin": "Not calculable - TCS reports expenses by nature, with no cost-of-sales / gross profit line.",
    "op_margin": "Operating profit / Revenue. Operating profit = Revenue - employee - equipment & licence - depreciation - other expenses (excludes other income, finance cost, exceptional items).",
    "net_margin": "Profit attributable to shareholders / Revenue from operations.",
    "roa": "Profit attributable to shareholders / Total assets (average or year-end, per sidebar).",
    "roe": "Profit attributable to shareholders / Equity attributable to shareholders (average or year-end).",
    "roce": "(Profit before exceptional items & tax + Finance costs) / (Total assets - Current liabilities).",
    "current_ratio": "Total current assets / Total current liabilities.",
    "quick_ratio": "(Current assets - inventories - other current assets - current tax assets) / Current liabilities.",
    "asset_turnover": "Revenue / Total assets (average or year-end).",
    "inventory_turnover": "Cost of equipment & software licences / Inventories. Inventories are immaterial, so the ratio is not meaningful.",
    "dso": "Current trade receivables (billed + unbilled) / Revenue x 365.",
    "debt_equity": "(Lease liabilities + preference shares classed as liabilities) / Total equity. TCS has no borrowings.",
    "interest_coverage": "Operating profit / Finance costs.",
}

MEANING = {
    "gross_margin": "Would show profit left after direct costs of delivery; unavailable for TCS.",
    "op_margin": "Share of each rupee of revenue left after running costs; the core measure of delivery efficiency and pricing power.",
    "net_margin": "Share of revenue that reaches shareholders after all costs, other income, tax and exceptional items.",
    "roa": "How much profit each rupee of assets generates; dilutes when large cash/investment balances sit on the balance sheet.",
    "roe": "Return earned on shareholders' money; high values are supported by high margins and heavy payouts to shareholders.",
    "roce": "Return on all long-term capital deployed, regardless of how it is financed.",
    "current_ratio": "Ability to meet obligations due within a year from assets that convert to cash within a year.",
    "quick_ratio": "A stricter test of short-term liquidity that excludes inventories and prepaid-type items.",
    "asset_turnover": "Revenue generated per rupee of assets; falling values mean assets are growing faster than sales.",
    "inventory_turnover": "How quickly traded hardware/licence stock turns over; immaterial for a services business like TCS.",
    "dso": "Days of revenue tied up in customer receivables; rising values mean slower cash collection.",
    "debt_equity": "Reliance on debt-like funding versus owners' funds; lower means a more conservative structure.",
    "interest_coverage": "Times operating profit covers finance costs (mostly lease interest at TCS); higher is safer.",
}


METRIC_LABELS = {
    "revenue": "Revenue from operations", "op_profit": "Operating profit (EBIT excl. other income)", "ebitda": "EBITDA",
    "pbe": "Profit before exceptional items & tax", "pbt": "Profit before tax", "net_profit": "Net profit (attributable to shareholders)",
    "profit_for_year": "Profit for the year (incl. NCI)", "eps": "EPS (INR)", "ebit_incl_other_income": "Profit before exceptional & tax + finance cost",
    "total_assets": "Total assets", "total_liabilities": "Total liabilities", "equity": "Shareholders' equity",
    "total_equity": "Total equity (incl. NCI)", "current_assets": "Current assets", "current_liabilities": "Current liabilities",
    "cash": "Cash and cash equivalents", "cash_liquid": "Cash + bank balances + current investments",
    "lease_liabilities": "Lease liabilities", "total_debt": "Debt-like obligations (leases + preference shares)",
    "net_cash": "Net cash (liquid assets - debt-like obligations)", "capital_employed": "Capital employed (TA - CL)",
    "rev_growth": "Revenue growth (%)", "op_growth": "Operating profit growth (%)", "np_growth": "Net profit growth (%)",
    "eps_growth": "EPS growth (%)", "ta_growth": "Total assets growth (%)", "op_margin": "Operating profit margin (%)",
    "ebitda_margin": "EBITDA margin (%)", "net_margin": "Net profit margin (%)", "pbt_margin": "PBT margin (%)",
    "gross_margin": "Gross profit margin (%) - NOT REPORTED", "contribution_margin_proxy": "Revenue less employee & equipment costs (% proxy)",
    "roa": "ROA (%)", "roe": "ROE (%)", "roce": "ROCE (%)", "tax_rate": "Effective tax rate (%)",
    "current_ratio": "Current ratio (x)", "quick_ratio": "Quick ratio (x)", "cash_ratio": "Cash ratio (x)",
    "asset_turnover": "Total asset turnover (x)", "inventory_turnover": "Inventory turnover (x) - not meaningful",
    "dso": "Receivable days", "debt_equity": "Debt-to-equity (x)", "liabilities_equity": "Total liabilities / equity (x)",
    "equity_ratio": "Equity / total assets (%)", "interest_coverage": "Interest coverage (x)",
    "cfo": "Cash flow from operations", "cfi": "Cash flow from investing", "cff": "Cash flow from financing",
    "capex": "Capex (PPE + intangibles + ROU advances)", "fcf": "Free cash flow (CFO - capex)",
    "fcf_after_leases": "Free cash flow after lease repayments", "cfo_to_np": "CFO / net profit (%)",
    "fcf_to_np": "FCF / net profit (%)", "payout": "Dividend payout (% of net profit)",
    "shareholder_returns": "Dividends + buy-backs",
}
