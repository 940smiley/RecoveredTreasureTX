#!/usr/bin/env python3
"""
Generate eBay listings from card collection data.
"""

import csv
import argparse
import json
import requests
from urllib.parse import urlparse
import os
import re

class eBayLister:
    def __init__(self, csv_file='download_RecoveredTreasures-2025-05-14-071313.csv'):
        self.csv_file = csv_file
        self.cards = []
        self.load_data()
    
    def load_data(self):
        """Load card data from CSV."""
        with open(self.csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    row['market_value'] = float(row['market_value']) if row['market_value'] else 0
                except:
                    row['market_value'] = 0
                
                try:
                    row['year'] = int(row['year']) if row['year'] else 0
                except:
                    row['year'] = 0
                
                self.cards.append(row)
    
    def find_card_by_id(self, collx_id):
        """Find a card by CollX ID."""
        for card in self.cards:
            if card['collx_id'] == str(collx_id):
                return card
        return None
    
    def find_cards_by_name(self, name):
        """Find cards by player name."""
        results = []
        name_lower = name.lower()
        for card in self.cards:
            if name_lower in card['name'].lower():
                results.append(card)
        return results
    
    def generate_title(self, card):
        """Generate eBay listing title."""
        # eBay title limit is 80 characters
        title_parts = []
        
        # Year
        if card['year']:
            title_parts.append(str(card['year']))
        
        # Brand and Set
        if card['brand']:
            title_parts.append(card['brand'])
        if card['set'] and card['set'] != card['brand']:
            # Shorten set name if needed
            set_name = card['set'].replace(str(card['year']), '').replace(card['brand'], '').strip()
            if set_name:
                title_parts.append(set_name)
        
        # Player name
        title_parts.append(card['name'])
        
        # Card number
        if card['number']:
            title_parts.append(f"#{card['number']}")
        
        # Rookie card flag
        if card['flags'] and 'RC' in card['flags']:
            title_parts.append('RC')
        
        # Team
        if card['team']:
            title_parts.append(card['team'])
        
        title = ' '.join(title_parts)
        
        # Truncate if too long
        if len(title) > 80:
            title = title[:77] + '...'
        
        return title
    
    def generate_description(self, card):
        """Generate detailed eBay listing description."""
        desc = []
        
        # Header
        desc.append(f"<h2>{card['name']} - {card['team']}</h2>")
        
        # Card details table
        desc.append("<table border='1' cellpadding='5' style='border-collapse: collapse;'>")
        desc.append("<tr><td><strong>Player:</strong></td><td>{}</td></tr>".format(card['name']))
        desc.append("<tr><td><strong>Team:</strong></td><td>{}</td></tr>".format(card['team']))
        desc.append("<tr><td><strong>Year:</strong></td><td>{}</td></tr>".format(card['year']))
        desc.append("<tr><td><strong>Brand:</strong></td><td>{}</td></tr>".format(card['brand']))
        desc.append("<tr><td><strong>Set:</strong></td><td>{}</td></tr>".format(card['set']))
        desc.append("<tr><td><strong>Card Number:</strong></td><td>{}</td></tr>".format(card['number']))
        
        if card['condition']:
            desc.append("<tr><td><strong>Condition:</strong></td><td>{}</td></tr>".format(card['condition']))
        
        if card['flags']:
            desc.append("<tr><td><strong>Special:</strong></td><td>{}</td></tr>".format(card['flags']))
        
        desc.append("</table>")
        
        # Condition details
        desc.append("<h3>Condition Details</h3>")
        if card['condition']:
            condition_details = {
                'Mint': 'Perfect condition with sharp corners, perfect centering, and no visible flaws.',
                'Near Mint': 'Excellent condition with very minor flaws that are barely noticeable.',
                'Excellent': 'Great condition with minor wear but still very collectible.',
                'Very Good': 'Good condition with noticeable wear but no major damage.',
                'Fair': 'Moderate wear with some creasing or edge wear.',
                'Poor': 'Significant wear, major flaws, or damage.'
            }
            desc.append(f"<p><strong>Condition: {card['condition']}</strong></p>")
            if card['condition'] in condition_details:
                desc.append(f"<p>{condition_details[card['condition']]}</p>")
        else:
            desc.append("<p>Please see photos for condition assessment.</p>")
        
        # Images note
        desc.append("<h3>Photos</h3>")
        desc.append("<p>High-resolution photos show the actual card you will receive. Please examine all photos carefully.</p>")
        
        # Shipping and handling
        desc.append("<h3>Shipping & Handling</h3>")
        desc.append("<ul>")
        desc.append("<li>Card will be shipped in a protective sleeve and toploader</li>")
        desc.append("<li>Orders over $20 will be shipped in a bubble mailer</li>")
        desc.append("<li>Orders over $100 will be shipped with tracking and insurance</li>")
        desc.append("<li>Fast and secure shipping with careful packaging</li>")
        desc.append("</ul>")
        
        # Return policy
        desc.append("<h3>Returns</h3>")
        desc.append("<p>30-day return policy. Item must be returned in same condition as received.</p>")
        
        # Footer
        desc.append("<hr>")
        desc.append("<p><em>Thank you for viewing this listing! Check out my other cards and collectibles.</em></p>")
        desc.append("<p><em>All items are from a smoke-free environment.</em></p>")
        
        return '\n'.join(desc)
    
    def suggest_pricing(self, card):
        """Suggest pricing based on market value."""
        market_value = card['market_value']
        
        if market_value == 0:
            return {
                'starting_bid': 0.99,
                'buy_it_now': 4.99,
                'reserve': None,
                'note': 'Market value unknown - conservative pricing suggested'
            }
        
        # Conservative pricing strategy
        starting_bid = max(0.99, market_value * 0.7)  # 70% of market value
        buy_it_now = market_value * 1.2  # 20% above market value
        reserve = market_value * 0.9 if market_value > 20 else None  # Reserve for higher value items
        
        return {
            'starting_bid': round(starting_bid, 2),
            'buy_it_now': round(buy_it_now, 2),
            'reserve': round(reserve, 2) if reserve else None,
            'market_value': market_value,
            'note': 'Pricing based on CollX market data'
        }
    
    def download_images(self, card, output_dir='listing_images'):
        """Download card images for listing."""
        os.makedirs(output_dir, exist_ok=True)
        
        downloaded_images = []
        
        # Front image
        if card['front_image']:
            try:
                response = requests.get(card['front_image'])
                if response.status_code == 200:
                    filename = f"{card['collx_id']}_front.jpg"
                    filepath = os.path.join(output_dir, filename)
                    with open(filepath, 'wb') as f:
                        f.write(response.content)
                    downloaded_images.append(filepath)
            except Exception as e:
                print(f"Failed to download front image: {e}")
        
        # Back image
        if card['back_image']:
            try:
                response = requests.get(card['back_image'])
                if response.status_code == 200:
                    filename = f"{card['collx_id']}_back.jpg"
                    filepath = os.path.join(output_dir, filename)
                    with open(filepath, 'wb') as f:
                        f.write(response.content)
                    downloaded_images.append(filepath)
            except Exception as e:
                print(f"Failed to download back image: {e}")
        
        return downloaded_images
    
    def generate_listing(self, card):
        """Generate complete eBay listing information."""
        listing = {
            'card_info': {
                'collx_id': card['collx_id'],
                'name': card['name'],
                'team': card['team'],
                'year': card['year'],
                'brand': card['brand'],
                'set': card['set'],
                'number': card['number'],
                'condition': card['condition'],
                'flags': card['flags']
            },
            'title': self.generate_title(card),
            'description': self.generate_description(card),
            'pricing': self.suggest_pricing(card),
            'category': self.suggest_category(card),
            'images': {
                'front_url': card['front_image'],
                'back_url': card['back_image']
            }
        }
        
        return listing
    
    def suggest_category(self, card):
        """Suggest eBay category."""
        # Basic sport detection
        football_teams = {
            'Kansas City Chiefs', 'Houston Texans', 'Minnesota Vikings', 'New England Patriots',
            'Carolina Panthers', 'Los Angeles Rams', 'New York Giants', 'Baltimore Ravens',
            'New York Jets', 'Detroit Lions', 'Tampa Bay Buccaneers', 'Pittsburgh Steelers',
            'Jacksonville Jaguars', 'Washington Redskins', 'Dallas Cowboys', 'Indianapolis Colts',
            'Green Bay Packers', 'Philadelphia Eagles', 'Miami Dolphins', 'Buffalo Bills',
            'Oakland Raiders', 'Cleveland Browns', 'Seattle Seahawks', 'Arizona Cardinals',
            'Los Angeles Raiders', 'Phoenix Cardinals', 'San Francisco 49ers', 'Denver Broncos'
        }
        
        if card['team'] in football_teams:
            if card['flags'] and 'RC' in card['flags']:
                return "Sports Mem, Cards & Fan Shop > Sports Trading Cards > Football Cards > NFL > Rookie"
            else:
                return "Sports Mem, Cards & Fan Shop > Sports Trading Cards > Football Cards > NFL"
        else:
            if card['flags'] and 'RC' in card['flags']:
                return "Sports Mem, Cards & Fan Shop > Sports Trading Cards > Baseball Cards > MLB > Rookie"
            else:
                return "Sports Mem, Cards & Fan Shop > Sports Trading Cards > Baseball Cards > MLB"
    
    def export_listing(self, listing, output_file):
        """Export listing data to JSON file."""
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(listing, f, indent=2, ensure_ascii=False)
        
        print(f"📁 Listing exported to {output_file}")
    
    def create_csv_import(self, listings, output_file):
        """Create CSV file for eBay bulk listing import."""
        # eBay CSV headers (simplified)
        headers = [
            'Title', 'Description', 'StartPrice', 'BuyItNowPrice', 'ReservePrice',
            'Category', 'Condition', 'PicURL', 'Quantity', 'Format', 'Duration'
        ]
        
        with open(output_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(headers)
            
            for listing in listings:
                pricing = listing['pricing']
                row = [
                    listing['title'],
                    listing['description'].replace('\n', '<br>'),
                    pricing['starting_bid'],
                    pricing['buy_it_now'],
                    pricing['reserve'] or '',
                    listing['category'],
                    listing['card_info']['condition'] or 'Used',
                    listing['images']['front_url'],
                    1,  # Quantity
                    'Auction',  # Format
                    7  # Duration in days
                ]
                writer.writerow(row)
        
        print(f"📊 eBay import CSV created: {output_file}")

def main():
    parser = argparse.ArgumentParser(description='Generate eBay listings for cards')
    
    parser.add_argument('--card-id', help='CollX ID of specific card to list')
    parser.add_argument('--name', help='Player name to search and list')
    parser.add_argument('--min-value', type=float, default=5, help='Minimum value for batch listing')
    parser.add_argument('--limit', type=int, help='Limit number of cards for batch listing')
    parser.add_argument('--output-dir', default='ebay_listings', help='Output directory')
    parser.add_argument('--download-images', action='store_true', help='Download card images')
    parser.add_argument('--create-csv', action='store_true', help='Create eBay import CSV')
    parser.add_argument('--condition', help='Filter by condition (e.g., "Mint", "Near Mint")')
    parser.add_argument('--rookie-only', action='store_true', help='Only list rookie cards')
    
    args = parser.parse_args()
    
    lister = eBayLister()
    os.makedirs(args.output_dir, exist_ok=True)
    
    cards_to_list = []
    
    if args.card_id:
        # List specific card
        card = lister.find_card_by_id(args.card_id)
        if card:
            cards_to_list = [card]
        else:
            print(f"❌ Card with ID {args.card_id} not found")
            return
    
    elif args.name:
        # List cards by player name
        cards_to_list = lister.find_cards_by_name(args.name)
        if not cards_to_list:
            print(f"❌ No cards found for player: {args.name}")
            return
    
    else:
        # Batch listing - find valuable cards
        cards_to_list = [card for card in lister.cards if card['market_value'] >= args.min_value]
        
        # Apply filters
        if args.condition:
            cards_to_list = [card for card in cards_to_list 
                           if card['condition'] and args.condition.lower() in card['condition'].lower()]
        
        if args.rookie_only:
            cards_to_list = [card for card in cards_to_list 
                           if card['flags'] and 'RC' in card['flags']]
        
        # Sort by value (highest first)
        cards_to_list.sort(key=lambda x: x['market_value'], reverse=True)
        
        if args.limit:
            cards_to_list = cards_to_list[:args.limit]
    
    if not cards_to_list:
        print("❌ No cards found matching criteria")
        return
    
    print(f"🎯 Creating listings for {len(cards_to_list)} cards...")
    
    listings = []
    
    for i, card in enumerate(cards_to_list, 1):
        print(f"📄 {i}/{len(cards_to_list)}: {card['name']} ({card['team']}) - ${card['market_value']:.2f}")
        
        listing = lister.generate_listing(card)
        listings.append(listing)
        
        # Export individual listing
        filename = f"listing_{card['collx_id']}.json"
        filepath = os.path.join(args.output_dir, filename)
        lister.export_listing(listing, filepath)
        
        # Download images if requested
        if args.download_images:
            images = lister.download_images(card, os.path.join(args.output_dir, 'images'))
            print(f"  📸 Downloaded {len(images)} images")
        
        # Display pricing suggestion
        pricing = listing['pricing']
        print(f"  💰 Suggested pricing: Start ${pricing['starting_bid']}, BIN ${pricing['buy_it_now']}")
        if pricing['reserve']:
            print(f"     Reserve: ${pricing['reserve']}")
        print()
    
    # Create bulk import CSV if requested
    if args.create_csv:
        csv_file = os.path.join(args.output_dir, 'ebay_import.csv')
        lister.create_csv_import(listings, csv_file)
    
    # Summary
    total_value = sum(card['market_value'] for card in cards_to_list)
    print(f"✅ Generated {len(listings)} listings")
    print(f"💎 Total collection value: ${total_value:.2f}")
    print(f"📁 Files saved to: {args.output_dir}")
    
    if args.download_images:
        print(f"📸 Images saved to: {args.output_dir}/images")

if __name__ == "__main__":
    main()
