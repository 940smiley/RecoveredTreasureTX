#!/usr/bin/env python3
"""
Simple analysis of the card collection data without pandas.
"""

import csv
from collections import defaultdict, Counter

def analyze_collection():
    print("=== RecoveredTreasures Collection Analysis ===\n")
    
    total_cards = 0
    total_value = 0
    values = []
    years = []
    brands = []
    conditions = []
    teams = []
    names = []
    rookie_count = 0
    
    # Read CSV data
    with open('download_RecoveredTreasures-2025-05-14-071313.csv', 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            total_cards += 1
            
            # Market value
            try:
                value = float(row['market_value']) if row['market_value'] else 0
                values.append(value)
                total_value += value
            except:
                values.append(0)
            
            # Other fields
            if row['year']:
                try:
                    years.append(int(row['year']))
                except:
                    pass
            
            if row['brand']:
                brands.append(row['brand'])
            
            if row['condition']:
                conditions.append(row['condition'])
            
            if row['team']:
                teams.append(row['team'])
            
            if row['name']:
                names.append(row['name'])
            
            # Check for rookie cards
            if row['flags'] and 'RC' in row['flags']:
                rookie_count += 1
    
    # Basic stats
    print(f"📊 **Total Cards:** {total_cards:,}")
    print(f"💰 **Total Collection Value:** ${total_value:,.2f}")
    
    if values:
        avg_value = sum(values) / len(values)
        values_sorted = sorted(values)
        median_value = values_sorted[len(values_sorted)//2]
        max_value = max(values)
        
        print(f"📈 **Average Card Value:** ${avg_value:.2f}")
        print(f"📊 **Median Card Value:** ${median_value:.2f}")
        print(f"🏆 **Most Valuable Card:** ${max_value:.2f}")
    
    # Sports breakdown
    football_teams = {
        'Kansas City Chiefs', 'Houston Texans', 'Minnesota Vikings', 'New England Patriots',
        'Carolina Panthers', 'Los Angeles Rams', 'New York Giants', 'Baltimore Ravens',
        'New York Jets', 'Detroit Lions', 'Tampa Bay Buccaneers', 'Pittsburgh Steelers',
        'Jacksonville Jaguars', 'Washington Redskins', 'Dallas Cowboys', 'Indianapolis Colts',
        'Green Bay Packers', 'Philadelphia Eagles', 'Miami Dolphins', 'Buffalo Bills',
        'Oakland Raiders', 'Cleveland Browns', 'Seattle Seahawks', 'Arizona Cardinals',
        'Los Angeles Raiders', 'Phoenix Cardinals', 'San Francisco 49ers', 'Denver Broncos'
    }
    
    football_count = sum(1 for team in teams if team in football_teams)
    baseball_count = total_cards - football_count
    
    print(f"\n🏈 **Sports Breakdown:**")
    print(f"   🏈 Football: {football_count:,} cards")
    print(f"   ⚾ Baseball: {baseball_count:,} cards")
    
    # Year breakdown
    print(f"\n📅 **Cards by Era:**")
    vintage_90s = sum(1 for year in years if year <= 1999)
    early_2000s = sum(1 for year in years if 2000 <= year <= 2009)
    modern_2010s = sum(1 for year in years if 2010 <= year <= 2019)
    recent_2020s = sum(1 for year in years if year >= 2020)
    
    print(f"   📼 Vintage (≤1999): {vintage_90s:,} cards")
    print(f"   🎮 Early 2000s (2000-2009): {early_2000s:,} cards")
    print(f"   📱 Modern (2010-2019): {modern_2010s:,} cards")
    print(f"   🆕 Recent (2020+): {recent_2020s:,} cards")
    
    # Brand breakdown
    print(f"\n🏭 **Top Manufacturers:**")
    brand_counts = Counter(brands)
    for brand, count in brand_counts.most_common(10):
        print(f"   {brand}: {count:,} cards")
    
    # Condition breakdown
    print(f"\n💎 **Card Conditions:**")
    condition_counts = Counter(conditions)
    for condition, count in condition_counts.most_common():
        if condition:
            print(f"   {condition}: {count:,} cards")
    
    # Rookie cards
    print(f"\n🌟 **Rookie Cards:** {rookie_count:,}")
    
    # Team breakdown
    print(f"\n🏈 **Top Teams in Collection:**")
    team_counts = Counter(teams)
    for team, count in team_counts.most_common(10):
        print(f"   {team}: {count:,} cards")

if __name__ == "__main__":
    analyze_collection()
