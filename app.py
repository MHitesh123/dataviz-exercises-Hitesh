#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st


st.set_page_config(page_title="World Happiness", page_icon=":earth_africa:", layout="wide")

DATA_FILE = Path(__file__).parent / "data" / "world_happiness_2023.csv"

df = pd.read_csv(DATA_FILE)
df.columns = [
    "Country",
    "Region",
    "Score",
    "GDP",
    "Social_Support",
    "Life_Expectancy",
    "Freedom",
    "Generosity",
    "Corruption",
]

global_average_score = df["Score"].mean()

with st.sidebar:
    st.header("Filters")
    regions = ["All"] + sorted(df["Region"].unique().tolist())
    selected_region = st.selectbox("Region", regions)
    top_n = st.slider("Show top N", 5, 25, 15)

filtered = df if selected_region == "All" else df[df["Region"] == selected_region]

st.title("World Happiness Dashboard")
st.caption("Source: World Happiness Report 2023 | Kaggle")

col1, col2, col3 = st.columns(3)
col1.metric("Countries", len(filtered))
col2.metric(
    "Avg Score",
    f"{filtered['Score'].mean():.2f}",
    f"{filtered['Score'].mean() - global_average_score:+.2f} vs global",
)
col3.metric("Happiest", filtered.nlargest(1, "Score")["Country"].values[0])

st.divider()

col_left, col_right = st.columns(2)

with col_left:
    st.subheader("Rankings")
    top = filtered.nlargest(top_n, "Score").sort_values("Score")

    fig1 = px.bar(
        top,
        x="Score",
        y="Country",
        orientation="h",
        color_discrete_sequence=["#2E75B6"],
        labels={"Score": "Score (0-10)", "Country": ""},
    )

    fig1.update_layout(
        plot_bgcolor="white",
        paper_bgcolor="white",
        xaxis=dict(range=[0, 8.5]),
        font=dict(family="Arial", size=12),
        margin=dict(l=10, r=10, t=5, b=10),
    )
    fig1.update_traces(marker_line_width=0)
    st.plotly_chart(fig1, width="stretch")

with col_right:
    st.subheader("Score vs GDP")
    fig2 = px.scatter(
        filtered,
        x="GDP",
        y="Score",
        hover_name="Country",
        color_discrete_sequence=["#E63946"],
        labels={"GDP": "Logged GDP per capita", "Score": "Score (0-10)"},
    )
    fig2.update_layout(
        plot_bgcolor="white",
        paper_bgcolor="white",
        font=dict(family="Arial", size=12),
        margin=dict(l=10, r=10, t=5, b=10),
    )
    st.plotly_chart(fig2, width="stretch")

st.divider()

st.subheader("Score Gap vs Global Average")

gap = filtered.copy()
gap["Score_Gap"] = gap["Score"] - global_average_score
gap = gap.reindex(gap["Score_Gap"].abs().sort_values(ascending=False).index).head(top_n)
gap = gap.sort_values("Score_Gap")

max_gap = max(abs(gap["Score_Gap"].min()), abs(gap["Score_Gap"].max()))

fig3 = px.bar(
    gap,
    x="Score_Gap",
    y="Country",
    orientation="h",
    color="Score_Gap",
    color_continuous_scale="RdBu",
    range_color=[-max_gap, max_gap],
    labels={
        "Score_Gap": "Difference from global average score",
        "Country": "",
    },
    hover_data={"Score": ":.3f", "Score_Gap": ":.3f"},
)

fig3.add_vline(
    x=0,
    line_width=2,
    line_dash="dash",
    line_color="#333333",
)
fig3.add_annotation(
    x=0,
    y=gap["Country"].iloc[-1],
    text=f"Midpoint: global average score = {global_average_score:.2f}",
    showarrow=True,
    arrowhead=2,
    ax=90,
    ay=-35,
    bgcolor="white",
    bordercolor="#333333",
    borderwidth=1,
)
fig3.update_layout(
    plot_bgcolor="white",
    paper_bgcolor="white",
    font=dict(family="Arial", size=12),
    xaxis=dict(zeroline=False, gridcolor="#EEEEEE"),
    yaxis=dict(showgrid=False),
    coloraxis_colorbar=dict(title="Gap"),
    margin=dict(l=10, r=20, t=5, b=10),
)
fig3.update_traces(marker_line_width=0)

st.plotly_chart(fig3, width="stretch")

st.caption("Built with Streamlit + Plotly")