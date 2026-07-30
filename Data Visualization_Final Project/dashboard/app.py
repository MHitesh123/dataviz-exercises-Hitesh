"""
The Steam Marketplace, 2004-2018 -- Interactive Dashboard
Final Individual Project, Data Visualization, Summer 2026

Run locally with:  streamlit run app.py
"""
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

from viz_style import (
    style_fig, OI_BLUE, OI_ORANGE, OI_GREEN, OI_VERMILLION, OI_PURPLE,
    OI_SKYBLUE, GREY, GREY_DARK, CATEGORY_SEQUENCE,
)

st.set_page_config(
    page_title="Steam Marketplace 2004-2018",
    page_icon="🎮",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --------------------------------------------------------------------------
# Data loading
# --------------------------------------------------------------------------
@st.cache_data
def load_data():
    df = pd.read_csv("video_games_clean.csv", parse_dates=["release_date_parsed"])
    owner_order = [
        '0 .. 20,000', '20,000 .. 50,000', '50,000 .. 100,000', '100,000 .. 200,000',
        '200,000 .. 500,000', '500,000 .. 1,000,000', '1,000,000 .. 2,000,000',
        '2,000,000 .. 5,000,000', '5,000,000 .. 10,000,000', '10,000,000 .. 20,000,000',
        '20,000,000 .. 50,000,000', '50,000,000 .. 100,000,000', '100,000,000 .. 200,000,000'
    ]
    df['owners'] = pd.Categorical(df['owners'], categories=owner_order, ordered=True)
    tier_order = ['Free', 'Budget (<$5)', 'Mid ($5-15)', 'Standard ($15-30)', 'Premium ($30+)']
    df['price_tier'] = pd.Categorical(df['price_tier'], categories=tier_order, ordered=True)

    def owner_bucket(cat):
        if pd.isna(cat):
            return np.nan
        if cat in ['0 .. 20,000', '20,000 .. 50,000']:
            return 'Niche (<50K owners)'
        elif cat in ['50,000 .. 100,000', '100,000 .. 200,000', '200,000 .. 500,000']:
            return 'Mid-size (50K-500K)'
        else:
            return 'Hit (500K+ owners)'
    df['owner_bucket'] = df['owners'].apply(owner_bucket)
    return df

df_full = load_data()
TIER_ORDER = list(df_full['price_tier'].cat.categories)
BUCKET_ORDER = ['Niche (<50K owners)', 'Mid-size (50K-500K)', 'Hit (500K+ owners)']
SOURCE_NOTE = "Source: SteamSpy / Steam Store, via TidyTuesday (2019-07-30)"

# --------------------------------------------------------------------------
# Sidebar filters
# --------------------------------------------------------------------------
st.sidebar.title("🎮 Filters")
st.sidebar.caption("Every chart on every tab updates live from these filters.")

year_min, year_max = int(df_full['release_year'].min()), int(df_full['release_year'].max())
year_range = st.sidebar.slider("Release year range", year_min, year_max, (year_min, year_max))

price_tiers = st.sidebar.multiselect(
    "Price tier", options=TIER_ORDER, default=TIER_ORDER
)

owner_buckets = st.sidebar.multiselect(
    "Popularity tier", options=BUCKET_ORDER, default=BUCKET_ORDER
)

only_reviewed = st.sidebar.checkbox("Only games with a Metacritic score", value=False)

st.sidebar.divider()
publisher_search = st.sidebar.text_input("Search publisher (contains)", "")

st.sidebar.divider()
st.sidebar.caption(
    "Built with Streamlit + Plotly. Full analysis (12 questions) available in the "
    "companion Jupyter notebook. " + SOURCE_NOTE
)

# --------------------------------------------------------------------------
# Apply filters
# --------------------------------------------------------------------------
df = df_full[
    (df_full['release_year'] >= year_range[0]) &
    (df_full['release_year'] <= year_range[1]) &
    (df_full['price_tier'].isin(price_tiers)) &
    (df_full['owner_bucket'].isin(owner_buckets))
].copy()

if only_reviewed:
    df = df[df['has_critic_score']]

if publisher_search:
    df = df[df['publisher'].astype(str).str.contains(publisher_search, case=False, na=False)]

if len(df) == 0:
    st.warning("No games match the current filters -- try widening your selection in the sidebar.")
    st.stop()

# --------------------------------------------------------------------------
# Header + KPIs
# --------------------------------------------------------------------------
st.title("The Steam Marketplace, 2004-2018")
st.caption(
    "Pricing, popularity, and quality across the Steam catalog. Adjust filters in the sidebar to explore."
)

k1, k2, k3, k4, k5 = st.columns(5)
k1.metric("Games (filtered)", f"{len(df):,}", help=f"out of {len(df_full):,} total")
k2.metric("Median price", f"${df['price'].median():.2f}")
k3.metric("Total est. owners", f"{df['owners_est'].sum()/1e6:,.1f}M")
k4.metric("Reviewed on Metacritic", f"{df['has_critic_score'].mean()*100:.1f}%")
k5.metric("Median avg. playtime", f"{df[df['average_playtime']>0]['average_playtime'].median():.0f} min")

st.divider()

# --------------------------------------------------------------------------
# Tabs
# --------------------------------------------------------------------------
tab1, tab2, tab3, tab4 = st.tabs([
    "📈 Market Overview", "💵 Pricing & Engagement", "⭐ Quality & Discovery", "🔎 Explore the Data"
])

# ============================================================ TAB 1
with tab1:
    st.subheader("How the catalog grew -- and what that did to prices")
    c1, c2 = st.columns(2)

    with c1:
        yearly = df.groupby('release_year').agg(
            releases=('game', 'count'), median_price=('price', 'median')
        ).reset_index()
        fig = go.Figure()
        fig.add_trace(go.Bar(x=yearly['release_year'], y=yearly['releases'],
                              name='Games released', marker_color=GREY, opacity=0.85))
        fig.add_trace(go.Scatter(x=yearly['release_year'], y=yearly['median_price'],
                                  name='Median price ($)', mode='lines+markers',
                                  line=dict(color=OI_VERMILLION, width=3), yaxis='y2'))
        fig.update_layout(
            yaxis=dict(title='Releases per year'),
            yaxis2=dict(title='Median price ($)', overlaying='y', side='right', showgrid=False),
        )
        fig = style_fig(fig, "Volume up, price down", "Releases (bars) vs. median price (line)",
                         xaxis_title="Year", show_grid_y=False, height=420, source_note=SOURCE_NOTE)
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        flood = df.groupby('release_year').apply(
            lambda g: (g['owners'] == '0 .. 20,000').mean() * 100, include_groups=False
        ).reset_index(name='low_owner_share')
        fig = px.area(flood, x='release_year', y='low_owner_share', color_discrete_sequence=[OI_VERMILLION])
        fig.update_traces(line=dict(width=3), fillcolor='rgba(213,94,0,0.15)')
        fig = style_fig(fig, "The long tail keeps getting longer",
                         "Share of releases with under 20K estimated owners",
                         xaxis_title="Year", yaxis_title="Share of releases (%)",
                         height=420, source_note=SOURCE_NOTE)
        st.plotly_chart(fig, use_container_width=True)

    st.subheader("Who controls the market?")
    pub_owners = df.groupby('publisher')['owners_est'].sum().sort_values(ascending=False)
    top_n = st.slider("Show top N publishers", 5, 25, 15, key="topn_pub")
    topk = pub_owners.head(top_n).reset_index()
    topk.columns = ['publisher', 'total_owners_est']
    total_market = pub_owners.sum()
    topk['cum_share'] = topk['total_owners_est'].cumsum() / total_market * 100
    colors = [OI_VERMILLION if i < 3 else OI_BLUE for i in range(len(topk))]

    fig = go.Figure()
    fig.add_trace(go.Bar(x=topk['publisher'], y=topk['total_owners_est'], marker_color=colors,
                          name='Est. total owners'))
    fig.add_trace(go.Scatter(x=topk['publisher'], y=topk['cum_share'], name='Cumulative share (%)',
                              mode='lines+markers', line=dict(color=GREY_DARK, width=2, dash='dot'),
                              yaxis='y2'))
    fig.update_layout(
        yaxis=dict(title='Estimated total owners'),
        yaxis2=dict(title='Cumulative % of market', overlaying='y', side='right', range=[0, 100], showgrid=False),
        xaxis=dict(tickangle=-35),
    )
    fig = style_fig(fig, f"Top {top_n} publishers and their share of estimated ownership",
                     xaxis_title="Publisher", show_grid_y=False, height=460, source_note=SOURCE_NOTE)
    st.plotly_chart(fig, use_container_width=True)

# ============================================================ TAB 2
with tab2:
    st.subheader("Does price buy engagement -- or does popularity?")
    engagement = (
        df[df['average_playtime'] > 0]
        .groupby(['price_tier', 'owner_bucket'], observed=True)['average_playtime']
        .mean().reset_index()
    )
    fig = px.bar(engagement, x='price_tier', y='average_playtime', color='owner_bucket',
                 barmode='group', category_orders={'price_tier': TIER_ORDER, 'owner_bucket': BUCKET_ORDER},
                 color_discrete_sequence=[OI_SKYBLUE, OI_BLUE, OI_VERMILLION])
    fig = style_fig(fig, "Popularity drives playtime more than price does",
                     "Mean average playtime (minutes) by price tier & popularity tier",
                     xaxis_title="Price tier", yaxis_title="Mean avg. playtime (min)",
                     height=460, source_note=SOURCE_NOTE)
    st.plotly_chart(fig, use_container_width=True)

    c1, c2 = st.columns(2)
    with c1:
        skew_df = df[(df['average_playtime'] > 0) & df['playtime_skew'].notna()]
        skew_stats = skew_df.groupby('price_tier', observed=True)['playtime_skew'].mean().reset_index()
        fig = px.bar(skew_stats, x='price_tier', y='playtime_skew', color='price_tier',
                     color_discrete_sequence=CATEGORY_SEQUENCE)
        fig.update_layout(showlegend=False)
        fig = style_fig(fig, "Free games have the most polarized audiences",
                         "Mean playtime-skew index by price tier (higher = more polarized)",
                         xaxis_title="Price tier", yaxis_title="Playtime-skew index",
                         height=420, source_note=SOURCE_NOTE)
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        seq_compare = (
            df[df['owners_est'] > 0]
            .groupby(['price_tier', 'is_sequel_like'], observed=True)['owners_est']
            .median().reset_index()
        )
        seq_compare['label'] = seq_compare['is_sequel_like'].map(
            {True: 'Sequel / edition marker', False: 'Original title'})
        fig = px.bar(seq_compare, x='price_tier', y='owners_est', color='label', barmode='group',
                     log_y=True, category_orders={'price_tier': TIER_ORDER},
                     color_discrete_sequence=[GREY, OI_BLUE])
        fig = style_fig(fig, "'Sequel' titles out-reach originals at every price",
                         "Median estimated owners (log scale)",
                         xaxis_title="Price tier", yaxis_title="Median owners (log)",
                         height=420, source_note=SOURCE_NOTE)
        st.plotly_chart(fig, use_container_width=True)

# ============================================================ TAB 3
with tab3:
    reviewed = df[df['has_critic_score'] & (df['average_playtime'] > 0)].copy()
    if len(reviewed) < 10:
        st.info("Not enough reviewed games in the current filter to show this section -- widen your filters.")
    else:
        st.subheader("Quality vs. reach: where are the hidden gems?")
        quad = df[df['has_critic_score'] & (df['owners_est'] > 0)].copy()
        score_med, owners_med = quad['metascore'].median(), quad['owners_est'].median()

        def quadrant(row):
            if row['metascore'] >= score_med and row['owners_est'] < owners_med:
                return 'Hidden gem (high score, low reach)'
            elif row['metascore'] >= score_med and row['owners_est'] >= owners_med:
                return 'Mainstream hit (high score, high reach)'
            elif row['metascore'] < score_med and row['owners_est'] >= owners_med:
                return 'Marketing win (low score, high reach)'
            else:
                return 'Overlooked / niche (low score, low reach)'

        quad['quadrant'] = quad.apply(quadrant, axis=1)
        fig = px.scatter(quad, x='owners_est', y='metascore', color='quadrant', log_x=True,
                          hover_name='game', opacity=0.6,
                          color_discrete_map={
                              'Hidden gem (high score, low reach)': OI_VERMILLION,
                              'Mainstream hit (high score, high reach)': OI_BLUE,
                              'Marketing win (low score, high reach)': OI_PURPLE,
                              'Overlooked / niche (low score, low reach)': GREY,
                          })
        fig.add_vline(x=owners_med, line_dash='dot', line_color=GREY_DARK, opacity=0.6)
        fig.add_hline(y=score_med, line_dash='dot', line_color=GREY_DARK, opacity=0.6)
        fig.update_traces(marker=dict(size=8))
        fig = style_fig(fig, "Hover any point to see the game",
                         "Metacritic score vs. estimated owners (log scale)",
                         xaxis_title="Estimated owners (log)", yaxis_title="Metacritic score",
                         height=520, source_note=SOURCE_NOTE)
        st.plotly_chart(fig, use_container_width=True)

        c1, c2 = st.columns(2)
        with c1:
            def catalog_bucket(n):
                if n == 1: return '1 game'
                elif n <= 5: return '2-5 games'
                elif n <= 20: return '6-20 games'
                else: return '20+ games'
            reviewed['dev_bucket'] = reviewed['developer_catalog_size'].apply(catalog_bucket)
            order2 = ['1 game', '2-5 games', '6-20 games', '20+ games']
            fig = px.box(reviewed, x='dev_bucket', y='metascore', color='dev_bucket',
                         category_orders={'dev_bucket': order2}, color_discrete_sequence=CATEGORY_SEQUENCE)
            fig.update_layout(showlegend=False)
            fig = style_fig(fig, "Scale buys consistency, not excellence",
                             "Metacritic score distribution by developer catalog size",
                             xaxis_title="Developer catalog size", yaxis_title="Metacritic score",
                             height=420, source_note=SOURCE_NOTE)
            st.plotly_chart(fig, use_container_width=True)

        with c2:
            reviewed['score_decile'] = pd.qcut(reviewed['metascore'], min(8, reviewed['metascore'].nunique()), duplicates='drop')
            decile_stats = reviewed.groupby('score_decile', observed=True)['average_playtime'].mean().reset_index()
            decile_stats['score_mid'] = decile_stats['score_decile'].apply(lambda iv: iv.mid)
            fig = px.line(decile_stats, x='score_mid', y='average_playtime', markers=True,
                          color_discrete_sequence=[OI_BLUE])
            fig.update_traces(line=dict(width=3), marker=dict(size=8))
            fig = style_fig(fig, "Engagement rises sharply only at the top of the scale",
                             "Mean avg. playtime by Metacritic score octile",
                             xaxis_title="Metacritic score", yaxis_title="Mean avg. playtime (min)",
                             height=420, source_note=SOURCE_NOTE)
            st.plotly_chart(fig, use_container_width=True)

# ============================================================ TAB 4
with tab4:
    st.subheader("Price tier x popularity: where does the catalog concentrate?")
    heat = df.groupby(['price_tier', 'owners'], observed=True).size().reset_index(name='count')
    heat_pivot = heat.pivot(index='price_tier', columns='owners', values='count').fillna(0)
    heat_pivot = heat_pivot.reindex(index=[t for t in TIER_ORDER if t in heat_pivot.index])
    fig = go.Figure(data=go.Heatmap(
        z=heat_pivot.values, x=[str(c) for c in heat_pivot.columns], y=[str(i) for i in heat_pivot.index],
        colorscale=[[0, '#F7F7F7'], [0.15, '#BFE1F0'], [0.4, '#56B4E9'], [1, '#0072B2']],
        colorbar=dict(title='Games'),
        hovertemplate='Price tier: %{y}<br>Owners: %{x}<br>Games: %{z:,.0f}<extra></extra>'
    ))
    fig = style_fig(fig, "Most of the catalog sits in the cheap + low-visibility cell",
                     xaxis_title="Estimated ownership bracket", yaxis_title="Price tier",
                     height=460, source_note=SOURCE_NOTE)
    fig.update_xaxes(tickangle=-30)
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Browse the filtered data")
    show_cols = ['game', 'release_date', 'developer', 'publisher', 'price', 'price_tier',
                 'owners', 'owners_est', 'average_playtime', 'metascore']
    sort_col = st.selectbox("Sort by", show_cols, index=show_cols.index('owners_est'))
    ascending = st.checkbox("Ascending", value=False)
    st.dataframe(
        df[show_cols].sort_values(sort_col, ascending=ascending).head(500),
        use_container_width=True, height=400
    )
    st.download_button(
        "Download filtered data as CSV",
        df[show_cols].to_csv(index=False).encode('utf-8'),
        file_name="steam_games_filtered.csv",
        mime="text/csv",
    )

st.divider()
st.caption(
    "Final Individual Project · Data Visualization · Summer 2026 &nbsp;|&nbsp; "
    "Dataset: Steam Store + SteamSpy via TidyTuesday (2019-07-30) &nbsp;|&nbsp; "
    "Built with Streamlit + Plotly"
)
