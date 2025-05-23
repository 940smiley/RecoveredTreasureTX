#!/usr/bin/env python3
"""
Create visualizations for the card collection.
"""

import csv
import matplotlib.pyplot as plt
import seaborn as sns
from collections import Counter, defaultdict
import os

# Set style for better looking plots
plt.style.use('seaborn-v0_8')
sns.set_palette("husl")

def load_collection_data():
    """Load and parse the collection CSV data."""
    data = []
    with open('download_RecoveredTreasures-2025-05-14-071313.csv', 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Clean and convert data types
            try:
                row['market_value'] = float(row['market_value']) if row['market_value'] else 0
            except:
                row['market_value'] = 0
            
            try:
                row['year'] = int(row['year']) if row['year'] else 0
            except:
                row['year'] = 0
            
            data.append(row)
    return data

def create_value_distribution(data):
    """Create a histogram of card values."""
    values = [card['market_value'] for card in data if card['market_value'] > 0]
    
    plt.figure(figsize=(12, 6))
    plt.hist(values, bins=50, alpha=0.7, edgecolor='black')
    plt.title('Distribution of Card Values', fontsize=16, fontweight='bold')
    plt.xlabel('Market Value ($)')
    plt.ylabel('Number of Cards')
    plt.axvline(sum(values)/len(values), color='red', linestyle='--', 
                label=f'Average: ${sum(values)/len(values):.2f}')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig('charts/value_distribution.png', dpi=300, bbox_inches='tight')
    plt.close()

def create_era_breakdown(data):
    """Create a pie chart of cards by era."""
    era_counts = defaultdict(int)
    
    for card in data:
        year = card['year']
        if year <= 1999:
            era_counts['Vintage (≤1999)'] += 1
        elif 2000 <= year <= 2009:
            era_counts['Early 2000s'] += 1
        elif 2010 <= year <= 2019:
            era_counts['Modern 2010s'] += 1
        elif year >= 2020:
            era_counts['Recent 2020+'] += 1
    
    plt.figure(figsize=(10, 8))
    colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4']
    plt.pie(era_counts.values(), labels=era_counts.keys(), autopct='%1.1f%%', 
            startangle=90, colors=colors)
    plt.title('Card Collection by Era', fontsize=16, fontweight='bold')
    plt.axis('equal')
    plt.tight_layout()
    plt.savefig('charts/era_breakdown.png', dpi=300, bbox_inches='tight')
    plt.close()

def create_manufacturer_chart(data):
    """Create a bar chart of top manufacturers."""
    brands = [card['brand'] for card in data if card['brand']]
    brand_counts = Counter(brands)
    
    top_brands = dict(brand_counts.most_common(10))
    
    plt.figure(figsize=(12, 8))
    bars = plt.bar(range(len(top_brands)), list(top_brands.values()))
    plt.title('Top 10 Card Manufacturers', fontsize=16, fontweight='bold')
    plt.xlabel('Manufacturer')
    plt.ylabel('Number of Cards')
    plt.xticks(range(len(top_brands)), list(top_brands.keys()), rotation=45, ha='right')
    
    # Add value labels on bars
    for i, bar in enumerate(bars):
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2., height,
                f'{int(height):,}', ha='center', va='bottom')
    
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig('charts/manufacturer_breakdown.png', dpi=300, bbox_inches='tight')
    plt.close()

def create_sports_comparison(data):
    """Create a comparison of football vs baseball cards."""
    football_teams = {
        'Kansas City Chiefs', 'Houston Texans', 'Minnesota Vikings', 'New England Patriots',
        'Carolina Panthers', 'Los Angeles Rams', 'New York Giants', 'Baltimore Ravens',
        'New York Jets', 'Detroit Lions', 'Tampa Bay Buccaneers', 'Pittsburgh Steelers',
        'Jacksonville Jaguars', 'Washington Redskins', 'Dallas Cowboys', 'Indianapolis Colts',
        'Green Bay Packers', 'Philadelphia Eagles', 'Miami Dolphins', 'Buffalo Bills',
        'Oakland Raiders', 'Cleveland Browns', 'Seattle Seahawks', 'Arizona Cardinals',
        'Los Angeles Raiders', 'Phoenix Cardinals', 'San Francisco 49ers', 'Denver Broncos'
    }
    
    football_count = sum(1 for card in data if card['team'] in football_teams)
    baseball_count = len(data) - football_count
    
    football_value = sum(card['market_value'] for card in data if card['team'] in football_teams)
    baseball_value = sum(card['market_value'] for card in data if card['team'] not in football_teams)
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
    
    # Card count comparison
    sports = ['Football', 'Baseball']
    counts = [football_count, baseball_count]
    colors = ['#FF6B6B', '#4ECDC4']
    
    bars1 = ax1.bar(sports, counts, color=colors)
    ax1.set_title('Card Count by Sport', fontsize=14, fontweight='bold')
    ax1.set_ylabel('Number of Cards')
    
    for bar in bars1:
        height = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2., height,
                f'{int(height):,}', ha='center', va='bottom')
    
    # Value comparison
    values = [football_value, baseball_value]
    bars2 = ax2.bar(sports, values, color=colors)
    ax2.set_title('Total Value by Sport', fontsize=14, fontweight='bold')
    ax2.set_ylabel('Total Value ($)')
    
    for bar in bars2:
        height = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width()/2., height,
                f'${int(height):,}', ha='center', va='bottom')
    
    plt.tight_layout()
    plt.savefig('charts/sports_comparison.png', dpi=300, bbox_inches='tight')
    plt.close()

def create_condition_analysis(data):
    """Create a chart showing card conditions."""
    conditions = [card['condition'] for card in data if card['condition']]
    condition_counts = Counter(conditions)
    
    plt.figure(figsize=(10, 6))
    bars = plt.bar(condition_counts.keys(), condition_counts.values())
    plt.title('Card Collection by Condition', fontsize=16, fontweight='bold')
    plt.xlabel('Condition')
    plt.ylabel('Number of Cards')
    plt.xticks(rotation=45)
    
    # Add value labels on bars
    for bar in bars:
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2., height,
                f'{int(height):,}', ha='center', va='bottom')
    
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig('charts/condition_breakdown.png', dpi=300, bbox_inches='tight')
    plt.close()

def create_top_teams_chart(data):
    """Create a chart of top teams in collection."""
    teams = [card['team'] for card in data if card['team']]
    team_counts = Counter(teams)
    
    top_teams = dict(team_counts.most_common(15))
    
    plt.figure(figsize=(14, 8))
    bars = plt.barh(range(len(top_teams)), list(top_teams.values()))
    plt.title('Top 15 Teams in Collection', fontsize=16, fontweight='bold')
    plt.xlabel('Number of Cards')
    plt.yticks(range(len(top_teams)), list(top_teams.keys()))
    
    # Add value labels on bars
    for i, bar in enumerate(bars):
        width = bar.get_width()
        plt.text(width, bar.get_y() + bar.get_height()/2.,
                f'{int(width):,}', ha='left', va='center')
    
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig('charts/top_teams.png', dpi=300, bbox_inches='tight')
    plt.close()

def create_value_by_year(data):
    """Create a chart showing total value by year."""
    year_values = defaultdict(float)
    
    for card in data:
        if card['year'] > 1980:  # Focus on modern era
            year_values[card['year']] += card['market_value']
    
    years = sorted(year_values.keys())
    values = [year_values[year] for year in years]
    
    plt.figure(figsize=(15, 6))
    plt.plot(years, values, marker='o', linewidth=2, markersize=4)
    plt.title('Total Collection Value by Year', fontsize=16, fontweight='bold')
    plt.xlabel('Year')
    plt.ylabel('Total Value ($)')
    plt.grid(True, alpha=0.3)
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig('charts/value_by_year.png', dpi=300, bbox_inches='tight')
    plt.close()

def main():
    """Generate all visualizations."""
    print("🎨 Generating collection visualizations...")
    
    # Create charts directory
    os.makedirs('charts', exist_ok=True)
    
    # Load data
    data = load_collection_data()
    
    # Generate all charts
    print("📊 Creating value distribution chart...")
    create_value_distribution(data)
    
    print("📅 Creating era breakdown chart...")
    create_era_breakdown(data)
    
    print("🏭 Creating manufacturer chart...")
    create_manufacturer_chart(data)
    
    print("🏈⚾ Creating sports comparison...")
    create_sports_comparison(data)
    
    print("💎 Creating condition analysis...")
    create_condition_analysis(data)
    
    print("🏆 Creating top teams chart...")
    create_top_teams_chart(data)
    
    print("📈 Creating value by year chart...")
    create_value_by_year(data)
    
    print("✅ All visualizations saved to 'charts/' directory!")
    print("\nGenerated charts:")
    charts = [
        "value_distribution.png - Distribution of card values",
        "era_breakdown.png - Cards by era (pie chart)",
        "manufacturer_breakdown.png - Top manufacturers",
        "sports_comparison.png - Football vs Baseball",
        "condition_breakdown.png - Card conditions",
        "top_teams.png - Most represented teams",
        "value_by_year.png - Value trends over time"
    ]
    
    for chart in charts:
        print(f"  📊 {chart}")

if __name__ == "__main__":
    main()
