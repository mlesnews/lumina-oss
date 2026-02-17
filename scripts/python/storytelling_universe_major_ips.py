#!/usr/bin/env python3
"""
Storytelling Universe Major IPs Registry - ORDER 66: @DOIT

Comprehensive registry of major Intellectual Properties for the storytelling universe:
- Star Wars
- LoTR (Lord of the Rings)
- Transformers
- BSG (Battlestar Galactica)
- Marvel
- DC
- And far too many to list...

Tags: #STORYTELLING #IP #REGISTRY #ORDER66 #DOIT @JARVIS @TEAM
"""

import sys
from pathlib import Path
from typing import Dict, List, Any
from lumina_storytelling_universe_system import (
    IntellectualProperty,
    Genre,
    ContentFormat
)

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))


# Major IPs Registry
MAJOR_IPS = {
    # Star Wars
    "star_wars": IntellectualProperty(
        ip_id="star_wars",
        title="Star Wars",
        description="A galaxy far, far away...",
        genres=[Genre.SCIENCE_FICTION, Genre.ACTION, Genre.ADVENTURE, Genre.FANTASY],
        formats=[
            ContentFormat.LIVE_ACTION, ContentFormat.ANIMATED_SERIES,
            ContentFormat.ANIMATED_MOVIE, ContentFormat.ANIME,
            ContentFormat.AUDIOBOOK, ContentFormat.VIDEO_GAME
        ],
        characters=[],
        virtual_actors=[],
        created_by="George Lucas",
        year_created=1977,
        status="active"
    ),

    # Lord of the Rings
    "lord_of_the_rings": IntellectualProperty(
        ip_id="lord_of_the_rings",
        title="The Lord of the Rings",
        description="One Ring to rule them all...",
        genres=[Genre.FANTASY, Genre.ADVENTURE, Genre.DRAMA],
        formats=[
            ContentFormat.LIVE_ACTION, ContentFormat.ANIMATED_MOVIE,
            ContentFormat.AUDIOBOOK, ContentFormat.VIDEO_GAME
        ],
        characters=[],
        virtual_actors=[],
        created_by="J.R.R. Tolkien",
        year_created=1954,
        status="active"
    ),

    # Transformers
    "transformers": IntellectualProperty(
        ip_id="transformers",
        title="Transformers",
        description="Robots in disguise...",
        genres=[Genre.SCIENCE_FICTION, Genre.ACTION, Genre.ADVENTURE],
        formats=[
            ContentFormat.LIVE_ACTION, ContentFormat.ANIMATED_SERIES,
            ContentFormat.ANIMATED_MOVIE, ContentFormat.ANIME,
            ContentFormat.VIDEO_GAME, ContentFormat.CARTOON
        ],
        characters=[],
        virtual_actors=[],
        created_by="Hasbro",
        year_created=1984,
        status="active"
    ),

    # Battlestar Galactica
    "battlestar_galactica": IntellectualProperty(
        ip_id="battlestar_galactica",
        title="Battlestar Galactica",
        description="So say we all...",
        genres=[Genre.SCIENCE_FICTION, Genre.DRAMA, Genre.THRILLER],
        formats=[
            ContentFormat.LIVE_ACTION, ContentFormat.ANIMATED_SERIES,
            ContentFormat.DOCUSERIES
        ],
        characters=[],
        virtual_actors=[],
        created_by="Glen A. Larson",
        year_created=1978,
        status="active"
    ),

    # Marvel
    "marvel": IntellectualProperty(
        ip_id="marvel",
        title="Marvel Cinematic Universe",
        description="Earth's Mightiest Heroes...",
        genres=[Genre.SCIENCE_FICTION, Genre.ACTION, Genre.ADVENTURE],
        formats=[
            ContentFormat.LIVE_ACTION, ContentFormat.ANIMATED_SERIES,
            ContentFormat.ANIMATED_MOVIE, ContentFormat.ANIME,
            ContentFormat.VIDEO_GAME, ContentFormat.CARTOON
        ],
        characters=[],
        virtual_actors=[],
        created_by="Marvel Comics",
        year_created=1961,
        status="active"
    ),

    # DC
    "dc": IntellectualProperty(
        ip_id="dc",
        title="DC Extended Universe",
        description="Justice League...",
        genres=[Genre.SCIENCE_FICTION, Genre.ACTION, Genre.ADVENTURE],
        formats=[
            ContentFormat.LIVE_ACTION, ContentFormat.ANIMATED_SERIES,
            ContentFormat.ANIMATED_MOVIE, ContentFormat.ANIME,
            ContentFormat.VIDEO_GAME, ContentFormat.CARTOON
        ],
        characters=[],
        virtual_actors=[],
        created_by="DC Comics",
        year_created=1934,
        status="active"
    ),

    # Star Trek
    "star_trek": IntellectualProperty(
        ip_id="star_trek",
        title="Star Trek",
        description="To boldly go where no one has gone before...",
        genres=[Genre.SCIENCE_FICTION, Genre.ADVENTURE, Genre.DRAMA],
        formats=[
            ContentFormat.LIVE_ACTION, ContentFormat.ANIMATED_SERIES,
            ContentFormat.ANIMATED_MOVIE
        ],
        characters=[],
        virtual_actors=[],
        created_by="Gene Roddenberry",
        year_created=1966,
        status="active"
    ),

    # Doctor Who
    "doctor_who": IntellectualProperty(
        ip_id="doctor_who",
        title="Doctor Who",
        description="The Doctor...",
        genres=[Genre.SCIENCE_FICTION, Genre.ADVENTURE, Genre.DRAMA],
        formats=[
            ContentFormat.LIVE_ACTION, ContentFormat.AUDIOBOOK,
            ContentFormat.VIDEO_GAME
        ],
        characters=[],
        virtual_actors=[],
        created_by="BBC",
        year_created=1963,
        status="active"
    ),

    # Harry Potter
    "harry_potter": IntellectualProperty(
        ip_id="harry_potter",
        title="Harry Potter",
        description="The boy who lived...",
        genres=[Genre.FANTASY, Genre.ADVENTURE, Genre.DRAMA],
        formats=[
            ContentFormat.LIVE_ACTION, ContentFormat.AUDIOBOOK,
            ContentFormat.VIDEO_GAME
        ],
        characters=[],
        virtual_actors=[],
        created_by="J.K. Rowling",
        year_created=1997,
        status="active"
    ),

    # Game of Thrones
    "game_of_thrones": IntellectualProperty(
        ip_id="game_of_thrones",
        title="Game of Thrones",
        description="Winter is coming...",
        genres=[Genre.FANTASY, Genre.DRAMA, Genre.THRILLER],
        formats=[
            ContentFormat.LIVE_ACTION, ContentFormat.ANIMATED_SERIES,
            ContentFormat.AUDIOBOOK, ContentFormat.VIDEO_GAME
        ],
        characters=[],
        virtual_actors=[],
        created_by="George R.R. Martin",
        year_created=1996,
        status="active"
    ),

    # The Matrix
    "the_matrix": IntellectualProperty(
        ip_id="the_matrix",
        title="The Matrix",
        description="Welcome to the real world...",
        genres=[Genre.SCIENCE_FICTION, Genre.ACTION, Genre.THRILLER],
        formats=[
            ContentFormat.LIVE_ACTION, ContentFormat.ANIMATED_SERIES,
            ContentFormat.VIDEO_GAME, ContentFormat.CGI_LIVE_ACTION
        ],
        characters=[],
        virtual_actors=[],
        created_by="The Wachowskis",
        year_created=1999,
        status="active"
    ),

    # Warhammer 40K
    "warhammer_40k": IntellectualProperty(
        ip_id="warhammer_40k",
        title="Warhammer 40,000",
        description="In the grim darkness of the far future...",
        genres=[Genre.SCIENCE_FICTION, Genre.ACTION, Genre.HORROR],
        formats=[
            ContentFormat.ANIMATED_SERIES, ContentFormat.ANIME,
            ContentFormat.VIDEO_GAME, ContentFormat.CARTOON
        ],
        characters=[],
        virtual_actors=[],
        created_by="Games Workshop",
        year_created=1987,
        status="active"
    ),

    # Dune
    "dune": IntellectualProperty(
        ip_id="dune",
        title="Dune",
        description="The spice must flow...",
        genres=[Genre.SCIENCE_FICTION, Genre.ADVENTURE, Genre.DRAMA],
        formats=[
            ContentFormat.LIVE_ACTION, ContentFormat.AUDIOBOOK,
            ContentFormat.VIDEO_GAME
        ],
        characters=[],
        virtual_actors=[],
        created_by="Frank Herbert",
        year_created=1965,
        status="active"
    ),

    # Avatar
    "avatar": IntellectualProperty(
        ip_id="avatar",
        title="Avatar: The Last Airbender",
        description="Long ago, the four nations lived in harmony...",
        genres=[Genre.FANTASY, Genre.ADVENTURE],
        formats=[
            ContentFormat.ANIMATED_SERIES, ContentFormat.ANIME,
            ContentFormat.LIVE_ACTION, ContentFormat.VIDEO_GAME
        ],
        characters=[],
        virtual_actors=[],
        created_by="Michael Dante DiMartino, Bryan Konietzko",
        year_created=2005,
        status="active"
    ),

    # One Piece
    "one_piece": IntellectualProperty(
        ip_id="one_piece",
        title="One Piece",
        description="The journey to find the One Piece...",
        genres=[Genre.ADVENTURE, Genre.ACTION, Genre.COMEDY],
        formats=[
            ContentFormat.ANIME, ContentFormat.ANIMATED_SERIES,
            ContentFormat.LIVE_ACTION, ContentFormat.VIDEO_GAME
        ],
        characters=[],
        virtual_actors=[],
        created_by="Eiichiro Oda",
        year_created=1997,
        status="active"
    ),

    # Naruto
    "naruto": IntellectualProperty(
        ip_id="naruto",
        title="Naruto",
        description="Believe it!",
        genres=[Genre.ACTION, Genre.ADVENTURE],
        formats=[
            ContentFormat.ANIME, ContentFormat.ANIMATED_SERIES,
            ContentFormat.VIDEO_GAME
        ],
        characters=[],
        virtual_actors=[],
        created_by="Masashi Kishimoto",
        year_created=1999,
        status="active"
    ),

    # Dragon Ball
    "dragon_ball": IntellectualProperty(
        ip_id="dragon_ball",
        title="Dragon Ball",
        description="Gather the Dragon Balls...",
        genres=[Genre.ACTION, Genre.ADVENTURE, Genre.COMEDY],
        formats=[
            ContentFormat.ANIME, ContentFormat.ANIMATED_SERIES,
            ContentFormat.VIDEO_GAME
        ],
        characters=[],
        virtual_actors=[],
        created_by="Akira Toriyama",
        year_created=1984,
        status="active"
    ),

    # And many, many more...
}


def get_all_major_ips() -> Dict[str, IntellectualProperty]:
    """Get all major IPs registry"""
    return MAJOR_IPS


def import_major_ips_to_universe(universe_system) -> Dict[str, Any]:
    """Import all major IPs to storytelling universe system"""
    imported = []
    errors = []

    for ip_id, ip in MAJOR_IPS.items():
        try:
            result = universe_system.add_ip(ip)
            if result.get("success"):
                imported.append(ip_id)
        except Exception as e:
            errors.append({"ip_id": ip_id, "error": str(e)})

    return {
        "imported": imported,
        "errors": errors,
        "total": len(MAJOR_IPS),
        "successful": len(imported),
        "failed": len(errors)
    }


if __name__ == "__main__":
    print("\n📚 Major IPs Registry")
    print("="*80)
    print(f"Total Major IPs: {len(MAJOR_IPS)}")
    print("\nRegistered IPs:")
    for ip_id, ip in MAJOR_IPS.items():
        print(f"  • {ip.title} ({ip_id})")
        print(f"    Genres: {', '.join([g.value for g in ip.genres])}")
        print(f"    Formats: {', '.join([f.value for f in ip.formats])}")
        print()
