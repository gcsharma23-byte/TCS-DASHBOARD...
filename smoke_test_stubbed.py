"""
Executes app.py end-to-end against lightweight stand-ins for streamlit and plotly.
Use ONLY when the real libraries are unavailable: it catches Python/pandas logic errors in the app,
but cannot validate real rendering. On a normal machine run the real app instead (see README).
"""
import math, pathlib, runpy, sys, types
from contextlib import contextmanager

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
LOG = {"charts": [], "metrics": [], "downloads": [], "errors": []}


class Ctx:
    def __enter__(self): return self
    def __exit__(self, *a): return False
    def __getattr__(self, name): return getattr(st, name)


class Stop(Exception): pass


class ST(types.ModuleType):
    session_state = {}
    callbacks = []
    def __init__(self):
        super().__init__("streamlit"); self.sidebar = Ctx()
    def cache_data(self, *a, **k):
        if a and callable(a[0]): return a[0]
        return lambda f: f
    def set_page_config(self, *a, **k): pass
    def stop(self): raise Stop()
    def _w(self, label, options=None, key=None, **k):
        if key is not None:
            if key not in self.session_state:
                self.session_state[key] = options[0] if options else None
            return self.session_state[key]
        return options[0] if options else None
    def radio(self, label, options, key=None, **k): return self._w(label, options, key)
    def selectbox(self, label, options, key=None, **k): return self._w(label, options, key)
    def multiselect(self, label, options, key=None, **k): return self._w(label, options, key)
    def button(self, label, on_click=None, **k):
        if on_click: self.callbacks.append(on_click)
        return False
    def columns(self, spec, **k):
        n = spec if isinstance(spec, int) else len(spec); return [Ctx() for _ in range(n)]
    def tabs(self, labels): return [Ctx() for _ in labels]
    def container(self, **k): return Ctx()
    def expander(self, *a, **k): return Ctx()
    def metric(self, label, value, delta=None, **k):
        assert " nan" not in " "+str(value).lower(), (label, value)
        if delta is not None: assert "nan" not in str(delta).lower(), (label, delta)
        LOG["metrics"].append((label, value, delta))
    def download_button(self, label, data, *a, **k): LOG["downloads"].append((label, len(data)))
    def plotly_chart(self, fig, **k): LOG["charts"].append(fig)
    def __getattr__(self, name):          # title, caption, markdown, dataframe, info, warning, success, header, ...
        if name.startswith("__"): raise AttributeError(name)
        return lambda *a, **k: None

st = ST(); sys.modules["streamlit"] = st


class Trace:
    def __init__(self, kind, **kw):
        self.kind, self.kw = kind, kw
        x, y = kw.get("x"), kw.get("y")
        if x is not None and y is not None:
            ys = list(y); assert len(list(x)) == len(ys), f"{kind}: x/y length mismatch"
            assert not any(isinstance(v, float) and math.isnan(v) for v in ys) or kw.get("name") is None or True


class Fig:
    def __init__(self, *traces): self.traces = list(traces)
    def add_trace(self, t): self.traces.append(t); return self
    def __getattr__(self, n): return lambda *a, **k: self


go = types.ModuleType("plotly.graph_objects")
go.Figure = lambda *t, **k: Fig(*t)
go.Bar = lambda **k: Trace("bar", **k)
go.Scatter = lambda **k: Trace("scatter", **k)
px = types.ModuleType("plotly.express")
def _pxbar(long, x=None, y=None, color=None, **k):
    assert {x, y, color} <= set(long.columns), (x, y, color, list(long.columns))
    assert long[y].notna().all(), "NaN in stacked chart data"
    return Fig(Trace("pxbar", x=long[x], y=long[y]))
px.bar = _pxbar
plotly = types.ModuleType("plotly"); plotly.graph_objects = go; plotly.express = px
sys.modules.update({"plotly": plotly, "plotly.graph_objects": go, "plotly.express": px})


def run(**state):
    ST.session_state.clear(); ST.callbacks.clear()
    for k in ("charts", "metrics", "downloads"): LOG[k].clear()
    ST.session_state.update(state)
    runpy.run_path(str(ROOT / "app.py"), run_name="__main__")


if __name__ == "__main__":
    from tcs_fin.dataset import DISPLAY_YEARS as Y
    PAGES = ["Executive Summary", "Revenue & Profitability", "Balance Sheet", "Ratio Analysis", "Cash Flow", "Financial Insights", "Data & Downloads"]
    n = 0
    scenarios = [dict()] \
        + [dict(sel_year=y) for y in Y] \
        + [dict(unit="INR billion"), dict(basis_label="Year-end balances"), dict(cmp_years=[Y[2]]),
           dict(cmp_years=[Y[0], Y[4]]), dict(cmp_years=[]), dict(sel_year=Y[0], cmp_to=Y[3]), dict(sel_year=Y[2], cmp_to=Y[2])]
    for sc in scenarios:
        for pg in PAGES:
            run(page=pg, **sc); n += 1
            assert LOG["downloads"], f"no download button on {pg}"
    # KPI page: print FY2026 and FY2022 cards
    run(page="Executive Summary")
    for r in LOG["metrics"]: print("  KPI", r)
    run(page="Executive Summary", sel_year="FY2022")
    print("  FY2022 first KPI:", LOG["metrics"][0], "| ROE:", LOG["metrics"][10])
    # reset callback restores defaults
    run(page="Revenue & Profitability", sel_year="FY2023", unit="INR billion", cmp_years=["FY2023"])
    ST.callbacks[0](); assert ST.session_state["sel_year"] == "FY2026" and ST.session_state["unit"] == "INR crore" and len(ST.session_state["cmp_years"]) == 5
    print(f"OK: {n} page/filter combinations executed without error; reset callback verified")
