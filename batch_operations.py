#!/usr/bin/env python3
"""
Batch operations for managing multiple cards at once.
"""

import csv
import argparse
import os
import json
from datetime import datetime
from card_search import CardSearcher
from ebay_lister import eBayLister
from facebook_lister import FacebookLister

class BatchOperations:
    def __init__(self, csv_file='download_RecoveredTreasures-2025-05-14-071313.csv'):
        self.csv_file = csv_file
        self.searcher = CardSearcher(csv_file)
        self.ebay_lister = eBayLister(csv_file)
        self.facebook_lister = FacebookLister(csv_file)
    
    def select_cards_for_sale(self, min_value=10, max_cards=50, exclude_favorites=True):
        """Select cards that are good candidates for selling."""
        candidates = []
        
        for card in self.searcher.cards:
            # Skip cards below minimum value
            if card['market_value'] < min_value:
                continue
            
            # Skip favorites (high-value rookies, vintage stars, etc.)
            if exclude_favorites:
                if card['market_value'] > 500:  # Very high value - might want to keep
                    continue
                if card['flags'] and 'RC' in card['flags'] and card['market_value'] > 100:
                    continue  # Valuable rookie cards
                if card['year'] <= 1980 and card['market_value'] > 50:
                    continue  # Vintage cards
            
            # Good condition cards sell better
            if card['condition'] in ['Mint', 'Near Mint', 'Excellent']:
                candidates.append(card)
        
        # Sort by value and limit results
        candidates.sort(key=lambda x: x['market_value'], reverse=True)
        return candidates[:max_cards]
    
    def create_sale_batch(self, cards, output_dir='sale_batch', platforms=['ebay', 'facebook']):
        """Create listings for multiple platforms."""
        os.makedirs(output_dir, exist_ok=True)
        
        batch_info = {
            'created_date': datetime.now().isoformat(),
            'total_cards': len(cards),
            'total_value': sum(card['market_value'] for card in cards),
            'platforms': platforms,
            'cards': []
        }
        
        print(f"📦 Creating sale batch for {len(cards)} cards...")
        
        for i, card in enumerate(cards, 1):
            print(f"📄 {i}/{len(cards)}: {card['name']} - ${card['market_value']:.2f}")
            
            card_batch_info = {
                'collx_id': card['collx_id'],
                'name': card['name'],
                'team': card['team'],
                'market_value': card['market_value'],
                'files_created': []
            }
            
            # Create eBay listing
            if 'ebay' in platforms:
                ebay_listing = self.ebay_lister.generate_listing(card)
                ebay_file = os.path.join(output_dir, f"ebay_{card['collx_id']}.json")
                self.ebay_lister.export_listing(ebay_listing, ebay_file)
                card_batch_info['files_created'].append(ebay_file)
            
            # Create Facebook listing
            if 'facebook' in platforms:
                fb_package = self.facebook_lister.generate_facebook_package(card)
                fb_file = os.path.join(output_dir, f"facebook_{card['collx_id']}.json")
                self.facebook_lister.export_facebook_package(fb_package, fb_file)
                card_batch_info['files_created'].append(fb_file)
            
            batch_info['cards'].append(card_batch_info)
        
        # Save batch summary
        batch_file = os.path.join(output_dir, 'batch_summary.json')
        with open(batch_file, 'w', encoding='utf-8') as f:
            json.dump(batch_info, f, indent=2, ensure_ascii=False)
        
        return batch_info
    
    def download_all_images(self, cards, output_dir='batch_images'):
        """Download images for multiple cards."""
        os.makedirs(output_dir, exist_ok=True)
        
        downloaded_count = 0
        failed_count = 0
        
        print(f"📸 Downloading images for {len(cards)} cards...")
        
        for i, card in enumerate(cards, 1):
            print(f"📷 {i}/{len(cards)}: {card['name']}")
            
            try:
                # Download for eBay
                ebay_images = self.ebay_lister.download_images(card, os.path.join(output_dir, 'ebay'))
                # Download for Facebook
                fb_images = self.facebook_lister.download_images(card, os.path.join(output_dir, 'facebook'))
                
                total_images = len(ebay_images) + len(fb_images)
                downloaded_count += total_images
                print(f"  ✅ Downloaded {total_images} images")
                
            except Exception as e:
                failed_count += 1
                print(f"  ❌ Failed: {e}")
        
        print(f"\n📊 Image download summary:")
        print(f"  ✅ Successfully downloaded: {downloaded_count} images")
        print(f"  ❌ Failed downloads: {failed_count} cards")
        
        return downloaded_count, failed_count
    
    def generate_inventory_report(self, output_file='inventory_report.csv'):
        """Generate a comprehensive inventory report."""
        print("📋 Generating inventory report...")
        
        # Prepare enhanced data
        enhanced_cards = []
        
        for card in self.searcher.cards:
            enhanced_card = card.copy()
            
            # Add calculated fields
            enhanced_card['is_rookie'] = 'Yes' if card['flags'] and 'RC' in card['flags'] else 'No'
            enhanced_card['is_vintage'] = 'Yes' if card['year'] <= 1999 else 'No'
            enhanced_card['is_modern'] = 'Yes' if card['year'] >= 2020 else 'No'
            enhanced_card['value_category'] = self._categorize_value(card['market_value'])
            enhanced_card['sport'] = self._determine_sport(card['team'])
            
            enhanced_cards.append(enhanced_card)
        
        # Sort by value
        enhanced_cards.sort(key=lambda x: x['market_value'], reverse=True)
        
        # Write to CSV
        if enhanced_cards:
            fieldnames = list(enhanced_cards[0].keys())
            
            with open(output_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(enhanced_cards)
        
        print(f"📁 Inventory report saved: {output_file}")
        return output_file
    
    def _categorize_value(self, value):
        """Categorize card value."""
        if value >= 100:
            return 'High Value ($100+)'
        elif value >= 20:
            return 'Medium Value ($20-$99)'
        elif value >= 5:
            return 'Low Value ($5-$19)'
        else:
            return 'Minimal Value (<$5)'
    
    def _determine_sport(self, team):
        """Determine sport based on team."""
        football_teams = {
            'Kansas City Chiefs', 'Houston Texans', 'Minnesota Vikings', 'New England Patriots',
            'Carolina Panthers', 'Los Angeles Rams', 'New York Giants', 'Baltimore Ravens',
            'New York Jets', 'Detroit Lions', 'Tampa Bay Buccaneers', 'Pittsburgh Steelers',
            'Jacksonville Jaguars', 'Washington Redskins', 'Dallas Cowboys', 'Indianapolis Colts',
            'Green Bay Packers', 'Philadelphia Eagles', 'Miami Dolphins', 'Buffalo Bills',
            'Oakland Raiders', 'Cleveland Browns', 'Seattle Seahawks', 'Arizona Cardinals',
            'Los Angeles Raiders', 'Phoenix Cardinals', 'San Francisco 49ers', 'Denver Broncos'
        }
        
        return 'Football' if team in football_teams else 'Baseball'
    
    def create_pricing_strategy(self, cards, market_factor=0.85):
        """Create pricing strategy for multiple cards."""
        strategy = {
            'created_date': datetime.now().isoformat(),
            'market_factor': market_factor,
            'total_cards': len(cards),
            'pricing_tiers': {},
            'cards': []
        }
        
        for card in cards:
            market_value = card['market_value']
            
            # Calculate pricing
            asking_price = market_value * market_factor
            quick_sale = market_value * 0.75
            minimum_price = market_value * 0.6
            
            card_pricing = {
                'collx_id': card['collx_id'],
                'name': card['name'],
                'market_value': market_value,
                'asking_price': round(asking_price, 2),
                'quick_sale': round(quick_sale, 2),
                'minimum_price': round(minimum_price, 2),
                'tier': self._categorize_value(market_value)
            }
            
            strategy['cards'].append(card_pricing)
        
        # Group by tiers
        tiers = {}
        for card in strategy['cards']:
            tier = card['tier']
            if tier not in tiers:
                tiers[tier] = []
            tiers[tier].append(card)
        
        strategy['pricing_tiers'] = tiers
        
        return strategy
    
    def export_for_accounting(self, cards, output_file='collection_accounting.csv'):
        """Export collection data for accounting/tax purposes."""
        print("💼 Generating accounting export...")
        
        accounting_data = []
        
        for card in cards:
            record = {
                'Date_Acquired': card.get('added', ''),
                'Item_Description': f"{card['year']} {card['brand']} {card['name']} #{card['number']}",
                'Player_Name': card['name'],
                'Team': card['team'],
                'Year': card['year'],
                'Brand_Set': f"{card['brand']} {card['set']}",
                'Card_Number': card['number'],
                'Condition': card['condition'],
                'Current_Market_Value': card['market_value'],
                'Category': 'Sports Trading Card',
                'Sport': self._determine_sport(card['team']),
                'Is_Rookie_Card': 'Yes' if card['flags'] and 'RC' in card['flags'] else 'No',
                'CollX_ID': card['collx_id'],
                'Image_URL': card['front_image']
            }
            
            accounting_data.append(record)
        
        # Sort by value for easier review
        accounting_data.sort(key=lambda x: x['Current_Market_Value'], reverse=True)
        
        # Write to CSV
        if accounting_data:
            fieldnames = list(accounting_data[0].keys())
            
            with open(output_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(accounting_data)
        
        print(f"📊 Accounting export saved: {output_file}")
        return output_file

def main():
    parser = argparse.ArgumentParser(description='Batch operations for card collection')
    
    # Operation types
    parser.add_argument('--operation', required=True, 
                       choices=['sale-batch', 'download-images', 'inventory-report', 
                               'pricing-strategy', 'accounting-export'],
                       help='Type of batch operation')
    
    # Selection criteria
    parser.add_argument('--min-value', type=float, default=10, help='Minimum card value')
    parser.add_argument('--max-cards', type=int, default=50, help='Maximum number of cards')
    parser.add_argument('--output-dir', default='batch_output', help='Output directory')
    parser.add_argument('--platforms', nargs='+', choices=['ebay', 'facebook'], 
                       default=['ebay', 'facebook'], help='Platforms for listings')
    
    # Filters
    parser.add_argument('--rookie-only', action='store_true', help='Only process rookie cards')
    parser.add_argument('--high-value', type=float, help='Only cards above this value')
    parser.add_argument('--team', help='Filter by team')
    parser.add_argument('--condition', help='Filter by condition')
    parser.add_argument('--exclude-favorites', action='store_true', default=True,
                       help='Exclude high-value cards that might be favorites')
    
    args = parser.parse_args()
    
    batch_ops = BatchOperations()
    os.makedirs(args.output_dir, exist_ok=True)
    
    # Get cards based on operation
    if args.operation == 'sale-batch':
        cards = batch_ops.select_cards_for_sale(
            min_value=args.min_value,
            max_cards=args.max_cards,
            exclude_favorites=args.exclude_favorites
        )
    else:
        # Use search criteria for other operations
        search_params = {}
        if args.rookie_only:
            search_params['rookie_only'] = True
        if args.high_value:
            search_params['min_value'] = args.high_value
        if args.team:
            search_params['team'] = args.team
        if args.condition:
            search_params['condition'] = args.condition
        
        if search_params:
            cards = batch_ops.searcher.advanced_search(**search_params)
        else:
            cards = batch_ops.searcher.cards
        
        # Apply value filter
        cards = [card for card in cards if card['market_value'] >= args.min_value]
        
        # Limit results
        if args.max_cards:
            cards = sorted(cards, key=lambda x: x['market_value'], reverse=True)[:args.max_cards]
    
    if not cards:
        print("❌ No cards found matching criteria")
        return
    
    print(f"🎯 Selected {len(cards)} cards for {args.operation}")
    total_value = sum(card['market_value'] for card in cards)
    print(f"💎 Total value: ${total_value:.2f}")
    print()
    
    # Execute operation
    if args.operation == 'sale-batch':
        batch_info = batch_ops.create_sale_batch(cards, args.output_dir, args.platforms)
        print(f"\n✅ Sale batch created successfully!")
        print(f"📁 Files saved to: {args.output_dir}")
        print(f"📦 Created listings for {batch_info['total_cards']} cards")
        print(f"💰 Total potential revenue: ${batch_info['total_value']:.2f}")
        
    elif args.operation == 'download-images':
        downloaded, failed = batch_ops.download_all_images(cards, args.output_dir)
        print(f"\n✅ Image download complete!")
        print(f"📸 Downloaded: {downloaded} images")
        if failed > 0:
            print(f"❌ Failed: {failed} cards")
        
    elif args.operation == 'inventory-report':
        report_file = os.path.join(args.output_dir, 'inventory_report.csv')
        batch_ops.generate_inventory_report(report_file)
        print(f"\n✅ Inventory report generated!")
        print(f"📋 Report saved to: {report_file}")
        
    elif args.operation == 'pricing-strategy':
        strategy = batch_ops.create_pricing_strategy(cards)
        strategy_file = os.path.join(args.output_dir, 'pricing_strategy.json')
        
        with open(strategy_file, 'w', encoding='utf-8') as f:
            json.dump(strategy, f, indent=2, ensure_ascii=False)
        
        print(f"\n✅ Pricing strategy created!")
        print(f"📊 Strategy saved to: {strategy_file}")
        print(f"💡 Pricing tiers:")
        for tier, tier_cards in strategy['pricing_tiers'].items():
            print(f"  {tier}: {len(tier_cards)} cards")
        
    elif args.operation == 'accounting-export':
        accounting_file = os.path.join(args.output_dir, 'accounting_export.csv')
        batch_ops.export_for_accounting(cards, accounting_file)
        print(f"\n✅ Accounting export created!")
        print(f"💼 Export saved to: {accounting_file}")
    
    print(f"\n📁 All files saved to: {args.output_dir}")

if __name__ == "__main__":
    main()
