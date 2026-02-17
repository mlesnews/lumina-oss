#!/usr/bin/env python3
"""
Execute EWTN Sermon TIME Extraction - Complete @ask @chains Workflow
Connects all @ask @chains and executes complete extraction workflow

@SYPHON @EWTN @YOUTUBE @SOURCES @DOIT @CHAINS
"""

import sys
import asyncio
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional

script_dir = Path(__file__).parent
sys.path.insert(0, str(script_dir))
project_root = script_dir.parent.parent

try:
    from lumina_logger import get_logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("EWTNExtractionChain")


class EWTNExtractionChain:
    """
    Complete EWTN Extraction Workflow Chain

    Chain Steps:
    1. Discover @asks related to EWTN extraction
    2. Search for EWTN sermon on TIME
    3. Extract with SYPHON
    4. Ingest to R5
    5. Update TODO
    6. Process @asks through unified system
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize extraction chain"""
        self.project_root = project_root or Path(__file__).parent.parent.parent
        self.results = {
            "chain_steps": [],
            "started_at": datetime.now().isoformat(),
            "success": False
        }

        logger.info("✅ EWTN Extraction Chain initialized")

    async def execute_complete_chain(self, youtube_url: Optional[str] = None) -> Dict[str, Any]:
        """Execute complete extraction chain"""
        logger.info("=" * 80)
        logger.info("🔗 EXECUTING EWTN EXTRACTION CHAIN - @DOIT")
        logger.info("=" * 80)

        try:
            # STEP 1: Connect @ask @chains - Discover
            logger.info("\n🔗 STEP 1: Connecting @ask @chains - Discover")
            await self._step_discover_asks()

            # STEP 2: Search for EWTN sermon (if URL not provided)
            logger.info("\n🔗 STEP 2: Searching for EWTN sermon on TIME")
            if not youtube_url:
                youtube_url = await self._step_search_ewtn_sermon()

            if not youtube_url:
                logger.warning("⚠️  No YouTube URL found - cannot proceed with extraction")
                self.results["success"] = False
                return self.results

            # STEP 3: Extract with SYPHON
            logger.info(f"\n🔗 STEP 3: Extracting with SYPHON from {youtube_url}")
            extraction_result = await self._step_syphon_extraction(youtube_url)

            # STEP 4: Ingest to R5
            logger.info("\n🔗 STEP 4: Ingesting to R5 Living Context Matrix")
            r5_result = await self._step_r5_ingestion(extraction_result)

            # STEP 5: Update TODO
            logger.info("\n🔗 STEP 5: Updating TODO status")
            todo_result = await self._step_update_todo(extraction_result)

            # STEP 6: Process @asks through unified system
            logger.info("\n🔗 STEP 6: Processing @asks through unified system")
            asks_result = await self._step_process_asks(extraction_result)

            self.results["completed_at"] = datetime.now().isoformat()
            self.results["success"] = True
            self.results["youtube_url"] = youtube_url
            self.results["extraction_result"] = extraction_result
            self.results["r5_result"] = r5_result
            self.results["todo_result"] = todo_result
            self.results["asks_result"] = asks_result

            logger.info("\n" + "=" * 80)
            logger.info("✅ EWTN EXTRACTION CHAIN COMPLETE - @DOIT")
            logger.info("=" * 80)

        except Exception as e:
            logger.error(f"❌ Chain execution error: {e}", exc_info=True)
            self.results["error"] = str(e)
            self.results["success"] = False

        return self.results

    async def _step_discover_asks(self):
        """Step 1: Discover @asks related to EWTN extraction"""
        try:
            # Try to import @ask system
            try:
                from jarvis_restack_all_asks import ASKRestacker
                restacker = ASKRestacker(project_root=self.project_root)
                all_asks = restacker.discover_all_asks()

                # Filter for EWTN-related asks
                ewtn_asks = [ask for ask in all_asks if any(
                    keyword in str(ask).lower() 
                    for keyword in ['ewtn', 'sermon', 'time', 'extract', 'syphon']
                )]

                logger.info(f"   ✅ Discovered {len(all_asks)} total @asks")
                logger.info(f"   ✅ Found {len(ewtn_asks)} EWTN-related @asks")

                self.results["chain_steps"].append({
                    "step": 1,
                    "name": "Discover @asks",
                    "status": "success",
                    "total_asks": len(all_asks),
                    "ewtn_asks": len(ewtn_asks)
                })

            except ImportError:
                logger.info("   ⚠️  @ask system not available - skipping")
                self.results["chain_steps"].append({
                    "step": 1,
                    "name": "Discover @asks",
                    "status": "skipped",
                    "reason": "System not available"
                })
        except Exception as e:
            logger.warning(f"   ⚠️  Error in discover step: {e}")
            self.results["chain_steps"].append({
                "step": 1,
                "name": "Discover @asks",
                "status": "error",
                "error": str(e)
            })

    async def _step_search_ewtn_sermon(self) -> Optional[str]:
        """Step 2: Search for EWTN sermon on TIME"""
        try:
            import subprocess

            # Try to use yt-dlp to search
            channel_url = "https://www.youtube.com/@EWTN"
            cmd = [
                'yt-dlp',
                '--flat-playlist',
                '--print', '%(id)s|%(title)s',
                f'{channel_url}/search?query=sermon+time',
                '--max-downloads', '20'
            ]

            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            if result.returncode == 0:
                videos = []
                for line in result.stdout.strip().split('\n'):
                    if '|' in line:
                        parts = line.split('|', 1)
                        if len(parts) >= 2:
                            video_id = parts[0]
                            title = parts[1]
                            if 'time' in title.lower() or 'TIME' in title:
                                url = f"https://www.youtube.com/watch?v={video_id}"
                                videos.append({"id": video_id, "title": title, "url": url})

                if videos:
                    selected = videos[0]  # Use first match
                    logger.info(f"   ✅ Found: {selected['title']}")
                    logger.info(f"   📹 URL: {selected['url']}")

                    self.results["chain_steps"].append({
                        "step": 2,
                        "name": "Search EWTN Sermon",
                        "status": "success",
                        "video_title": selected['title'],
                        "video_url": selected['url']
                    })

                    return selected['url']

            logger.warning("   ⚠️  Could not automatically find sermon")
            self.results["chain_steps"].append({
                "step": 2,
                "name": "Search EWTN Sermon",
                "status": "partial",
                "message": "Manual URL required"
            })
            return None

        except Exception as e:
            logger.warning(f"   ⚠️  Search error: {e}")
            self.results["chain_steps"].append({
                "step": 2,
                "name": "Search EWTN Sermon",
                "status": "error",
                "error": str(e)
            })
            return None

    async def _step_syphon_extraction(self, youtube_url: str) -> Dict[str, Any]:
        """Step 3: Extract with SYPHON"""
        try:
            from syphon.core import SYPHONSystem, SYPHONConfig, SubscriptionTier
            from syphon.models import DataSourceType

            syphon = SYPHONSystem(SYPHONConfig(
                project_root=self.project_root,
                subscription_tier=SubscriptionTier.ENTERPRISE
            ))

            metadata = {
                "title": "EWTN Sermon on TIME",
                "source": "EWTN",
                "topic": "TIME",
                "url": youtube_url,
                "provider": "Comcast/Xfinity/YouTubeTV",
                "extraction_date": datetime.now().isoformat()
            }

            logger.info("   🔍 SYPHON: Extracting intelligence...")
            result = syphon.extract(DataSourceType.SOCIAL, youtube_url, metadata)

            if result.success and result.data:
                syphon_data = result.data
                logger.info(f"   ✅ Extracted: {len(syphon_data.actionable_items)} actionable items")
                logger.info(f"   ✅ Tasks: {len(syphon_data.tasks)}")
                logger.info(f"   ✅ Intelligence: {len(syphon_data.intelligence)}")

                self.results["chain_steps"].append({
                    "step": 3,
                    "name": "SYPHON Extraction",
                    "status": "success",
                    "actionable_items": len(syphon_data.actionable_items),
                    "tasks": len(syphon_data.tasks),
                    "intelligence": len(syphon_data.intelligence)
                })

                return {
                    "success": True,
                    "syphon_data": syphon_data,
                    "actionable_items": syphon_data.actionable_items,
                    "tasks": syphon_data.tasks,
                    "intelligence": syphon_data.intelligence
                }
            else:
                raise Exception(result.error or "SYPHON extraction failed")

        except Exception as e:
            logger.error(f"   ❌ SYPHON extraction error: {e}")
            self.results["chain_steps"].append({
                "step": 3,
                "name": "SYPHON Extraction",
                "status": "error",
                "error": str(e)
            })
            return {"success": False, "error": str(e)}

    async def _step_r5_ingestion(self, extraction_result: Dict[str, Any]) -> Dict[str, Any]:
        """Step 4: Ingest to R5"""
        try:
            if not extraction_result.get("success"):
                return {"success": False, "error": "No extraction data"}

            from r5_living_context_matrix import R5LivingContextMatrix
            syphon_data = extraction_result["syphon_data"]

            r5 = R5LivingContextMatrix(project_root=self.project_root)

            session_id = r5.ingest_session({
                "session_id": f"ewtn_sermon_time_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                "session_type": "ewtn_sermon_extraction",
                "timestamp": datetime.now().isoformat(),
                "content": syphon_data.content,
                "metadata": {
                    **syphon_data.metadata,
                    "actionable_items": syphon_data.actionable_items,
                    "tasks": syphon_data.tasks,
                    "intelligence": syphon_data.intelligence
                }
            })

            logger.info(f"   ✅ Ingested to R5: {session_id}")

            self.results["chain_steps"].append({
                "step": 4,
                "name": "R5 Ingestion",
                "status": "success",
                "session_id": session_id
            })

            return {"success": True, "session_id": session_id}

        except Exception as e:
            logger.error(f"   ❌ R5 ingestion error: {e}")
            self.results["chain_steps"].append({
                "step": 4,
                "name": "R5 Ingestion",
                "status": "error",
                "error": str(e)
            })
            return {"success": False, "error": str(e)}

    async def _step_update_todo(self, extraction_result: Dict[str, Any]) -> Dict[str, Any]:
        """Step 5: Update TODO"""
        try:
            from master_todo_tracker import MasterTodoTracker, TaskStatus

            tracker = MasterTodoTracker(project_root=self.project_root)
            todos = tracker.get_todos()

            # Find EWTN TODO
            ewtn_todo = next((t for t in todos if 'EWTN' in t.title and 'TIME' in t.title), None)

            if ewtn_todo:
                if extraction_result.get("success"):
                    tracker.update_status(ewtn_todo.id, TaskStatus.IN_PROGRESS)
                    logger.info(f"   ✅ Updated TODO: {ewtn_todo.title} -> IN_PROGRESS")
                else:
                    logger.info(f"   ⚠️  TODO not updated - extraction failed")

                self.results["chain_steps"].append({
                    "step": 5,
                    "name": "Update TODO",
                    "status": "success",
                    "todo_id": ewtn_todo.id
                })

                return {"success": True, "todo_id": ewtn_todo.id}
            else:
                logger.warning("   ⚠️  EWTN TODO not found")
                return {"success": False, "error": "TODO not found"}

        except Exception as e:
            logger.warning(f"   ⚠️  DONE update error: {e}")
            return {"success": False, "error": str(e)}

    async def _step_process_asks(self, extraction_result: Dict[str, Any]) -> Dict[str, Any]:
        """Step 6: Process @asks through unified system"""
        try:
            # Try to process through unified system
            try:
                from syphon_agents_asks_unified_system import SYPHONAgentsAsksUnifiedSystem

                system = SYPHONAgentsAsksUnifiedSystem(project_root=self.project_root)
                system._process_asks()

                logger.info("   ✅ @asks processed through unified system")

                self.results["chain_steps"].append({
                    "step": 6,
                    "name": "Process @asks",
                    "status": "success"
                })

                return {"success": True}

            except ImportError:
                logger.info("   ⚠️  Unified system not available - skipping")
                return {"success": False, "error": "System not available"}

        except Exception as e:
            logger.warning(f"   ⚠️  @asks processing error: {e}")
            return {"success": False, "error": str(e)}


async def main():
    """Main execution"""
    import sys

    # Get URL from command line if provided
    youtube_url = sys.argv[1] if len(sys.argv) > 1 else None

    chain = EWTNExtractionChain()
    results = await chain.execute_complete_chain(youtube_url=youtube_url)

    # Print summary
    print("\n" + "=" * 80)
    print("📊 EXTRACTION CHAIN SUMMARY")
    print("=" * 80)
    print(f"Success: {results['success']}")
    print(f"Steps Completed: {len(results['chain_steps'])}")

    for step in results['chain_steps']:
        status_icon = "✅" if step['status'] == 'success' else "⚠️" if step['status'] == 'partial' else "❌"
        print(f"{status_icon} Step {step['step']}: {step['name']} - {step['status']}")

    if results.get('extraction_result', {}).get('success'):
        ext = results['extraction_result']
        print(f"\n📊 Extraction Stats:")
        print(f"   Actionable Items: {len(ext.get('actionable_items', []))}")
        print(f"   Tasks: {len(ext.get('tasks', []))}")
        print(f"   Intelligence Points: {len(ext.get('intelligence', []))}")

    if results.get('r5_result', {}).get('success'):
        print(f"\n📚 R5 Session: {results['r5_result']['session_id']}")

    return 0 if results['success'] else 1


if __name__ == "__main__":


    sys.exit(asyncio.run(main()))