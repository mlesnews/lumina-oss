"""
HVAC Bid n8n Workflow Helper
Creates/triggers n8n workflow to search Gmail for contractor bids.

#JARVIS #LUMINA #N8N
"""

import json
import logging
import os
from pathlib import Path
from typing import Dict, List, Optional, Any

try:
    from scripts.python.lumina_logger import get_logger
    logger = get_logger("HVACN8NBidWorkflow")
except ImportError:
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("HVACN8NBidWorkflow")


class HVACN8NBidWorkflow:
    """Helper for n8n workflow to search Gmail for HVAC bids."""

    def __init__(self, project_root: Path):
        """
        Initialize n8n workflow helper.

        Args:
            project_root: Root path of the LUMINA project
        """
        self.project_root = Path(project_root)
        self.config_dir = self.project_root / "config" / "n8n"
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self.n8n_url = os.getenv("N8N_URL", "http://localhost:5678")

    def create_gmail_bid_search_workflow(self) -> Dict[str, Any]:
        try:
            """
            Create n8n workflow configuration for Gmail bid search.

            Returns:
                Workflow configuration dictionary
            """
            workflow = {
                "name": "HVAC Bid Gmail Search",
                "nodes": [
                    {
                        "parameters": {},
                        "id": "webhook-trigger",
                        "name": "Webhook - Trigger Search",
                        "type": "n8n-nodes-base.webhook",
                        "typeVersion": 1,
                        "position": [250, 300],
                        "webhookId": "hvac-bid-search"
                    },
                    {
                        "parameters": {
                            "authentication": "oAuth2",
                            "resource": "message",
                            "operation": "search",
                            "returnAll": False,
                            "limit": 50,
                            "simple": False,
                            "options": {
                                "q": "={{$json.query}}"
                            }
                        },
                        "id": "gmail-search",
                        "name": "Gmail - Search Messages",
                        "type": "n8n-nodes-base.gmail",
                        "typeVersion": 1,
                        "position": [450, 300],
                        "credentials": {
                            "gmailOAuth2": {
                                "id": "1",
                                "name": "Gmail OAuth2"
                            }
                        }
                    },
                    {
                        "parameters": {
                            "operation": "get",
                            "messageId": "={{$json.id}}",
                            "options": {
                                "format": "full"
                            }
                        },
                        "id": "gmail-get",
                        "name": "Gmail - Get Message",
                        "type": "n8n-nodes-base.gmail",
                        "typeVersion": 1,
                        "position": [650, 300],
                        "credentials": {
                            "gmailOAuth2": {
                                "id": "1",
                                "name": "Gmail OAuth2"
                            }
                        }
                    },
                    {
                        "parameters": {
                            "operation": "download",
                            "messageId": "={{$json.id}}",
                            "attachmentId": "={{$json.attachmentId}}"
                        },
                        "id": "gmail-attachment",
                        "name": "Gmail - Download Attachment",
                        "type": "n8n-nodes-base.gmail",
                        "typeVersion": 1,
                        "position": [850, 300],
                        "credentials": {
                            "gmailOAuth2": {
                                "id": "1",
                                "name": "Gmail OAuth2"
                            }
                        }
                    },
                    {
                        "parameters": {
                            "operation": "write",
                            "fileName": "={{$json.filename}}",
                            "dataPropertyName": "data",
                            "options": {}
                        },
                        "id": "write-file",
                        "name": "Write Binary File",
                        "type": "n8n-nodes-base.writeBinaryFile",
                        "typeVersion": 1,
                        "position": [1050, 300],
                        "parameters": {
                            "fileName": "={{$json.filename}}",
                            "filePath": "={{$env.PROJECT_ROOT}}/data/hvac_bids/attachments/",
                            "dataPropertyName": "data"
                        }
                    },
                    {
                        "parameters": {
                            "url": "http://localhost:8000/api/hvac/extract-bid",
                            "sendBody": True,
                            "specifyBody": "json",
                            "jsonBody": "={{JSON.stringify($json)}}",
                            "options": {}
                        },
                        "id": "extract-bid",
                        "name": "Extract Bid Info",
                        "type": "n8n-nodes-base.httpRequest",
                        "typeVersion": 1,
                        "position": [1250, 300]
                    }
                ],
                "connections": {
                    "webhook-trigger": {
                        "main": [[{"node": "gmail-search", "type": "main", "index": 0}]]
                    },
                    "gmail-search": {
                        "main": [[{"node": "gmail-get", "type": "main", "index": 0}]]
                    },
                    "gmail-get": {
                        "main": [[{"node": "gmail-attachment", "type": "main", "index": 0}]]
                    },
                    "gmail-attachment": {
                        "main": [[{"node": "write-file", "type": "main", "index": 0}]]
                    },
                    "write-file": {
                        "main": [[{"node": "extract-bid", "type": "main", "index": 0}]]
                    }
                },
                "pinData": {},
                "settings": {
                    "executionOrder": "v1"
                },
                "staticData": None,
                "tags": []
            }

            return workflow

        except Exception as e:
            self.logger.error(f"Error in create_gmail_bid_search_workflow: {e}", exc_info=True)
            raise
    def save_workflow_config(self) -> Path:
        try:
            """
            Save workflow configuration to file.

            Returns:
                Path to saved workflow file
            """
            workflow = self.create_gmail_bid_search_workflow()
            workflow_file = self.config_dir / "hvac_bid_gmail_search_workflow.json"

            with open(workflow_file, 'w') as f:
                json.dump(workflow, f, indent=2)

            logger.info(f"Saved workflow config to: {workflow_file}")
            return workflow_file

        except Exception as e:
            self.logger.error(f"Error in save_workflow_config: {e}", exc_info=True)
            raise
    def trigger_search(self, search_queries: List[str]) -> Dict[str, Any]:
        """
        Trigger n8n workflow to search Gmail.

        Args:
            search_queries: List of Gmail search queries

        Returns:
            Response from n8n
        """
        try:
            import requests

            # Combine queries
            combined_query = " OR ".join([f"({q})" for q in search_queries])
            combined_query += " has:attachment"

            # Trigger webhook
            webhook_url = f"{self.n8n_url}/webhook/hvac-bid-search"

            response = requests.post(
                webhook_url,
                json={"query": combined_query},
                timeout=30
            )

            if response.status_code == 200:
                logger.info("Successfully triggered n8n workflow")
                return {"success": True, "data": response.json()}
            else:
                logger.error(f"n8n workflow returned status {response.status_code}")
                return {"success": False, "error": f"Status {response.status_code}"}

        except ImportError:
            logger.error("requests library not installed")
            return {"success": False, "error": "requests library required"}
        except Exception as e:
            logger.error(f"Error triggering n8n workflow: {e}")
            return {"success": False, "error": str(e)}


def main():
    try:
        """Main function."""
        import argparse

        parser = argparse.ArgumentParser(description="HVAC Bid n8n Workflow Helper")
        parser.add_argument("--project-root", type=Path,
                           default=Path(__file__).parent.parent.parent,
                           help="Project root directory")
        parser.add_argument("--create-workflow", action="store_true",
                           help="Create n8n workflow configuration file")
        parser.add_argument("--trigger-search", nargs="+",
                           help="Trigger search with Gmail queries")
        parser.add_argument("--contractor-emails", nargs="+",
                           help="Contractor email addresses")

        args = parser.parse_args()

        workflow_helper = HVACN8NBidWorkflow(args.project_root)

        if args.create_workflow:
            workflow_file = workflow_helper.save_workflow_config()
            print(f"✓ Created workflow config: {workflow_file}")
            print("\nNext steps:")
            print("1. Import this workflow into n8n")
            print("2. Configure Gmail OAuth2 credentials in n8n")
            print("3. Set PROJECT_ROOT environment variable")
            print("4. Activate the workflow")

        if args.trigger_search:
            queries = args.trigger_search
            if args.contractor_emails:
                queries.extend([f"from:{email}" for email in args.contractor_emails])

            result = workflow_helper.trigger_search(queries)
            if result.get("success"):
                print("✓ Workflow triggered successfully")
            else:
                print(f"✗ Error: {result.get('error')}")


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()