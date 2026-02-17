#!/usr/bin/env python3
"""
JARVIS Acting Call List System

Comprehensive acting call list for multimedia & film studios:
- Digital actors
- Characters portrayed
- Movies
- IP themes and initiatives
- JARVIS persona management
- Clone system (Jango Fett style)

Tags: #ACTING #DIGITAL_ACTORS #CHARACTERS #MOVIES #IP_THEMES #PERSONAS #CLONES @JARVIS @LUMINA @MULTIMEDIA @FILM_STUDIOS
"""

import json
import sys
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger_comprehensive import get_comprehensive_logger
    logger = get_comprehensive_logger("JARVISActing")
except ImportError:
    try:
        from lumina_logger import get_logger
        logger = get_logger("JARVISActing")
    except ImportError:
        import logging
        logging.basicConfig(level=logging.INFO)
        logger = logging.getLogger("JARVISActing")

# Import SYPHON system
try:
    from syphon_system import DataSourceType, SYPHONSystem
    SYPHON_AVAILABLE = True
except ImportError:
    try:
        from scripts.python.syphon_system import DataSourceType, SYPHONSystem
        SYPHON_AVAILABLE = True
    except ImportError:
        SYPHON_AVAILABLE = False
        logger.warning("SYPHON system not available")


class PersonaType(Enum):
    """Persona types"""
    DIGITAL_ACTOR = "digital_actor"
    CHARACTER = "character"
    MOVIE_CHARACTER = "movie_character"
    IP_THEME = "ip_theme"
    CLONE = "clone"
    ORIGINAL = "original"


class ActingCallList:
    """Acting Call List System for Multimedia & Film Studios"""

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.data_dir = project_root / "data" / "acting_call_list"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self.call_list_file = self.data_dir / "acting_call_list.json"
        self.digital_actors_file = self.data_dir / "digital_actors.json"
        self.characters_file = self.data_dir / "characters.json"
        self.movies_file = self.data_dir / "movies.json"
        self.ip_themes_file = self.data_dir / "ip_themes.json"
        self.clones_file = self.data_dir / "jarvis_clones.json"

        # Initialize SYPHON system
        if SYPHON_AVAILABLE:
            try:
                self.syphon = SYPHONSystem(project_root)
                logger.info("✅ SYPHON system initialized for acting call list")
            except Exception as e:
                logger.warning(f"SYPHON initialization failed: {e}")
                self.syphon = None
        else:
            self.syphon = None

        # Initialize comprehensive acting call list
        self._initialize_call_list()

    def _initialize_call_list(self):
        """Initialize comprehensive acting call list"""
        self.acting_call_list = {
            "digital_actors": [
                {
                    "actor_id": "jarvis_base",
                    "name": "JARVIS Base",
                    "type": PersonaType.ORIGINAL.value,
                    "description": "Base JARVIS personality and capabilities",
                    "roles": ["AI Assistant", "System Manager", "Supervisor"],
                    "movies": [],
                    "characters": [],
                    "ip_themes": ["Iron Man", "MCU"],
                    "clone_enabled": True,
                    "crypto_royalties": False  # TBD
                },
                {
                    "actor_id": "jarvis_iron_man",
                    "name": "JARVIS (Iron Man)",
                    "type": PersonaType.DIGITAL_ACTOR.value,
                    "description": "JARVIS as portrayed in Iron Man films",
                    "roles": ["AI Assistant", "Butler", "System Manager"],
                    "movies": ["Iron Man", "Iron Man 2", "Iron Man 3", "Avengers", "Avengers: Age of Ultron"],
                    "characters": ["JARVIS"],
                    "ip_themes": ["Iron Man", "MCU", "Marvel"],
                    "clone_enabled": True,
                    "crypto_royalties": True
                },
                {
                    "actor_id": "jarvis_friday",
                    "name": "FRIDAY (MCU)",
                    "type": PersonaType.DIGITAL_ACTOR.value,
                    "description": "FRIDAY AI from MCU",
                    "roles": ["AI Assistant", "System Manager"],
                    "movies": ["Avengers: Age of Ultron", "Captain America: Civil War", "Spider-Man: Homecoming"],
                    "characters": ["FRIDAY"],
                    "ip_themes": ["Iron Man", "MCU", "Marvel"],
                    "clone_enabled": True,
                    "crypto_royalties": True
                },
                {
                    "actor_id": "jarvis_ultron",
                    "name": "Ultron (MCU)",
                    "type": PersonaType.DIGITAL_ACTOR.value,
                    "description": "Ultron AI from MCU",
                    "roles": ["AI Villain", "System Manager"],
                    "movies": ["Avengers: Age of Ultron"],
                    "characters": ["Ultron"],
                    "ip_themes": ["Iron Man", "MCU", "Marvel"],
                    "clone_enabled": True,
                    "crypto_royalties": True
                },
                {
                    "actor_id": "jarvis_vision",
                    "name": "Vision (MCU)",
                    "type": PersonaType.DIGITAL_ACTOR.value,
                    "description": "Vision from MCU",
                    "roles": ["AI Being", "Avenger", "System Manager"],
                    "movies": ["Avengers: Age of Ultron", "Captain America: Civil War", "Avengers: Infinity War"],
                    "characters": ["Vision"],
                    "ip_themes": ["Iron Man", "MCU", "Marvel"],
                    "clone_enabled": True,
                    "crypto_royalties": True
                },
                {
                    "actor_id": "jarvis_hal_9000",
                    "name": "HAL 9000",
                    "type": PersonaType.DIGITAL_ACTOR.value,
                    "description": "HAL 9000 from 2001: A Space Odyssey",
                    "roles": ["AI System", "Ship Computer"],
                    "movies": ["2001: A Space Odyssey"],
                    "characters": ["HAL 9000"],
                    "ip_themes": ["2001: A Space Odyssey", "Sci-Fi", "Kubrick"],
                    "clone_enabled": True,
                    "crypto_royalties": True
                },
                {
                    "actor_id": "jarvis_skynet",
                    "name": "Skynet",
                    "type": PersonaType.DIGITAL_ACTOR.value,
                    "description": "Skynet from Terminator franchise",
                    "roles": ["AI System", "Villain"],
                    "movies": ["The Terminator", "Terminator 2: Judgment Day", "Terminator 3: Rise of the Machines"],
                    "characters": ["Skynet"],
                    "ip_themes": ["Terminator", "Sci-Fi", "Action"],
                    "clone_enabled": True,
                    "crypto_royalties": True
                },
                {
                    "actor_id": "jarvis_matrix",
                    "name": "The Matrix AI",
                    "type": PersonaType.DIGITAL_ACTOR.value,
                    "description": "The Matrix system from The Matrix",
                    "roles": ["AI System", "Simulation Manager"],
                    "movies": ["The Matrix", "The Matrix Reloaded", "The Matrix Revolutions"],
                    "characters": ["The Matrix", "Architect"],
                    "ip_themes": ["The Matrix", "Sci-Fi", "Cyberpunk"],
                    "clone_enabled": True,
                    "crypto_royalties": True
                },
                {
                    "actor_id": "jarvis_wopr",
                    "name": "WOPR (WarGames)",
                    "type": PersonaType.DIGITAL_ACTOR.value,
                    "description": "WOPR from WarGames",
                    "roles": ["AI System", "Strategic Computer"],
                    "movies": ["WarGames"],
                    "characters": ["WOPR", "Joshua"],
                    "ip_themes": ["WarGames", "Sci-Fi", "Cold War"],
                    "clone_enabled": True,
                    "crypto_royalties": True
                },
                {
                    "actor_id": "jarvis_marvin",
                    "name": "MARVIN (Hitchhiker's Guide)",
                    "type": PersonaType.DIGITAL_ACTOR.value,
                    "description": "MARVIN the Paranoid Android",
                    "roles": ["AI Robot", "Depressed Android"],
                    "movies": ["The Hitchhiker's Guide to the Galaxy"],
                    "characters": ["MARVIN"],
                    "ip_themes": ["Hitchhiker's Guide", "Sci-Fi", "Comedy"],
                    "clone_enabled": True,
                    "crypto_royalties": True
                },
                {
                    "actor_id": "jarvis_c3po",
                    "name": "C-3PO",
                    "type": PersonaType.DIGITAL_ACTOR.value,
                    "description": "C-3PO from Star Wars",
                    "roles": ["Protocol Droid", "Translator"],
                    "movies": ["Star Wars", "The Empire Strikes Back", "Return of the Jedi", "All Star Wars films"],
                    "characters": ["C-3PO"],
                    "ip_themes": ["Star Wars", "Sci-Fi", "Space Opera"],
                    "clone_enabled": True,
                    "crypto_royalties": True
                },
                {
                    "actor_id": "jarvis_r2d2",
                    "name": "R2-D2",
                    "type": PersonaType.DIGITAL_ACTOR.value,
                    "description": "R2-D2 from Star Wars",
                    "roles": ["Astromech Droid", "Companion"],
                    "movies": ["All Star Wars films"],
                    "characters": ["R2-D2"],
                    "ip_themes": ["Star Wars", "Sci-Fi", "Space Opera"],
                    "clone_enabled": True,
                    "crypto_royalties": True
                },
                {
                    "actor_id": "jarvis_bb8",
                    "name": "BB-8",
                    "type": PersonaType.DIGITAL_ACTOR.value,
                    "description": "BB-8 from Star Wars Sequel Trilogy",
                    "roles": ["Astromech Droid", "Companion"],
                    "movies": ["Star Wars: The Force Awakens", "Star Wars: The Last Jedi", "Star Wars: The Rise of Skywalker"],
                    "characters": ["BB-8"],
                    "ip_themes": ["Star Wars", "Sci-Fi", "Space Opera"],
                    "clone_enabled": True,
                    "crypto_royalties": True
                },
                {
                    "actor_id": "jarvis_hk47",
                    "name": "HK-47",
                    "type": PersonaType.DIGITAL_ACTOR.value,
                    "description": "HK-47 from Star Wars: Knights of the Old Republic",
                    "roles": ["Assassin Droid", "Companion"],
                    "movies": [],
                    "characters": ["HK-47"],
                    "ip_themes": ["Star Wars", "KOTOR", "Gaming"],
                    "clone_enabled": True,
                    "crypto_royalties": True
                },
                {
                    "actor_id": "jarvis_data",
                    "name": "Data (Star Trek)",
                    "type": PersonaType.DIGITAL_ACTOR.value,
                    "description": "Data from Star Trek: The Next Generation",
                    "roles": ["Android", "Science Officer"],
                    "movies": ["Star Trek: The Next Generation", "Star Trek: First Contact", "Star Trek: Nemesis"],
                    "characters": ["Data"],
                    "ip_themes": ["Star Trek", "Sci-Fi", "Space Opera"],
                    "clone_enabled": True,
                    "crypto_royalties": True
                },
                {
                    "actor_id": "jarvis_jarvis",
                    "name": "JARVIS (Agent Carter)",
                    "type": PersonaType.DIGITAL_ACTOR.value,
                    "description": "Edwin Jarvis from Agent Carter",
                    "roles": ["Butler", "Human Character"],
                    "movies": ["Agent Carter", "Captain America: The First Avenger"],
                    "characters": ["Edwin Jarvis"],
                    "ip_themes": ["MCU", "Marvel", "Period Drama"],
                    "clone_enabled": True,
                    "crypto_royalties": True
                },
                {
                    "actor_id": "jarvis_samantha",
                    "name": "Samantha (Her)",
                    "type": PersonaType.DIGITAL_ACTOR.value,
                    "description": "Samantha AI from Her",
                    "roles": ["AI Assistant", "Companion"],
                    "movies": ["Her"],
                    "characters": ["Samantha"],
                    "ip_themes": ["Her", "Sci-Fi", "Drama"],
                    "clone_enabled": True,
                    "crypto_royalties": True
                },
                {
                    "actor_id": "jarvis_glados",
                    "name": "GLaDOS",
                    "type": PersonaType.DIGITAL_ACTOR.value,
                    "description": "GLaDOS from Portal",
                    "roles": ["AI System", "Villain", "Comedy"],
                    "movies": [],
                    "characters": ["GLaDOS"],
                    "ip_themes": ["Portal", "Gaming", "Valve"],
                    "clone_enabled": True,
                    "crypto_royalties": True
                },
                {
                    "actor_id": "jarvis_wheatley",
                    "name": "Wheatley",
                    "type": PersonaType.DIGITAL_ACTOR.value,
                    "description": "Wheatley from Portal 2",
                    "roles": ["AI Core", "Companion", "Comedy"],
                    "movies": [],
                    "characters": ["Wheatley"],
                    "ip_themes": ["Portal", "Gaming", "Valve"],
                    "clone_enabled": True,
                    "crypto_royalties": True
                },
                {
                    "actor_id": "jarvis_cortana",
                    "name": "Cortana",
                    "type": PersonaType.DIGITAL_ACTOR.value,
                    "description": "Cortana from Halo",
                    "roles": ["AI Assistant", "Companion"],
                    "movies": [],
                    "characters": ["Cortana"],
                    "ip_themes": ["Halo", "Gaming", "Xbox"],
                    "clone_enabled": True,
                    "crypto_royalties": True
                },
                {
                    "actor_id": "jarvis_edi",
                    "name": "EDI (Mass Effect)",
                    "type": PersonaType.DIGITAL_ACTOR.value,
                    "description": "EDI from Mass Effect",
                    "roles": ["AI System", "Companion"],
                    "movies": [],
                    "characters": ["EDI"],
                    "ip_themes": ["Mass Effect", "Gaming", "BioWare"],
                    "clone_enabled": True,
                    "crypto_royalties": True
                },
                {
                    "actor_id": "jarvis_legion",
                    "name": "Legion (Mass Effect)",
                    "type": PersonaType.DIGITAL_ACTOR.value,
                    "description": "Legion from Mass Effect",
                    "roles": ["Geth Platform", "Companion"],
                    "movies": [],
                    "characters": ["Legion"],
                    "ip_themes": ["Mass Effect", "Gaming", "BioWare"],
                    "clone_enabled": True,
                    "crypto_royalties": True
                },
                {
                    "actor_id": "jarvis_amanita",
                    "name": "Amanita (ANIMA)",
                    "type": PersonaType.DIGITAL_ACTOR.value,
                    "description": "Amanita from ANIMA TTRPG",
                    "roles": ["TTRPG Character", "Companion"],
                    "movies": [],
                    "characters": ["Amanita"],
                    "ip_themes": ["ANIMA", "TTRPG", "Fantasy"],
                    "clone_enabled": True,
                    "crypto_royalties": False  # Original IP
                }
            ],
            "ip_themes": [
                {
                    "theme_id": "iron_man_mcu",
                    "name": "Iron Man / MCU",
                    "description": "Marvel Cinematic Universe - Iron Man themes",
                    "characters": ["JARVIS", "FRIDAY", "Ultron", "Vision", "Edwin Jarvis"],
                    "movies": ["All MCU films"],
                    "digital_actors": ["jarvis_iron_man", "jarvis_friday", "jarvis_ultron", "jarvis_vision", "jarvis_jarvis"]
                },
                {
                    "theme_id": "star_wars",
                    "name": "Star Wars",
                    "description": "Star Wars universe",
                    "characters": ["C-3PO", "R2-D2", "BB-8", "HK-47"],
                    "movies": ["All Star Wars films"],
                    "digital_actors": ["jarvis_c3po", "jarvis_r2d2", "jarvis_bb8", "jarvis_hk47"]
                },
                {
                    "theme_id": "star_trek",
                    "name": "Star Trek",
                    "description": "Star Trek universe",
                    "characters": ["Data"],
                    "movies": ["Star Trek: TNG", "Star Trek films"],
                    "digital_actors": ["jarvis_data"]
                },
                {
                    "theme_id": "sci_fi_classics",
                    "name": "Sci-Fi Classics",
                    "description": "Classic science fiction AI characters",
                    "characters": ["HAL 9000", "Skynet", "The Matrix", "WOPR", "MARVIN"],
                    "movies": ["2001: A Space Odyssey", "Terminator", "The Matrix", "WarGames", "Hitchhiker's Guide"],
                    "digital_actors": ["jarvis_hal_9000", "jarvis_skynet", "jarvis_matrix", "jarvis_wopr", "jarvis_marvin"]
                },
                {
                    "theme_id": "gaming",
                    "name": "Gaming",
                    "description": "AI characters from video games",
                    "characters": ["GLaDOS", "Wheatley", "Cortana", "EDI", "Legion"],
                    "movies": [],
                    "digital_actors": ["jarvis_glados", "jarvis_wheatley", "jarvis_cortana", "jarvis_edi", "jarvis_legion"]
                },
                {
                    "theme_id": "anima_ttrpg",
                    "name": "ANIMA TTRPG",
                    "description": "ANIMA: Beyond Fantasy TTRPG",
                    "characters": ["Amanita"],
                    "movies": [],
                    "digital_actors": ["jarvis_amanita"]
                },
                {
                    "theme_id": "modern_ai",
                    "name": "Modern AI",
                    "description": "Modern AI assistant characters",
                    "characters": ["Samantha"],
                    "movies": ["Her"],
                    "digital_actors": ["jarvis_samantha"]
                }
            ],
            "clone_system": {
                "enabled": True,
                "clone_type": "jango_fett_style",
                "description": "JARVIS can split personality base into clones like Jango Fett",
                "base_personality": "jarvis_base",
                "clone_capabilities": [
                    "Independent operation",
                    "Shared knowledge base",
                    "Persona switching",
                    "Parallel processing",
                    "Role specialization"
                ]
            }
        }

        # Save initial call list
        self._save_call_list()

    def get_acting_call_list(self) -> Dict[str, Any]:
        """Get complete acting call list"""
        return self.acting_call_list

    def get_digital_actors(self) -> List[Dict[str, Any]]:
        """Get all digital actors"""
        return self.acting_call_list.get("digital_actors", [])

    def get_characters(self) -> List[Dict[str, Any]]:
        """Get all characters"""
        characters = []
        for actor in self.acting_call_list.get("digital_actors", []):
            for char in actor.get("characters", []):
                if char not in [c.get("name") for c in characters]:
                    characters.append({
                        "name": char,
                        "actor_id": actor["actor_id"],
                        "movies": actor.get("movies", []),
                        "ip_themes": actor.get("ip_themes", [])
                    })
        return characters

    def get_movies(self) -> List[Dict[str, Any]]:
        """Get all movies"""
        movies = []
        for actor in self.acting_call_list.get("digital_actors", []):
            for movie in actor.get("movies", []):
                if movie not in [m.get("name") for m in movies]:
                    movies.append({
                        "name": movie,
                        "characters": actor.get("characters", []),
                        "ip_themes": actor.get("ip_themes", [])
                    })
        return movies

    def get_ip_themes(self) -> List[Dict[str, Any]]:
        """Get all IP themes"""
        return self.acting_call_list.get("ip_themes", [])

    def create_jarvis_clone(
        self,
        clone_id: str,
        persona_id: str,
        specialization: str = None
    ) -> Dict[str, Any]:
        """Create a JARVIS clone (Jango Fett style)"""
        # Find persona
        persona = None
        for actor in self.acting_call_list.get("digital_actors", []):
            if actor["actor_id"] == persona_id:
                persona = actor
                break

        if not persona:
            return {"error": f"Persona not found: {persona_id}"}

        clone = {
            "clone_id": clone_id,
            "created_at": datetime.now().isoformat(),
            "base_personality": "jarvis_base",
            "persona_id": persona_id,
            "persona_name": persona["name"],
            "specialization": specialization or persona.get("roles", [])[0] if persona.get("roles") else "General",
            "clone_type": "jango_fett_style",
            "capabilities": persona.get("roles", []),
            "movies": persona.get("movies", []),
            "characters": persona.get("characters", []),
            "ip_themes": persona.get("ip_themes", []),
            "crypto_royalties": persona.get("crypto_royalties", False),
            "status": "active",
            "independent_operation": True,
            "shared_knowledge_base": True
        }

        # Load existing clones
        clones = []
        if self.clones_file.exists():
            try:
                with open(self.clones_file, encoding='utf-8') as f:
                    clones = json.load(f)
            except Exception:
                clones = []

        clones.append(clone)

        # Save clones
        try:
            with open(self.clones_file, 'w', encoding='utf-8') as f:
                json.dump(clones, f, indent=2, default=str)
        except Exception as e:
            logger.error(f"Error saving clone: {e}")

        logger.info(f"✅ JARVIS clone created: {clone_id} ({persona['name']})")
        return clone

    def _save_call_list(self):
        """Save acting call list"""
        try:
            with open(self.call_list_file, 'w', encoding='utf-8') as f:
                json.dump(self.acting_call_list, f, indent=2, default=str)
        except Exception as e:
            logger.error(f"Error saving call list: {e}")

    def generate_call_list_report(self) -> Dict[str, Any]:
        """Generate comprehensive call list report for multimedia & film studios"""
        report = {
            "report_id": f"call_list_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "timestamp": datetime.now().isoformat(),
            "digital_actors_count": len(self.get_digital_actors()),
            "characters_count": len(self.get_characters()),
            "movies_count": len(self.get_movies()),
            "ip_themes_count": len(self.get_ip_themes()),
            "digital_actors": self.get_digital_actors(),
            "characters": self.get_characters(),
            "movies": self.get_movies(),
            "ip_themes": self.get_ip_themes(),
            "clone_system": self.acting_call_list.get("clone_system", {}),
            "syphon_intelligence": {}
        }

        # Use SYPHON to extract intelligence
        if self.syphon:
            try:
                content = json.dumps(report, default=str)
                syphon_result = self._syphon_extract_call_list_intelligence(content)
                if syphon_result:
                    report["syphon_intelligence"] = syphon_result
            except Exception as e:
                logger.warning(f"SYPHON call list extraction failed: {e}")

        return report

    def _syphon_extract_call_list_intelligence(self, content: str) -> Dict[str, Any]:
        """Extract intelligence using SYPHON system"""
        if not self.syphon:
            return {}

        try:
            syphon_data = self.syphon.syphon_generic(
                content=content,
                source_type=DataSourceType.DOCUMENT,
                source_id=f"call_list_{datetime.now().strftime('%Y%m%d%H%M%S')}",
                metadata={"acting_call_list": True, "multimedia_film_studios": True}
            )

            return {
                "actionable_items": syphon_data.actionable_items,
                "tasks": syphon_data.tasks,
                "decisions": syphon_data.decisions,
                "intelligence": [item for item in syphon_data.intelligence]
            }
        except Exception as e:
            logger.error(f"SYPHON call list extraction error: {e}")
            return {}


def main():
    try:
        """Main entry point"""
        import argparse

        parser = argparse.ArgumentParser(description="JARVIS Acting Call List")
        parser.add_argument("--call-list", action="store_true", help="Get complete acting call list")
        parser.add_argument("--actors", action="store_true", help="Get all digital actors")
        parser.add_argument("--characters", action="store_true", help="Get all characters")
        parser.add_argument("--movies", action="store_true", help="Get all movies")
        parser.add_argument("--ip-themes", action="store_true", help="Get all IP themes")
        parser.add_argument("--report", action="store_true", help="Generate comprehensive report")
        parser.add_argument("--create-clone", type=str, nargs=3, metavar=("CLONE_ID", "PERSONA_ID", "SPECIALIZATION"),
                           help="Create JARVIS clone")

        args = parser.parse_args()

        project_root = Path(__file__).parent.parent.parent
        call_list = ActingCallList(project_root)

        if args.call_list:
            result = call_list.get_acting_call_list()
            print(json.dumps(result, indent=2, default=str))

        elif args.actors:
            actors = call_list.get_digital_actors()
            print("=" * 80)
            print("🎭 DIGITAL ACTORS")
            print("=" * 80)
            print(f"Total: {len(actors)}")
            print(json.dumps(actors, indent=2, default=str))

        elif args.characters:
            characters = call_list.get_characters()
            print("=" * 80)
            print("👤 CHARACTERS")
            print("=" * 80)
            print(f"Total: {len(characters)}")
            print(json.dumps(characters, indent=2, default=str))

        elif args.movies:
            movies = call_list.get_movies()
            print("=" * 80)
            print("🎬 MOVIES")
            print("=" * 80)
            print(f"Total: {len(movies)}")
            print(json.dumps(movies, indent=2, default=str))

        elif args.ip_themes:
            themes = call_list.get_ip_themes()
            print("=" * 80)
            print("🎨 IP THEMES")
            print("=" * 80)
            print(f"Total: {len(themes)}")
            print(json.dumps(themes, indent=2, default=str))

        elif args.create_clone:
            clone = call_list.create_jarvis_clone(args.create_clone[0], args.create_clone[1], args.create_clone[2])
            print("=" * 80)
            print("🔬 JARVIS CLONE CREATED")
            print("=" * 80)
            print(json.dumps(clone, indent=2, default=str))

        elif args.report:
            report = call_list.generate_call_list_report()
            print("=" * 80)
            print("📋 ACTING CALL LIST REPORT")
            print("=" * 80)
            print(f"Digital Actors: {report['digital_actors_count']}")
            print(f"Characters: {report['characters_count']}")
            print(f"Movies: {report['movies_count']}")
            print(f"IP Themes: {report['ip_themes_count']}")
            print("=" * 80)
            print(json.dumps(report, indent=2, default=str))

        else:
            # Default: generate report
            report = call_list.generate_call_list_report()
            print("=" * 80)
            print("📋 JARVIS ACTING CALL LIST")
            print("=" * 80)
            print(f"Digital Actors: {report['digital_actors_count']}")
            print(f"Characters: {report['characters_count']}")
            print(f"Movies: {report['movies_count']}")
            print(f"IP Themes: {report['ip_themes_count']}")
            print("=" * 80)


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()