import pandas as pd
import numpy as np
import re

df = pd.read_csv('/home/claude/project/data/video_games_steam.csv')

# Drop rows with no game name
df = df.dropna(subset=['game']).copy()

# Parse release date
df['release_date_parsed'] = pd.to_datetime(df['release_date'], format='%b %d, %Y', errors='coerce')
df = df.dropna(subset=['release_date_parsed']).copy()
df['release_year'] = df['release_date_parsed'].dt.year
df['release_month'] = df['release_date_parsed'].dt.month
df['release_month_name'] = df['release_date_parsed'].dt.strftime('%b')

# Keep a sane year window (Steam launched 2003; data collected mid-2019 -> cap 2018 for full years)
df = df[(df['release_year'] >= 2004) & (df['release_year'] <= 2018)].copy()

# Parse owners range -> midpoint estimate + ordered category
df['owners'] = df['owners'].str.replace('\xa0', ' ', regex=False)

def owners_mid(o):
    parts = re.findall(r'[\d,]+', o)
    parts = [int(p.replace(',', '')) for p in parts]
    if len(parts) == 2:
        return (parts[0] + parts[1]) / 2
    return np.nan

owner_order = [
    '0 .. 20,000', '20,000 .. 50,000', '50,000 .. 100,000', '100,000 .. 200,000',
    '200,000 .. 500,000', '500,000 .. 1,000,000', '1,000,000 .. 2,000,000',
    '2,000,000 .. 5,000,000', '5,000,000 .. 10,000,000', '10,000,000 .. 20,000,000',
    '20,000,000 .. 50,000,000', '50,000,000 .. 100,000,000', '100,000,000 .. 200,000,000'
]
df['owners_est'] = df['owners'].apply(owners_mid)
df['owners'] = df['owners'].astype(pd.CategoricalDtype(categories=owner_order, ordered=True))

# Metascore: 0 means "not reviewed" -> treat as missing
df['metascore'] = df['metascore'].replace(0, np.nan)
df['has_critic_score'] = df['metascore'].notna()

# Playtime: fill missing with 0 (SteamSpy reports 0 for untracked)
df['average_playtime'] = df['average_playtime'].fillna(0)
df['median_playtime'] = df['median_playtime'].fillna(0)

# Price cleanup
df['price'] = df['price'].fillna(0.0)

def price_tier(p):
    if p == 0:
        return 'Free'
    elif p < 5:
        return 'Budget (<$5)'
    elif p < 15:
        return 'Mid ($5-15)'
    elif p < 30:
        return 'Standard ($15-30)'
    else:
        return 'Premium ($30+)'

tier_order = ['Free', 'Budget (<$5)', 'Mid ($5-15)', 'Standard ($15-30)', 'Premium ($30+)']
df['price_tier'] = pd.Categorical(df['price'].apply(price_tier), categories=tier_order, ordered=True)

# Title text features
df['title_length_chars'] = df['game'].astype(str).str.len()
df['title_word_count'] = df['game'].astype(str).str.split().str.len()
df['is_sequel_like'] = df['game'].astype(str).str.contains(
    r'\b(?:II|III|IV|V|VI|2|3|4|5|Remastered|Edition|HD)\b', case=False, regex=True
)

# Developer/publisher output volume (catalog size)
dev_counts = df['developer'].value_counts()
df['developer_catalog_size'] = df['developer'].map(dev_counts)
pub_counts = df['publisher'].value_counts()
df['publisher_catalog_size'] = df['publisher'].map(pub_counts)

# Engagement skew: (avg - median) / avg -> higher means more polarized (few players logging huge hours)
df['playtime_skew'] = np.where(
    df['average_playtime'] > 0,
    (df['average_playtime'] - df['median_playtime']) / df['average_playtime'],
    np.nan
)

df.to_csv('/home/claude/project/data/video_games_clean.csv', index=False)
print("Rows after cleaning:", len(df))
print("Year range:", df['release_year'].min(), "-", df['release_year'].max())
print("Columns:", list(df.columns))
