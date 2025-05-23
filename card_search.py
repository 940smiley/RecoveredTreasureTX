#!/usr/bin/env python3
"""
Advanced search and filter tools for the card collection.
"""

import csv
import argparse
import re
from collections import defaultdict
import json

class CardSearcher:
    def __init__(self, csv_file='download_RecoveredTreasures-2025-05-14-071313.csv'):
        self.csv_file = csv_file
        self.cards = []
        self.load_data()
    
    def load_data(self):
        """Load card data from CSV."""
        with open(self.csv_file, 'r', encoding='utf-8') as f:
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
                
                self.cards.append(row)
    
    def search_by_name(self, name, exact=False):
        """Search cards by player name."""
        results = []
        name_lower = name.lower()
        
        for card in self.cards:
            card_name = card['name'].lower()
            if exact:
                if card_name == name_lower:
                    results.append(card)
            else:
                if name_lower in card_name:
                    results.append(card)
        
        return results
    
    def search_by_team(self, team):
        """Search cards by team."""
        results = []
        team_lower = team.lower()
        
        for card in self.cards:
            if team_lower in card['team'].lower():
                results.append(card)
        
        return results
    
    def search_by_year(self, year=None, year_min=None, year_max=None):
        """Search cards by year or year range."""
        results = []
        
        for card in self.cards:
            card_year = card['year']
            
            if year is not None:
                if card_year == year:
                    results.append(card)
            elif year_min is not None or year_max is not None:
                if year_min and card_year < year_min:
                    continue
                if year_max and card_year > year_max:
                    continue
                results.append(card)
        
        return results
    
    def search_by_brand(self, brand):
        """Search cards by manufacturer/brand."""
        results = []
        brand_lower = brand.lower()
        
        for card in self.cards:
            if brand_lower in card['brand'].lower():
                results.append(card)
        
        return results
    
    def search_by_value(self, min_value=None, max_value=None):
        """Search cards by market value range."""
        results = []
        
        for card in self.cards:
            value = card['market_value']
            
            if min_value is not None and value < min_value:
                continue
            if max_value is not None and value > max_value:
                continue
            
            results.append(card)
        
        return results
    
    def search_by_condition(self, condition):
        """Search cards by condition."""
        results = []
        condition_lower = condition.lower()
        
        for card in self.cards:
            if card['condition'] and condition_lower in card['condition'].lower():
                results.append(card)
        
        return results
    
    def search_rookie_cards(self):
        """Find all rookie cards."""
        results = []
        
        for card in self.cards:
            if card['flags'] and 'RC' in card['flags']:
                results.append(card)
        
        return results
    
    def search_high_value_cards(self, threshold=50):
        """Find cards above a certain value threshold."""
        results = []
        
        for card in self.cards:
            if card['market_value'] >= threshold:
                results.append(card)
        
        return results
    
    def advanced_search(self, **kwargs):
        """Perform advanced search with multiple criteria."""
        results = self.cards.copy()
        
        # Apply each filter
        if kwargs.get('name'):
            name_results = self.search_by_name(kwargs['name'], kwargs.get('exact_name', False))
            results = [card for card in results if card in name_results]
        
        if kwargs.get('team'):
            team_results = self.search_by_team(kwargs['team'])
            results = [card for card in results if card in team_results]
        
        if kwargs.get('year'):
            year_results = self.search_by_year(year=kwargs['year'])
            results = [card for card in results if card in year_results]
        
        if kwargs.get('year_min') or kwargs.get('year_max'):
            year_results = self.search_by_year(year_min=kwargs.get('year_min'), year_max=kwargs.get('year_max'))
            results = [card for card in results if card in year_results]
        
        if kwargs.get('brand'):
            brand_results = self.search_by_brand(kwargs['brand'])
            results = [card for card in results if card in brand_results]
        
        if kwargs.get('min_value') or kwargs.get('max_value'):
            value_results = self.search_by_value(kwargs.get('min_value'), kwargs.get('max_value'))
            results = [card for card in results if card in value_results]
        
        if kwargs.get('condition'):
            condition_results = self.search_by_condition(kwargs['condition'])
            results = [card for card in results if card in condition_results]
        
        if kwargs.get('rookie_only'):
            rookie_results = self.search_rookie_cards()
            results = [card for card in results if card in rookie_results]
        
        return results
    
    def sort_results(self, results, sort_by='value', descending=True):
        """Sort search results."""
        if sort_by == 'value':
            results.sort(key=lambda x: x['market_value'], reverse=descending)
        elif sort_by == 'year':
            results.sort(key=lambda x: x['year'], reverse=descending)
        elif sort_by == 'name':
            results.sort(key=lambda x: x['name'].lower(), reverse=descending)
        elif sort_by == 'team':
            results.sort(key=lambda x: x['team'].lower(), reverse=descending)
        elif sort_by == 'brand':
            results.sort(key=lambda x: x['brand'].lower(), reverse=descending)
        
        return results
    
    def format_results(self, results, detailed=False, limit=None):
        """Format search results for display."""
        if limit:
            results = results[:limit]
        
        if not results:
            return "No cards found matching your criteria."
        
        output = []
        output.append(f"\n🔍 Found {len(results)} cards:")
        output.append("=" * 60)
        
        for i, card in enumerate(results, 1):
            if detailed:
                output.append(f"\n#{i}. {card['name']} ({card['team']})")
                output.append(f"   Year: {card['year']} | Brand: {card['brand']}")
                output.append(f"   Set: {card['set']} | Number: {card['number']}")
                output.append(f"   Condition: {card['condition']}")
                output.append(f"   Market Value: ${card['market_value']:.2f}")
                output.append(f"   CollX ID: {card['collx_id']}")
                if card['flags']:
                    output.append(f"   Flags: {card['flags']}")
                if card['front_image']:
                    output.append(f"   Image: {card['front_image']}")
                output.append("-" * 40)
            else:
                flags_str = f" [{card['flags']}]" if card['flags'] else ""
                output.append(f"{i:3d}. {card['name']} ({card['team']}) - {card['year']} {card['brand']} - ${card['market_value']:.2f}{flags_str}")
        
        return "\n".join(output)
    
    def export_results(self, results, filename, format='csv'):
        """Export search results to file."""
        if format == 'csv':
            with open(filename, 'w', newline='', encoding='utf-8') as f:
                if results:
                    writer = csv.DictWriter(f, fieldnames=results[0].keys())
                    writer.writeheader()
                    writer.writerows(results)
        elif format == 'json':
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False)
        
        print(f"📁 Exported {len(results)} cards to {filename}")

def main():
    parser = argparse.ArgumentParser(description='Search your card collection')
    
    # Search criteria
    parser.add_argument('--name', help='Player name to search for')
    parser.add_argument('--team', help='Team name to search for')
    parser.add_argument('--year', type=int, help='Specific year')
    parser.add_argument('--year-min', type=int, help='Minimum year')
    parser.add_argument('--year-max', type=int, help='Maximum year')
    parser.add_argument('--brand', help='Card manufacturer/brand')
    parser.add_argument('--condition', help='Card condition')
    parser.add_argument('--min-value', type=float, help='Minimum market value')
    parser.add_argument('--max-value', type=float, help='Maximum market value')
    parser.add_argument('--rookie-only', action='store_true', help='Show only rookie cards')
    parser.add_argument('--high-value', type=float, default=50, help='Show cards above this value (default: $50)')
    
    # Display options
    parser.add_argument('--detailed', action='store_true', help='Show detailed card information')
    parser.add_argument('--limit', type=int, help='Limit number of results')
    parser.add_argument('--sort', choices=['value', 'year', 'name', 'team', 'brand'], 
                       default='value', help='Sort results by field')
    parser.add_argument('--ascending', action='store_true', help='Sort in ascending order')
    
    # Export options
    parser.add_argument('--export', help='Export results to file')
    parser.add_argument('--format', choices=['csv', 'json'], default='csv', help='Export format')
    
    # Quick searches
    parser.add_argument('--top-value', type=int, help='Show top N most valuable cards')
    parser.add_argument('--vintage', action='store_true', help='Show vintage cards (1999 and earlier)')
    parser.add_argument('--modern', action='store_true', help='Show modern cards (2020+)')
    
    args = parser.parse_args()
    
    # Initialize searcher
    searcher = CardSearcher()
    
    # Handle quick searches
    if args.top_value:
        results = searcher.search_high_value_cards(0)
        results = searcher.sort_results(results, 'value', True)[:args.top_value]
        print(f"🏆 Top {args.top_value} Most Valuable Cards:")
    elif args.vintage:
        results = searcher.search_by_year(year_max=1999)
        results = searcher.sort_results(results, args.sort, not args.ascending)
        print("📼 Vintage Cards (1999 and earlier):")
    elif args.modern:
        results = searcher.search_by_year(year_min=2020)
        results = searcher.sort_results(results, args.sort, not args.ascending)
        print("🆕 Modern Cards (2020+):")
    elif args.high_value:
        results = searcher.search_high_value_cards(args.high_value)
        results = searcher.sort_results(results, 'value', True)
        print(f"💎 Cards valued at ${args.high_value}+ :")
    else:
        # Advanced search
        search_params = {
            'name': args.name,
            'team': args.team,
            'year': args.year,
            'year_min': args.year_min,
            'year_max': args.year_max,
            'brand': args.brand,
            'condition': args.condition,
            'min_value': args.min_value,
            'max_value': args.max_value,
            'rookie_only': args.rookie_only
        }
        
        # Remove None values
        search_params = {k: v for k, v in search_params.items() if v is not None}
        
        if not search_params:
            print("❓ No search criteria provided. Use --help for options.")
            print("\n🔥 Quick examples:")
            print("python card_search.py --name 'Tom Brady'")
            print("python card_search.py --team 'Cowboys' --min-value 10")
            print("python card_search.py --rookie-only --top-value 20")
            print("python card_search.py --vintage --detailed")
            return
        
        results = searcher.advanced_search(**search_params)
        results = searcher.sort_results(results, args.sort, not args.ascending)
    
    # Display results
    print(searcher.format_results(results, args.detailed, args.limit))
    
    # Export if requested
    if args.export:
        searcher.export_results(results, args.export, args.format)

if __name__ == "__main__":
    main()
