"""
TCS Financial Analytics Dashboard  -  Python / Streamlit / Plotly only.
Run:  streamlit run app.py
Data: consolidated Ind AS statements FY2022-FY2026 (FY2021 used as base year), INR crore.
"""
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
if not DATA_FILE.exists():
    st.error(f"Data file not found: {DATA_FILE}. Run `python scripts/build_dataset.py` first.")
    st.stop()


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
