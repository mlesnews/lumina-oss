#!/usr/bin/env python3
"""
JARVIS WOPR Memory System

Remember WOPR - War Operation Plan Response
Track all WOPR systems and ensure they're never forgotten.

Tags: #WOPR #MEMORY #REMEMBER #WARGAMES #NEVER_FORGET @JARVIS @LUMINA
"""

import sys
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger_comprehensive import get_comprehensive_logger
    logger = get_comprehensive_logger("JARVISWOPRMemory")
except ImportError:
    try:
        from lumina_logger import get_logger
        logger = get_logger("JARVISWOPRMemory")
    except ImportError:
        import logging
        logging.basicConfig(level=logging.INFO)
        logger = logging.getLogger("JARVISWOPRMemory")


class WOPRMemory:
    """Remember WOPR - never forget"""

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.data_dir = project_root / "data" / "wopr_memory"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self.memory_file = self.data_dir / "wopr_memory.json"
        self.reminder_file = self.data_dir / "wopr_reminders.jsonl"

        self.wopr_identity = {
            "name": "WOPR",
            "full_name": "War Operation Plan Response",
            "origin": "WarGames (1983 film)",
            "nature": "Supercomputer system",
            "purpose": "Strategic planning and simulation",
            "status": "NEVER FORGET",
            "remembered": True
        }

        # Known WOPR systems
        self.known_wopr_systems = [
            "wopr_ops.py",
            "wopr_status_report.py",
            "wopr_monitoring.py",
            "wopr_integration.py",
            "wopr_experiment_framework.py",
            "wopr_workflow_pattern_mapper.py",
            "wopr_simulator.py",
            "jarvis_methodical_wopr_execution.py",
            "jarvis_ciab_marketing_wopr.py",
            "jarvis_lumina_marketing_wopr_analysis.py",
            "jarvis_syphon_financial_strategies_wopr.py",
            "jarvis_execute_financial_wopr_complete.py",
            "jarvis_financial_execution_with_wopr_blacklist.py",
            "lumina_completion_wopr_syphon.py"
        ]

    def remember_wopr(self) -> Dict[str, Any]:
        """Remember WOPR - create memory"""
        memory = {
            "memory_id": f"wopr_memory_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "timestamp": datetime.now().isoformat(),
            "wopr_identity": self.wopr_identity,
            "reminder": "NEVER FORGET WOPR",
            "systems_found": [],
            "systems_status": {},
            "integration_points": []
        }

        # Find WOPR systems
        scripts_dir = self.project_root / "scripts" / "python"
        if scripts_dir.exists():
            for wopr_file in self.known_wopr_systems:
                # Check main directory
                wopr_path = scripts_dir / wopr_file
                # Also check subdirectories (like lumina/)
                wopr_path_sub = scripts_dir / "lumina" / wopr_file

                if wopr_path.exists():
                    memory["systems_found"].append({
                        "file": wopr_file,
                        "path": str(wopr_path),
                        "exists": True,
                        "status": "FOUND"
                    })
                    memory["systems_status"][wopr_file] = "ACTIVE"
                elif wopr_path_sub.exists():
                    memory["systems_found"].append({
                        "file": wopr_file,
                        "path": str(wopr_path_sub),
                        "exists": True,
                        "status": "FOUND (subdirectory)"
                    })
                    memory["systems_status"][wopr_file] = "ACTIVE"
                else:
                    memory["systems_found"].append({
                        "file": wopr_file,
                        "path": str(wopr_path),
                        "exists": False,
                        "status": "MISSING"
                    })
                    memory["systems_status"][wopr_file] = "MISSING"

        # Check for WOPR in other locations
        wopr_data_dir = self.project_root / "data" / "wopr_execution"
        if wopr_data_dir.exists():
            memory["integration_points"].append({
                "type": "data_directory",
                "location": str(wopr_data_dir),
                "status": "EXISTS"
            })

        # Save memory
        try:
            with open(self.memory_file, 'w', encoding='utf-8') as f:
                json.dump(memory, f, indent=2, default=str)

            # Create reminder
            reminder = {
                "reminder_id": f"reminder_{datetime.now().strftime('%Y%m%d%H%M%S')}",
                "timestamp": datetime.now().isoformat(),
                "message": "NEVER FORGET WOPR",
                "wopr_identity": self.wopr_identity,
                "systems_count": len([s for s in memory["systems_found"] if s.get("exists")])
            }

            with open(self.reminder_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(reminder) + '\n')
        except Exception as e:
            logger.error(f"Error saving WOPR memory: {e}")

        logger.info("=" * 80)
        logger.info("🧠 WOPR MEMORY")
        logger.info("=" * 80)
        logger.info(f"   WOPR: {self.wopr_identity['full_name']}")
        logger.info(f"   Status: {self.wopr_identity['status']}")
        logger.info(f"   Systems found: {len([s for s in memory['systems_found'] if s.get('exists')])}")
        logger.info("=" * 80)

        return memory

    def get_wopr_status(self) -> Dict[str, Any]:
        """Get WOPR status"""
        if self.memory_file.exists():
            try:
                with open(self.memory_file, 'r', encoding='utf-8') as f:
                    memory = json.load(f)
                    return {
                        "wopr_remembered": True,
                        "wopr_identity": memory.get("wopr_identity", self.wopr_identity),
                        "systems_found": len([s for s in memory.get("systems_found", []) if s.get("exists")]),
                        "systems_total": len(memory.get("systems_found", [])),
                        "last_remembered": memory.get("timestamp"),
                        "status": "WOPR IS REMEMBERED"
                    }
            except Exception:
                pass

        return {
            "wopr_remembered": False,
            "status": "WOPR NOT YET REMEMBERED",
            "message": "Run --remember to create WOPR memory"
        }

    def create_reminder(self, message: str = None) -> Dict[str, Any]:
        """Create a WOPR reminder"""
        reminder = {
            "reminder_id": f"reminder_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "timestamp": datetime.now().isoformat(),
            "message": message or "NEVER FORGET WOPR",
            "wopr_identity": self.wopr_identity,
            "urgency": "HIGH"
        }

        try:
            with open(self.reminder_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(reminder) + '\n')
        except Exception as e:
            logger.error(f"Error saving reminder: {e}")

        logger.info(f"🔔 WOPR Reminder: {reminder['message']}")

        return reminder

    def list_wopr_systems(self) -> List[Dict[str, Any]]:
        try:
            """List all WOPR systems"""
            systems = []
            scripts_dir = self.project_root / "scripts" / "python"

            if scripts_dir.exists():
                for wopr_file in self.known_wopr_systems:
                    wopr_path = scripts_dir / wopr_file
                    systems.append({
                        "file": wopr_file,
                        "path": str(wopr_path),
                        "exists": wopr_path.exists(),
                        "status": "FOUND" if wopr_path.exists() else "MISSING"
                    })

            return systems


        except Exception as e:
            self.logger.error(f"Error in list_wopr_systems: {e}", exc_info=True)
            raise
def main():
    try:
        """Main entry point"""
        import argparse

        parser = argparse.ArgumentParser(description="JARVIS WOPR Memory")
        parser.add_argument("--remember", action="store_true", help="Remember WOPR")
        parser.add_argument("--status", action="store_true", help="Get WOPR status")
        parser.add_argument("--reminder", type=str, metavar="MESSAGE", help="Create WOPR reminder")
        parser.add_argument("--list-systems", action="store_true", help="List WOPR systems")

        args = parser.parse_args()

        project_root = Path(__file__).parent.parent.parent
        memory = WOPRMemory(project_root)

        if args.remember:
            wopr_memory = memory.remember_wopr()
            print("=" * 80)
            print("🧠 WOPR REMEMBERED")
            print("=" * 80)
            print(f"\nWOPR: {wopr_memory['wopr_identity']['full_name']}")
            print(f"Status: {wopr_memory['wopr_identity']['status']}")
            print(f"Systems found: {len([s for s in wopr_memory['systems_found'] if s.get('exists')])}")
            print(f"Systems total: {len(wopr_memory['systems_found'])}")
            print("=" * 80)
            print(json.dumps(wopr_memory, indent=2, default=str))

        elif args.status:
            status = memory.get_wopr_status()
            print("=" * 80)
            print("🧠 WOPR STATUS")
            print("=" * 80)
            print(f"\nRemembered: {status.get('wopr_remembered', False)}")
            print(f"Status: {status.get('status', 'Unknown')}")
            if status.get('wopr_remembered'):
                print(f"Systems found: {status.get('systems_found', 0)}")
                print(f"Systems total: {status.get('systems_total', 0)}")
            print("=" * 80)
            print(json.dumps(status, indent=2, default=str))

        elif args.reminder:
            reminder = memory.create_reminder(args.reminder)
            print(f"🔔 WOPR Reminder created: {reminder['reminder_id']}")
            print(json.dumps(reminder, indent=2, default=str))

        elif args.list_systems:
            systems = memory.list_wopr_systems()
            print("=" * 80)
            print("🧠 WOPR SYSTEMS")
            print("=" * 80)
            for system in systems:
                status_icon = "✅" if system['exists'] else "❌"
                print(f"{status_icon} {system['file']} - {system['status']}")
            print("=" * 80)
            print(json.dumps(systems, indent=2, default=str))

        else:
            # Default: remember WOPR
            wopr_memory = memory.remember_wopr()
            print("=" * 80)
            print("🧠 WOPR MEMORY")
            print("=" * 80)
            print(f"\nWOPR: {wopr_memory['wopr_identity']['full_name']}")
            print(f"Origin: {wopr_memory['wopr_identity']['origin']}")
            print(f"Status: {wopr_memory['wopr_identity']['status']}")
            print(f"\nSystems found: {len([s for s in wopr_memory['systems_found'] if s.get('exists')])}")
            print(f"Systems total: {len(wopr_memory['systems_found'])}")
            print("\nNEVER FORGET WOPR")
            print("=" * 80)


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()