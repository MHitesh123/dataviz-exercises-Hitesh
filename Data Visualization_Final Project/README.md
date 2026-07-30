# 🎮 The Steam Marketplace, 2004–2018

**Final Individual Project — Data Visualization, Summer 2026**

A data story about how the PC gaming market on Steam changed as it grew from a
curated, premium-priced storefront into a high-volume, budget-priced marketplace —
told through 12 analytical questions, publication-ready Plotly visuals, and an
interactive Streamlit dashboard.

🔗 **Live dashboard:** _add your Streamlit Community Cloud URL here after deploying_
📓 **Full analysis notebook:** [`notebook/Final_Project_Analysis.ipynb`](notebook/Final_Project_Analysis.ipynb) · [HTML export](notebook/Final_Project_Analysis.html)
🖼️ **Slide deck:** [`presentation/Final_Project_Presentation.pdf`](presentation/Final_Project_Presentation.pdf)

---

## The dataset

**26,643 games** released on Steam between 2004 and 2018, scraped from the Steam
Store and SteamSpy, distributed via the [TidyTuesday project](https://github.com/rfordatascience/tidytuesday/blob/master/data/2019/2019-07-30/readme.md)
(week of 2019-07-30). Real-world, non-synthetic data — not a toy teaching set.

| Attribute type | Columns |
|---|---|
| **Numerical** | `price`, `average_playtime`, `median_playtime`, `metascore`, `owners_est` |
| **Categorical** | `developer`, `publisher`, `owners` (ordinal bracket), `price_tier` (engineered) |
| **Temporal** | `release_date`, `release_year`, `release_month` |
| **Text** | `game` (title) — length, word count, sequel/edition-marker patterns |

Raw data: [`data/video_games_steam.csv`](data/video_games_steam.csv)
Cleaning & feature engineering: [`data/clean_data.py`](data/clean_data.py)
Cleaned data used everywhere downstream: [`data/video_games_clean.csv`](data/video_games_clean.csv)

## The 12 analytical questions

1. As the catalog exploded, did typical launch prices fall?
2. Are there fewer fewer "holiday launch window" effects as the platform matured?
3. Does price or popularity drive player engagement (playtime)?
4. How concentrated is the market among top publishers?
5. Does critical acclaim (Metacritic score) predict more playtime?
6. Are there "hidden gems" — high score, low reach?
7. Do prolific developers sustain quality as they scale output?
8. Which price tiers produce the most polarized play patterns?
9. Have title length and sequel-labeling conventions shifted over time?
10. Do sequel/edition-labeled titles out-sell originals at every price point?
11. Is the market "flooding" with low-visibility titles over time?
12. Where does the bulk of the catalog sit on price × popularity?

Full write-up, methodology, and takeaways for each question are in the notebook.

## Repository structure

```
├── data/
│   ├── video_games_steam.csv       # raw data (TidyTuesday / SteamSpy)
│   ├── clean_data.py                # cleaning & feature engineering
│   └── video_games_clean.csv        # cleaned data used by notebook + dashboard
├── notebook/
│   ├── Final_Project_Analysis.ipynb # 10+ analytical Q&A, Plotly visuals
│   ├── Final_Project_Analysis.html  # static export
│   └── viz_style.py                 # shared CVD-safe Plotly theme
├── dashboard/
│   ├── app.py                       # Streamlit app (4 tabs, live filters)
│   ├── viz_style.py                 # same shared theme
│   ├── video_games_clean.csv        # data copy for standalone deployment
│   ├── requirements.txt
│   └── .streamlit/config.toml       # theme config
├── presentation/
│   └── Final_Project_Presentation.pdf
└── requirements.txt                  # copy at root for Streamlit Cloud auto-detect
```

## Running locally

```bash
git clone <this-repo-url>
cd <repo>
pip install -r requirements.txt

# Notebook
jupyter notebook notebook/Final_Project_Analysis.ipynb

# Dashboard
cd dashboard
streamlit run app.py
```

## Deploying the dashboard on Streamlit Community Cloud

1. Push this repo to a **public** GitHub repository.
2. Go to [share.streamlit.io](https://share.streamlit.io), sign in, click **New app**.
3. Pick this repo/branch, set **Main file path** to `dashboard/app.py`.
4. Deploy — Streamlit Cloud will pick up `requirements.txt` automatically.
5. Paste the resulting URL back into this README and the presentation.

## Design principles applied

- **Plotly only** — no Matplotlib/Seaborn anywhere in the codebase.
- **CVD-safe palette** — Okabe–Ito colorblind-safe colors throughout (`notebook/viz_style.py`, reused by the dashboard).
- **Explanatory, not exploratory** — every chart title states the takeaway, not just the variables plotted.
- **Decluttered** — gridlines, chart-junk, and redundant ink removed; muted grey for context, one highlight color for focus.
- **Consistent design** — the same style module drives every chart in both the notebook and the dashboard.

## Limitations

Ownership and playtime are SteamSpy *estimates* (subject to API/privacy-setting
changes), Metacritic coverage is sparse (~10.7% of titles), and the snapshot ends in
2019 — before more recent shifts in Steam's discovery algorithm and the further
indie-market expansion of the 2020s.
