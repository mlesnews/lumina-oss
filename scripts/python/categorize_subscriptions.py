"""Auto-categorize YouTube subscriptions into SYPHON categories."""
import json
import re
from pathlib import Path

SYPHON_DIR = Path(__file__).parent.parent.parent / "data" / "syphon"

# Category rules: (category_name, keywords_in_name, keywords_in_handle, priority_override)
CATEGORY_RULES = [
    # AI / Tech / Coding — order matters, first match wins
    ("ai_tech", [
        "ai ", " ai", "artificial intelligence", "machine learning", "deep learning",
        "llm", "gpt", "openai", "anthropic", "claude", "gemini",
        "neural", "transformer", "diffusion", "stable diffusion",
        "coding", "coder", "programmer", "developer", "software",
        "python", "javascript", "typescript", "rust lang",
        "devops", "linux", "github", "vscode", "neovim",
        "tech tip", "tech lead", "techcrunch",
        "freecodecamp", "fireship", "computerphile", "two minute papers",
        "3blue1brown", "veritasium", "sentdex", "primeagen",
        "karpathy", "lex fridman", "david shapiro",
        "networkchuck", "linus tech tips", "level1tech",
        "ai explained", "ai uncovered", "ai for humans",
        "ai revolution", "ai grid", "ai samson", "ai news",
        "ai voice", "ai engineer", "ai automation",
        "wes roth", "matthew berman", "matt wolfe",
        "dylan curious", "nate b jones", "julia mccoy", "farzad",
        "nate herk", "rob the ai", "ken kai", "kyle friel",
        "indydevdan", "1littlecoder", "brandon ai",
        "moon dev", "hacksmith", "chris titus tech",
        "anastasi in tech", "bitbiased", "nexalith",
        "insider ai", "world of ai", "nutshell brainery",
        "tech with tim", "tech rank", "herotech",
        "tamer zaky", "badseed tech", "mahmut",
        "robeytech", "nick puru", "michael automates",
    ], [
        "ai", "code", "dev", "tech", "hack",
    ]),

    ("finance_crypto", [
        "crypto", "bitcoin", "blockchain", "defi", "nft", "web3",
        "trading", "trader", "invest", "stock", "market", "forex",
        "finance", "fintech", "wealth", "money", "economic",
        "coin bureau", "coinbureau", "datadash", "graham stephan",
        "andrei jikh", "ben felix", "plain bagel", "swedish investor",
        "tradingview", "ziptrader", "trey's trades",
        "trading parrot", "crypto banter", "justin jack bear",
        "wealth frequency", "red fox crypto", "modern investor",
        "unstoppable domains", "real world finance",
        "cents invest", "tim talks finance",
        "trade alts", "trade talks",
        "braiins", "hive digital", "cryptotag",
        "crypto llc", "crypto mining", "sebs fintech",
    ], [
        "crypto", "trade", "invest", "finance", "btc",
    ]),

    ("star_wars", [
        "star wars", "jedi", "sith", "mandalorian", "lightsaber",
        "star wars theory", "stupendous wave", "dash star", "angry badger",
        "lore star", "cantina talk", "generation tech",
        "star wars explained", "star wars comics", "star wars audio",
        "star wars reading", "star wars lost legends",
        "tales untold", "100% star wars", "sylo",
        "echelon entertainment", "redbaron_germany",
        "ea star wars", "theory's arcade", "savage narrator",
        "marvelous wave",
    ], [
        "starwars", "jedi", "sith",
    ]),

    ("marvel_comics", [
        "marvel", "avenger", "spider-man", "x-men", "mcu",
        "comics explained", "explainer comics",
        "marvelous videos", "stanforce",
    ], [
        "marvel",
    ]),

    ("entertainment", [
        "saturday night live", "hbo", "nbc news", "rotten tomatoes",
        "charlie hopkinson", "joe rogan", "founders podcast",
        "limitless podcast", "echelon front",
        "rollin' wild",
    ], []),

    ("gaming", [
        "gaming", "gamer", "game guide", "gamepl",
        "elder scrolls", "skyrim", "fallout", "bethesda",
        "final fantasy", "ffxiv", "eso", "zenimax",
        "starcraft", "baldur", "larian", "bg3",
        "battlefront", "destiny",
        "critical role", "geek & sundry",
        "holytaboo", "hakurai", "cineonplays",
        "fevir", "mmorpg", "newegg",
        "save or dice", "machinima",
    ], [
        "gaming", "plays", "gamer",
    ]),

    ("dnd_ttrpg", [
        "dungeons", "d&d", "dnd", "dungeon master", "dm screen",
        "ttrpg", "tabletop", "pathfinder", "fantasy grounds",
        "forgotten realms", "sword coast", "undermountain",
        "puffin forest", "matthew colville", "web dm",
        "taking20", "aj pickett", "mrrhexx", "arcane library",
        "dm lair", "nerd wurx", "rob2e", "dulux oz",
        "zee bashew", "tablestory", "weave the tale",
        "rpg frequenc",
    ], [
        "dnd", "dmblair", "dm",
    ]),

    ("music", [
        "metallica", "led zeppelin", "ac/dc", "van halen",
        "guns n' roses", "aerosmith", "ozzy", "motley crue",
        "judas priest", "slayer", "anthrax", "megadeth",
        "iron maiden", "black sabbath", "rammstein",
        "slipknot", "system of a down", "alice in chains",
        "beastie boys", "joan jett", "janis joplin",
        "guitar", "music workshop", "malukah",
        "celestial aeon", "juliettev",
    ], [
        "music", "guitar", "band",
    ]),

    ("diy_outdoor", [
        "paracord", "woodwork", "blacktail studio",
        "primitive technology", "build a bronco",
        "trail recon", "jim baird", "stormdrane",
        "vibram", "ddp yoga", "ford media",
        "3d print", "m3d",
    ], [
        "paracord", "diy", "craft",
    ]),

    ("faith_inspiration", [
        "jesus", "faith", "church", "gospel", "prayer",
        "notre-dame", "lourdes", "ministry", "unshackled",
        "christian", "bible",
    ], []),

    ("strategy_lean", [
        "swedish investor", "book summar",
        "self improvement", "productivity",
        "business strategy",
    ], []),
]

def categorize_channel(name: str, handle: str) -> tuple[str, str]:
    """Return (category, priority) for a channel."""
    name_lower = name.lower()
    handle_lower = handle.lower()

    for cat_name, name_keywords, handle_keywords, *_ in CATEGORY_RULES:
        # Check name keywords
        for kw in name_keywords:
            if kw in name_lower:
                return cat_name, "medium"
        # Check handle keywords (partial match, but be careful)
        for kw in handle_keywords:
            if kw in handle_lower and len(kw) >= 3:
                return cat_name, "low"

    return "uncategorized", "low"


def main():
    # Load raw subscriptions
    with open(SYPHON_DIR / "youtube_all_subscriptions_raw.json") as f:
        raw = json.load(f)

    # Load existing config to preserve priorities and IDs
    with open(SYPHON_DIR / "youtube_channels.json") as f:
        existing = json.load(f)

    # Build lookup of existing channels by handle
    existing_lookup = {}
    for cat, channels in existing["channels"].items():
        for ch in channels:
            key = ch.get("handle", "").lower()
            if key:
                existing_lookup[key] = {**ch, "_category": cat}

    # Categorize all subscriptions
    categorized = {}
    stats = {"matched_existing": 0, "auto_categorized": 0, "uncategorized": 0}

    for sub in raw["channels"]:
        handle = sub.get("handle", "")
        name = sub.get("name", "")
        if not name:
            continue

        handle_lower = handle.lower()

        # Check if already in existing config
        if handle_lower in existing_lookup:
            ex = existing_lookup[handle_lower]
            cat = ex["_category"]
            entry = {
                "name": ex["name"],
                "id": ex.get("id", ""),
                "handle": ex.get("handle", handle),
                "priority": ex.get("priority", "medium"),
            }
            if ex.get("note"):
                entry["note"] = ex["note"]
            stats["matched_existing"] += 1
        else:
            cat, priority = categorize_channel(name, handle)
            entry = {
                "name": name,
                "id": sub.get("channel_id", ""),
                "handle": handle,
                "priority": priority,
            }
            if cat == "uncategorized":
                stats["uncategorized"] += 1
            else:
                stats["auto_categorized"] += 1

        categorized.setdefault(cat, []).append(entry)

    # Sort categories and channels within
    category_order = [
        "ai_tech", "finance_crypto", "star_wars", "marvel_comics",
        "entertainment", "gaming", "dnd_ttrpg", "music",
        "diy_outdoor", "faith_inspiration", "strategy_lean", "uncategorized"
    ]

    ordered = {}
    for cat in category_order:
        if cat in categorized:
            # Sort by priority (high > medium > low) then name
            priority_rank = {"high": 0, "medium": 1, "low": 2}
            categorized[cat].sort(key=lambda x: (priority_rank.get(x["priority"], 3), x["name"]))
            ordered[cat] = categorized[cat]

    # Add any categories not in the order
    for cat in sorted(categorized.keys()):
        if cat not in ordered:
            ordered[cat] = categorized[cat]

    # Build output config
    output = {
        "version": "2.0.0",
        "updated": "2026-02-12",
        "updated_by": "@SYPHON",
        "source": "youtube_subscription_export",
        "total_channels": sum(len(v) for v in ordered.values()),
        "sweep_config": existing["sweep_config"],
        "categories_summary": {cat: len(channels) for cat, channels in ordered.items()},
        "channels": ordered
    }

    # Save full config
    out_path = SYPHON_DIR / "youtube_channels_full.json"
    with open(out_path, "w") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print(f"Categorization complete!")
    print(f"  Matched existing config: {stats['matched_existing']}")
    print(f"  Auto-categorized: {stats['auto_categorized']}")
    print(f"  Uncategorized: {stats['uncategorized']}")
    print(f"  Total: {output['total_channels']}")
    print()
    print("Category breakdown:")
    for cat, channels in ordered.items():
        high = sum(1 for c in channels if c["priority"] == "high")
        med = sum(1 for c in channels if c["priority"] == "medium")
        low = sum(1 for c in channels if c["priority"] == "low")
        print(f"  {cat:25} {len(channels):4} channels  (H:{high} M:{med} L:{low})")
    print(f"\nSaved to: {out_path}")

if __name__ == "__main__":
    main()
