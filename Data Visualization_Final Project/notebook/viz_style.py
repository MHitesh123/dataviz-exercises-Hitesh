"""
Shared visual style for the Final Project.
CVD-safe palette (Okabe-Ito), muted-grey-for-context + highlight-color-for-focus,
decluttered layout, consistent typography. Import this in the notebook and the
Streamlit dashboard so every chart looks like it belongs to the same report.
"""
import plotly.graph_objects as go
import plotly.io as pio

# Okabe-Ito colorblind-safe palette
OI_BLUE = "#0072B2"
OI_ORANGE = "#E69F00"
OI_GREEN = "#009E73"
OI_YELLOW = "#F0E442"
OI_SKYBLUE = "#56B4E9"
OI_VERMILLION = "#D55E00"
OI_PURPLE = "#CC79A7"
OI_BLACK = "#000000"

GREY = "#B0B0B0"       # muted context grey
GREY_DARK = "#4D4D4D"  # labels / axis text
BG = "#FFFFFF"

CATEGORY_SEQUENCE = [OI_BLUE, OI_ORANGE, OI_GREEN, OI_VERMILLION, OI_PURPLE, OI_SKYBLUE, OI_YELLOW]

FONT_FAMILY = "Arial, Helvetica, sans-serif"

BASE_LAYOUT = dict(
    template="plotly_white",
    font=dict(family=FONT_FAMILY, size=13, color=GREY_DARK),
    title_font=dict(family=FONT_FAMILY, size=18, color="#1a1a1a"),
    paper_bgcolor=BG,
    plot_bgcolor=BG,
    margin=dict(l=60, r=40, t=90, b=60),
    legend=dict(
        orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0,
        bgcolor="rgba(0,0,0,0)", font=dict(size=12)
    ),
    hoverlabel=dict(bgcolor="white", font_size=12, font_family=FONT_FAMILY),
)

AXIS_STYLE = dict(
    showgrid=False,
    zeroline=False,
    showline=True,
    linecolor="#D9D9D9",
    ticks="outside",
    tickcolor="#D9D9D9",
    title_font=dict(size=13, color=GREY_DARK),
)

AXIS_STYLE_GRID = dict(
    showgrid=True,
    gridcolor="#EDEDED",
    gridwidth=1,
    zeroline=False,
    showline=True,
    linecolor="#D9D9D9",
    ticks="outside",
    tickcolor="#D9D9D9",
    title_font=dict(size=13, color=GREY_DARK),
)


def style_fig(fig: go.Figure, title: str, subtitle: str = None,
              xaxis_title: str = None, yaxis_title: str = None,
              show_grid_y: bool = True, height: int = 520, width: int = 900,
              source_note: str = "Source: SteamSpy / Steam Store, via TidyTuesday (2019-07-30) \u2022 n = 26,643 games, 2004\u20132018") -> go.Figure:
    """Apply the house style to any Plotly figure and add a takeaway-style title."""
    full_title = f"<b>{title}</b>"
    if subtitle:
        full_title += f"<br><span style='font-size:13px;color:{GREY_DARK}'>{subtitle}</span>"

    fig.update_layout(**BASE_LAYOUT)
    fig.update_layout(
        title=dict(text=full_title, x=0.02, xanchor="left", y=0.95),
        height=height, width=width,
    )
    fig.update_xaxes(title_text=xaxis_title, **(AXIS_STYLE_GRID if False else AXIS_STYLE))
    fig.update_yaxes(title_text=yaxis_title, **(AXIS_STYLE_GRID if show_grid_y else AXIS_STYLE))

    fig.add_annotation(
        text=source_note,
        xref="paper", yref="paper", x=0, y=-0.16, xanchor="left", yanchor="top",
        showarrow=False, font=dict(size=10, color="#999999")
    )
    return fig


def set_default_renderer():
    pio.templates.default = "plotly_white"
    # Static PNG rendering (via kaleido) so figures show up in GitHub previews,
    # nbconvert HTML/PDF exports, and the graded PDF export -- not just live Jupyter.
    pio.renderers.default = "png"
    pio.kaleido.scope.default_width = 950
    pio.kaleido.scope.default_height = 560
    pio.kaleido.scope.default_scale = 2
    import warnings
    warnings.filterwarnings("ignore", category=DeprecationWarning, module="plotly")
