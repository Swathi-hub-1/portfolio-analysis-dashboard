import plotly.express as px
import plotly.graph_objects as go
import numpy as np


PALETTE = px.colors.qualitative.D3
CONTINUOUS_SCALE = px.colors.sequential.Teal
COMMON_TEMPLATE = 'plotly_dark'


def pie_chart(labels, values, title=None):
    fig = px.pie(names=labels, values=values, template=COMMON_TEMPLATE)
    fig.update_traces(hoverinfo='label+percent', textinfo='label', pull=[0.03] * len(values))
    fig.update_layout(margin=dict(t=60, b=60), title=title or "")
    return fig


def line_chart(df, x, y, color=None, title=None, labels=None, markers=None):
    fig = px.line(df, x=x, y=y, color=color, template=COMMON_TEMPLATE, labels=labels, color_discrete_sequence=PALETTE, markers=markers)
    fig.update_layout(margin=dict(t=60, b=60), title=title or "", legend=dict(orientation='h', yanchor='bottom', y=-0.3, xanchor='center', x=0.5))
    return fig


def area_chart(x, y, title=None, underwater=False):
    fig = px.area(x=x, y=y, template=COMMON_TEMPLATE, labels={"x": "Date", "y": "Drawdown %"}, color_discrete_sequence=PALETTE)
    fig.update_traces(line=dict(width=2))
    fig.update_layout(title=title or "", margin=dict(t=60, b=60))
    fig.update_yaxes( range=[min(y), 0], tickformat=".0%")
    return fig


def scatter_plot(df, x, y, color=None, size=None, title=None, hover=None, trendline=None, reference_line=False):
    fig = px.scatter(df, x=x, y=y, hover_name=hover, color=color, size=size, template=COMMON_TEMPLATE, title=title or "", trendline=trendline, color_discrete_sequence=PALETTE,)
    fig.update_traces(mode="markers", marker=dict(size=12, opacity=0.85, line=dict(width=0.5, color="#ffffff")))
    fig.update_layout(margin=dict(t=60, b=60), showlegend=False)
    if reference_line:
        x_mean = df[x].mean()
        y_mean = df[y].mean()
        fig.add_vline(x=x_mean, line_dash="dash", line_width=1, line_color="#94a3b8")
        fig.add_hline(y=y_mean, line_dash="dash", line_width=1, line_color="#94a3b8")
    fig.update_traces(hovertemplate=("<b>%{hovertext}</b><br>"
                                     "Volatility: %{x:.2%}<br>"
                                     "Return: %{y:.2%}"
                                     "<extra></extra>"))
    return fig


def heatmap_chart(df, title=None):
    fig = px.imshow(df, text_auto=".2f", color_continuous_scale=CONTINUOUS_SCALE, template=COMMON_TEMPLATE, title=title or "")
    fig.update_traces(hovertemplate=("<b>%{x}</b> vs <b>%{y}</b><br>"
                                     "Correlation: <b>%{z:.4f}</b><extra></extra>"))
    fig.update_layout(margin=dict(t=60, b=60))
    return fig


def dual_axis_line_chart(df, x, y1, y2, y1_name="Series 1", y2_name="Series 2", title=None):
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df[x], y=df[y1], mode="lines", name=y1_name, line=dict(width=2, color=PALETTE[0]),))
    fig.add_trace(go.Scatter(x=df[x], y=df[y2], mode="lines", name=y2_name, yaxis="y2", line=dict(width=2, color=PALETTE[2]),))
    fig.update_layout(title=title or "", template=COMMON_TEMPLATE, xaxis=dict(title=x), yaxis=dict(title=y1_name), yaxis2=dict(title=y2_name, overlaying="y", side="right"), legend=dict(orientation="h", y=-0.2), margin=dict(t=60, b=60),)
    return fig


def bubble_chart(df, x, y, size, color=None, hover=None, title=None):
    fig = px.scatter(df, x=x, y=y, size=size, color=color, hover_name=hover, template=COMMON_TEMPLATE, title=title or "", size_max=60, color_discrete_sequence=PALETTE,)
    fig.update_traces(mode="markers", marker=dict(opacity=0.85))
    fig.update_layout(margin=dict(t=60, b=60))
    return fig


def box_chart(df,x_col, y_col, title, hover_label_col=None, color_col=None):
    custom = None
    hovertemplate = "%{y:.2f}"

    if hover_label_col and hover_label_col in df.columns:
        custom = np.stack([df[hover_label_col]], axis=1)
        hovertemplate = "<b>%{customdata[0]}</b><br>Value: %{y:.2f}"

    fig = px.box(df, x=x_col, y=y_col, color=color_col if color_col else x_col, points="all", template=COMMON_TEMPLATE, title=title or "", color_discrete_sequence=PALETTE,)
    fig.update_traces(hovertemplate=hovertemplate, customdata=custom)
    fig.update_layout(margin=dict(t=60, b=60), yaxis_title=y_col, xaxis_title=x_col)
    return fig


def bar_chart(df, x, y, color=None, title=None, labels=None, show_text=False, hover_col=None):
    fig = px.bar(df, x=x, y=y, color=color, labels=labels, text=y if show_text else None, template=COMMON_TEMPLATE, color_discrete_sequence=PALETTE)
    fig.update_traces(hovertemplate="<b>%{customdata}</b><br>" f"{x}: %{{x}}<br>" f"{y}: %{{y}}", customdata=df[hover_col],)
    fig.update_layout(title=title or "", margin=dict(t=60, b=60),  xaxis_title=labels.get(x) if labels else x, yaxis_title=labels.get(y) if labels else y, legend=dict(orientation="h", y=-0.25))
    return fig