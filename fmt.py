"""Number formatting helpers (Indian digit grouping for INR crore)."""
import math

UNITS = {"INR crore": 1.0, "INR billion": 0.01}


def indian(n, decimals=0):
    if n is None or (isinstance(n, float) and math.isnan(n)):
        return "n/a"
    neg = n < 0
    s = f"{abs(n):.{decimals}f}"
    ip, _, fp = s.partition(".")
    if len(ip) > 3:
        head, tail, groups = ip[:-3], ip[-3:], []
        while len(head) > 2:
            groups.insert(0, head[-2:]); head = head[:-2]
        if head:
            groups.insert(0, head)
        ip = ",".join(groups + [tail])
    return ("-" if neg else "") + ip + ("." + fp if fp else "")


def money(x, unit="INR crore"):
    if x is None or (isinstance(x, float) and math.isnan(x)):
        return "n/a"
    if unit == "INR billion":
        return f"₹{x * 0.01:,.1f} bn"
    return f"₹{indian(x)} cr"


def pct(x, d=1):
    return "n/a" if x is None or (isinstance(x, float) and math.isnan(x)) else f"{x:.{d}f}%"


def times(x, d=2):
    return "n/a" if x is None or (isinstance(x, float) and math.isnan(x)) else f"{x:.{d}f}x"


def pp(x, d=1):
    return "n/a" if x is None or (isinstance(x, float) and math.isnan(x)) else f"{x:+.{d}f} pp"


def short(y):
    """FY2026 -> FY26"""
    return "FY" + y[-2:]
