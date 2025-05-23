#!/usr/bin/env python3
"""
Generate Facebook Marketplace listings and social media posts for cards.
"""

import csv
import argparse
import json
import requests
import os
from datetime import datetime

class FacebookLister:
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
    
    def generate_marketplace_title(self, card):
        """Generate Facebook Marketplace listing title."""
        # Facebook Marketplace title should be concise and searchable
        title_parts = []
        
        # Year and player name are most important
        if card['year']:
            title_parts.append(str(card['year']))
        
        title_parts.append(card['name'])
        
        # Add team for recognition
        if card['team']:
            title_parts.append(card['team'])
        
        # Card type/brand
        if card['brand']:
            title_parts.append(card['brand'])
        
        # Rookie card is valuable info
        if card['flags'] and 'RC' in card['flags']:
            title_parts.append('Rookie Card')
        
        title = ' '.join(title_parts)
        
        # Keep under 100 characters for readability
        if len(title) > 100:
            title = title[:97] + '...'
        
        return title
    
    def generate_marketplace_description(self, card):
        """Generate Facebook Marketplace listing description."""
        desc = []
        
        # Opening line
        desc.append(f"🏈⚾ {card['name']} - {card['team']}")
        desc.append("")
        
        # Key details
        desc.append("📋 CARD DETAILS:")
        details = []
        details.append(f"• Player: {card['name']}")
        details.append(f"• Team: {card['team']}")
        details.append(f"• Year: {card['year']}")
        details.append(f"• Brand: {card['brand']}")
        if card['set']:
            details.append(f"• Set: {card['set']}")
        if card['number']:
            details.append(f"• Card #: {card['number']}")
        if card['condition']:
            details.append(f"• Condition: {card['condition']}")
        if card['flags'] and 'RC' in card['flags']:
            details.append(f"• 🌟 ROOKIE CARD 🌟")
        
        desc.extend(details)
        desc.append("")
        
        # Condition details
        if card['condition']:
            desc.append("💎 CONDITION:")
            condition_desc = {
                'Mint': 'Perfect condition - like it just came from the pack!',
                'Near Mint': 'Excellent condition with minimal wear',
                'Excellent': 'Great condition, well-preserved',
                'Very Good': 'Good condition with minor wear',
                'Fair': 'Moderate wear but still collectible',
                'Poor': 'Significant wear'
            }
            if card['condition'] in condition_desc:
                desc.append(f"• {condition_desc[card['condition']]}")
            desc.append("")
        
        # Value/pricing context
        if card['market_value'] > 0:
            desc.append(f"📊 Market Value: ${card['market_value']:.2f} (CollX)")
            desc.append("")
        
        # Selling points
        desc.append("✅ WHY BUY:")
        desc.append("• High-quality photos show exact card you'll receive")
        desc.append("• Smoke-free home")
        desc.append("• Careful packaging for safe shipping")
        desc.append("• Fast response to messages")
        desc.append("")
        
        # Call to action
        desc.append("💬 Message me with any questions!")
        desc.append("🚗 Local pickup available")
        desc.append("📦 Can ship if needed")
        desc.append("")
        desc.append("#SportCards #CollectibleCards #Trading Cards")
        
        # Add sport-specific hashtags
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
            desc.append("#NFL #Football")
        else:
            desc.append("#MLB #Baseball")
        
        if card['flags'] and 'RC' in card['flags']:
            desc.append("#RookieCard")
        
        return '\n'.join(desc)
    
    def generate_social_post(self, card, post_type='showcase'):
        """Generate social media post for Facebook sharing."""
        posts = {
            'showcase': self._generate_showcase_post(card),
            'new_addition': self._generate_new_addition_post(card),
            'throwback': self._generate_throwback_post(card),
            'collection_highlight': self._generate_collection_highlight_post(card)
        }
        
        return posts.get(post_type, posts['showcase'])
    
    def _generate_showcase_post(self, card):
        """Generate a card showcase post."""
        post = []
        
        # Eye-catching opener
        post.append(f"🔥 Check out this {card['name']} card! 🔥")
        post.append("")
        
        # Card info
        post.append(f"📅 {card['year']} {card['brand']}")
        post.append(f"🏆 {card['team']}")
        
        if card['flags'] and 'RC' in card['flags']:
            post.append("🌟 ROOKIE CARD! 🌟")
        
        if card['market_value'] > 50:
            post.append(f"💎 Valued at ${card['market_value']:.2f}")
        
        post.append("")
        
        # Personal touch
        post.append("Love finding gems like this in my collection! 📈")
        post.append("")
        post.append("What's your favorite card in your collection? 👇")
        post.append("")
        
        # Hashtags
        hashtags = ["#CardCollector", "#SportsCards", "#Trading Cards", "#Collecting"]
        
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
            hashtags.extend(["#NFL", "#Football"])
        else:
            hashtags.extend(["#MLB", "#Baseball"])
        
        post.append(' '.join(hashtags))
        
        return '\n'.join(post)
    
    def _generate_new_addition_post(self, card):
        """Generate a new addition to collection post."""
        post = []
        
        post.append(f"🆕 New addition to the collection! 🆕")
        post.append("")
        post.append(f"Just picked up this {card['year']} {card['name']} ({card['team']})!")
        
        if card['flags'] and 'RC' in card['flags']:
            post.append("Even better - it's a ROOKIE CARD! 🌟")
        
        post.append("")
        post.append(f"Really excited about this {card['brand']} card. The condition is fantastic!")
        post.append("")
        post.append("Always hunting for more cards like this. Drop a comment if you have any recommendations! 👇")
        post.append("")
        post.append("#NewPickup #CardCollection #AlwaysCollecting")
        
        return '\n'.join(post)
    
    def _generate_throwback_post(self, card):
        """Generate a throwback/vintage card post."""
        if card['year'] >= 2010:
            return self._generate_showcase_post(card)  # Fall back for modern cards
        
        post = []
        
        post.append(f"🕰️ Throwback Thursday! 🕰️")
        post.append("")
        post.append(f"Taking it back to {card['year']} with this {card['name']} card!")
        post.append("")
        post.append(f"📼 {card['brand']} was putting out some great sets back then.")
        post.append(f"🏆 {card['team']} had some amazing players!")
        post.append("")
        post.append("Love the vintage feel of these older cards. They just don't make them like this anymore! 📈")
        post.append("")
        post.append("What's your favorite vintage card? Share in the comments! 👇")
        post.append("")
        post.append("#ThrowbackThursday #VintageCards #RetroCollecting #SportsHistory")
        
        return '\n'.join(post)
    
    def _generate_collection_highlight_post(self, card):
        """Generate a collection highlight post."""
        post = []
        
        post.append(f"💎 Collection Highlight! 💎")
        post.append("")
        post.append(f"One of my favorite cards: {card['year']} {card['name']}")
        post.append("")
        
        # Why it's special
        reasons = []
        if card['flags'] and 'RC' in card['flags']:
            reasons.append("🌟 It's a rookie card")
        if card['market_value'] > 20:
            reasons.append(f"💰 Great investment potential (${card['market_value']:.2f} value)")
        if card['condition'] in ['Mint', 'Near Mint']:
            reasons.append(f"💎 Excellent condition ({card['condition']})")
        if card['year'] <= 1999:
            reasons.append("📼 Vintage appeal")
        
        if reasons:
            post.append("What makes this card special:")
            post.extend(reasons)
            post.append("")
        
        post.append("This is exactly why I love collecting - each card tells a story! 📚")
        post.append("")
        post.append("What card in your collection means the most to you? 💭")
        post.append("")
        post.append("#CollectionHighlight #CardStory #Collecting #SportsMemories")
        
        return '\n'.join(post)
    
    def suggest_marketplace_pricing(self, card):
        """Suggest Facebook Marketplace pricing."""
        market_value = card['market_value']
        
        if market_value == 0:
            return {
                'asking_price': 5.00,
                'quick_sale': 3.00,
                'note': 'Conservative pricing - market value unknown'
            }
        
        # Facebook Marketplace strategy - slightly below market for quick sales
        asking_price = market_value * 0.9  # 10% below market
        quick_sale = market_value * 0.75   # 25% below for quick sale
        
        return {
            'asking_price': round(max(asking_price, 2.00), 2),
            'quick_sale': round(max(quick_sale, 1.00), 2),
            'market_value': market_value,
            'note': 'Competitive Facebook Marketplace pricing'
        }
    
    def download_images(self, card, output_dir='facebook_images'):
        """Download card images for Facebook posts."""
        os.makedirs(output_dir, exist_ok=True)
        
        downloaded_images = []
        
        # Front image
        if card['front_image']:
            try:
                response = requests.get(card['front_image'])
                if response.status_code == 200:
                    filename = f"fb_{card['collx_id']}_front.jpg"
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
                    filename = f"fb_{card['collx_id']}_back.jpg"
                    filepath = os.path.join(output_dir, filename)
                    with open(filepath, 'wb') as f:
                        f.write(response.content)
                    downloaded_images.append(filepath)
            except Exception as e:
                print(f"Failed to download back image: {e}")
        
        return downloaded_images
    
    def generate_facebook_package(self, card):
        """Generate complete Facebook listing and social post package."""
        package = {
            'card_info': {
                'collx_id': card['collx_id'],
                'name': card['name'],
                'team': card['team'],
                'year': card['year'],
                'brand': card['brand'],
                'condition': card['condition'],
                'market_value': card['market_value']
            },
            'marketplace': {
                'title': self.generate_marketplace_title(card),
                'description': self.generate_marketplace_description(card),
                'pricing': self.suggest_marketplace_pricing(card)
            },
            'social_posts': {
                'showcase': self.generate_social_post(card, 'showcase'),
                'new_addition': self.generate_social_post(card, 'new_addition'),
                'throwback': self.generate_social_post(card, 'throwback'),
                'collection_highlight': self.generate_social_post(card, 'collection_highlight')
            },
            'images': {
                'front_url': card['front_image'],
                'back_url': card['back_image']
            },
            'generated_date': datetime.now().isoformat()
        }
        
        return package
    
    def export_facebook_package(self, package, output_file):
        """Export Facebook package to JSON file."""
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(package, f, indent=2, ensure_ascii=False)
        
        print(f"📁 Facebook package exported to {output_file}")

def main():
    parser = argparse.ArgumentParser(description='Generate Facebook listings and social posts')
    
    parser.add_argument('--card-id', help='CollX ID of specific card')
    parser.add_argument('--name', help='Player name to search')
    parser.add_argument('--min-value', type=float, default=3, help='Minimum value for listings')
    parser.add_argument('--limit', type=int, help='Limit number of cards')
    parser.add_argument('--output-dir', default='facebook_content', help='Output directory')
    parser.add_argument('--download-images', action='store_true', help='Download card images')
    parser.add_argument('--post-type', choices=['showcase', 'new_addition', 'throwback', 'collection_highlight'],
                       default='showcase', help='Type of social post to generate')
    parser.add_argument('--marketplace-only', action='store_true', help='Generate only marketplace listings')
    parser.add_argument('--social-only', action='store_true', help='Generate only social posts')
    parser.add_argument('--rookie-only', action='store_true', help='Only process rookie cards')
    parser.add_argument('--high-value', type=float, help='Only cards above this value')
    
    args = parser.parse_args()
    
    lister = FacebookLister()
    os.makedirs(args.output_dir, exist_ok=True)
    
    cards_to_process = []
    
    if args.card_id:
        # Process specific card
        card = lister.find_card_by_id(args.card_id)
        if card:
            cards_to_process = [card]
        else:
            print(f"❌ Card with ID {args.card_id} not found")
            return
    
    elif args.name:
        # Process cards by player name
        cards_to_process = lister.find_cards_by_name(args.name)
        if not cards_to_process:
            print(f"❌ No cards found for player: {args.name}")
            return
    
    else:
        # Batch processing
        cards_to_process = [card for card in lister.cards if card['market_value'] >= args.min_value]
        
        # Apply filters
        if args.rookie_only:
            cards_to_process = [card for card in cards_to_process 
                              if card['flags'] and 'RC' in card['flags']]
        
        if args.high_value:
            cards_to_process = [card for card in cards_to_process 
                              if card['market_value'] >= args.high_value]
        
        # Sort by value
        cards_to_process.sort(key=lambda x: x['market_value'], reverse=True)
        
        if args.limit:
            cards_to_process = cards_to_process[:args.limit]
    
    if not cards_to_process:
        print("❌ No cards found matching criteria")
        return
    
    print(f"📱 Creating Facebook content for {len(cards_to_process)} cards...")
    
    for i, card in enumerate(cards_to_process, 1):
        print(f"📄 {i}/{len(cards_to_process)}: {card['name']} ({card['team']}) - ${card['market_value']:.2f}")
        
        if args.social_only:
            # Generate only social post
            post = lister.generate_social_post(card, args.post_type)
            filename = f"social_{card['collx_id']}_{args.post_type}.txt"
            filepath = os.path.join(args.output_dir, filename)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(post)
            
            print(f"  📱 Social post saved: {filename}")
            
        elif args.marketplace_only:
            # Generate only marketplace listing
            title = lister.generate_marketplace_title(card)
            description = lister.generate_marketplace_description(card)
            pricing = lister.suggest_marketplace_pricing(card)
            
            filename = f"marketplace_{card['collx_id']}.txt"
            filepath = os.path.join(args.output_dir, filename)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(f"TITLE:\n{title}\n\n")
                f.write(f"DESCRIPTION:\n{description}\n\n")
                f.write(f"PRICING:\n")
                f.write(f"Asking Price: ${pricing['asking_price']:.2f}\n")
                f.write(f"Quick Sale: ${pricing['quick_sale']:.2f}\n")
                f.write(f"Market Value: ${pricing['market_value']:.2f}\n")
            
            print(f"  🛒 Marketplace listing saved: {filename}")
            print(f"     💰 Suggested price: ${pricing['asking_price']:.2f}")
            
        else:
            # Generate complete package
            package = lister.generate_facebook_package(card)
            
            filename = f"facebook_package_{card['collx_id']}.json"
            filepath = os.path.join(args.output_dir, filename)
            lister.export_facebook_package(package, filepath)
            
            # Also save individual text files for easy copy/paste
            # Marketplace listing
            mp_filename = f"marketplace_{card['collx_id']}.txt"
            mp_filepath = os.path.join(args.output_dir, mp_filename)
            with open(mp_filepath, 'w', encoding='utf-8') as f:
                f.write(f"TITLE:\n{package['marketplace']['title']}\n\n")
                f.write(f"DESCRIPTION:\n{package['marketplace']['description']}\n\n")
                f.write(f"ASKING PRICE: ${package['marketplace']['pricing']['asking_price']:.2f}\n")
            
            # Social post
            social_filename = f"social_{card['collx_id']}_{args.post_type}.txt"
            social_filepath = os.path.join(args.output_dir, social_filename)
            with open(social_filepath, 'w', encoding='utf-8') as f:
                f.write(package['social_posts'][args.post_type])
            
            print(f"  📦 Complete package saved: {filename}")
            print(f"  🛒 Marketplace text: {mp_filename}")
            print(f"  📱 Social post: {social_filename}")
            print(f"     💰 Suggested price: ${package['marketplace']['pricing']['asking_price']:.2f}")
        
        # Download images if requested
        if args.download_images:
            images = lister.download_images(card, os.path.join(args.output_dir, 'images'))
            print(f"  📸 Downloaded {len(images)} images")
        
        print()
    
    # Summary
    total_value = sum(card['market_value'] for card in cards_to_process)
    print(f"✅ Generated Facebook content for {len(cards_to_process)} cards")
    print(f"💎 Total collection value: ${total_value:.2f}")
    print(f"📁 Files saved to: {args.output_dir}")
    
    if args.download_images:
        print(f"📸 Images saved to: {args.output_dir}/images")
    
    print(f"\n📱 Quick tip: Use the text files for easy copy/paste to Facebook!")

if __name__ == "__main__":
    main()
