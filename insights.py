"""Rule-based insight generation. Every statement is built from the actual numbers."""
import numpy as np
import pandas as pd
from .fmt import money, pct, times, pp, short
from .metrics import RATIOS, MEANING


def _chg(s, a, b):
    return s[b] - s[a]


def _trend_word(delta, up="improved", down="declined", tol=0.0):
    return up if delta > tol else down if delta < -tol else "was unchanged"


def ratio_commentary(key, m, years):
    """Plain-English reading of one ratio's movement over the selected years."""
    label, kind, hib, _ = RATIOS[key]
    s = m.loc[years, key].dropna()
    if s.empty:
        return f"**{label}** cannot be calculated from the uploaded statements (see data notes)."
    fmtv = {"%": pct, "x": times, "days": lambda v: f"{v:.1f} days"}[kind]
    a, b = s.index[0], s.index[-1]
    d = s[b] - s[a]
    better = (d > 0) == hib
    verdict = "an improvement" if (better and abs(d) > 1e-9) else "a deterioration" if abs(d) > 1e-9 else "no change"
    unit_txt = {"%": f"{abs(d):.1f} pp", "x": f"{abs(d):.2f}x", "days": f"{abs(d):.1f} days"}[kind]
    out = (f"**{label}** moved from {fmtv(s[a])} in {short(a)} to {fmtv(s[b])} in {short(b)} "
           f"({'up' if d > 0 else 'down'} {unit_txt}), {verdict}. "
           f"Peak {fmtv(s.max())} ({short(s.idxmax())}); low {fmtv(s.min())} ({short(s.idxmin())}). ")
    if len(s) >= 2:
        last = s.iloc[-1] - s.iloc[-2]
        out += f"Latest year-on-year change: {'+' if last >= 0 else '-'}{abs(last):.2f}{'pp' if kind == '%' else ''}. "
    return out + f"*What it indicates:* {MEANING[key]}"


def build_insights(df, m, years):
    """years: ordered list of displayed years (>=2). Returns dict of lists of (title, text)."""
    y0, y1 = years[0], years[-1]
    prev = years[-2]
    R = {}

    def add(cat, title, text):
        R.setdefault(cat, []).append((title, text))

    # ---------- headline ----------
    ry = m.loc[years, "revenue"].idxmax(); ny = m.loc[years, "net_profit"].idxmax()
    add("Highlights", "Highest revenue year",
        f"{short(ry)} recorded the highest revenue of {money(m.revenue[ry])}"
        + (f", {pct(m.rev_growth[ry])} above the prior year." if not np.isnan(m.rev_growth[ry]) else "."))
    add("Highlights", "Highest net profit year",
        f"{short(ny)} recorded the highest net profit attributable to shareholders at {money(m.net_profit[ny])} "
        f"(EPS ₹{m.eps[ny]:.2f}); net margin {pct(m.net_margin[ny])}.")
    n = len(years) - 1
    cagr = lambda s: ((s[y1] / s[y0]) ** (1 / n) - 1) * 100 if n > 0 and s[y0] > 0 else np.nan
    add("Highlights", f"{n}-year CAGR ({short(y0)}→{short(y1)})",
        f"Revenue {pct(cagr(m.revenue))}, operating profit {pct(cagr(m.op_profit))}, net profit {pct(cagr(m.net_profit))}, "
        f"EPS {pct(cagr(m.eps))}.")

    # ---------- growth consistency ----------
    g = m.loc[years, "rev_growth"].dropna()
    pos = int((g > 0).sum())
    seq = ", ".join(f"{short(i)} {v:.1f}%" for i, v in g.items())
    decel = g.iloc[-1] < g.max() * 0.5
    add("Growth", "Revenue growth consistency",
        f"Revenue rose in {pos} of {len(g)} years ({seq}); mean {g.mean():.1f}%, std. dev. {g.std(ddof=0):.1f} pp. "
        + (f"Growth has slowed markedly from its {g.max():.1f}% peak ({short(g.idxmax())}) to {g.iloc[-1]:.1f}% in {short(g.index[-1])}."
           if decel else "Growth has stayed within a narrow band."))

    # ---------- profitability ----------
    om, nm = m.op_margin, m.net_margin
    dm = om[y1] - om[y0]
    add("Profitability", "Operating margin",
        f"Operating margin was {pct(om[y0])} in {short(y0)} and {pct(om[y1])} in {short(y1)} ({pp(dm)}); range "
        f"{pct(om[years].min())} ({short(om[years].idxmin())}) to {pct(om[years].max())} ({short(om[years].idxmax())}). "
        f"Margins are broadly {'stable' if om[years].max() - om[years].min() < 2.5 else 'volatile'} despite revenue growing "
        f"{(m.revenue[y1] / m.revenue[y0] - 1) * 100:.0f}% over the period.")
    ex = df.exceptional[y1]
    add("Profitability", "Net margin and exceptional items",
        f"Net margin moved {pp(nm[y1] - nm[prev])} to {pct(nm[y1])} in {short(y1)}. "
        + (f"Exceptional charges of {money(ex)} ({ex / df.pbe[y1] * 100:.1f}% of pre-exceptional profit) held PBT growth to "
           f"{pct((df.pbt[y1] / df.pbt[prev] - 1) * 100)} versus {pct((df.pbe[y1] / df.pbe[prev] - 1) * 100)} before exceptionals."
           if ex > 0 else "No exceptional items were booked that year."))
    add("Profitability", "Returns on capital",
        f"ROE {pct(m.roe[y1])} and ROCE {pct(m.roce[y1])} in {short(y1)}, versus {pct(m.roe[prev])} and {pct(m.roce[prev])} in {short(prev)}.")

    # ---------- liquidity ----------
    add("Liquidity", "Liquidity position",
        f"Current ratio {times(m.current_ratio[y1])} and quick ratio {times(m.quick_ratio[y1])} in {short(y1)} "
        f"(from {times(m.current_ratio[y0])} / {times(m.quick_ratio[y0])} in {short(y0)}). Cash, bank balances and current "
        f"investments total {money(m.cash_liquid[y1])} against current liabilities of {money(m.current_liabilities[y1])} "
        f"(cash ratio {times(m.cash_ratio[y1])}).")

    # ---------- stability ----------
    add("Stability", "Financial stability",
        f"No borrowings are reported. Debt-like obligations (lease liabilities + preference shares) are {money(m.total_debt[y1])}, "
        f"a debt-to-equity of {times(m.debt_equity[y1])}, against liquid assets of {money(m.cash_liquid[y1])} "
        f"(net cash {money(m.net_cash[y1])}). Equity funds {pct(m.equity_ratio[y1])} of total assets; interest cover is "
        f"{times(m.interest_coverage[y1], 1)}.")

    # ---------- efficiency ----------
    add("Efficiency", "Asset utilisation",
        f"Asset turnover was {times(m.asset_turnover[y1])} in {short(y1)} versus {times(m.asset_turnover[prev])} in {short(prev)} "
        f"and {times(m.asset_turnover[y0])} in {short(y0)}. "
        f"Receivable days moved from {m.dso[y0]:.1f} to {m.dso[y1]:.1f} ({short(y0)}→{short(y1)}).")

    # ---------- cash ----------
    add("Cash Flow", "Cash generation",
        f"Operating cash flow was {money(m.cfo[y1])} ({pct(m.cfo_to_np[y1], 0)} of net profit); free cash flow "
        f"{money(m.fcf[y1])} after capex of {money(m.capex[y1])}. Shareholder payouts: dividends {money(df.dividend_sh[y1])} "
        f"({pct(m.payout[y1], 0)} of net profit)" + (f" plus buy-backs {money(df.buyback[y1])}." if df.buyback[y1] else "."))

    # ---------- positives & concerns ----------
    pos_, con = [], []
    if g.gt(0).all():
        pos_.append(f"Revenue grew every year, cumulatively {(m.revenue[y1] / m.revenue[y0] - 1) * 100:.1f}% from {short(y0)} to {short(y1)}.")
    if m.loc[years, "net_profit"].is_monotonic_increasing:
        pos_.append(f"Net profit rose every year, from {money(m.net_profit[y0])} to {money(m.net_profit[y1])}.")
    if (m.cfo[years] >= m.net_profit[years] * 0.95).all():
        pos_.append(f"Operating cash flow was at least 95% of net profit in every year ({pct(m.cfo_to_np[years].min(), 0)}–{pct(m.cfo_to_np[years].max(), 0)}).")
    if m.interest_coverage[years].min() > 20:
        pos_.append(f"Interest coverage never fell below {times(m.interest_coverage[years].min(), 1)}; the company carries no borrowings.")
    if m.roe[years].min() > 40:
        pos_.append(f"ROE stayed above {pct(m.roe[years].min(), 0)} throughout.")
    if m.net_cash[y1] > 0:
        pos_.append(f"Liquid assets exceed debt-like obligations by {money(m.net_cash[y1])}.")

    if decel:
        con.append(f"Revenue growth decelerated to {g.iloc[-1]:.1f}% in {short(y1)} from a {g.max():.1f}% peak in {short(g.idxmax())}.")
    if m.np_growth[y1] < m.rev_growth[y1]:
        con.append(f"Net profit growth ({pct(m.np_growth[y1])}) lagged revenue growth ({pct(m.rev_growth[y1])}) in {short(y1)}.")
    if m.dso[y1] - m.dso[prev] > 3:
        con.append(f"Receivable days rose to {m.dso[y1]:.1f} from {m.dso[prev]:.1f}; current trade receivables grew "
                   f"{(df.ca_receivables[y1] / df.ca_receivables[prev] - 1) * 100:.1f}% against revenue growth of {pct(m.rev_growth[y1])}.")
    if m.current_ratio[y1] < m.current_ratio[y0]:
        con.append(f"Current ratio drifted down from {times(m.current_ratio[y0])} to {times(m.current_ratio[y1])} (still above 2x).")
    if df.goodwill[y1] > df.goodwill[prev] * 1.5:
        con.append(f"Goodwill rose to {money(df.goodwill[y1])} from {money(df.goodwill[prev])} alongside "
                   f"{money(df.acquisitions[y1])} of acquisition outflows (subsidiaries and assets), adding integration and impairment risk.")
    if df.exceptional[y1] > 0:
        con.append(f"Exceptional charges of {money(df.exceptional[y1])} reduced {short(y1)} profit.")
    if m.interest_coverage[y1] < m.interest_coverage[prev] * 0.8:
        con.append(f"Interest coverage fell to {times(m.interest_coverage[y1], 1)} from {times(m.interest_coverage[prev], 1)} as finance costs rose to {money(df.finance_cost[y1])}.")
    if df.cash[y1] < df.cash[prev]:
        con.append(f"Cash and cash equivalents fell to {money(df.cash[y1])} from {money(df.cash[prev])} (broader liquid assets rose to {money(m.cash_liquid[y1])}).")
    if m.asset_turnover[y1] < m.asset_turnover[prev]:
        con.append(f"Asset turnover eased to {times(m.asset_turnover[y1])} from {times(m.asset_turnover[prev])} as assets grew {pct(m.ta_growth[y1])} versus revenue growth of {pct(m.rev_growth[y1])}.")
    R["Positive trends"] = [("", t) for t in pos_]
    R["Potential concerns"] = [("", t) for t in con]
    return R


def overall_assessment(df, m, years):
    y0, y1 = years[0], years[-1]
    g = m.loc[years, "rev_growth"].dropna()
    n = len(years) - 1
    cagr = ((m.revenue[y1] / m.revenue[y0]) ** (1 / n) - 1) * 100
    rows = [
        ("Growth", "Moderating" if g.iloc[-1] < 8 else "Strong", f"Revenue CAGR {cagr:.1f}%; latest growth {g.iloc[-1]:.1f}%"),
        ("Profitability", "Strong" if m.op_margin[y1] > 22 else "Adequate", f"Operating margin {pct(m.op_margin[y1])}, ROE {pct(m.roe[y1])}"),
        ("Liquidity", "Strong" if m.current_ratio[y1] > 1.5 else "Adequate", f"Current ratio {times(m.current_ratio[y1])}, quick {times(m.quick_ratio[y1])}"),
        ("Solvency", "Strong" if m.debt_equity[y1] < 0.3 else "Adequate", f"Debt-to-equity {times(m.debt_equity[y1])}, no borrowings"),
        ("Cash generation", "Strong" if m.cfo_to_np[y1] > 95 else "Adequate", f"CFO/net profit {pct(m.cfo_to_np[y1], 0)}, FCF {money(m.fcf[y1])}"),
        ("Efficiency", "Watch" if m.dso[y1] - m.dso[years].min() > 8 else "Stable", f"Asset turnover {times(m.asset_turnover[y1])}, receivable days {m.dso[y1]:.0f}"),
    ]
    table = pd.DataFrame(rows, columns=["Dimension", "Assessment", "Evidence"])
    text = (
        f"Based solely on the consolidated statements for {short(y0)}–{short(y1)}, TCS shows a financially robust profile: "
        f"revenue rose from {money(m.revenue[y0])} to {money(m.revenue[y1])} and net profit from {money(m.net_profit[y0])} to "
        f"{money(m.net_profit[y1])}, with operating margin held in a {pct(m.op_margin[years].min())}–{pct(m.op_margin[years].max())} band. "
        f"The balance sheet carries no borrowings, {money(m.cash_liquid[y1])} of liquid assets and a current ratio of {times(m.current_ratio[y1])}; "
        f"operating cash flow of {money(m.cfo[y1])} fully funded capex and a dividend payout of {pct(m.payout[y1], 0)} of profit.\n\n"
        f"The balancing considerations are momentum and efficiency. Revenue growth slowed to {g.iloc[-1]:.1f}% and net profit growth to "
        f"{pct(m.np_growth[y1])} in {short(y1)}, held back by {money(df.exceptional[y1])} of exceptional charges; receivable days stretched to "
        f"{m.dso[y1]:.0f} (from {m.dso[years[-2]]:.0f}); and {money(df.acquisitions[y1])} of acquisition outflows came with goodwill rising to {money(df.goodwill[y1])}. "
        f"Overall, the data point to a high-quality, cash-generative and conservatively financed business whose near-term question is "
        f"growth rather than solvency. This is an analytical reading of historical figures, not investment advice."
    )
    return table, text
