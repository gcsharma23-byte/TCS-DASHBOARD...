"""Static preview (matplotlib) of the dashboard pages, using the same data/metrics as the Streamlit app."""
import sys, pathlib
ROOT = pathlib.Path(__file__).resolve().parents[1]; sys.path.insert(0, str(ROOT))
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
from tcs_fin.loader import load_statements
from tcs_fin.metrics import compute_metrics
from tcs_fin.insights import build_insights, overall_assessment
from tcs_fin.fmt import money, pct, times, short
import textwrap

NAVY, BLUE, SKY, SLATE, GREY, TEAL = "#0B2A5B", "#1F6FD1", "#6FB1FC", "#5B6B82", "#E8EDF4", "#14A3A3"
df, labels, _ = load_statements(ROOT / "data" / "tcs_consolidated_financials.xlsx")
m = compute_metrics(df, "average")
Y = list(df.index[1:]); mv = m.loc[Y]; X = [short(y) for y in Y]
OUT = ROOT / "preview"; OUT.mkdir(exist_ok=True)
plt.rcParams.update({"font.family": "DejaVu Sans", "axes.spines.top": False, "axes.spines.right": False, "axes.edgecolor": "#B8C4D6"})


def page(title, sub):
    fig = plt.figure(figsize=(16, 10), facecolor="white")
    fig.patches.append(plt.Rectangle((0, 0.92), 1, 0.08, transform=fig.transFigure, color=NAVY))
    fig.text(0.03, 0.96, title, color="white", fontsize=20, weight="bold", va="center")
    fig.text(0.97, 0.96, sub, color=SKY, fontsize=11, ha="right", va="center")
    return fig


def card(fig, x, y, w, h, label, value, delta, good=True):
    fig.patches.append(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.002,rounding_size=0.01", transform=fig.transFigure,
                                      fc="#F4F7FC", ec="#D5DEEC"))
    fig.text(x + 0.012, y + h - 0.025, label, fontsize=10, color=SLATE)
    fig.text(x + 0.012, y + h / 2 - 0.012, value, fontsize=17, weight="bold", color=NAVY)
    fig.text(x + 0.012, y + 0.012, delta, fontsize=9.5, color="#1E8E5A" if good else "#C0392B")


def ax_at(fig, rect, title):
    a = fig.add_axes(rect); a.set_title(title, loc="left", fontsize=12, color=NAVY, weight="bold"); a.grid(axis="y", color=GREY); a.set_axisbelow(True)
    return a


def bars(a, cols, names, scale=1, colors=(NAVY, BLUE, SKY)):
    import numpy as np
    w = 0.8 / len(cols); xs = np.arange(len(X))
    for i, c in enumerate(cols):
        a.bar(xs + i * w - 0.4 + w / 2, mv[c] * scale, w, label=names[i], color=colors[i % 3])
    a.set_xticks(xs); a.set_xticklabels(X); a.legend(frameon=False, fontsize=9, loc="upper left")


def line(a, cols, names, fmt="{:.1f}"):
    for i, c in enumerate(cols):
        a.plot(X, mv[c], marker="o", lw=2.5, color=[NAVY, BLUE, SKY, TEAL][i], label=names[i])
        for x, v in zip(X, mv[c]): a.annotate(fmt.format(v), (x, v), textcoords="offset points", xytext=(0, 7), ha="center", fontsize=8.5)
    a.legend(frameon=False, fontsize=9)


c, p = m.loc["FY2026"], m.loc["FY2025"]
d = lambda a, b: f"{(a / b - 1) * 100:+.1f}% vs FY25"
dp = lambda a, b: f"{a - b:+.1f} pp vs FY25"

# ---- 1 Executive summary
f = page("TCS | Executive Financial Summary", "FY2026 vs FY2025 · consolidated · ₹ crore")
K = [("Total Revenue", money(c.revenue), d(c.revenue, p.revenue), 1), ("Revenue Growth", pct(c.rev_growth), dp(c.rev_growth, p.rev_growth), 0),
     ("Operating Profit", money(c.op_profit), d(c.op_profit, p.op_profit), 1), ("Operating Margin", pct(c.op_margin), dp(c.op_margin, p.op_margin), 1),
     ("Net Profit", money(c.net_profit), d(c.net_profit, p.net_profit), 1), ("Net Margin", pct(c.net_margin), dp(c.net_margin, p.net_margin), 0),
     ("EPS", f"₹{c.eps:.2f}", d(c.eps, p.eps), 1), ("Total Assets", money(c.total_assets), d(c.total_assets, p.total_assets), 1),
     ("Total Liabilities", money(c.total_liabilities), d(c.total_liabilities, p.total_liabilities), 0), ("Shareholders' Equity", money(c.equity), d(c.equity, p.equity), 1),
     ("ROE", pct(c.roe), dp(c.roe, p.roe), 0), ("ROCE", pct(c.roce), dp(c.roce, p.roce), 0)]
for i, (l, v, dl, g) in enumerate(K):
    card(f, 0.03 + (i % 4) * 0.2415, 0.76 - (i // 4) * 0.125, 0.23, 0.11, l, v, dl, bool(g))
a = ax_at(f, [0.05, 0.08, 0.40, 0.27], "Revenue (₹ crore)"); bars(a, ["revenue"], ["Revenue"], colors=(BLUE,))
a.twinx().plot(X, mv.op_margin, color=NAVY, marker="o", lw=2.5)
a = ax_at(f, [0.56, 0.08, 0.40, 0.27], "Net profit (₹ crore)"); bars(a, ["net_profit"], ["Net profit"], colors=(NAVY,))
f.savefig(OUT / "1_executive_summary.png", dpi=110); plt.close(f)

# ---- 2 Profitability
f = page("TCS | Revenue & Profitability", "FY2022–FY2026 · ₹ crore")
a = ax_at(f, [0.05, 0.54, 0.43, 0.33], "Revenue vs Operating Profit vs Net Profit"); bars(a, ["revenue", "op_profit", "net_profit"], ["Revenue", "Operating profit", "Net profit"])
a = ax_at(f, [0.55, 0.54, 0.40, 0.33], "Margins (%)"); line(a, ["op_margin", "net_margin"], ["Operating margin", "Net margin"])
a = ax_at(f, [0.05, 0.08, 0.43, 0.33], "Year-on-year growth (%)"); bars(a, ["rev_growth", "op_growth", "np_growth"], ["Revenue", "Operating profit", "Net profit"])
a = ax_at(f, [0.55, 0.08, 0.40, 0.33], "Operating cost as % of revenue")
import numpy as np
bot = np.zeros(len(X))
for k, col in zip(["employee_cost", "equipment_cost", "depreciation", "other_expenses"], [NAVY, BLUE, SKY, "#B8C4D6"]):
    v = (df.loc[Y, k] / df.loc[Y, "revenue"] * 100).values; a.bar(X, v, bottom=bot, color=col, label=labels[k][:28]); bot += v
a.legend(frameon=False, fontsize=8, loc="upper left", ncol=2)
f.savefig(OUT / "2_revenue_profitability.png", dpi=110); plt.close(f)

# ---- 3 Balance sheet & ratios
f = page("TCS | Balance Sheet & Ratio Analysis", "FY2022–FY2026 · average-balance basis")
a = ax_at(f, [0.05, 0.54, 0.28, 0.33], "Assets vs liabilities vs equity"); bars(a, ["total_assets", "total_liabilities", "equity"], ["Assets", "Liabilities", "Equity"])
a = ax_at(f, [0.38, 0.54, 0.26, 0.33], "Current assets vs liabilities"); bars(a, ["current_assets", "current_liabilities"], ["Current assets", "Current liabilities"])
a = ax_at(f, [0.70, 0.54, 0.26, 0.33], "Liquidity ratios (x)"); line(a, ["current_ratio", "quick_ratio"], ["Current", "Quick"], "{:.2f}")
a = ax_at(f, [0.05, 0.08, 0.28, 0.33], "ROE · ROCE · ROA (%)"); line(a, ["roe", "roce", "roa"], ["ROE", "ROCE", "ROA"])
a = ax_at(f, [0.38, 0.08, 0.26, 0.33], "Asset turnover (x)"); line(a, ["asset_turnover"], ["Asset turnover"], "{:.2f}")
a = ax_at(f, [0.70, 0.08, 0.26, 0.33], "Receivable days"); line(a, ["dso"], ["DSO"], "{:.0f}")
f.savefig(OUT / "3_balance_sheet_ratios.png", dpi=110); plt.close(f)

# ---- 4 Cash flow
f = page("TCS | Cash Flow Analysis", "FY2022–FY2026 · ₹ crore")
a = ax_at(f, [0.05, 0.54, 0.43, 0.33], "Operating / investing / financing cash flow"); bars(a, ["cfo", "cfi", "cff"], ["Operating", "Investing", "Financing"]); a.axhline(0, color=SLATE, lw=0.8)
a = ax_at(f, [0.55, 0.54, 0.40, 0.33], "Free cash flow"); bars(a, ["cfo", "capex", "fcf"], ["Operating CF", "Capex", "Free cash flow"])
a = ax_at(f, [0.05, 0.08, 0.43, 0.33], "Operating cash flow vs net profit"); bars(a, ["cfo", "net_profit"], ["Operating CF", "Net profit"])
a = ax_at(f, [0.55, 0.08, 0.40, 0.33], "Cash conversion (% of net profit)"); line(a, ["cfo_to_np", "fcf_to_np"], ["CFO / net profit", "FCF / net profit"], "{:.0f}")
f.savefig(OUT / "4_cash_flow.png", dpi=110); plt.close(f)

# ---- 5 Insights
f = page("TCS | Financial Insights", "Generated automatically from the data")
ins = build_insights(df, m, Y); table, text = overall_assessment(df, m, Y)
y = 0.88
for head, items in (("Positive trends", ins["Positive trends"][:4]), ("Potential concerns", ins["Potential concerns"][:5])):
    f.text(0.03, y, head, fontsize=14, weight="bold", color=NAVY); y -= 0.035
    for _, t in items:
        for j, ln in enumerate(textwrap.wrap(t, 140)):
            f.text(0.04, y, ("• " if j == 0 else "  ") + ln, fontsize=10.5); y -= 0.027
    y -= 0.015
f.text(0.03, y, "Overall Financial Performance Assessment of TCS", fontsize=14, weight="bold", color=NAVY); y -= 0.035
for _, r in table.iterrows():
    f.text(0.04, y, f"{r.Dimension}: {r.Assessment}  -  {r.Evidence}", fontsize=10.5); y -= 0.027
y -= 0.01
for para in text.split("\n\n"):
    for ln in textwrap.wrap(para, 150): f.text(0.04, y, ln, fontsize=10, color=SLATE); y -= 0.024
    y -= 0.01
f.savefig(OUT / "5_insights.png", dpi=110); plt.close(f)
print(sorted(p.name for p in OUT.iterdir()))
