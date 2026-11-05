"""Plotly figure builders (Plotly Express + Graph Objects)."""
import plotly.express as px
import plotly.graph_objects as go

NAVY, BLUE, SKY, SLATE, GREY, RED, TEAL = "#0B2A5B", "#1F6FD1", "#6FB1FC", "#5B6B82", "#C7D2E0", "#C0392B", "#14A3A3"
PALETTE = [NAVY, BLUE, SKY, SLATE, TEAL, GREY]


def _style(fig, title, height=380, ytitle=None, yfmt=None):
    fig.update_layout(
        title=dict(text=title, font=dict(size=16, color=NAVY)), template="plotly_white", height=height,
        margin=dict(l=10, r=10, t=60, b=10), hovermode="x unified", font=dict(family="Arial", size=12),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    )
    fig.update_yaxes(title_text=ytitle, gridcolor="#E8EDF4", tickformat=yfmt)
    fig.update_xaxes(type="category")
    return fig


def grouped_bar(d, cols, names, title, ytitle, yfmt=",.0f", hover="%{y:,.0f}", barmode="group"):
    fig = go.Figure()
    for i, c in enumerate(cols):
        fig.add_trace(go.Bar(x=d.index, y=d[c], name=names[c], marker_color=PALETTE[i % len(PALETTE)],
                             hovertemplate=names[c] + ": " + hover + "<extra></extra>"))
    fig.update_layout(barmode=barmode)
    return _style(fig, title, ytitle=ytitle, yfmt=yfmt)


def line(d, cols, names, title, ytitle, suffix="", dec=1, markers=True):
    fig = go.Figure()
    for i, c in enumerate(cols):
        fig.add_trace(go.Scatter(x=d.index, y=d[c], name=names[c], mode="lines+markers" if markers else "lines",
                                 line=dict(color=PALETTE[i % len(PALETTE)], width=3), marker=dict(size=8),
                                 hovertemplate=names[c] + ": %{y:,." + str(dec) + "f}" + suffix + "<extra></extra>"))
    return _style(fig, title, ytitle=ytitle)


def bar_with_line(d, bar_col, line_col, bar_name, line_name, title, ytitle, ytitle2):
    fig = go.Figure()
    fig.add_trace(go.Bar(x=d.index, y=d[bar_col], name=bar_name, marker_color=BLUE,
                         hovertemplate=bar_name + ": %{y:,.0f}<extra></extra>"))
    fig.add_trace(go.Scatter(x=d.index, y=d[line_col], name=line_name, yaxis="y2", mode="lines+markers",
                             line=dict(color=NAVY, width=3), hovertemplate=line_name + ": %{y:.1f}%<extra></extra>"))
    fig.update_layout(yaxis2=dict(title=ytitle2, overlaying="y", side="right", showgrid=False))
    return _style(fig, title, ytitle=ytitle)


def growth_bars(d, cols, names, title):
    fig = go.Figure()
    for i, c in enumerate(cols):
        fig.add_trace(go.Bar(x=d.index, y=d[c], name=names[c], marker_color=PALETTE[i % len(PALETTE)],
                             hovertemplate=names[c] + ": %{y:.1f}%<extra></extra>"))
    fig.update_layout(barmode="group")
    fig.add_hline(y=0, line_color=SLATE, line_width=1)
    return _style(fig, title, ytitle="YoY growth (%)", yfmt=".1f")


def stacked_long(d, cols, names, title, ytitle, as_pct=False):
    """Plotly Express stacked bar from a wide frame (optionally normalised to 100%)."""
    x = d[cols].copy()
    if as_pct:
        x = x.div(x.sum(axis=1), axis=0) * 100
    long = x.rename(columns=names).reset_index().melt(id_vars=d.index.name or "index", var_name="Component", value_name="Value")
    fig = px.bar(long, x=d.index.name or "index", y="Value", color="Component", color_discrete_sequence=PALETTE + [TEAL, RED],
                 barmode="stack")
    fig.update_traces(hovertemplate="%{fullData.name}: %{y:,.1f}" + ("%" if as_pct else "") + "<extra></extra>")
    return _style(fig, title, ytitle=ytitle, height=400)


def ratio_chart(d, key, label, kind, dec=2):
    suffix = {"%": "%", "x": "x", "days": " days"}[kind]
    fig = go.Figure(go.Scatter(x=d.index, y=d[key], mode="lines+markers+text", line=dict(color=BLUE, width=3),
                               marker=dict(size=9, color=NAVY), text=[f"{v:.{dec}f}" for v in d[key]], textposition="top center",
                               hovertemplate=label + ": %{y:." + str(dec) + "f}" + suffix + "<extra></extra>"))
    fig.update_yaxes(rangemode="tozero")
    return _style(fig, label, height=320, ytitle=suffix.strip())


def waterfall_like(d, cols, names, title, ytitle):
    """Cash-flow components as signed bars."""
    return grouped_bar(d, cols, names, title, ytitle, hover="%{y:,.0f}")
