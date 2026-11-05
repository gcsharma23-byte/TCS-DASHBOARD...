"""
Hand-extracted TCS *consolidated* financial statements (Ind AS), INR crore.

Source mapping (all CONSOLIDATED; standalone figures are never used):
  FY2025-26 Integrated Annual Report -> FY2026 (current) and FY2025 (comparative)  [pp.196-203]
  FY2023-24 Integrated Annual Report -> FY2024 (current) and FY2023 (comparative)  [pp.180-185]
  FY2021-22 Integrated Annual Report -> FY2022 (current) and FY2021 (comparative)  [pp.243-251]

The text layer of the FY2024-25 PDF is corrupted (digits dropped, e.g. "1,5 6" for 1,546), so
FY2025 is read from the clean comparative column of the FY2025-26 report. FY2023 figures were
cross-checked against the FY2022-23 report's own statements (no restatements found).

FY2021 is a *base year* only (for FY2022 growth and average balances). The dashboard
displays FY2022-FY2026, the five most recent years.
"""
from collections import OrderedDict

YEARS = ["FY2021", "FY2022", "FY2023", "FY2024", "FY2025", "FY2026"]
BASE_YEAR = "FY2021"
DISPLAY_YEARS = YEARS[1:]

INCOME = OrderedDict([
    ("revenue",        ("Revenue from operations",                     [164177, 191754, 225458, 240893, 255324, 267021])),
    ("other_income",   ("Other income",                                [3134, 4018, 3449, 4422, 3962, 4402])),
    ("total_income",   ("Total income",                                [167311, 195772, 228907, 245315, 259286, 271423])),
    ("employee_cost",  ("Employee benefit expenses",                   [91814, 107554, 127522, 140131, 145788, 154994])),
    ("equipment_cost", ("Cost of equipment and software licences",     [1462, 1163, 1881, 3702, 11648, 4399])),
    ("finance_cost",   ("Finance costs",                               [637, 784, 779, 778, 796, 1227])),
    ("depreciation",   ("Depreciation and amortisation expense",       [4065, 4604, 5022, 4985, 5242, 5560])),
    ("other_expenses", ("Other expenses",                              [24355, 29980, 36796, 32764, 30481, 35230])),
    ("total_expenses", ("Total expenses",                              [122333, 144085, 172000, 182360, 193955, 201410])),
    ("pbe",            ("Profit before exceptional items and tax",     [44978, 51687, 56907, 62955, 65331, 70013])),
    ("exceptional",    ("Exceptional items (expense)",                 [1218, 0, 0, 958, 0, 4526])),
    ("pbt",            ("Profit before tax",                           [43760, 51687, 56907, 61997, 65331, 65487])),
    ("current_tax",    ("Current tax",                                 [11635, 13654, 14757, 15864, 16910, 16388])),
    ("deferred_tax",   ("Deferred tax",                                [-437, -416, -153, 34, -376, -355])),
    ("total_tax",      ("Total tax expense",                           [11198, 13238, 14604, 15898, 16534, 16033])),
    ("pat",            ("Profit for the year",                         [32562, 38449, 42303, 46099, 48797, 49454])),
    ("pat_sh",         ("Profit attributable to shareholders",         [32430, 38327, 42147, 45908, 48553, 49210])),
    ("pat_nci",        ("Profit attributable to non-controlling interests", [132, 122, 156, 191, 244, 244])),
    ("eps",            ("Earnings per share - basic & diluted (INR)",  [86.71, 103.62, 115.19, 125.88, 134.19, 136.01])),
    ("shares_cr",      ("Weighted average equity shares (crore)",      [374.0110733, 369.8832195, 365.9051373, 364.6851755, 361.8087518, 361.8087518])),
])

BALANCE = OrderedDict([
    ("ppe",             ("Property, plant and equipment",             [11110, 10774, 10230, 9376, 10978, 11032])),
    ("cwip",            ("Capital work-in-progress",                  [926, 1205, 1234, 1564, 1546, 2665])),
    ("rou",             ("Right-of-use assets",                       [7633, 7636, 7560, 7886, 9275, 11027])),
    ("goodwill",        ("Goodwill",                                  [1798, 1787, 1858, 1832, 1860, 9108])),
    ("intangibles",     ("Other intangible assets",                   [480, 1101, 867, 510, 940, 176])),
    ("nca_investments", ("Non-current investments",                   [213, 223, 266, 281, 275, 218])),
    ("nca_receivables", ("Non-current trade receivables (billed+unbilled)", [328, 200, 348, 143, 129, 213])),
    ("nca_loans",       ("Non-current loans",                         [29, 311, 173, 2, 25, 775])),
    ("nca_other_fin",   ("Non-current other financial assets",        [1573, 2253, 2149, 3272, 2731, 2944])),
    ("dta",             ("Deferred tax assets (net)",                 [3931, 3708, 3307, 3403, 3578, 4465])),
    ("nca_tax_assets",  ("Non-current income tax assets (net)",       [1845, 1983, 2583, 1600, 1569, 1439])),
    ("nca_other",       ("Non-current other assets",                  [1613, 2023, 2806, 3596, 3712, 2605])),
    ("total_nca",       ("Total non-current assets",                  [31479, 33204, 33381, 33465, 36618, 46667])),
    ("inventories",     ("Inventories",                               [8, 20, 28, 28, 21, 29])),
    ("ca_investments",  ("Current investments",                       [29160, 30262, 36897, 31481, 30689, 33770])),
    ("ca_receivables",  ("Current trade receivables (billed+unbilled)", [36662, 41810, 49954, 53577, 59046, 67714])),
    ("cash",            ("Cash and cash equivalents",                 [6858, 12488, 7123, 9016, 8342, 6417])),
    ("other_bank",      ("Other balances with banks",                 [2471, 5733, 3909, 4270, 7121, 6491])),
    ("ca_loans",        ("Current loans",                             [11472, 6445, 1325, 491, 9, 1659])),
    ("ca_other_fin",    ("Current other financial assets",            [1394, 1390, 1319, 1703, 2742, 1833])),
    ("ca_tax_assets",   ("Current income tax assets (net)",           [19, 11, 8, 151, 257, 1259])),
    ("ca_other",        ("Current other assets",                      [11236, 10151, 9707, 12267, 14784, 16533])),
    ("total_ca",        ("Total current assets",                      [99280, 108310, 110270, 112984, 123011, 135705])),
    ("total_assets",    ("TOTAL ASSETS",                              [130759, 141514, 143651, 146449, 159629, 182372])),
    ("share_capital",   ("Share capital",                             [370, 366, 366, 362, 362, 362])),
    ("other_equity",    ("Other equity",                              [86063, 88773, 90058, 90127, 94394, 106878])),
    ("equity_sh",       ("Equity attributable to shareholders",       [86433, 89139, 90424, 90489, 94756, 107240])),
    ("nci",             ("Non-controlling interests",                 [675, 707, 782, 830, 1015, 1238])),
    ("total_equity",    ("Total equity",                              [87108, 89846, 91206, 91319, 95771, 108478])),
    ("ccps",            ("Class B compulsorily convertible preference shares", [0, 0, 0, 0, 0, 126])),
    ("lease_nc",        ("Non-current lease liabilities",             [6503, 6368, 6203, 6516, 7838, 9453])),
    ("other_fin_nc",    ("Non-current other financial liabilities",   [280, 572, 353, 365, 680, 588])),
    ("emp_nc",          ("Non-current employee benefit obligations",  [749, 677, 536, 686, 841, 961])),
    ("dtl",             ("Deferred tax liabilities (net)",            [767, 590, 792, 977, 980, 1205])),
    ("unearned_nc",     ("Non-current unearned and deferred revenue", [1197, 1110, 1003, 482, 518, 647])),
    ("total_ncl",       ("Total non-current liabilities",             [9496, 9317, 8887, 9026, 10857, 12980])),
    ("lease_c",         ("Current lease liabilities",                 [1292, 1450, 1485, 1505, 1554, 1830])),
    ("trade_payables",  ("Trade payables",                            [7860, 8045, 10515, 9981, 13909, 14808])),
    ("other_fin_c",     ("Current other financial liabilities",       [6150, 7687, 9068, 8362, 8542, 11194])),
    ("unearned_c",      ("Current unearned and deferred revenue",     [3650, 3635, 3843, 3640, 4028, 4487])),
    ("other_liab_c",    ("Current other liabilities",                 [4068, 8392, 4892, 6524, 7188, 6866])),
    ("provisions",      ("Provisions",                                [1394, 1411, 345, 140, 180, 1378])),
    ("emp_c",           ("Current employee benefit obligations",      [3498, 3810, 4065, 4519, 4885, 5600])),
    ("tax_liab",        ("Income tax liabilities (net)",              [6243, 7921, 9345, 11433, 12715, 14751])),
    ("total_cl",        ("Total current liabilities",                 [34155, 42351, 43558, 46104, 53001, 60914])),
])

CASHFLOW = OrderedDict([
    ("op_profit_pre_wc", ("Operating profit before working capital changes", [47031, 54204, 59148, 63709, 67853, 68688])),
    ("taxes_paid",       ("Taxes paid (net of refunds)",                  [9092, 11486, 12966, 12489, 15586, 14384])),
    ("cfo",              ("Net cash from operating activities",           [38802, 39949, 41965, 44338, 48908, 52094])),
    ("cfi",              ("Net cash from / (used in) investing activities", [-8129, -897, 39, 6026, -2318, -12845])),
    ("cff",              ("Net cash used in financing activities",        [-32634, -33581, -47878, -48536, -47438, -42133])),
    ("capex_ppe",        ("Purchase of property, plant and equipment",    [2719, 2483, 2532, 2202, 2917, 3670])),
    ("capex_rou",        ("Payments incl. advances for right-of-use assets", [101, 15, 213, 30, 76, 109])),
    ("capex_intang",     ("Purchase of intangible assets",                [356, 497, 355, 442, 944, 367])),
    ("acquisitions",     ("Acquisition of subsidiaries and assets",       [0, 0, 0, 0, 1063, 7304])),
    ("lease_repay",      ("Repayment of lease liabilities",               [1336, 1417, 1515, 1614, 1664, 1861])),
    ("interest_paid",    ("Interest paid",                                [634, 698, 779, 699, 840, 901])),
    ("dividend_sh",      ("Dividend paid to shareholders",                [10850, 13317, 41347, 25137, 44864, 39437])),
    ("dividend_nci",     ("Dividend paid to non-controlling interests",   [57, 58, 63, 81, 98, 134])),
    ("buyback",          ("Buy-back of shares incl. tax and expenses",    [19757, 18049, 4192, 21005, 0, 0])),
    ("net_change_cash",  ("Net change in cash and cash equivalents",      [-1961, 5471, -5874, 1828, -848, -2884])),
    ("cash_begin",       ("Cash and cash equivalents - beginning",        [8646, 6858, 12488, 7123, 9016, 8342])),
    ("fx_effect",        ("FX effect on cash and cash equivalents",       [173, 159, 509, 65, 174, 959])),
    ("cash_end",         ("Cash and cash equivalents - end",              [6858, 12488, 7123, 9016, 8342, 6417])),
])

SOURCES = {
    "FY2026": "FY2025-26 Integrated Annual Report, consolidated statements (pp.196-203)",
    "FY2025": "FY2025-26 report comparative column (FY2024-25 report text layer is corrupted; its legible totals agree)",
    "FY2024": "FY2023-24 Integrated Annual Report, consolidated statements (pp.180-185)",
    "FY2023": "FY2023-24 report comparative column; agrees with FY2022-23 report's own figures",
    "FY2022": "FY2021-22 Integrated Annual Report, consolidated statements (pp.243-251); agrees with FY2022-23 comparative",
    "FY2021": "FY2021-22 report comparative column (base year for growth and average balances only)",
}

NOT_REPORTED = {
    "Gross Profit / Gross Profit Margin":
        "TCS presents expenses by nature (no cost-of-sales line), so gross profit is not reported and cannot be "
        "calculated. A clearly labelled proxy (revenue less employee and equipment costs) is shown instead.",
    "Borrowings / classic Debt-to-Equity":
        "TCS reports no bank or bond borrowings in FY2021-FY2026. Debt is taken as lease liabilities plus (FY2026 only) "
        "Class B compulsorily convertible preference shares of INR 126 crore.",
    "Inventory Turnover":
        "Inventories are immaterial (INR 8-29 crore, under 0.03% of assets). The ratio uses cost of equipment & "
        "software licences as the cost base but is not analytically meaningful.",
    "US$ values":
        "No exchange-rate data is in the uploaded files, so no US$ conversion is attempted.",
}


def all_statements():
    return {"Income Statement": INCOME, "Balance Sheet": BALANCE, "Cash Flow": CASHFLOW}
