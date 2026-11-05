"""TCS Financial Analytics Dashboard - single-file deployment (code + data embedded). Run: streamlit run app.py"""
import sys, types

_SRC = {
    'dataset': '"""\nHand-extracted TCS *consolidated* financial statements (Ind AS), INR crore.\n\nSource mapping (all CONSOLIDATED; standalone figures are never used):\n  FY2025-26 Integrated Annual Report -> FY2026 (current) and FY2025 (comparative)  [pp.196-203]\n  FY2023-24 Integrated Annual Report -> FY2024 (current) and FY2023 (comparative)  [pp.180-185]\n  FY2021-22 Integrated Annual Report -> FY2022 (current) and FY2021 (comparative)  [pp.243-251]\n\nThe text layer of the FY2024-25 PDF is corrupted (digits dropped, e.g. "1,5 6" for 1,546), so\nFY2025 is read from the clean comparative column of the FY2025-26 report. FY2023 figures were\ncross-checked against the FY2022-23 report\'s own statements (no restatements found).\n\nFY2021 is a *base year* only (for FY2022 growth and average balances). The dashboard\ndisplays FY2022-FY2026, the five most recent years.\n"""\nfrom collections import OrderedDict\n\nYEARS = ["FY2021", "FY2022", "FY2023", "FY2024", "FY2025", "FY2026"]\nBASE_YEAR = "FY2021"\nDISPLAY_YEARS = YEARS[1:]\n\nINCOME = OrderedDict([\n    ("revenue",        ("Revenue from operations",                     [164177, 191754, 225458, 240893, 255324, 267021])),\n    ("other_income",   ("Other income",                                [3134, 4018, 3449, 4422, 3962, 4402])),\n    ("total_income",   ("Total income",                                [167311, 195772, 228907, 245315, 259286, 271423])),\n    ("employee_cost",  ("Employee benefit expenses",                   [91814, 107554, 127522, 140131, 145788, 154994])),\n    ("equipment_cost", ("Cost of equipment and software licences",     [1462, 1163, 1881, 3702, 11648, 4399])),\n    ("finance_cost",   ("Finance costs",                               [637, 784, 779, 778, 796, 1227])),\n    ("depreciation",   ("Depreciation and amortisation expense",       [4065, 4604, 5022, 4985, 5242, 5560])),\n    ("other_expenses", ("Other expenses",                              [24355, 29980, 36796, 32764, 30481, 35230])),\n    ("total_expenses", ("Total expenses",                              [122333, 144085, 172000, 182360, 193955, 201410])),\n    ("pbe",            ("Profit before exceptional items and tax",     [44978, 51687, 56907, 62955, 65331, 70013])),\n    ("exceptional",    ("Exceptional items (expense)",                 [1218, 0, 0, 958, 0, 4526])),\n    ("pbt",            ("Profit before tax",                           [43760, 51687, 56907, 61997, 65331, 65487])),\n    ("current_tax",    ("Current tax",                                 [11635, 13654, 14757, 15864, 16910, 16388])),\n    ("deferred_tax",   ("Deferred tax",                                [-437, -416, -153, 34, -376, -355])),\n    ("total_tax",      ("Total tax expense",                           [11198, 13238, 14604, 15898, 16534, 16033])),\n    ("pat",            ("Profit for the year",                         [32562, 38449, 42303, 46099, 48797, 49454])),\n    ("pat_sh",         ("Profit attributable to shareholders",         [32430, 38327, 42147, 45908, 48553, 49210])),\n    ("pat_nci",        ("Profit attributable to non-controlling interests", [132, 122, 156, 191, 244, 244])),\n    ("eps",            ("Earnings per share - basic & diluted (INR)",  [86.71, 103.62, 115.19, 125.88, 134.19, 136.01])),\n    ("shares_cr",      ("Weighted average equity shares (crore)",      [374.0110733, 369.8832195, 365.9051373, 364.6851755, 361.8087518, 361.8087518])),\n])\n\nBALANCE = OrderedDict([\n    ("ppe",             ("Property, plant and equipment",             [11110, 10774, 10230, 9376, 10978, 11032])),\n    ("cwip",            ("Capital work-in-progress",                  [926, 1205, 1234, 1564, 1546, 2665])),\n    ("rou",             ("Right-of-use assets",                       [7633, 7636, 7560, 7886, 9275, 11027])),\n    ("goodwill",        ("Goodwill",                                  [1798, 1787, 1858, 1832, 1860, 9108])),\n    ("intangibles",     ("Other intangible assets",                   [480, 1101, 867, 510, 940, 176])),\n    ("nca_investments", ("Non-current investments",                   [213, 223, 266, 281, 275, 218])),\n    ("nca_receivables", ("Non-current trade receivables (billed+unbilled)", [328, 200, 348, 143, 129, 213])),\n    ("nca_loans",       ("Non-current loans",                         [29, 311, 173, 2, 25, 775])),\n    ("nca_other_fin",   ("Non-current other financial assets",        [1573, 2253, 2149, 3272, 2731, 2944])),\n    ("dta",             ("Deferred tax assets (net)",                 [3931, 3708, 3307, 3403, 3578, 4465])),\n    ("nca_tax_assets",  ("Non-current income tax assets (net)",       [1845, 1983, 2583, 1600, 1569, 1439])),\n    ("nca_other",       ("Non-current other assets",                  [1613, 2023, 2806, 3596, 3712, 2605])),\n    ("total_nca",       ("Total non-current assets",                  [31479, 33204, 33381, 33465, 36618, 46667])),\n    ("inventories",     ("Inventories",                               [8, 20, 28, 28, 21, 29])),\n    ("ca_investments",  ("Current investments",                       [29160, 30262, 36897, 31481, 30689, 33770])),\n    ("ca_receivables",  ("Current trade receivables (billed+unbilled)", [36662, 41810, 49954, 53577, 59046, 67714])),\n    ("cash",            ("Cash and cash equivalents",                 [6858, 12488, 7123, 9016, 8342, 6417])),\n    ("other_bank",      ("Other balances with banks",                 [2471, 5733, 3909, 4270, 7121, 6491])),\n    ("ca_loans",        ("Current loans",                             [11472, 6445, 1325, 491, 9, 1659])),\n    ("ca_other_fin",    ("Current other financial assets",            [1394, 1390, 1319, 1703, 2742, 1833])),\n    ("ca_tax_assets",   ("Current income tax assets (net)",           [19, 11, 8, 151, 257, 1259])),\n    ("ca_other",        ("Current other assets",                      [11236, 10151, 9707, 12267, 14784, 16533])),\n    ("total_ca",        ("Total current assets",                      [99280, 108310, 110270, 112984, 123011, 135705])),\n    ("total_assets",    ("TOTAL ASSETS",                              [130759, 141514, 143651, 146449, 159629, 182372])),\n    ("share_capital",   ("Share capital",                             [370, 366, 366, 362, 362, 362])),\n    ("other_equity",    ("Other equity",                              [86063, 88773, 90058, 90127, 94394, 106878])),\n    ("equity_sh",       ("Equity attributable to shareholders",       [86433, 89139, 90424, 90489, 94756, 107240])),\n    ("nci",             ("Non-controlling interests",                 [675, 707, 782, 830, 1015, 1238])),\n    ("total_equity",    ("Total equity",                              [87108, 89846, 91206, 91319, 95771, 108478])),\n    ("ccps",            ("Class B compulsorily convertible preference shares", [0, 0, 0, 0, 0, 126])),\n    ("lease_nc",        ("Non-current lease liabilities",             [6503, 6368, 6203, 6516, 7838, 9453])),\n    ("other_fin_nc",    ("Non-current other financial liabilities",   [280, 572, 353, 365, 680, 588])),\n    ("emp_nc",          ("Non-current employee benefit obligations",  [749, 677, 536, 686, 841, 961])),\n    ("dtl",             ("Deferred tax liabilities (net)",            [767, 590, 792, 977, 980, 1205])),\n    ("unearned_nc",     ("Non-current unearned and deferred revenue", [1197, 1110, 1003, 482, 518, 647])),\n    ("total_ncl",       ("Total non-current liabilities",             [9496, 9317, 8887, 9026, 10857, 12980])),\n    ("lease_c",         ("Current lease liabilities",                 [1292, 1450, 1485, 1505, 1554, 1830])),\n    ("trade_payables",  ("Trade payables",                            [7860, 8045, 10515, 9981, 13909, 14808])),\n    ("other_fin_c",     ("Current other financial liabilities",       [6150, 7687, 9068, 8362, 8542, 11194])),\n    ("unearned_c",      ("Current unearned and deferred revenue",     [3650, 3635, 3843, 3640, 4028, 4487])),\n    ("other_liab_c",    ("Current other liabilities",                 [4068, 8392, 4892, 6524, 7188, 6866])),\n    ("provisions",      ("Provisions",                                [1394, 1411, 345, 140, 180, 1378])),\n    ("emp_c",           ("Current employee benefit obligations",      [3498, 3810, 4065, 4519, 4885, 5600])),\n    ("tax_liab",        ("Income tax liabilities (net)",              [6243, 7921, 9345, 11433, 12715, 14751])),\n    ("total_cl",        ("Total current liabilities",                 [34155, 42351, 43558, 46104, 53001, 60914])),\n])\n\nCASHFLOW = OrderedDict([\n    ("op_profit_pre_wc", ("Operating profit before working capital changes", [47031, 54204, 59148, 63709, 67853, 68688])),\n    ("taxes_paid",       ("Taxes paid (net of refunds)",                  [9092, 11486, 12966, 12489, 15586, 14384])),\n    ("cfo",              ("Net cash from operating activities",           [38802, 39949, 41965, 44338, 48908, 52094])),\n    ("cfi",              ("Net cash from / (used in) investing activities", [-8129, -897, 39, 6026, -2318, -12845])),\n    ("cff",              ("Net cash used in financing activities",        [-32634, -33581, -47878, -48536, -47438, -42133])),\n    ("capex_ppe",        ("Purchase of property, plant and equipment",    [2719, 2483, 2532, 2202, 2917, 3670])),\n    ("capex_rou",        ("Payments incl. advances for right-of-use assets", [101, 15, 213, 30, 76, 109])),\n    ("capex_intang",     ("Purchase of intangible assets",                [356, 497, 355, 442, 944, 367])),\n    ("acquisitions",     ("Acquisition of subsidiaries and assets",       [0, 0, 0, 0, 1063, 7304])),\n    ("lease_repay",      ("Repayment of lease liabilities",               [1336, 1417, 1515, 1614, 1664, 1861])),\n    ("interest_paid",    ("Interest paid",                                [634, 698, 779, 699, 840, 901])),\n    ("dividend_sh",      ("Dividend paid to shareholders",                [10850, 13317, 41347, 25137, 44864, 39437])),\n    ("dividend_nci",     ("Dividend paid to non-controlling interests",   [57, 58, 63, 81, 98, 134])),\n    ("buyback",          ("Buy-back of shares incl. tax and expenses",    [19757, 18049, 4192, 21005, 0, 0])),\n    ("net_change_cash",  ("Net change in cash and cash equivalents",      [-1961, 5471, -5874, 1828, -848, -2884])),\n    ("cash_begin",       ("Cash and cash equivalents - beginning",        [8646, 6858, 12488, 7123, 9016, 8342])),\n    ("fx_effect",        ("FX effect on cash and cash equivalents",       [173, 159, 509, 65, 174, 959])),\n    ("cash_end",         ("Cash and cash equivalents - end",              [6858, 12488, 7123, 9016, 8342, 6417])),\n])\n\nSOURCES = {\n    "FY2026": "FY2025-26 Integrated Annual Report, consolidated statements (pp.196-203)",\n    "FY2025": "FY2025-26 report comparative column (FY2024-25 report text layer is corrupted; its legible totals agree)",\n    "FY2024": "FY2023-24 Integrated Annual Report, consolidated statements (pp.180-185)",\n    "FY2023": "FY2023-24 report comparative column; agrees with FY2022-23 report\'s own figures",\n    "FY2022": "FY2021-22 Integrated Annual Report, consolidated statements (pp.243-251); agrees with FY2022-23 comparative",\n    "FY2021": "FY2021-22 report comparative column (base year for growth and average balances only)",\n}\n\nNOT_REPORTED = {\n    "Gross Profit / Gross Profit Margin":\n        "TCS presents expenses by nature (no cost-of-sales line), so gross profit is not reported and cannot be "\n        "calculated. A clearly labelled proxy (revenue less employee and equipment costs) is shown instead.",\n    "Borrowings / classic Debt-to-Equity":\n        "TCS reports no bank or bond borrowings in FY2021-FY2026. Debt is taken as lease liabilities plus (FY2026 only) "\n        "Class B compulsorily convertible preference shares of INR 126 crore.",\n    "Inventory Turnover":\n        "Inventories are immaterial (INR 8-29 crore, under 0.03% of assets). The ratio uses cost of equipment & "\n        "software licences as the cost base but is not analytically meaningful.",\n    "US$ values":\n        "No exchange-rate data is in the uploaded files, so no US$ conversion is attempted.",\n}\n\n\ndef all_statements():\n    return {"Income Statement": INCOME, "Balance Sheet": BALANCE, "Cash Flow": CASHFLOW}\n',
    'fmt': '"""Number formatting helpers (Indian digit grouping for INR crore)."""\nimport math\n\nUNITS = {"INR crore": 1.0, "INR billion": 0.01}\n\n\ndef indian(n, decimals=0):\n    if n is None or (isinstance(n, float) and math.isnan(n)):\n        return "n/a"\n    neg = n < 0\n    s = f"{abs(n):.{decimals}f}"\n    ip, _, fp = s.partition(".")\n    if len(ip) > 3:\n        head, tail, groups = ip[:-3], ip[-3:], []\n        while len(head) > 2:\n            groups.insert(0, head[-2:]); head = head[:-2]\n        if head:\n            groups.insert(0, head)\n        ip = ",".join(groups + [tail])\n    return ("-" if neg else "") + ip + ("." + fp if fp else "")\n\n\ndef money(x, unit="INR crore"):\n    if x is None or (isinstance(x, float) and math.isnan(x)):\n        return "n/a"\n    if unit == "INR billion":\n        return f"₹{x * 0.01:,.1f} bn"\n    return f"₹{indian(x)} cr"\n\n\ndef pct(x, d=1):\n    return "n/a" if x is None or (isinstance(x, float) and math.isnan(x)) else f"{x:.{d}f}%"\n\n\ndef times(x, d=2):\n    return "n/a" if x is None or (isinstance(x, float) and math.isnan(x)) else f"{x:.{d}f}x"\n\n\ndef pp(x, d=1):\n    return "n/a" if x is None or (isinstance(x, float) and math.isnan(x)) else f"{x:+.{d}f} pp"\n\n\ndef short(y):\n    """FY2026 -> FY26"""\n    return "FY" + y[-2:]\n',
    'metrics': '"""Financial metric and ratio calculations (pandas / NumPy). All money in INR crore."""\nimport numpy as np\nimport pandas as pd\n\n\ndef _bal(s, basis):\n    """Balance used as denominator: average of opening+closing, or closing only."""\n    return (s + s.shift(1)) / 2 if basis == "average" else s\n\n\ndef compute_metrics(df, basis="average"):\n    """df: wide statements frame indexed by FY (incl. base year). Returns metrics frame, same index.\n    The base year has NaN for anything needing a prior year."""\n    m = pd.DataFrame(index=df.index)\n    rev = df.revenue\n\n    # ---- derived profit measures -------------------------------------------------\n    m["revenue"] = rev\n    m["op_profit"] = rev - (df.employee_cost + df.equipment_cost + df.depreciation + df.other_expenses)\n    m["ebitda"] = m.op_profit + df.depreciation\n    m["pbe"] = df.pbe\n    m["pbt"] = df.pbt\n    m["net_profit"] = df.pat_sh               # attributable to shareholders (basis for EPS/ROE)\n    m["profit_for_year"] = df.pat\n    m["eps"] = df.eps\n    m["ebit_incl_other_income"] = df.pbe + df.finance_cost\n\n    # ---- structure ---------------------------------------------------------------\n    m["total_assets"] = df.total_assets\n    m["total_liabilities"] = df.total_ncl + df.total_cl\n    m["equity"] = df.equity_sh\n    m["total_equity"] = df.total_equity\n    m["current_assets"] = df.total_ca\n    m["current_liabilities"] = df.total_cl\n    m["cash"] = df.cash\n    m["cash_liquid"] = df.cash + df.other_bank + df.ca_investments\n    m["lease_liabilities"] = df.lease_nc + df.lease_c\n    m["total_debt"] = m.lease_liabilities + df.ccps      # no borrowings are reported\n    m["net_cash"] = m.cash_liquid - m.total_debt\n    m["capital_employed"] = df.total_assets - df.total_cl\n\n    # ---- growth ------------------------------------------------------------------\n    for k, s in {"rev": rev, "op": m.op_profit, "np": m.net_profit, "eps": df.eps, "ta": df.total_assets}.items():\n        m[f"{k}_growth"] = s.pct_change() * 100\n\n    # ---- profitability -----------------------------------------------------------\n    m["op_margin"] = m.op_profit / rev * 100\n    m["ebitda_margin"] = m.ebitda / rev * 100\n    m["net_margin"] = m.net_profit / rev * 100\n    m["pbt_margin"] = df.pbt / rev * 100\n    m["gross_margin"] = np.nan                            # not reported by TCS\n    m["contribution_margin_proxy"] = (rev - df.employee_cost - df.equipment_cost) / rev * 100\n    m["roa"] = m.net_profit / _bal(df.total_assets, basis) * 100\n    m["roe"] = m.net_profit / _bal(df.equity_sh, basis) * 100\n    m["roce"] = m.ebit_incl_other_income / _bal(m.capital_employed, basis) * 100\n    m["tax_rate"] = df.total_tax / df.pbt * 100\n\n    # ---- liquidity ---------------------------------------------------------------\n    quick_assets = df.total_ca - df.inventories - df.ca_other - df.ca_tax_assets\n    m["current_ratio"] = df.total_ca / df.total_cl\n    m["quick_ratio"] = quick_assets / df.total_cl\n    m["cash_ratio"] = m.cash_liquid / df.total_cl\n\n    # ---- efficiency --------------------------------------------------------------\n    m["asset_turnover"] = rev / _bal(df.total_assets, basis)\n    m["inventory_turnover"] = df.equipment_cost / _bal(df.inventories, basis)\n    m["dso"] = df.ca_receivables / rev * 365\n\n    # ---- solvency ----------------------------------------------------------------\n    m["debt_equity"] = m.total_debt / df.total_equity\n    m["liabilities_equity"] = m.total_liabilities / df.total_equity\n    m["equity_ratio"] = df.total_equity / df.total_assets * 100\n    m["interest_coverage"] = m.op_profit / df.finance_cost\n\n    # ---- cash flow ---------------------------------------------------------------\n    m["cfo"], m["cfi"], m["cff"] = df.cfo, df.cfi, df.cff\n    m["capex"] = df.capex_ppe + df.capex_intang + df.capex_rou\n    m["fcf"] = df.cfo - m.capex\n    m["fcf_after_leases"] = m.fcf - df.lease_repay\n    m["cfo_to_np"] = df.cfo / m.net_profit * 100\n    m["fcf_to_np"] = m.fcf / m.net_profit * 100\n    m["payout"] = df.dividend_sh / m.net_profit * 100\n    m["shareholder_returns"] = df.dividend_sh + df.buyback\n    return m\n\n\n# metadata used by the UI: key -> (label, unit-kind, higher_is_better, group)\nRATIOS = {\n    "gross_margin":        ("Gross Profit Margin", "%", True, "Profitability"),\n    "op_margin":           ("Operating Profit Margin", "%", True, "Profitability"),\n    "net_margin":          ("Net Profit Margin", "%", True, "Profitability"),\n    "roa":                 ("Return on Assets (ROA)", "%", True, "Profitability"),\n    "roe":                 ("Return on Equity (ROE)", "%", True, "Profitability"),\n    "roce":                ("Return on Capital Employed (ROCE)", "%", True, "Profitability"),\n    "current_ratio":       ("Current Ratio", "x", True, "Liquidity"),\n    "quick_ratio":         ("Quick Ratio", "x", True, "Liquidity"),\n    "asset_turnover":      ("Total Asset Turnover", "x", True, "Efficiency"),\n    "inventory_turnover":  ("Inventory Turnover", "x", True, "Efficiency"),\n    "dso":                 ("Receivable Days (DSO)", "days", False, "Efficiency"),\n    "debt_equity":         ("Debt-to-Equity (incl. leases)", "x", False, "Solvency"),\n    "interest_coverage":   ("Interest Coverage (EBIT / finance cost)", "x", True, "Solvency"),\n}\n\nFORMULAS = {\n    "gross_margin": "Not calculable - TCS reports expenses by nature, with no cost-of-sales / gross profit line.",\n    "op_margin": "Operating profit / Revenue. Operating profit = Revenue - employee - equipment & licence - depreciation - other expenses (excludes other income, finance cost, exceptional items).",\n    "net_margin": "Profit attributable to shareholders / Revenue from operations.",\n    "roa": "Profit attributable to shareholders / Total assets (average or year-end, per sidebar).",\n    "roe": "Profit attributable to shareholders / Equity attributable to shareholders (average or year-end).",\n    "roce": "(Profit before exceptional items & tax + Finance costs) / (Total assets - Current liabilities).",\n    "current_ratio": "Total current assets / Total current liabilities.",\n    "quick_ratio": "(Current assets - inventories - other current assets - current tax assets) / Current liabilities.",\n    "asset_turnover": "Revenue / Total assets (average or year-end).",\n    "inventory_turnover": "Cost of equipment & software licences / Inventories. Inventories are immaterial, so the ratio is not meaningful.",\n    "dso": "Current trade receivables (billed + unbilled) / Revenue x 365.",\n    "debt_equity": "(Lease liabilities + preference shares classed as liabilities) / Total equity. TCS has no borrowings.",\n    "interest_coverage": "Operating profit / Finance costs.",\n}\n\nMEANING = {\n    "gross_margin": "Would show profit left after direct costs of delivery; unavailable for TCS.",\n    "op_margin": "Share of each rupee of revenue left after running costs; the core measure of delivery efficiency and pricing power.",\n    "net_margin": "Share of revenue that reaches shareholders after all costs, other income, tax and exceptional items.",\n    "roa": "How much profit each rupee of assets generates; dilutes when large cash/investment balances sit on the balance sheet.",\n    "roe": "Return earned on shareholders\' money; high values are supported by high margins and heavy payouts to shareholders.",\n    "roce": "Return on all long-term capital deployed, regardless of how it is financed.",\n    "current_ratio": "Ability to meet obligations due within a year from assets that convert to cash within a year.",\n    "quick_ratio": "A stricter test of short-term liquidity that excludes inventories and prepaid-type items.",\n    "asset_turnover": "Revenue generated per rupee of assets; falling values mean assets are growing faster than sales.",\n    "inventory_turnover": "How quickly traded hardware/licence stock turns over; immaterial for a services business like TCS.",\n    "dso": "Days of revenue tied up in customer receivables; rising values mean slower cash collection.",\n    "debt_equity": "Reliance on debt-like funding versus owners\' funds; lower means a more conservative structure.",\n    "interest_coverage": "Times operating profit covers finance costs (mostly lease interest at TCS); higher is safer.",\n}\n\n\nMETRIC_LABELS = {\n    "revenue": "Revenue from operations", "op_profit": "Operating profit (EBIT excl. other income)", "ebitda": "EBITDA",\n    "pbe": "Profit before exceptional items & tax", "pbt": "Profit before tax", "net_profit": "Net profit (attributable to shareholders)",\n    "profit_for_year": "Profit for the year (incl. NCI)", "eps": "EPS (INR)", "ebit_incl_other_income": "Profit before exceptional & tax + finance cost",\n    "total_assets": "Total assets", "total_liabilities": "Total liabilities", "equity": "Shareholders\' equity",\n    "total_equity": "Total equity (incl. NCI)", "current_assets": "Current assets", "current_liabilities": "Current liabilities",\n    "cash": "Cash and cash equivalents", "cash_liquid": "Cash + bank balances + current investments",\n    "lease_liabilities": "Lease liabilities", "total_debt": "Debt-like obligations (leases + preference shares)",\n    "net_cash": "Net cash (liquid assets - debt-like obligations)", "capital_employed": "Capital employed (TA - CL)",\n    "rev_growth": "Revenue growth (%)", "op_growth": "Operating profit growth (%)", "np_growth": "Net profit growth (%)",\n    "eps_growth": "EPS growth (%)", "ta_growth": "Total assets growth (%)", "op_margin": "Operating profit margin (%)",\n    "ebitda_margin": "EBITDA margin (%)", "net_margin": "Net profit margin (%)", "pbt_margin": "PBT margin (%)",\n    "gross_margin": "Gross profit margin (%) - NOT REPORTED", "contribution_margin_proxy": "Revenue less employee & equipment costs (% proxy)",\n    "roa": "ROA (%)", "roe": "ROE (%)", "roce": "ROCE (%)", "tax_rate": "Effective tax rate (%)",\n    "current_ratio": "Current ratio (x)", "quick_ratio": "Quick ratio (x)", "cash_ratio": "Cash ratio (x)",\n    "asset_turnover": "Total asset turnover (x)", "inventory_turnover": "Inventory turnover (x) - not meaningful",\n    "dso": "Receivable days", "debt_equity": "Debt-to-equity (x)", "liabilities_equity": "Total liabilities / equity (x)",\n    "equity_ratio": "Equity / total assets (%)", "interest_coverage": "Interest coverage (x)",\n    "cfo": "Cash flow from operations", "cfi": "Cash flow from investing", "cff": "Cash flow from financing",\n    "capex": "Capex (PPE + intangibles + ROU advances)", "fcf": "Free cash flow (CFO - capex)",\n    "fcf_after_leases": "Free cash flow after lease repayments", "cfo_to_np": "CFO / net profit (%)",\n    "fcf_to_np": "FCF / net profit (%)", "payout": "Dividend payout (% of net profit)",\n    "shareholder_returns": "Dividends + buy-backs",\n}\n',
    'loader': '"""Reads the Excel workbook (OpenPyXL via pandas) and reconciles the statements."""\nimport pandas as pd\nimport numpy as np\n\nSHEETS = ["Income Statement", "Balance Sheet", "Cash Flow"]\n\n\ndef _from_dataset():\n    from . import dataset as ds\n    frames, labels = [], {}\n    for rows in ds.all_statements().values():\n        labels.update({k: v[0] for k, v in rows.items()})\n        frames.append(pd.DataFrame({k: v[1] for k, v in rows.items()}, index=ds.YEARS))\n    df = pd.concat(frames, axis=1).apply(pd.to_numeric, errors="coerce")\n    df.index.name = "Year"\n    return df, labels, None\n\n\ndef load_statements(path=None):\n    """Return (wide DataFrame indexed by FY, label dict, raw sheets).\n    Reads the Excel workbook with OpenPyXL; if it is not present, uses the identical built-in dataset."""\n    import os\n    if path is None or not os.path.exists(str(path)):\n        return _from_dataset()\n    raw = pd.read_excel(path, sheet_name=None, engine="openpyxl")\n    frames, labels = [], {}\n    for s in SHEETS:\n        t = raw[s].copy()\n        labels.update(dict(zip(t["Key"], t.iloc[:, 1])))\n        frames.append(t.drop(columns=t.columns[1]).set_index("Key").T)\n    df = pd.concat(frames, axis=1).apply(pd.to_numeric, errors="coerce")\n    df.index.name = "Year"\n    return df, labels, raw\n\n\ndef reconcile(df):\n    """Arithmetic tie-outs. Returns DataFrame: Check, Year, Reported, Recomputed, Difference, Status."""\n    c = lambda *k: df[list(k)].sum(axis=1)\n    checks = {\n        "Total income = revenue + other income": (df.total_income, c("revenue", "other_income"), 0),\n        "Total expenses = sum of expense lines": (df.total_expenses, c("employee_cost", "equipment_cost", "finance_cost", "depreciation", "other_expenses"), 0),\n        "PBE = total income - total expenses": (df.pbe, df.total_income - df.total_expenses, 0),\n        "PBT = PBE - exceptional items": (df.pbt, df.pbe - df.exceptional, 0),\n        "Total tax = current + deferred": (df.total_tax, c("current_tax", "deferred_tax"), 0),\n        "Profit = PBT - tax": (df.pat, df.pbt - df.total_tax, 0),\n        "Profit = shareholders + NCI": (df.pat, c("pat_sh", "pat_nci"), 0),\n        "EPS = shareholder profit / weighted shares": (df.eps, df.pat_sh / df.shares_cr, 0.02),\n        "Total non-current assets = sum": (df.total_nca, c("ppe", "cwip", "rou", "goodwill", "intangibles", "nca_investments", "nca_receivables", "nca_loans", "nca_other_fin", "dta", "nca_tax_assets", "nca_other"), 0),\n        "Total current assets = sum": (df.total_ca, c("inventories", "ca_investments", "ca_receivables", "cash", "other_bank", "ca_loans", "ca_other_fin", "ca_tax_assets", "ca_other"), 0),\n        "Total assets = NCA + CA": (df.total_assets, c("total_nca", "total_ca"), 0),\n        "Shareholder equity = capital + other equity": (df.equity_sh, c("share_capital", "other_equity"), 0),\n        "Total equity = shareholders + NCI": (df.total_equity, c("equity_sh", "nci"), 0),\n        "Total non-current liabilities = sum": (df.total_ncl, c("ccps", "lease_nc", "other_fin_nc", "emp_nc", "dtl", "unearned_nc"), 0),\n        "Total current liabilities = sum": (df.total_cl, c("lease_c", "trade_payables", "other_fin_c", "unearned_c", "other_liab_c", "provisions", "emp_c", "tax_liab"), 0),\n        "Balance sheet balances (A = E + L)": (df.total_assets, c("total_equity", "total_ncl", "total_cl"), 0),\n        "Cash flow: opening + net change + FX = closing": (df.cash_end, c("cash_begin", "net_change_cash", "fx_effect"), 0),\n        "Cash flow: CFO + CFI + CFF = net change": (df.net_change_cash, c("cfo", "cfi", "cff"), 0),\n        "Cash flow closing cash = balance sheet cash": (df.cash_end, df.cash, 0),\n    }\n    rows = []\n    for name, (rep, calc, tol) in checks.items():\n        for y in df.index:\n            diff = float(rep[y] - calc[y])\n            ok = abs(diff) <= tol\n            rows.append([name, y, float(rep[y]), float(calc[y]), diff, "PASS" if ok else "FAIL"])\n    return pd.DataFrame(rows, columns=["Check", "Year", "Reported", "Recomputed", "Difference", "Status"])\n',
    'insights': '"""Rule-based insight generation. Every statement is built from the actual numbers."""\nimport numpy as np\nimport pandas as pd\nfrom .fmt import money, pct, times, pp, short\nfrom .metrics import RATIOS, MEANING\n\n\ndef _chg(s, a, b):\n    return s[b] - s[a]\n\n\ndef _trend_word(delta, up="improved", down="declined", tol=0.0):\n    return up if delta > tol else down if delta < -tol else "was unchanged"\n\n\ndef ratio_commentary(key, m, years):\n    """Plain-English reading of one ratio\'s movement over the selected years."""\n    label, kind, hib, _ = RATIOS[key]\n    s = m.loc[years, key].dropna()\n    if s.empty:\n        return f"**{label}** cannot be calculated from the uploaded statements (see data notes)."\n    fmtv = {"%": pct, "x": times, "days": lambda v: f"{v:.1f} days"}[kind]\n    a, b = s.index[0], s.index[-1]\n    d = s[b] - s[a]\n    better = (d > 0) == hib\n    verdict = "an improvement" if (better and abs(d) > 1e-9) else "a deterioration" if abs(d) > 1e-9 else "no change"\n    unit_txt = {"%": f"{abs(d):.1f} pp", "x": f"{abs(d):.2f}x", "days": f"{abs(d):.1f} days"}[kind]\n    out = (f"**{label}** moved from {fmtv(s[a])} in {short(a)} to {fmtv(s[b])} in {short(b)} "\n           f"({\'up\' if d > 0 else \'down\'} {unit_txt}), {verdict}. "\n           f"Peak {fmtv(s.max())} ({short(s.idxmax())}); low {fmtv(s.min())} ({short(s.idxmin())}). ")\n    if len(s) >= 2:\n        last = s.iloc[-1] - s.iloc[-2]\n        out += f"Latest year-on-year change: {\'+\' if last >= 0 else \'-\'}{abs(last):.2f}{\'pp\' if kind == \'%\' else \'\'}. "\n    return out + f"*What it indicates:* {MEANING[key]}"\n\n\ndef build_insights(df, m, years):\n    """years: ordered list of displayed years (>=2). Returns dict of lists of (title, text)."""\n    y0, y1 = years[0], years[-1]\n    prev = years[-2]\n    R = {}\n\n    def add(cat, title, text):\n        R.setdefault(cat, []).append((title, text))\n\n    # ---------- headline ----------\n    ry = m.loc[years, "revenue"].idxmax(); ny = m.loc[years, "net_profit"].idxmax()\n    add("Highlights", "Highest revenue year",\n        f"{short(ry)} recorded the highest revenue of {money(m.revenue[ry])}"\n        + (f", {pct(m.rev_growth[ry])} above the prior year." if not np.isnan(m.rev_growth[ry]) else "."))\n    add("Highlights", "Highest net profit year",\n        f"{short(ny)} recorded the highest net profit attributable to shareholders at {money(m.net_profit[ny])} "\n        f"(EPS ₹{m.eps[ny]:.2f}); net margin {pct(m.net_margin[ny])}.")\n    n = len(years) - 1\n    cagr = lambda s: ((s[y1] / s[y0]) ** (1 / n) - 1) * 100 if n > 0 and s[y0] > 0 else np.nan\n    add("Highlights", f"{n}-year CAGR ({short(y0)}→{short(y1)})",\n        f"Revenue {pct(cagr(m.revenue))}, operating profit {pct(cagr(m.op_profit))}, net profit {pct(cagr(m.net_profit))}, "\n        f"EPS {pct(cagr(m.eps))}.")\n\n    # ---------- growth consistency ----------\n    g = m.loc[years, "rev_growth"].dropna()\n    pos = int((g > 0).sum())\n    seq = ", ".join(f"{short(i)} {v:.1f}%" for i, v in g.items())\n    decel = g.iloc[-1] < g.max() * 0.5\n    add("Growth", "Revenue growth consistency",\n        f"Revenue rose in {pos} of {len(g)} years ({seq}); mean {g.mean():.1f}%, std. dev. {g.std(ddof=0):.1f} pp. "\n        + (f"Growth has slowed markedly from its {g.max():.1f}% peak ({short(g.idxmax())}) to {g.iloc[-1]:.1f}% in {short(g.index[-1])}."\n           if decel else "Growth has stayed within a narrow band."))\n\n    # ---------- profitability ----------\n    om, nm = m.op_margin, m.net_margin\n    dm = om[y1] - om[y0]\n    add("Profitability", "Operating margin",\n        f"Operating margin was {pct(om[y0])} in {short(y0)} and {pct(om[y1])} in {short(y1)} ({pp(dm)}); range "\n        f"{pct(om[years].min())} ({short(om[years].idxmin())}) to {pct(om[years].max())} ({short(om[years].idxmax())}). "\n        f"Margins are broadly {\'stable\' if om[years].max() - om[years].min() < 2.5 else \'volatile\'} despite revenue growing "\n        f"{(m.revenue[y1] / m.revenue[y0] - 1) * 100:.0f}% over the period.")\n    ex = df.exceptional[y1]\n    add("Profitability", "Net margin and exceptional items",\n        f"Net margin moved {pp(nm[y1] - nm[prev])} to {pct(nm[y1])} in {short(y1)}. "\n        + (f"Exceptional charges of {money(ex)} ({ex / df.pbe[y1] * 100:.1f}% of pre-exceptional profit) held PBT growth to "\n           f"{pct((df.pbt[y1] / df.pbt[prev] - 1) * 100)} versus {pct((df.pbe[y1] / df.pbe[prev] - 1) * 100)} before exceptionals."\n           if ex > 0 else "No exceptional items were booked that year."))\n    add("Profitability", "Returns on capital",\n        f"ROE {pct(m.roe[y1])} and ROCE {pct(m.roce[y1])} in {short(y1)}, versus {pct(m.roe[prev])} and {pct(m.roce[prev])} in {short(prev)}.")\n\n    # ---------- liquidity ----------\n    add("Liquidity", "Liquidity position",\n        f"Current ratio {times(m.current_ratio[y1])} and quick ratio {times(m.quick_ratio[y1])} in {short(y1)} "\n        f"(from {times(m.current_ratio[y0])} / {times(m.quick_ratio[y0])} in {short(y0)}). Cash, bank balances and current "\n        f"investments total {money(m.cash_liquid[y1])} against current liabilities of {money(m.current_liabilities[y1])} "\n        f"(cash ratio {times(m.cash_ratio[y1])}).")\n\n    # ---------- stability ----------\n    add("Stability", "Financial stability",\n        f"No borrowings are reported. Debt-like obligations (lease liabilities + preference shares) are {money(m.total_debt[y1])}, "\n        f"a debt-to-equity of {times(m.debt_equity[y1])}, against liquid assets of {money(m.cash_liquid[y1])} "\n        f"(net cash {money(m.net_cash[y1])}). Equity funds {pct(m.equity_ratio[y1])} of total assets; interest cover is "\n        f"{times(m.interest_coverage[y1], 1)}.")\n\n    # ---------- efficiency ----------\n    add("Efficiency", "Asset utilisation",\n        f"Asset turnover was {times(m.asset_turnover[y1])} in {short(y1)} versus {times(m.asset_turnover[prev])} in {short(prev)} "\n        f"and {times(m.asset_turnover[y0])} in {short(y0)}. "\n        f"Receivable days moved from {m.dso[y0]:.1f} to {m.dso[y1]:.1f} ({short(y0)}→{short(y1)}).")\n\n    # ---------- cash ----------\n    add("Cash Flow", "Cash generation",\n        f"Operating cash flow was {money(m.cfo[y1])} ({pct(m.cfo_to_np[y1], 0)} of net profit); free cash flow "\n        f"{money(m.fcf[y1])} after capex of {money(m.capex[y1])}. Shareholder payouts: dividends {money(df.dividend_sh[y1])} "\n        f"({pct(m.payout[y1], 0)} of net profit)" + (f" plus buy-backs {money(df.buyback[y1])}." if df.buyback[y1] else "."))\n\n    # ---------- positives & concerns ----------\n    pos_, con = [], []\n    if g.gt(0).all():\n        pos_.append(f"Revenue grew every year, cumulatively {(m.revenue[y1] / m.revenue[y0] - 1) * 100:.1f}% from {short(y0)} to {short(y1)}.")\n    if m.loc[years, "net_profit"].is_monotonic_increasing:\n        pos_.append(f"Net profit rose every year, from {money(m.net_profit[y0])} to {money(m.net_profit[y1])}.")\n    if (m.cfo[years] >= m.net_profit[years] * 0.95).all():\n        pos_.append(f"Operating cash flow was at least 95% of net profit in every year ({pct(m.cfo_to_np[years].min(), 0)}–{pct(m.cfo_to_np[years].max(), 0)}).")\n    if m.interest_coverage[years].min() > 20:\n        pos_.append(f"Interest coverage never fell below {times(m.interest_coverage[years].min(), 1)}; the company carries no borrowings.")\n    if m.roe[years].min() > 40:\n        pos_.append(f"ROE stayed above {pct(m.roe[years].min(), 0)} throughout.")\n    if m.net_cash[y1] > 0:\n        pos_.append(f"Liquid assets exceed debt-like obligations by {money(m.net_cash[y1])}.")\n\n    if decel:\n        con.append(f"Revenue growth decelerated to {g.iloc[-1]:.1f}% in {short(y1)} from a {g.max():.1f}% peak in {short(g.idxmax())}.")\n    if m.np_growth[y1] < m.rev_growth[y1]:\n        con.append(f"Net profit growth ({pct(m.np_growth[y1])}) lagged revenue growth ({pct(m.rev_growth[y1])}) in {short(y1)}.")\n    if m.dso[y1] - m.dso[prev] > 3:\n        con.append(f"Receivable days rose to {m.dso[y1]:.1f} from {m.dso[prev]:.1f}; current trade receivables grew "\n                   f"{(df.ca_receivables[y1] / df.ca_receivables[prev] - 1) * 100:.1f}% against revenue growth of {pct(m.rev_growth[y1])}.")\n    if m.current_ratio[y1] < m.current_ratio[y0]:\n        con.append(f"Current ratio drifted down from {times(m.current_ratio[y0])} to {times(m.current_ratio[y1])} (still above 2x).")\n    if df.goodwill[y1] > df.goodwill[prev] * 1.5:\n        con.append(f"Goodwill rose to {money(df.goodwill[y1])} from {money(df.goodwill[prev])} alongside "\n                   f"{money(df.acquisitions[y1])} of acquisition outflows (subsidiaries and assets), adding integration and impairment risk.")\n    if df.exceptional[y1] > 0:\n        con.append(f"Exceptional charges of {money(df.exceptional[y1])} reduced {short(y1)} profit.")\n    if m.interest_coverage[y1] < m.interest_coverage[prev] * 0.8:\n        con.append(f"Interest coverage fell to {times(m.interest_coverage[y1], 1)} from {times(m.interest_coverage[prev], 1)} as finance costs rose to {money(df.finance_cost[y1])}.")\n    if df.cash[y1] < df.cash[prev]:\n        con.append(f"Cash and cash equivalents fell to {money(df.cash[y1])} from {money(df.cash[prev])} (broader liquid assets rose to {money(m.cash_liquid[y1])}).")\n    if m.asset_turnover[y1] < m.asset_turnover[prev]:\n        con.append(f"Asset turnover eased to {times(m.asset_turnover[y1])} from {times(m.asset_turnover[prev])} as assets grew {pct(m.ta_growth[y1])} versus revenue growth of {pct(m.rev_growth[y1])}.")\n    R["Positive trends"] = [("", t) for t in pos_]\n    R["Potential concerns"] = [("", t) for t in con]\n    return R\n\n\ndef overall_assessment(df, m, years):\n    y0, y1 = years[0], years[-1]\n    g = m.loc[years, "rev_growth"].dropna()\n    n = len(years) - 1\n    cagr = ((m.revenue[y1] / m.revenue[y0]) ** (1 / n) - 1) * 100\n    rows = [\n        ("Growth", "Moderating" if g.iloc[-1] < 8 else "Strong", f"Revenue CAGR {cagr:.1f}%; latest growth {g.iloc[-1]:.1f}%"),\n        ("Profitability", "Strong" if m.op_margin[y1] > 22 else "Adequate", f"Operating margin {pct(m.op_margin[y1])}, ROE {pct(m.roe[y1])}"),\n        ("Liquidity", "Strong" if m.current_ratio[y1] > 1.5 else "Adequate", f"Current ratio {times(m.current_ratio[y1])}, quick {times(m.quick_ratio[y1])}"),\n        ("Solvency", "Strong" if m.debt_equity[y1] < 0.3 else "Adequate", f"Debt-to-equity {times(m.debt_equity[y1])}, no borrowings"),\n        ("Cash generation", "Strong" if m.cfo_to_np[y1] > 95 else "Adequate", f"CFO/net profit {pct(m.cfo_to_np[y1], 0)}, FCF {money(m.fcf[y1])}"),\n        ("Efficiency", "Watch" if m.dso[y1] - m.dso[years].min() > 8 else "Stable", f"Asset turnover {times(m.asset_turnover[y1])}, receivable days {m.dso[y1]:.0f}"),\n    ]\n    table = pd.DataFrame(rows, columns=["Dimension", "Assessment", "Evidence"])\n    text = (\n        f"Based solely on the consolidated statements for {short(y0)}–{short(y1)}, TCS shows a financially robust profile: "\n        f"revenue rose from {money(m.revenue[y0])} to {money(m.revenue[y1])} and net profit from {money(m.net_profit[y0])} to "\n        f"{money(m.net_profit[y1])}, with operating margin held in a {pct(m.op_margin[years].min())}–{pct(m.op_margin[years].max())} band. "\n        f"The balance sheet carries no borrowings, {money(m.cash_liquid[y1])} of liquid assets and a current ratio of {times(m.current_ratio[y1])}; "\n        f"operating cash flow of {money(m.cfo[y1])} fully funded capex and a dividend payout of {pct(m.payout[y1], 0)} of profit.\\n\\n"\n        f"The balancing considerations are momentum and efficiency. Revenue growth slowed to {g.iloc[-1]:.1f}% and net profit growth to "\n        f"{pct(m.np_growth[y1])} in {short(y1)}, held back by {money(df.exceptional[y1])} of exceptional charges; receivable days stretched to "\n        f"{m.dso[y1]:.0f} (from {m.dso[years[-2]]:.0f}); and {money(df.acquisitions[y1])} of acquisition outflows came with goodwill rising to {money(df.goodwill[y1])}. "\n        f"Overall, the data point to a high-quality, cash-generative and conservatively financed business whose near-term question is "\n        f"growth rather than solvency. This is an analytical reading of historical figures, not investment advice."\n    )\n    return table, text\n',
    'charts': '"""Plotly figure builders (Plotly Express + Graph Objects)."""\nimport plotly.express as px\nimport plotly.graph_objects as go\n\nNAVY, BLUE, SKY, SLATE, GREY, RED, TEAL = "#0B2A5B", "#1F6FD1", "#6FB1FC", "#5B6B82", "#C7D2E0", "#C0392B", "#14A3A3"\nPALETTE = [NAVY, BLUE, SKY, SLATE, TEAL, GREY]\n\n\ndef _style(fig, title, height=380, ytitle=None, yfmt=None):\n    fig.update_layout(\n        title=dict(text=title, font=dict(size=16, color=NAVY)), template="plotly_white", height=height,\n        margin=dict(l=10, r=10, t=60, b=10), hovermode="x unified", font=dict(family="Arial", size=12),\n        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),\n    )\n    fig.update_yaxes(title_text=ytitle, gridcolor="#E8EDF4", tickformat=yfmt)\n    fig.update_xaxes(type="category")\n    return fig\n\n\ndef grouped_bar(d, cols, names, title, ytitle, yfmt=",.0f", hover="%{y:,.0f}", barmode="group"):\n    fig = go.Figure()\n    for i, c in enumerate(cols):\n        fig.add_trace(go.Bar(x=d.index, y=d[c], name=names[c], marker_color=PALETTE[i % len(PALETTE)],\n                             hovertemplate=names[c] + ": " + hover + "<extra></extra>"))\n    fig.update_layout(barmode=barmode)\n    return _style(fig, title, ytitle=ytitle, yfmt=yfmt)\n\n\ndef line(d, cols, names, title, ytitle, suffix="", dec=1, markers=True):\n    fig = go.Figure()\n    for i, c in enumerate(cols):\n        fig.add_trace(go.Scatter(x=d.index, y=d[c], name=names[c], mode="lines+markers" if markers else "lines",\n                                 line=dict(color=PALETTE[i % len(PALETTE)], width=3), marker=dict(size=8),\n                                 hovertemplate=names[c] + ": %{y:,." + str(dec) + "f}" + suffix + "<extra></extra>"))\n    return _style(fig, title, ytitle=ytitle)\n\n\ndef bar_with_line(d, bar_col, line_col, bar_name, line_name, title, ytitle, ytitle2):\n    fig = go.Figure()\n    fig.add_trace(go.Bar(x=d.index, y=d[bar_col], name=bar_name, marker_color=BLUE,\n                         hovertemplate=bar_name + ": %{y:,.0f}<extra></extra>"))\n    fig.add_trace(go.Scatter(x=d.index, y=d[line_col], name=line_name, yaxis="y2", mode="lines+markers",\n                             line=dict(color=NAVY, width=3), hovertemplate=line_name + ": %{y:.1f}%<extra></extra>"))\n    fig.update_layout(yaxis2=dict(title=ytitle2, overlaying="y", side="right", showgrid=False))\n    return _style(fig, title, ytitle=ytitle)\n\n\ndef growth_bars(d, cols, names, title):\n    fig = go.Figure()\n    for i, c in enumerate(cols):\n        fig.add_trace(go.Bar(x=d.index, y=d[c], name=names[c], marker_color=PALETTE[i % len(PALETTE)],\n                             hovertemplate=names[c] + ": %{y:.1f}%<extra></extra>"))\n    fig.update_layout(barmode="group")\n    fig.add_hline(y=0, line_color=SLATE, line_width=1)\n    return _style(fig, title, ytitle="YoY growth (%)", yfmt=".1f")\n\n\ndef stacked_long(d, cols, names, title, ytitle, as_pct=False):\n    """Plotly Express stacked bar from a wide frame (optionally normalised to 100%)."""\n    x = d[cols].copy()\n    if as_pct:\n        x = x.div(x.sum(axis=1), axis=0) * 100\n    long = x.rename(columns=names).reset_index().melt(id_vars=d.index.name or "index", var_name="Component", value_name="Value")\n    fig = px.bar(long, x=d.index.name or "index", y="Value", color="Component", color_discrete_sequence=PALETTE + [TEAL, RED],\n                 barmode="stack")\n    fig.update_traces(hovertemplate="%{fullData.name}: %{y:,.1f}" + ("%" if as_pct else "") + "<extra></extra>")\n    return _style(fig, title, ytitle=ytitle, height=400)\n\n\ndef ratio_chart(d, key, label, kind, dec=2):\n    suffix = {"%": "%", "x": "x", "days": " days"}[kind]\n    fig = go.Figure(go.Scatter(x=d.index, y=d[key], mode="lines+markers+text", line=dict(color=BLUE, width=3),\n                               marker=dict(size=9, color=NAVY), text=[f"{v:.{dec}f}" for v in d[key]], textposition="top center",\n                               hovertemplate=label + ": %{y:." + str(dec) + "f}" + suffix + "<extra></extra>"))\n    fig.update_yaxes(rangemode="tozero")\n    return _style(fig, label, height=320, ytitle=suffix.strip())\n\n\ndef waterfall_like(d, cols, names, title, ytitle):\n    """Cash-flow components as signed bars."""\n    return grouped_bar(d, cols, names, title, ytitle, hover="%{y:,.0f}")\n',
    'export': '"""Builds the downloadable Excel workbook (OpenPyXL engine)."""\nimport io\nimport pandas as pd\nfrom openpyxl.styles import Font, PatternFill, Alignment\nfrom openpyxl.utils import get_column_letter\nfrom .dataset import NOT_REPORTED, SOURCES\nfrom .metrics import METRIC_LABELS\n\n\ndef _statement(df, labels, keys):\n    t = df[[k for k in keys if k in df.columns]].T\n    t.insert(0, "Line item", [labels.get(k, k) for k in t.index])\n    return t.reset_index(drop=True)\n\n\ndef build_workbook(df, labels, m, recon, insights, years, basis):\n    from .dataset import INCOME, BALANCE, CASHFLOW\n    buf = io.BytesIO()\n    met = m.loc[years, [c for c in METRIC_LABELS if c in m.columns]].T.round(4)\n    met.insert(0, "Metric", [METRIC_LABELS[k] for k in met.index])\n    ins = pd.DataFrame([(cat, t, x) for cat, items in insights.items() for t, x in items], columns=["Category", "Title", "Insight"])\n    notes = pd.DataFrame([("Basis for return/turnover ratios", "Average of opening and closing balances" if basis == "average" else "Year-end balances"),\n                          ("Units", "INR crore unless stated"), ("Scope", "Consolidated Ind AS statements only")]\n                         + [(k, v) for k, v in NOT_REPORTED.items()] + [(y, SOURCES[y]) for y in years], columns=["Item", "Note"])\n    with pd.ExcelWriter(buf, engine="openpyxl") as xw:\n        for name, rows in (("Income Statement", INCOME), ("Balance Sheet", BALANCE), ("Cash Flow", CASHFLOW)):\n            _statement(df.loc[years], labels, rows.keys()).to_excel(xw, sheet_name=name, index=False)\n        met.reset_index(drop=True).to_excel(xw, sheet_name="Ratios & Metrics", index=False)\n        recon.to_excel(xw, sheet_name="Data Checks", index=False)\n        ins.to_excel(xw, sheet_name="Insights", index=False)\n        notes.to_excel(xw, sheet_name="Notes", index=False)\n        for ws in xw.book.worksheets:\n            for c in ws[1]:\n                c.font = Font(bold=True, color="FFFFFF"); c.fill = PatternFill("solid", fgColor="0B2A5B")\n                c.alignment = Alignment(horizontal="center", wrap_text=True)\n            for i, col in enumerate(ws.columns, 1):\n                width = max(len(str(c.value)) if c.value is not None else 0 for c in col)\n                ws.column_dimensions[get_column_letter(i)].width = min(max(12, width + 2), 70 if i <= 3 else 22)\n            ws.freeze_panes = "B2"\n    return buf.getvalue()\n',
}


def _bootstrap():
    pkg = types.ModuleType("tcs_fin"); pkg.__path__ = []; sys.modules["tcs_fin"] = pkg
    for name in ['dataset', 'fmt', 'metrics', 'loader', 'insights', 'charts', 'export']:
        mod = types.ModuleType("tcs_fin." + name); mod.__package__ = "tcs_fin"
        sys.modules["tcs_fin." + name] = mod; setattr(pkg, name, mod)
        exec(compile(_SRC[name], "tcs_fin/" + name + ".py", "exec"), mod.__dict__)


_bootstrap()

import copy
import pathlib

import pandas as pd
import streamlit as st

from tcs_fin import charts as ch
from tcs_fin.dataset import DISPLAY_YEARS, NOT_REPORTED, SOURCES
from tcs_fin.export import build_workbook
from tcs_fin.fmt import UNITS, money, pct, pp, short, times
from tcs_fin.insights import build_insights, overall_assessment, ratio_commentary
from tcs_fin.loader import load_statements, reconcile
from tcs_fin.metrics import FORMULAS, METRIC_LABELS, RATIOS, compute_metrics

st.set_page_config(page_title="TCS Financial Dashboard", page_icon="📊", layout="wide",
                   initial_sidebar_state="expanded")

DATA_FILE = pathlib.Path(__file__).parent / "data" / "tcs_consolidated_financials.xlsx"
PAGES = ["Executive Summary", "Revenue & Profitability", "Balance Sheet", "Ratio Analysis",
         "Cash Flow", "Financial Insights", "Data & Downloads"]

GROWTH_OPTS = {"rev_growth": "Revenue", "op_growth": "Operating profit", "np_growth": "Net profit", "eps_growth": "EPS"}
PL_OPTS = {"revenue": "Revenue", "op_profit": "Operating profit", "net_profit": "Net profit"}
CF_OPTS = {"cfo": "Operating activities", "cfi": "Investing activities", "cff": "Financing activities"}
GROUPS = ["Profitability", "Liquidity", "Efficiency", "Solvency"]

DEFAULTS = {
    "sel_year": DISPLAY_YEARS[-1], "cmp_to": "Previous year", "cmp_years": list(DISPLAY_YEARS),
    "basis_label": "Average balances", "unit": "INR crore",
    "pl_metrics": list(PL_OPTS), "growth_metrics": list(GROWTH_OPTS), "cf_metrics": list(CF_OPTS),
    **{f"ratios_{g}": [k for k, v in RATIOS.items() if v[3] == g] for g in GROUPS},
}

# ------------------------------------------------------------------ data
@st.cache_data(show_spinner=False)
def get_statements(path: str):
    df, labels, _ = load_statements(path)
    return df, labels


@st.cache_data(show_spinner=False)
def get_metrics(df: pd.DataFrame, basis: str):
    return compute_metrics(df, basis)


def span(years):
    """Contiguous run of years from the earliest to the latest selected (insights need an unbroken series)."""
    idx = [DISPLAY_YEARS.index(y) for y in years]
    return DISPLAY_YEARS[min(idx): max(idx) + 1]


@st.cache_data(show_spinner=False)
def get_excel(years: tuple, basis: str):
    df, labels = get_statements(str(DATA_FILE))
    m = get_metrics(df, basis)
    yrs = list(years)
    sp = span(yrs)
    return build_workbook(df, labels, m, reconcile(df), build_insights(df, m, sp) if len(sp) > 1 else {}, yrs, basis)


# ------------------------------------------------------------------ state / sidebar
for _k, _v in DEFAULTS.items():
    st.session_state.setdefault(_k, copy.deepcopy(_v))
st.session_state.setdefault("page", PAGES[0])


def reset_filters():
    for k, v in DEFAULTS.items():
        st.session_state[k] = copy.deepcopy(v)


df_all, labels = get_statements(str(DATA_FILE))

st.sidebar.title("TCS Financial Analytics")
st.sidebar.caption("Tata Consultancy Services Ltd. | Consolidated, Ind AS")
st.sidebar.radio("Navigate", PAGES, key="page")
st.sidebar.divider()
st.sidebar.subheader("Filters")
st.sidebar.selectbox("Financial year (KPIs & snapshots)", DISPLAY_YEARS, key="sel_year")
st.sidebar.multiselect("Years to compare (charts & tables)", DISPLAY_YEARS, key="cmp_years")
_cmp_opts = ["Previous year"] + [y for y in DISPLAY_YEARS if y != st.session_state["sel_year"]]
if st.session_state["cmp_to"] not in _cmp_opts:
    st.session_state["cmp_to"] = "Previous year"
st.sidebar.selectbox("Compare KPIs against", _cmp_opts, key="cmp_to")
st.sidebar.radio("Return / turnover ratio basis", ["Average balances", "Year-end balances"], key="basis_label")
st.sidebar.radio("Currency unit", list(UNITS), key="unit", horizontal=True)
st.sidebar.button("Reset filters", on_click=reset_filters, use_container_width=True)

basis = "average" if st.session_state["basis_label"].startswith("Average") else "closing"
unit = st.session_state["unit"]
U = UNITS[unit]
sel = st.session_state["sel_year"]
cmp_years = [y for y in DISPLAY_YEARS if y in st.session_state["cmp_years"]]
if not cmp_years:
    st.sidebar.warning("No years selected - showing all five years.")
    cmp_years = list(DISPLAY_YEARS)

m_all = get_metrics(df_all, basis)
all_years = list(df_all.index)
prev_default = all_years[all_years.index(sel) - 1]
cmp_to = prev_default if st.session_state["cmp_to"] == "Previous year" else st.session_state["cmp_to"]

MONEY_COLS = ["revenue", "op_profit", "ebitda", "pbe", "pbt", "net_profit", "profit_for_year", "total_assets", "total_liabilities",
              "equity", "total_equity", "current_assets", "current_liabilities", "cash", "cash_liquid", "lease_liabilities",
              "total_debt", "net_cash", "capital_employed", "cfo", "cfi", "cff", "capex", "fcf", "fcf_after_leases", "shareholder_returns"]
m = m_all.loc[cmp_years].copy()
d = df_all.loc[cmp_years].copy()
m_s = m.copy()
m_s[MONEY_COLS] = m_s[MONEY_COLS] * U               # unit-scaled copy for charts
d_s = d.copy()
for c in d.columns:
    if c not in ("eps", "shares_cr"):
        d_s[c] = d[c] * U
HOV = "%{y:,.0f}" if unit == "INR crore" else "%{y:,.1f}"
YF = ",.0f" if unit == "INR crore" else ",.1f"
YT = f"{unit}"


def show(fig, key):
    st.plotly_chart(fig, use_container_width=True, key=key)


def kpi(col, label, value, delta=None, inverse=False, help=None):
    with col:
        with st.container(border=True):
            st.metric(label, value, delta, delta_color="inverse" if inverse else "normal", help=help)


def pct_delta(cur, old, ref):
    return f"{(cur / old - 1) * 100:+.1f}% vs {short(ref)}"


def pp_delta(cur, old, ref):
    return f"{cur - old:+.1f} pp vs {short(ref)}"


def header(title, sub):
    st.title(title)
    st.caption(sub)


UNIT_NOTE = f"All amounts in {unit} · consolidated · {short(cmp_years[0])}–{short(cmp_years[-1])} · ratios on {st.session_state['basis_label'].lower()}"

# ------------------------------------------------------------------ pages
def page_summary():
    header("Tata Consultancy Services - Executive Financial Summary", UNIT_NOTE)
    c, p = m_all.loc[sel], m_all.loc[cmp_to]
    st.subheader(f"{sel} snapshot vs {cmp_to}")
    r1, r2, r3 = st.columns(4), st.columns(4), st.columns(4)
    kpi(r1[0], "Total Revenue", money(c.revenue, unit), pct_delta(c.revenue, p.revenue, cmp_to))
    kpi(r1[1], "Revenue Growth (YoY)", pct(c.rev_growth), pp_delta(c.rev_growth, p.rev_growth, cmp_to) if pd.notna(p.rev_growth) else None,
        help="Growth over the immediately preceding year.")
    kpi(r1[2], "Operating Profit", money(c.op_profit, unit), pct_delta(c.op_profit, p.op_profit, cmp_to),
        help="Revenue less employee, equipment, depreciation and other expenses; excludes other income, finance cost and exceptional items.")
    kpi(r1[3], "Operating Profit Margin", pct(c.op_margin), pp_delta(c.op_margin, p.op_margin, cmp_to))
    kpi(r2[0], "Net Profit", money(c.net_profit, unit), pct_delta(c.net_profit, p.net_profit, cmp_to), help="Attributable to shareholders.")
    kpi(r2[1], "Net Profit Margin", pct(c.net_margin), pp_delta(c.net_margin, p.net_margin, cmp_to))
    kpi(r2[2], "Earnings Per Share", f"₹{c.eps:.2f}", pct_delta(c.eps, p.eps, cmp_to), help="Basic & diluted, as reported.")
    kpi(r2[3], "Total Assets", money(c.total_assets, unit), pct_delta(c.total_assets, p.total_assets, cmp_to))
    kpi(r3[0], "Total Liabilities", money(c.total_liabilities, unit), pct_delta(c.total_liabilities, p.total_liabilities, cmp_to), inverse=True)
    kpi(r3[1], "Shareholders' Equity", money(c.equity, unit), pct_delta(c.equity, p.equity, cmp_to))
    kpi(r3[2], "Return on Equity", pct(c.roe), pp_delta(c.roe, p.roe, cmp_to) if pd.notna(p.roe) else None)
    kpi(r3[3], "Return on Capital Employed", pct(c.roce), pp_delta(c.roce, p.roce, cmp_to) if pd.notna(p.roce) else None)
    st.divider()
    a, b = st.columns(2)
    with a:
        show(ch.bar_with_line(m_s, "revenue", "op_margin", "Revenue", "Operating margin", "Revenue and operating margin", YT, "Margin (%)"), "sum_rev")
    with b:
        show(ch.bar_with_line(m_s, "net_profit", "net_margin", "Net profit", "Net margin", "Net profit and net margin", YT, "Margin (%)"), "sum_np")
    st.subheader("Selected years at a glance")
    keys = ["revenue", "op_profit", "net_profit", "eps", "op_margin", "net_margin", "roe", "roce", "total_assets", "total_liabilities", "equity", "cfo", "fcf"]
    t = m_s[keys].T.round(2)
    t.index = [METRIC_LABELS[k] for k in t.index]
    st.dataframe(t, use_container_width=True)


def page_profit():
    header("Revenue & Profitability Analysis", UNIT_NOTE)
    t1, t2, t3, t4 = st.tabs(["Trends", "Margins", "Growth", "Cost structure"])
    with t1:
        st.multiselect("Metrics to plot", list(PL_OPTS), format_func=PL_OPTS.get, key="pl_metrics")
        cols = [k for k in PL_OPTS if k in st.session_state["pl_metrics"]] or list(PL_OPTS)
        show(ch.grouped_bar(m_s, cols, PL_OPTS, "Revenue vs Operating Profit vs Net Profit", YT, YF, HOV), "pl_group")
        for col, k in zip(st.columns(3), PL_OPTS):
            with col:
                show(ch.line(m_s, [k], PL_OPTS, f"{PL_OPTS[k]} trend", YT, dec=0 if unit == "INR crore" else 1), f"pl_line_{k}")
    with t2:
        a, b = st.columns(2)
        with a:
            show(ch.line(m, ["op_margin"], METRIC_LABELS, "Operating profit margin (%)", "%", "%"), "mg_op")
        with b:
            show(ch.line(m, ["net_margin"], METRIC_LABELS, "Net profit margin (%)", "%", "%"), "mg_np")
        show(ch.line(m, ["op_margin", "ebitda_margin", "pbt_margin", "net_margin"], METRIC_LABELS, "Margin comparison (%)", "%", "%"), "mg_all")
    with t3:
        st.multiselect("Growth metrics", list(GROWTH_OPTS), format_func=GROWTH_OPTS.get, key="growth_metrics")
        cols = [k for k in GROWTH_OPTS if k in st.session_state["growth_metrics"]] or list(GROWTH_OPTS)
        show(ch.growth_bars(m, cols, GROWTH_OPTS, "Year-on-year growth (%)"), "gr")
        st.caption(f"{short(DISPLAY_YEARS[0])} growth uses FY2021 as the comparative base year.")
    with t4:
        cost = ["employee_cost", "equipment_cost", "depreciation", "other_expenses"]
        names = {k: labels[k] for k in cost}
        show(ch.stacked_long(d_s, cost, names, f"Operating cost components ({unit})", YT), "cost_abs")
        pc = d[cost].div(d.revenue, axis=0) * 100
        pc.index.name = "Year"
        show(ch.stacked_long(pc, cost, names, "Operating cost components (% of revenue)", "% of revenue"), "cost_pct")


def page_balance():
    header("Balance Sheet Analysis", UNIT_NOTE)
    show(ch.grouped_bar(m_s, ["total_assets", "total_liabilities", "equity"],
                        {"total_assets": "Total assets", "total_liabilities": "Total liabilities", "equity": "Shareholders' equity"},
                        "Total assets vs liabilities vs equity", YT, YF, HOV), "bs_main")
    a, b = st.columns(2)
    with a:
        show(ch.grouped_bar(m_s, ["current_assets", "current_liabilities"], {"current_assets": "Current assets", "current_liabilities": "Current liabilities"},
                            "Current assets vs current liabilities", YT, YF, HOV), "bs_cur")
    with b:
        liq = ["cash", "other_bank", "ca_investments"]
        show(ch.stacked_long(d_s, liq, {k: labels[k] for k in liq}, "Cash, bank balances and current investments", YT), "bs_cash")
    a, b = st.columns(2)
    with a:
        debt = ["lease_nc", "lease_c", "ccps"]
        show(ch.stacked_long(d_s, debt, {k: labels[k] for k in debt}, "Debt position (leases and preference shares)", YT), "bs_debt")
        st.caption("TCS reports no bank or bond borrowings in any year shown; lease liabilities are the main debt-like item.")
    with b:
        struct = pd.DataFrame({"Total equity": d.total_equity, "Non-current liabilities": d.total_ncl, "Current liabilities": d.total_cl})
        struct.index.name = "Year"
        show(ch.stacked_long(struct, list(struct.columns), {k: k for k in struct.columns}, "Financial structure (% of total assets)", "%", as_pct=True), "bs_struct")
    comp = pd.DataFrame({"PPE + CWIP": d.ppe + d.cwip, "Right-of-use assets": d.rou, "Goodwill + intangibles": d.goodwill + d.intangibles,
                         "Investments": d.nca_investments + d.ca_investments, "Trade receivables": d.ca_receivables + d.nca_receivables,
                         "Cash and bank": d.cash + d.other_bank,
                         "Other assets": d.total_assets - (d.ppe + d.cwip + d.rou + d.goodwill + d.intangibles + d.nca_investments + d.ca_investments
                                                             + d.ca_receivables + d.nca_receivables + d.cash + d.other_bank)})
    comp.index.name = "Year"
    show(ch.stacked_long(comp, list(comp.columns), {k: k for k in comp.columns}, "Asset composition (% of total assets)", "%", as_pct=True), "bs_assets")
    st.subheader(f"Changes in financial structure: {sel} vs {cmp_to}")
    keys = ["total_assets", "total_ca", "total_nca", "goodwill", "ca_receivables", "cash", "ca_investments", "total_equity", "total_ncl", "total_cl", "lease_nc", "trade_payables"]
    ch_df = pd.DataFrame({cmp_to: df_all.loc[cmp_to, keys] * U, sel: df_all.loc[sel, keys] * U})
    ch_df["Change"] = ch_df[sel] - ch_df[cmp_to]
    ch_df["Change %"] = (ch_df[sel] / ch_df[cmp_to] - 1) * 100
    ch_df.index = [labels[k] for k in keys]
    st.dataframe(ch_df.round(1), use_container_width=True)


def page_ratios():
    header("Financial Ratio Analysis", UNIT_NOTE)
    tabs = st.tabs(GROUPS + ["Formulas & notes"])
    for tab, g in zip(tabs[:4], GROUPS):
        with tab:
            opts = [k for k, v in RATIOS.items() if v[3] == g]
            st.multiselect("Ratios to display", opts, format_func=lambda k: RATIOS[k][0], key=f"ratios_{g}")
            chosen = [k for k in opts if k in st.session_state[f"ratios_{g}"]] or opts
            for k in chosen:
                label, kind, _, _ = RATIOS[k]
                c1, c2 = st.columns([3, 2])
                if m[k].isna().all():
                    st.info(f"**{label}** cannot be calculated: {FORMULAS[k]}")
                    continue
                with c1:
                    show(ch.ratio_chart(m, k, label, kind), f"ratio_{k}")
                with c2:
                    st.markdown("&nbsp;")
                    st.markdown(ratio_commentary(k, m, cmp_years) if len(cmp_years) > 1 else f"**{label}**: {m[k].iloc[0]:.2f} in {cmp_years[0]}.")
    with tabs[4]:
        st.markdown(f"Return and turnover ratios use **{st.session_state['basis_label'].lower()}** (change in the sidebar).")
        t = pd.DataFrame({RATIOS[k][0]: {"Group": RATIOS[k][3], "Formula": FORMULAS[k]} for k in RATIOS}).T
        st.dataframe(t, use_container_width=True)
        st.subheader("Not reported / not calculable")
        for k, v in NOT_REPORTED.items():
            st.markdown(f"- **{k}:** {v}")


def page_cash():
    header("Cash Flow Analysis", UNIT_NOTE)
    st.multiselect("Cash flow categories", list(CF_OPTS), format_func=CF_OPTS.get, key="cf_metrics")
    cols = [k for k in CF_OPTS if k in st.session_state["cf_metrics"]] or list(CF_OPTS)
    show(ch.grouped_bar(m_s, cols, CF_OPTS, "Cash flow from operating, investing and financing activities", YT, YF, HOV), "cf_main")
    a, b = st.columns(2)
    with a:
        show(ch.grouped_bar(m_s, ["cfo", "capex", "fcf"], {"cfo": "Operating cash flow", "capex": "Capex", "fcf": "Free cash flow"},
                            "Free cash flow (CFO less capex)", YT, YF, HOV), "cf_fcf")
        st.caption("Capex = purchase of PPE + intangibles + advances for right-of-use assets. Acquisitions are excluded.")
    with b:
        show(ch.grouped_bar(m_s, ["cfo", "net_profit"], {"cfo": "Operating cash flow", "net_profit": "Net profit"},
                            "Operating cash flow vs net profit", YT, YF, HOV), "cf_np")
    a, b = st.columns(2)
    with a:
        show(ch.line(m, ["cfo_to_np", "fcf_to_np"], METRIC_LABELS, "Cash conversion (% of net profit)", "%", "%", dec=0), "cf_conv")
    with b:
        uses = pd.DataFrame({"Capex": m.capex, "Acquisitions": d.acquisitions, "Lease repayments": d.lease_repay,
                             "Dividends": d.dividend_sh, "Buy-backs": d.buyback}) * U
        uses.index.name = "Year"
        show(ch.stacked_long(uses, list(uses.columns), {k: k for k in uses.columns}, f"Uses of cash ({unit})", YT), "cf_uses")
    t = m_s[["cfo", "cfi", "cff", "fcf", "fcf_after_leases", "cfo_to_np", "payout"]].T.round(1)
    t.index = [METRIC_LABELS[k] for k in t.index]
    st.dataframe(t, use_container_width=True)


def page_insights():
    header("Automated Financial Insights", UNIT_NOTE)
    yrs = span(cmp_years)
    if len(yrs) < 2:
        st.warning("Select at least two years in the sidebar to generate trend-based insights.")
        return
    if yrs != cmp_years:
        st.caption(f"Insights use the unbroken span {short(yrs[0])}-{short(yrs[-1])} so that year-on-year statements stay accurate.")
    ins = build_insights(df_all, m_all, yrs)
    for cat in ["Highlights", "Growth", "Profitability", "Liquidity", "Stability", "Efficiency", "Cash Flow"]:
        if cat in ins:
            st.subheader(cat)
            for title, text in ins[cat]:
                st.markdown(f"**{title}.** {text}")
    a, b = st.columns(2)
    with a:
        st.subheader("Positive financial trends")
        for _, t in ins.get("Positive trends", []):
            st.success(t)
    with b:
        st.subheader("Potential financial concerns")
        for _, t in ins.get("Potential concerns", []):
            st.warning(t)
    st.divider()
    st.header("Overall Financial Performance Assessment of TCS")
    table, text = overall_assessment(df_all, m_all, yrs)
    st.dataframe(table, use_container_width=True, hide_index=True)
    st.markdown(text)


def page_data():
    header("Data Quality & Downloads", UNIT_NOTE)
    rec = reconcile(df_all)
    st.subheader("Data quality")
    c = st.columns(4)
    c[0].metric("Line items", df_all.shape[1])
    c[1].metric("Missing values", int(df_all.isna().sum().sum()))
    c[2].metric("Reconciliation checks passed", f"{(rec.Status == 'PASS').sum()} / {len(rec)}")
    c[3].metric("Metrics not calculable", len(NOT_REPORTED) - 1)
    with st.expander("Reconciliation detail"):
        st.dataframe(rec, use_container_width=True, hide_index=True)
    with st.expander("Sources and availability notes"):
        for y in reversed(list(SOURCES)):
            st.markdown(f"- **{y}:** {SOURCES[y]}")
        for k, v in NOT_REPORTED.items():
            st.markdown(f"- **{k}:** {v}")
    st.subheader("Statements")
    which = st.selectbox("Statement", ["Income Statement", "Balance Sheet", "Cash Flow"])
    from tcs_fin.dataset import all_statements
    keys = list(all_statements()[which])
    t = d[keys].T
    t.index = [labels[k] for k in keys]
    st.dataframe(t, use_container_width=True)
    st.subheader("Computed ratios and metrics")
    mt = m[[k for k in METRIC_LABELS if k in m.columns]].T.round(3)
    mt.index = [METRIC_LABELS[k] for k in mt.index]
    st.dataframe(mt, use_container_width=True)
    st.subheader("Download analysed data")
    st.caption(f"Exports the years currently selected ({', '.join(cmp_years)}) with ratios on {st.session_state['basis_label'].lower()}.")
    a, b = st.columns(2)
    a.download_button("Download Excel workbook (.xlsx)", get_excel(tuple(cmp_years), basis), "TCS_analysed_financials.xlsx",
                      "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", use_container_width=True)
    b.download_button("Download ratios (.csv)", mt.to_csv().encode("utf-8"), "TCS_ratios_and_metrics.csv", "text/csv", use_container_width=True)


PAGE_FUNCS = {"Executive Summary": page_summary, "Revenue & Profitability": page_profit, "Balance Sheet": page_balance,
              "Ratio Analysis": page_ratios, "Cash Flow": page_cash, "Financial Insights": page_insights, "Data & Downloads": page_data}
PAGE_FUNCS[st.session_state["page"]]()

st.sidebar.divider()
st.sidebar.download_button("Download analysed data (.xlsx)", get_excel(tuple(cmp_years), basis), "TCS_analysed_financials.xlsx",
                           "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", use_container_width=True)
st.sidebar.caption("Source: TCS Integrated Annual Reports FY2021-22 to FY2025-26 (consolidated). Not investment advice.")
