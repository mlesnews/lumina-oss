#!/usr/bin/env python3
"""
Deploy SYPHON N8N Workflows to NAS

Deploys comprehensive N8N workflows for all SYPHON sources:
- Email (all accounts)
- SMS (all sources)
- Social-News-Education (white papers, thesis, education)

All workflows run on N8N@NAS (<NAS_PRIMARY_IP>:5678)

Tags: #SYPHON #N8N #NAS #WORKFLOWS #EMAIL #SMS #EDUCATION @JARVIS @LUMINA
"""

import sys
import json
import requests
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("DeploySyphonN8NWorkflowsNAS")


class SyphonN8NWorkflowDeployer:
    """Deploy SYPHON workflows to N8N on NAS"""

    def __init__(self, nas_ip: str = "<NAS_PRIMARY_IP>", n8n_port: int = None):
        """Initialize deployer"""
        self.nas_ip = nas_ip
        # Auto-detect port if not provided
        if n8n_port is None:
            n8n_port = self._detect_n8n_port()
        self.n8n_port = n8n_port
        self.n8n_base_url = f"http://{nas_ip}:{n8n_port}"
        self.n8n_api_url = f"{self.n8n_base_url}/api/v1"
        self.n8n_webhook_base = f"{self.n8n_base_url}/webhook"

        # Data directory
        self.data_dir = project_root / "data" / "n8n_syphon_workflows"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # Workflow registry
        self.workflows: Dict[str, Dict[str, Any]] = {}
        self.workflows_file = self.data_dir / "deployed_workflows.json"
        self._load_workflows()

        logger.info(f"✅ SYPHON N8N Workflow Deployer initialized")
        logger.info(f"   N8N URL: {self.n8n_base_url}")

    def _load_workflows(self):
        """Load deployed workflows registry"""
        if self.workflows_file.exists():
            try:
                with open(self.workflows_file, 'r', encoding='utf-8') as f:
                    self.workflows = json.load(f)
            except Exception as e:
                logger.debug(f"Could not load workflows: {e}")

    def _save_workflows(self):
        """Save workflows registry"""
        try:
            with open(self.workflows_file, 'w', encoding='utf-8') as f:
                json.dump(self.workflows, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving workflows: {e}")

    def _detect_n8n_port(self) -> int:
        """Detect N8N port by trying common ports"""
        ports = [5000, 5678, 8080, 3000, 5001]
        for port in ports:
            try:
                url = f"http://{self.nas_ip}:{port}"
                response = requests.get(url, timeout=2, verify=False)
                if response.status_code < 500:
                    # Check if it's N8N
                    if "n8n" in response.text.lower() or response.status_code == 200:
                        logger.info(f"   ✅ Detected N8N on port {port}")
                        return port
            except:
                continue
        # Default to 5678 if not found
        return 5678

    def _check_n8n_connection(self) -> bool:
        """Check if N8N is accessible"""
        try:
            # Try multiple endpoints
            endpoints = ["/healthz", "/health", "/", "/rest/settings"]
            for endpoint in endpoints:
                try:
                    response = requests.get(f"{self.n8n_base_url}{endpoint}", timeout=5, verify=False)
                    if response.status_code < 500:
                        return True
                except:
                    continue
            return False
        except:
            return False

    def create_email_syphon_workflow(self) -> Dict[str, Any]:
        """Create N8N workflow for email SYPHON"""
        workflow = {
            "name": "SYPHON Email Intelligence Extraction",
            "nodes": [
                {
                    "parameters": {
                        "rule": {
                            "interval": [
                                {
                                    "field": "hours",
                                    "hoursInterval": 2
                                }
                            ]
                        }
                    },
                    "id": "email_schedule_trigger",
                    "name": "Email Schedule Trigger",
                    "type": "n8n-nodes-base.scheduleTrigger",
                    "typeVersion": 1,
                    "position": [250, 300]
                },
                {
                    "parameters": {
                        "authentication": "predefinedCredentialType",
                        "nodeCredentialType": "imap",
                        "operation": "getAll",
                        "options": {
                            "allowUnauthorizedCerts": True
                        }
                    },
                    "id": "email_fetch",
                    "name": "Fetch All Emails",
                    "type": "n8n-nodes-base.emailReadImap",
                    "typeVersion": 1,
                    "position": [450, 300],
                    "credentials": {
                        "imap": {
                            "id": "1",
                            "name": "NAS Email Account"
                        }
                    }
                },
                {
                    "parameters": {
                        "jsCode": """
// Process each email for SYPHON extraction
const emails = $input.all();
const results = [];

for (const email of emails) {
  const emailData = {
    email_id: email.json.messageId || email.json.uid,
    subject: email.json.subject || '',
    body: email.json.text || email.json.html || '',
    from: email.json.from?.text || email.json.from || '',
    to: email.json.to?.text || email.json.to || '',
    date: email.json.date,
    metadata: {
      uid: email.json.uid,
      flags: email.json.flags,
      attachments: email.json.attachments || []
    }
  };
  results.push({ json: emailData });
}

return results;
"""
                    },
                    "id": "email_format",
                    "name": "Format Email Data",
                    "type": "n8n-nodes-base.code",
                    "typeVersion": 2,
                    "position": [650, 300]
                },
                {
                    "parameters": {
                        "url": "http://<NAS_IP>:8000/api/syphon/email",
                        "method": "POST",
                        "sendBody": True,
                        "bodyParameters": {
                            "parameters": [
                                {
                                    "name": "email_id",
                                    "value": "={{ $json.email_id }}"
                                },
                                {
                                    "name": "subject",
                                    "value": "={{ $json.subject }}"
                                },
                                {
                                    "name": "body",
                                    "value": "={{ $json.body }}"
                                },
                                {
                                    "name": "from",
                                    "value": "={{ $json.from }}"
                                },
                                {
                                    "name": "to",
                                    "value": "={{ $json.to }}"
                                },
                                {
                                    "name": "metadata",
                                    "value": "={{ $json.metadata }}"
                                }
                            ]
                        },
                        "options": {}
                    },
                    "id": "syphon_extract",
                    "name": "SYPHON Extract Intelligence",
                    "type": "n8n-nodes-base.httpRequest",
                    "typeVersion": 4.1,
                    "position": [850, 300]
                },
                {
                    "parameters": {
                        "conditions": {
                            "options": {
                                "caseSensitive": True,
                                "leftValue": "",
                                "typeValidation": "strict"
                            },
                            "conditions": [
                                {
                                    "id": "success_check",
                                    "leftValue": "={{ $json.success }}",
                                    "rightValue": True,
                                    "operator": {
                                        "type": "boolean",
                                        "operation": "true"
                                    }
                                }
                            ],
                            "combinator": "and"
                        },
                        "options": {}
                    },
                    "id": "check_success",
                    "name": "Check Success",
                    "type": "n8n-nodes-base.if",
                    "typeVersion": 2,
                    "position": [1050, 300]
                },
                {
                    "parameters": {
                        "operation": "append",
                        "fileName": "=/data/syphon/email_intelligence/{{ $now.format('YYYY-MM-DD') }}_email_intelligence.jsonl",
                        "dataPropertyName": "json",
                        "options": {
                            "append": True
                        }
                    },
                    "id": "save_intelligence",
                    "name": "Save Intelligence",
                    "type": "n8n-nodes-base.writeBinaryFile",
                    "typeVersion": 1,
                    "position": [1250, 200]
                },
                {
                    "parameters": {
                        "url": "http://<NAS_IP>:8000/api/unified-queue/add",
                        "method": "POST",
                        "sendBody": True,
                        "bodyParameters": {
                            "parameters": [
                                {
                                    "name": "item_type",
                                    "value": "intelligence"
                                },
                                {
                                    "name": "title",
                                    "value": "={{ $json.syphon_data.title || $('Format Email Data').json.subject }}"
                                },
                                {
                                    "name": "content",
                                    "value": "={{ JSON.stringify($json.syphon_data) }}"
                                },
                                {
                                    "name": "priority",
                                    "value": "medium"
                                },
                                {
                                    "name": "tags",
                                    "value": "['email', 'syphon', 'intelligence']"
                                }
                            ]
                        }
                    },
                    "id": "add_to_queue",
                    "name": "Add to Unified Queue",
                    "type": "n8n-nodes-base.httpRequest",
                    "typeVersion": 4.1,
                    "position": [1250, 400]
                }
            ],
            "connections": {
                "email_schedule_trigger": {
                    "main": [[{"node": "email_fetch", "type": "main", "index": 0}]]
                },
                "email_fetch": {
                    "main": [[{"node": "email_format", "type": "main", "index": 0}]]
                },
                "email_format": {
                    "main": [[{"node": "syphon_extract", "type": "main", "index": 0}]]
                },
                "syphon_extract": {
                    "main": [[{"node": "check_success", "type": "main", "index": 0}]]
                },
                "check_success": {
                    "main": [
                        [{"node": "save_intelligence", "type": "main", "index": 0}],
                        [{"node": "add_to_queue", "type": "main", "index": 0}]
                    ]
                }
            },
            "pinData": {},
            "settings": {
                "executionOrder": "v1"
            },
            "staticData": None,
            "tags": [
                {
                    "createdAt": datetime.now().isoformat(),
                    "updatedAt": datetime.now().isoformat(),
                    "id": "syphon",
                    "name": "SYPHON"
                },
                {
                    "createdAt": datetime.now().isoformat(),
                    "updatedAt": datetime.now().isoformat(),
                    "id": "email",
                    "name": "Email"
                }
            ],
            "triggerCount": 0,
            "updatedAt": datetime.now().isoformat(),
            "versionId": "1"
        }
        return workflow

    def create_sms_syphon_workflow(self) -> Dict[str, Any]:
        """Create N8N workflow for SMS SYPHON"""
        workflow = {
            "name": "SYPHON SMS Intelligence Extraction",
            "nodes": [
                {
                    "parameters": {
                        "rule": {
                            "interval": [
                                {
                                    "field": "hours",
                                    "hoursInterval": 3
                                }
                            ]
                        }
                    },
                    "id": "sms_schedule_trigger",
                    "name": "SMS Schedule Trigger",
                    "type": "n8n-nodes-base.scheduleTrigger",
                    "typeVersion": 1,
                    "position": [250, 300]
                },
                {
                    "parameters": {
                        "httpMethod": "POST",
                        "path": "sms/syphon",
                        "responseMode": "responseNode",
                        "options": {}
                    },
                    "id": "sms_webhook",
                    "name": "SMS Webhook Receiver",
                    "type": "n8n-nodes-base.webhook",
                    "typeVersion": 2,
                    "position": [450, 300],
                    "webhookId": "sms-syphon-webhook"
                },
                {
                    "parameters": {
                        "jsCode": """
// Process SMS for SYPHON extraction
const smsData = {
  sms_id: $json.body?.sms_id || $json.body?.id || Date.now().toString(),
  message: $json.body?.message || $json.body?.text || '',
  from: $json.body?.from || $json.body?.sender || '',
  to: $json.body?.to || $json.body?.recipient || '',
  timestamp: $json.body?.timestamp || new Date().toISOString(),
  metadata: $json.body?.metadata || {}
};

return { json: smsData };
"""
                    },
                    "id": "sms_format",
                    "name": "Format SMS Data",
                    "type": "n8n-nodes-base.code",
                    "typeVersion": 2,
                    "position": [650, 300]
                },
                {
                    "parameters": {
                        "url": "http://<NAS_IP>:8000/api/syphon/sms",
                        "method": "POST",
                        "sendBody": True,
                        "bodyParameters": {
                            "parameters": [
                                {
                                    "name": "sms_id",
                                    "value": "={{ $json.sms_id }}"
                                },
                                {
                                    "name": "message",
                                    "value": "={{ $json.message }}"
                                },
                                {
                                    "name": "from",
                                    "value": "={{ $json.from }}"
                                },
                                {
                                    "name": "to",
                                    "value": "={{ $json.to }}"
                                },
                                {
                                    "name": "metadata",
                                    "value": "={{ $json.metadata }}"
                                }
                            ]
                        }
                    },
                    "id": "syphon_extract_sms",
                    "name": "SYPHON Extract Intelligence",
                    "type": "n8n-nodes-base.httpRequest",
                    "typeVersion": 4.1,
                    "position": [850, 300]
                },
                {
                    "parameters": {
                        "operation": "append",
                        "fileName": "=/data/syphon/sms_intelligence/{{ $now.format('YYYY-MM-DD') }}_sms_intelligence.jsonl",
                        "dataPropertyName": "json",
                        "options": {
                            "append": True
                        }
                    },
                    "id": "save_sms_intelligence",
                    "name": "Save SMS Intelligence",
                    "type": "n8n-nodes-base.writeBinaryFile",
                    "typeVersion": 1,
                    "position": [1050, 200]
                },
                {
                    "parameters": {
                        "url": "http://<NAS_IP>:8000/api/unified-queue/add",
                        "method": "POST",
                        "sendBody": True,
                        "bodyParameters": {
                            "parameters": [
                                {
                                    "name": "item_type",
                                    "value": "intelligence"
                                },
                                {
                                    "name": "title",
                                    "value": "SMS Intelligence: {{ $json.sms_id }}"
                                },
                                {
                                    "name": "content",
                                    "value": "={{ JSON.stringify($json.syphon_data) }}"
                                },
                                {
                                    "name": "priority",
                                    "value": "medium"
                                },
                                {
                                    "name": "tags",
                                    "value": "['sms', 'syphon', 'intelligence']"
                                }
                            ]
                        }
                    },
                    "id": "add_sms_to_queue",
                    "name": "Add to Unified Queue",
                    "type": "n8n-nodes-base.httpRequest",
                    "typeVersion": 4.1,
                    "position": [1050, 400]
                }
            ],
            "connections": {
                "sms_webhook": {
                    "main": [[{"node": "sms_format", "type": "main", "index": 0}]]
                },
                "sms_format": {
                    "main": [[{"node": "syphon_extract_sms", "type": "main", "index": 0}]]
                },
                "syphon_extract_sms": {
                    "main": [
                        [{"node": "save_sms_intelligence", "type": "main", "index": 0}],
                        [{"node": "add_sms_to_queue", "type": "main", "index": 0}]
                    ]
                }
            },
            "tags": [
                {"id": "syphon", "name": "SYPHON"},
                {"id": "sms", "name": "SMS"}
            ]
        }
        return workflow

    def create_social_news_education_workflow(self) -> Dict[str, Any]:
        """Create N8N workflow for social-news-education SYPHON (white papers, thesis)"""
        workflow = {
            "name": "SYPHON Social-News-Education Intelligence Extraction",
            "nodes": [
                {
                    "parameters": {
                        "rule": {
                            "interval": [
                                {
                                    "field": "hours",
                                    "hoursInterval": 6
                                }
                            ]
                        }
                    },
                    "id": "education_schedule_trigger",
                    "name": "Education Schedule Trigger",
                    "type": "n8n-nodes-base.scheduleTrigger",
                    "typeVersion": 1,
                    "position": [250, 300]
                },
                {
                    "parameters": {
                        "url": "https://arxiv.org/search/advanced",
                        "method": "GET",
                        "options": {
                            "queryParameters": {
                                "parameters": [
                                    {
                                        "name": "query",
                                        "value": "white paper OR thesis OR research paper"
                                    },
                                    {
                                        "name": "searchtype",
                                        "value": "all"
                                    },
                                    {
                                        "name": "order",
                                        "value": "-submittedDate"
                                    },
                                    {
                                        "name": "size",
                                        "value": "50"
                                    }
                                ]
                            }
                        }
                    },
                    "id": "fetch_arxiv",
                    "name": "Fetch ArXiv Papers",
                    "type": "n8n-nodes-base.httpRequest",
                    "typeVersion": 4.1,
                    "position": [450, 200]
                },
                {
                    "parameters": {
                        "url": "https://api.researchgate.net/v2/publications",
                        "method": "GET",
                        "options": {
                            "queryParameters": {
                                "parameters": [
                                    {
                                        "name": "query",
                                        "value": "white paper thesis research"
                                    },
                                    {
                                        "name": "limit",
                                        "value": "50"
                                    }
                                ]
                            }
                        }
                    },
                    "id": "fetch_researchgate",
                    "name": "Fetch ResearchGate",
                    "type": "n8n-nodes-base.httpRequest",
                    "typeVersion": 4.1,
                    "position": [450, 300]
                },
                {
                    "parameters": {
                        "url": "https://www.google.com/search",
                        "method": "GET",
                        "options": {
                            "queryParameters": {
                                "parameters": [
                                    {
                                        "name": "q",
                                        "value": "filetype:pdf (white paper OR thesis OR research paper)"
                                    },
                                    {
                                        "name": "num",
                                        "value": "50"
                                    }
                                ]
                            }
                        }
                    },
                    "id": "fetch_web_sources",
                    "name": "Fetch Web Sources",
                    "type": "n8n-nodes-base.httpRequest",
                    "typeVersion": 4.1,
                    "position": [450, 400]
                },
                {
                    "parameters": {
                        "jsCode": """
// Merge and format all education sources
const sources = [];
const arxiv = $input.first().json;
const researchgate = $input.item(1)?.json || {};
const web = $input.item(2)?.json || {};

// Process ArXiv results
if (arxiv.entries) {
  for (const entry of arxiv.entries) {
    sources.push({
      source_type: 'arxiv',
      title: entry.title,
      url: entry.id,
      content: entry.summary,
      authors: entry.authors,
      published: entry.published,
      category: 'white_paper'
    });
  }
}

// Process ResearchGate results
if (researchgate.data) {
  for (const pub of researchgate.data) {
    sources.push({
      source_type: 'researchgate',
      title: pub.title,
      url: pub.url,
      content: pub.abstract,
      authors: pub.authors,
      published: pub.publicationDate,
      category: 'thesis'
    });
  }
}

// Process web results (would need parsing)
// This is a placeholder - actual implementation would parse HTML

return sources.map(s => ({ json: s }));
"""
                    },
                    "id": "merge_sources",
                    "name": "Merge Education Sources",
                    "type": "n8n-nodes-base.code",
                    "typeVersion": 2,
                    "position": [650, 300]
                },
                {
                    "parameters": {
                        "url": "http://<NAS_IP>:8000/api/syphon/web",
                        "method": "POST",
                        "sendBody": True,
                        "bodyParameters": {
                            "parameters": [
                                {
                                    "name": "url",
                                    "value": "={{ $json.url }}"
                                },
                                {
                                    "name": "title",
                                    "value": "={{ $json.title }}"
                                },
                                {
                                    "name": "content",
                                    "value": "={{ $json.content }}"
                                },
                                {
                                    "name": "source_type",
                                    "value": "={{ $json.source_type }}"
                                },
                                {
                                    "name": "category",
                                    "value": "={{ $json.category }}"
                                },
                                {
                                    "name": "metadata",
                                    "value": "={{ JSON.stringify($json) }}"
                                }
                            ]
                        }
                    },
                    "id": "syphon_extract_education",
                    "name": "SYPHON Extract Intelligence",
                    "type": "n8n-nodes-base.httpRequest",
                    "typeVersion": 4.1,
                    "position": [850, 300]
                },
                {
                    "parameters": {
                        "operation": "append",
                        "fileName": "=/data/syphon/education_intelligence/{{ $now.format('YYYY-MM-DD') }}_education_intelligence.jsonl",
                        "dataPropertyName": "json",
                        "options": {
                            "append": True
                        }
                    },
                    "id": "save_education_intelligence",
                    "name": "Save Education Intelligence",
                    "type": "n8n-nodes-base.writeBinaryFile",
                    "typeVersion": 1,
                    "position": [1050, 200]
                },
                {
                    "parameters": {
                        "url": "http://<NAS_IP>:8000/api/unified-queue/add",
                        "method": "POST",
                        "sendBody": True,
                        "bodyParameters": {
                            "parameters": [
                                {
                                    "name": "item_type",
                                    "value": "intelligence"
                                },
                                {
                                    "name": "title",
                                    "value": "={{ $json.title }}"
                                },
                                {
                                    "name": "content",
                                    "value": "={{ JSON.stringify($json) }}"
                                },
                                {
                                    "name": "priority",
                                    "value": "low"
                                },
                                {
                                    "name": "tags",
                                    "value": "=['education', 'white_paper', 'thesis', 'syphon', 'intelligence']"
                                }
                            ]
                        }
                    },
                    "id": "add_education_to_queue",
                    "name": "Add to Unified Queue",
                    "type": "n8n-nodes-base.httpRequest",
                    "typeVersion": 4.1,
                    "position": [1050, 400]
                }
            ],
            "connections": {
                "education_schedule_trigger": {
                    "main": [
                        [{"node": "fetch_arxiv", "type": "main", "index": 0}],
                        [{"node": "fetch_researchgate", "type": "main", "index": 0}],
                        [{"node": "fetch_web_sources", "type": "main", "index": 0}]
                    ]
                },
                "fetch_arxiv": {
                    "main": [[{"node": "merge_sources", "type": "main", "index": 0}]]
                },
                "fetch_researchgate": {
                    "main": [[{"node": "merge_sources", "type": "main", "index": 0}]]
                },
                "fetch_web_sources": {
                    "main": [[{"node": "merge_sources", "type": "main", "index": 0}]]
                },
                "merge_sources": {
                    "main": [[{"node": "syphon_extract_education", "type": "main", "index": 0}]]
                },
                "syphon_extract_education": {
                    "main": [
                        [{"node": "save_education_intelligence", "type": "main", "index": 0}],
                        [{"node": "add_education_to_queue", "type": "main", "index": 0}]
                    ]
                }
            },
            "tags": [
                {"id": "syphon", "name": "SYPHON"},
                {"id": "education", "name": "Education"},
                {"id": "white_paper", "name": "White Paper"},
                {"id": "thesis", "name": "Thesis"}
            ]
        }
        return workflow

    def deploy_workflow(self, workflow: Dict[str, Any], workflow_name: str) -> bool:
        """Deploy workflow to N8N on NAS"""
        try:
            # Check if workflow already exists
            workflow_id = None
            if workflow_name in self.workflows:
                workflow_id = self.workflows[workflow_name].get("id")

            # Prepare workflow data
            workflow_data = {
                "name": workflow["name"],
                "nodes": workflow["nodes"],
                "connections": workflow.get("connections", {}),
                "settings": workflow.get("settings", {}),
                "staticData": workflow.get("staticData"),
                "tags": workflow.get("tags", [])
            }

            # Try N8N REST API (older versions use /rest/workflows)
            # Try both /api/v1/workflows and /rest/workflows
            api_endpoints = [
                f"{self.n8n_base_url}/rest/workflows",
                f"{self.n8n_api_url}/workflows"
            ]

            if workflow_id:
                # Update existing workflow
                api_endpoints = [
                    f"{self.n8n_base_url}/rest/workflows/{workflow_id}",
                    f"{self.n8n_api_url}/workflows/{workflow_id}"
                ]
                method = "PUT"
            else:
                # Create new workflow
                method = "POST"

            # Try each endpoint
            response = None
            for url in api_endpoints:
                try:
                    response = requests.request(
                        method=method,
                        url=url,
                        json=workflow_data,
                        headers={"Content-Type": "application/json"},
                        timeout=30
                    )
                    if response.status_code in [200, 201]:
                        break
                except:
                    continue

            if not response:
                logger.error(f"   ❌ Could not connect to N8N API")
                return False

            response = requests.request(
                method=method,
                url=url,
                json=workflow_data,
                headers={"Content-Type": "application/json"},
                timeout=30
            )

            if response.status_code in [200, 201]:
                result = response.json()
                workflow_id = result.get("id") or workflow_id

                # Save to registry
                self.workflows[workflow_name] = {
                    "id": workflow_id,
                    "name": workflow["name"],
                    "deployed_at": datetime.now().isoformat(),
                    "n8n_url": f"{self.n8n_base_url}/workflow/{workflow_id}"
                }
                self._save_workflows()

                logger.info(f"   ✅ Deployed workflow: {workflow_name} (ID: {workflow_id})")
                return True
            else:
                logger.error(f"   ❌ Failed to deploy {workflow_name}: {response.status_code} - {response.text}")
                return False

        except Exception as e:
            logger.error(f"   ❌ Error deploying {workflow_name}: {e}")
            return False

    def deploy_all_workflows(self) -> Dict[str, bool]:
        """Deploy all SYPHON workflows"""
        logger.info("="*80)
        logger.info("🚀 DEPLOYING SYPHON N8N WORKFLOWS TO NAS")
        logger.info("="*80)
        logger.info("")

        # Check N8N connection
        if not self._check_n8n_connection():
            logger.error("   ❌ Cannot connect to N8N on NAS")
            logger.error(f"   Please verify N8N is running at {self.n8n_base_url}")
            return {}

        logger.info("   ✅ N8N connection verified")
        logger.info("")

        results = {}

        # Deploy Email workflow
        logger.info("📧 Deploying Email SYPHON workflow...")
        email_workflow = self.create_email_syphon_workflow()
        results["email"] = self.deploy_workflow(email_workflow, "email_syphon")
        logger.info("")

        # Deploy SMS workflow
        logger.info("📱 Deploying SMS SYPHON workflow...")
        sms_workflow = self.create_sms_syphon_workflow()
        results["sms"] = self.deploy_workflow(sms_workflow, "sms_syphon")
        logger.info("")

        # Deploy Social-News-Education workflow
        logger.info("📚 Deploying Social-News-Education SYPHON workflow...")
        education_workflow = self.create_social_news_education_workflow()
        results["education"] = self.deploy_workflow(education_workflow, "education_syphon")
        logger.info("")

        # Summary
        logger.info("="*80)
        logger.info("📊 DEPLOYMENT SUMMARY")
        logger.info("="*80)
        for name, success in results.items():
            icon = "✅" if success else "❌"
            logger.info(f"   {icon} {name.upper()}: {'Deployed' if success else 'Failed'}")
        logger.info("")

        return results


def main():
    try:
        """Main execution"""
        deployer = SyphonN8NWorkflowDeployer()
        results = deployer.deploy_all_workflows()

        # Save deployment report
        report = {
            "deployment_timestamp": datetime.now().isoformat(),
            "n8n_url": deployer.n8n_base_url,
            "results": results,
            "workflows": deployer.workflows
        }

        report_file = deployer.data_dir / f"deployment_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2)

        logger.info(f"   📄 Deployment report saved: {report_file}")
        logger.info("")
        logger.info("="*80)
        logger.info("✅ SYPHON N8N WORKFLOW DEPLOYMENT COMPLETE")
        logger.info("="*80)


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()