#!/usr/bin/env python3
"""
Analyze the card collection data and generate statistics.
"""

import pandas as pd
import numpy as np
from collections import Counter
import re

def analyze_collection():
    # Load the CSV data
    df = pd.read_csv('download_RecoveredTreasures-2025-05-14-071313.csv')
    
    print("=== RecoveredTreasures Collection Analysis ===\n")
    
    # Basic stats
    total_cards = len(df)
    print(f"📊 **Total Cards:** {total_cards:,}")
    
    # Market value analysis
    df['market_value'] = pd.to_numeric(df['market_value'], errors='coerce')
    total_value = df['market_value'].sum()
    avg_value = df['market_value'].mean()
    median_value = df['market_value'].median()
    max_value = df['market_value'].max()
    
    print(f"💰 **Total Collection Value:** ${total_value:,.2f}")
    print(f"📈 **Average Card Value:** ${avg_value:.2f}")
    print(f"📊 **Median Card Value:** ${median_value:.2f}")
    print(f"🏆 **Most Valuable Card:** ${max_value:.2f}")
    
    # Most valuable cards
    print("\n🔥 **Top 10 Most Valuable Cards:**")
    top_cards = df.nlargest(10, 'market_value')[['name', 'team', 'year', 'brand', 'market_value']]
    for idx, row in top_cards.iterrows():
        print(f"   {row['name']} ({row['team']}) - {row['year']} {row['brand']} - ${row['market_value']:.2f}")
    
    # Sports breakdown
    print(f"\n🏈 **Sports Breakdown:**")
    # Analyze teams to determine sport
    football_teams = {
        'Kansas City Chiefs', 'Houston Texans', 'Minnesota Vikings', 'New England Patriots',
        'Carolina Panthers', 'Los Angeles Rams', 'New York Giants', 'Baltimore Ravens',
        'New York Jets', 'Detroit Lions', 'Tampa Bay Buccaneers', 'Pittsburgh Steelers',
        'Jacksonville Jaguars', 'Washington Redskins', 'Dallas Cowboys', 'Indianapolis Colts',
        'Green Bay Packers', 'Philadelphia Eagles', 'Miami Dolphins', 'Buffalo Bills',
        'Oakland Raiders', 'Cleveland Browns', 'Seattle Seahawks', 'Arizona Cardinals',
        'Los Angeles Raiders', 'Phoenix Cardinals', 'San Francisco 49ers', 'Denver Broncos',
        'Cincinnati Bengals', 'Tennessee Titans', 'Atlanta Falcons', 'Chicago Bears',
        'Los Angeles Chargers', 'Las Vegas Raiders'
    }
    
    football_cards = df[df['team'].isin(football_teams)]
    baseball_cards = df[~df['team'].isin(football_teams)]
    
    print(f"   🏈 Football: {len(football_cards):,} cards")
    print(f"   ⚾ Baseball: {len(baseball_cards):,} cards")
    
    # Year breakdown
    print(f"\n📅 **Cards by Era:**")
    year_counts = df['year'].value_counts().sort_index()
    vintage_90s = df[df['year'] <= 1999]
    early_2000s = df[(df['year'] >= 2000) & (df['year'] <= 2009)]
    modern_2010s = df[(df['year'] >= 2010) & (df['year'] <= 2019)]
    recent_2020s = df[df['year'] >= 2020]
    
    print(f"   📼 Vintage (≤1999): {len(vintage_90s):,} cards")
    print(f"   🎮 Early 2000s (2000-2009): {len(early_2000s):,} cards")
    print(f"   📱 Modern (2010-2019): {len(modern_2010s):,} cards")
    print(f"   🆕 Recent (2020+): {len(recent_2020s):,} cards")
    
    # Brand breakdown
    print(f"\n🏭 **Top Manufacturers:**")
    brand_counts = df['brand'].value_counts().head(10)
    for brand, count in brand_counts.items():
        print(f"   {brand}: {count:,} cards")
    
    # Condition breakdown
    print(f"\n💎 **Card Conditions:**")
    condition_counts = df['condition'].value_counts()
    for condition, count in condition_counts.items():
        if pd.notna(condition):
            print(f"   {condition}: {count:,} cards")
    
    # Rookie cards
    rookie_cards = df[df['flags'].str.contains('RC', na=False)]
    print(f"\n🌟 **Rookie Cards:** {len(rookie_cards):,}")
    
    # Team breakdown for football
    print(f"\n🏈 **Top Football Teams in Collection:**")
    football_team_counts = football_cards['team'].value_counts().head(10)
    for team, count in football_team_counts.items():
        print(f"   {team}: {count:,} cards")
    
    return df

if __name__ == "__main__":
    df = analyze_collection()
