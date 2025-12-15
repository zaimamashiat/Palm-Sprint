"""
Kenney Pixel Platformer Asset Scanner
Scans the asset pack and shows what's available for game design
"""

import os
from pathlib import Path

ASSET_PATH = r"C:\Users\zaima.nabi\Downloads\kenney_pixel-platformer"

def scan_assets(base_path):
    """Scan and categorize all available assets"""
    
    assets = {
        'characters': [],
        'tiles': [],
        'items': [],
        'enemies': [],
        'backgrounds': [],
        'other': []
    }
    
    print("="*70)
    print("SCANNING KENNEY PIXEL PLATFORMER ASSET PACK")
    print("="*70)
    
    if not os.path.exists(base_path):
        print(f"\n❌ ERROR: Path not found: {base_path}")
        print("\nPlease check the path and try again.")
        return None
    
    # Scan all files
    all_files = []
    for root, dirs, files in os.walk(base_path):
        for file in files:
            if file.endswith(('.png', '.jpg', '.jpeg')):
                rel_path = os.path.relpath(os.path.join(root, file), base_path)
                all_files.append((file.lower(), rel_path))
    
    print(f"\n✓ Found {len(all_files)} image files")
    print("\n" + "="*70)
    print("CATEGORIZING ASSETS")
    print("="*70)
    
    # Categorize files
    for filename_lower, rel_path in all_files:
        # Characters
        if any(word in filename_lower for word in ['character', 'player', 'hero', 'alien', 'zombie', 'person']):
            assets['characters'].append(rel_path)
        # Enemies
        elif any(word in filename_lower for word in ['enemy', 'monster', 'slime', 'fly', 'bee', 'saw', 'spike']):
            assets['enemies'].append(rel_path)
        # Items/Collectibles
        elif any(word in filename_lower for word in ['coin', 'gem', 'star', 'key', 'item', 'pickup', 'cherry', 'heart']):
            assets['items'].append(rel_path)
        # Tiles
        elif any(word in filename_lower for word in ['tile', 'ground', 'grass', 'stone', 'brick', 'platform', 'block']):
            assets['tiles'].append(rel_path)
        # Backgrounds
        elif any(word in filename_lower for word in ['background', 'bg', 'sky', 'cloud', 'hill', 'mountain']):
            assets['backgrounds'].append(rel_path)
        else:
            assets['other'].append(rel_path)
    
    # Print results
    print(f"\n📦 CHARACTERS: {len(assets['characters'])} files")
    for item in sorted(assets['characters'])[:10]:  # Show first 10
        print(f"   • {item}")
    if len(assets['characters']) > 10:
        print(f"   ... and {len(assets['characters']) - 10} more")
    
    print(f"\n👾 ENEMIES/OBSTACLES: {len(assets['enemies'])} files")
    for item in sorted(assets['enemies'])[:10]:
        print(f"   • {item}")
    if len(assets['enemies']) > 10:
        print(f"   ... and {len(assets['enemies']) - 10} more")
    
    print(f"\n💎 ITEMS/COLLECTIBLES: {len(assets['items'])} files")
    for item in sorted(assets['items'])[:10]:
        print(f"   • {item}")
    if len(assets['items']) > 10:
        print(f"   ... and {len(assets['items']) - 10} more")
    
    print(f"\n🧱 TILES/PLATFORMS: {len(assets['tiles'])} files")
    for item in sorted(assets['tiles'])[:10]:
        print(f"   • {item}")
    if len(assets['tiles']) > 10:
        print(f"   ... and {len(assets['tiles']) - 10} more")
    
    print(f"\n🌄 BACKGROUNDS: {len(assets['backgrounds'])} files")
    for item in sorted(assets['backgrounds'])[:10]:
        print(f"   • {item}")
    if len(assets['backgrounds']) > 10:
        print(f"   ... and {len(assets['backgrounds']) - 10} more")
    
    print(f"\n📁 OTHER: {len(assets['other'])} files")
    for item in sorted(assets['other'])[:5]:
        print(f"   • {item}")
    if len(assets['other']) > 5:
        print(f"   ... and {len(assets['other']) - 5} more")
    
    print("\n" + "="*70)
    print("GAME DESIGN RECOMMENDATIONS")
    print("="*70)
    
    # Suggest game design based on assets
    print("\nBased on available assets, I recommend:")
    print("\n🎮 GAME STYLE:")
    if len(assets['characters']) > 0:
        print("   ✓ Use available character sprites for the player")
    if len(assets['enemies']) > 5:
        print("   ✓ Multiple enemy/obstacle types available")
    if len(assets['items']) > 0:
        print("   ✓ Collectible items found (coins, gems, etc.)")
    if len(assets['backgrounds']) > 0:
        print("   ✓ Background layers available for parallax effect")
    
    print("\n🎨 VISUAL THEME:")
    print("   • Pixel art style (retro/indie aesthetic)")
    print("   • Colorful and vibrant")
    print("   • Perfect for runner/platformer game")
    
    print("\n💡 SUGGESTED FEATURES:")
    print("   1. Use character sprites with walk/jump animations")
    print("   2. Add variety with different enemy types")
    print("   3. Collect items (coins/gems) for score")
    print("   4. Use tile sets for ground and platforms")
    print("   5. Layer backgrounds for depth")
    
    # Save detailed list to file
    output_file = os.path.join(ASSET_PATH, "asset_inventory.txt")
    try:
        with open(output_file, 'w') as f:
            f.write("KENNEY PIXEL PLATFORMER ASSET INVENTORY\n")
            f.write("="*70 + "\n\n")
            
            for category, files in assets.items():
                f.write(f"\n{category.upper()} ({len(files)} files):\n")
                f.write("-"*70 + "\n")
                for file in sorted(files):
                    f.write(f"{file}\n")
        
        print(f"\n✓ Detailed inventory saved to: {output_file}")
    except:
        pass
    
    return assets

def suggest_specific_assets(assets):
    """Suggest specific assets for the runner game"""
    print("\n" + "="*70)
    print("SPECIFIC ASSET RECOMMENDATIONS FOR YOUR RUNNER GAME")
    print("="*70)
    
    # Find best character
    print("\n🏃 PLAYER CHARACTER:")
    character_options = []
    for char in assets['characters']:
        if 'idle' in char.lower() or 'stand' in char.lower():
            character_options.append(char)
    
    if character_options:
        print(f"   Recommended: {character_options[0]}")
        print("   Look for matching: walk, jump, duck animations")
    else:
        print(f"   Use: {assets['characters'][0] if assets['characters'] else 'Not found'}")
    
    # Find obstacles
    print("\n🚧 OBSTACLES:")
    obstacle_options = [e for e in assets['enemies'] if 'spike' in e.lower() or 'saw' in e.lower() or 'block' in e.lower()]
    for i, obs in enumerate(obstacle_options[:3], 1):
        print(f"   {i}. {obs}")
    
    # Find collectibles
    print("\n💰 COLLECTIBLES:")
    collectible_options = [item for item in assets['items'] if 'coin' in item.lower() or 'gem' in item.lower() or 'star' in item.lower()]
    for i, col in enumerate(collectible_options[:3], 1):
        print(f"   {i}. {col}")
    
    # Find ground tiles
    print("\n🌍 GROUND/PLATFORMS:")
    tile_options = [t for t in assets['tiles'] if 'ground' in t.lower() or 'grass' in t.lower()]
    for i, tile in enumerate(tile_options[:3], 1):
        print(f"   {i}. {tile}")
    
    print("\n" + "="*70)

if __name__ == "__main__":
    assets = scan_assets(ASSET_PATH)
    
    if assets:
        suggest_specific_assets(assets)
        
        print("\n" + "="*70)
        print("NEXT STEPS")
        print("="*70)
        print("\n1. Review the asset inventory above")
        print("2. I'll create an updated game using these specific assets")
        print("3. The game will automatically load the best available sprites")
        print("\n✓ Ready to build your pixel art runner game!")
        print("="*70)