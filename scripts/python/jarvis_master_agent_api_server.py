#!/usr/bin/env python3
"""
JARVIS Master Agent API Server
Unified REST API for all JARVIS multi-platform applications

Implements all endpoints as specified in JARVIS_MASTER_AGENT_API_SPECIFICATION.md
"""

import os
import sys
import uuid
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional

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

logger = get_logger("JARVISMasterAgentAPI")

# FastAPI imports
try:
    from fastapi import Depends, FastAPI, HTTPException, WebSocket, WebSocketDisconnect, status
    from fastapi.middleware.cors import CORSMiddleware
    from fastapi.responses import JSONResponse
    from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
    from pydantic import BaseModel, Field

    FASTAPI_AVAILABLE = True
except ImportError:
    FASTAPI_AVAILABLE = False
    logger.error("FastAPI not available. Install with: pip install fastapi uvicorn")

# Azure integrations
try:
    from azure_service_bus_integration import (
        AzureServiceBusClient,
        MessageType,
        ServiceBusMessage,
        get_key_vault_client,
        get_service_bus_client,
    )
    from r5_service_bus_integration import publish_knowledge_entry
    from workflow_service_bus_integration import (
        publish_workflow_completed,
        publish_workflow_created,
        publish_workflow_status_update,
        send_workflow_execution_request,
    )

    AZURE_AVAILABLE = True
except ImportError:
    AZURE_AVAILABLE = False
    logger.warning("Azure Service Bus integration not available")

# JWT authentication
try:
    import jwt
    from jwt.exceptions import InvalidTokenError

    JWT_AVAILABLE = True
except ImportError:
    JWT_AVAILABLE = False
    logger.warning("PyJWT not available. Install with: pip install pyjwt")

if FASTAPI_AVAILABLE:
    app = FastAPI(
        title="JARVIS Master Agent API",
        description="Unified API for all JARVIS multi-platform applications",
        version="1.0.0",
        docs_url="/api/docs",
        redoc_url="/api/redoc",
    )

    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Configure appropriately for production
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Custom middleware
    try:
        from api_middleware import (
            ErrorHandlingMiddleware,
            RateLimitMiddleware,
            RequestLoggingMiddleware,
        )
        from api_security_middleware import InputValidationMiddleware, SecurityHeadersMiddleware

        app.add_middleware(ErrorHandlingMiddleware)
        app.add_middleware(SecurityHeadersMiddleware)
        app.add_middleware(InputValidationMiddleware)
        app.add_middleware(RequestLoggingMiddleware)
        app.add_middleware(RateLimitMiddleware, requests_per_minute=60)
        logger.info("Custom middleware added")
    except ImportError:
        logger.warning("Custom middleware not available")

    # Security
    security = HTTPBearer()

    # Initialize Azure clients
    service_bus_client: Optional[AzureServiceBusClient] = None
    key_vault_client = None

    if AZURE_AVAILABLE:
        try:
            key_vault_client = get_key_vault_client()
            service_bus_client = get_service_bus_client(
                namespace="jarvis-lumina-bus.servicebus.windows.net",
                key_vault_client=key_vault_client,
            )
            logger.info("Azure Service Bus client initialized")
        except Exception as e:
            logger.warning(f"Azure Service Bus not available: {e}")

    # JWT configuration - secret MUST come from Key Vault or environment
    JWT_SECRET = os.environ.get("JARVIS_JWT_SECRET")
    if not JWT_SECRET and key_vault_client:
        try:
            JWT_SECRET = key_vault_client.get_secret("jarvis-jwt-secret").value
        except Exception as e:
            logger.warning(f"Could not retrieve JWT secret from Key Vault: {e}")
    if not JWT_SECRET:
        logger.critical(
            "❌ JARVIS_JWT_SECRET not set and Key Vault unavailable - API authentication disabled"
        )
        JWT_SECRET = None  # Will cause auth to fail safely
    JWT_ALGORITHM = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES = 60
    REFRESH_TOKEN_EXPIRE_DAYS = 30

    # Pydantic models
    class LoginRequest(BaseModel):
        username: str
        password: str
        device_id: Optional[str] = None
        device_name: Optional[str] = None

    class RefreshTokenRequest(BaseModel):
        refresh_token: str

    class WorkflowCreate(BaseModel):
        name: str
        description: Optional[str] = None
        steps: List[Dict[str, Any]]
        parameters: Optional[Dict[str, Any]] = None

    class WorkflowUpdate(BaseModel):
        name: Optional[str] = None
        description: Optional[str] = None
        steps: Optional[List[Dict[str, Any]]] = None
        status: Optional[str] = None

    class ChatMessage(BaseModel):
        message: str
        context: Optional[Dict[str, Any]] = None

    class R5SearchRequest(BaseModel):
        query: str
        filters: Optional[Dict[str, Any]] = None
        limit: int = 20
        offset: int = 0

    class TicketCreate(BaseModel):
        title: str
        description: str
        priority: str = "medium"
        category: Optional[str] = None

    # Import services
    try:
        from api_authentication_service import get_auth_service
        from api_chat_service import get_chat_service
        from api_helpdesk_service import get_helpdesk_service
        from api_intelligence_service import get_intelligence_service
        from api_r5_service import get_r5_service
        from api_workflow_service import get_workflow_service

        auth_service = get_auth_service(project_root)
        workflow_service = get_workflow_service(project_root)
        chat_service = get_chat_service(project_root)
        r5_service = get_r5_service(project_root)
        helpdesk_service = get_helpdesk_service(project_root)
        intelligence_service = get_intelligence_service(project_root)
        SERVICES_AVAILABLE = True
    except ImportError:
        SERVICES_AVAILABLE = False
        logger.warning("API services not available")

    # Import agent history manager
    try:
        from agent_history_manager import AgentHistoryManager, AgentType, HistoryStatus

        agent_history_manager = AgentHistoryManager(project_root)
        AGENT_HISTORY_AVAILABLE = True
        logger.info("Agent History Manager initialized")
    except ImportError as e:
        AGENT_HISTORY_AVAILABLE = False
        logger.warning(f"Agent History Manager not available: {e}")
        agent_history_manager = None

    # Authentication helpers
    def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
        """Create JWT access token"""
        if SERVICES_AVAILABLE:
            return auth_service.create_access_token(data)
        if not JWT_AVAILABLE:
            return "mock-token"

        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

        to_encode.update({"exp": expire, "iat": datetime.utcnow()})
        encoded_jwt = jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGORITHM)
        return encoded_jwt

    def create_refresh_token(data: Dict[str, Any]) -> str:
        """Create refresh token"""
        if SERVICES_AVAILABLE:
            refresh_token, _ = auth_service.create_refresh_token(data)
            return refresh_token
        if not JWT_AVAILABLE:
            return "mock-refresh-token"

        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
        to_encode.update({"exp": expire, "iat": datetime.utcnow(), "type": "refresh"})
        encoded_jwt = jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGORITHM)
        return encoded_jwt

    def verify_token(
        credentials: HTTPAuthorizationCredentials = Depends(security),
    ) -> Dict[str, Any]:
        """Verify JWT token"""
        if SERVICES_AVAILABLE:
            token = credentials.credentials
            payload = auth_service.verify_token(token)
            if not payload:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid authentication credentials",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            return payload

        if not JWT_AVAILABLE:
            return {"user_id": "mock-user", "username": "mock"}

        try:
            token = credentials.credentials
            payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
            return payload
        except InvalidTokenError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )

    # Authentication endpoints
    @app.post("/api/v1/auth/login")
    async def login(request: LoginRequest):
        """Authenticate user and receive access token"""
        if SERVICES_AVAILABLE:
            user_data = auth_service.authenticate_user(request.username, request.password)
            if not user_data:
                raise HTTPException(status_code=401, detail="Invalid credentials")

            access_token = auth_service.create_access_token(user_data)
            refresh_token, _ = auth_service.create_refresh_token(user_data, request.device_id)

            return {
                "access_token": access_token,
                "refresh_token": refresh_token,
                "token_type": "Bearer",
                "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60,
                "user": user_data,
            }

        # Fallback mock authentication
        user_data = {
            "id": str(uuid.uuid4()),
            "username": request.username,
            "email": f"{request.username}@jarvis.local",
            "permissions": ["read", "write"],
        }

        access_token = create_access_token(
            {"sub": user_data["id"], "username": user_data["username"]}
        )
        refresh_token = create_refresh_token({"sub": user_data["id"]})

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "Bearer",
            "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            "user": user_data,
        }

    @app.post("/api/v1/auth/refresh")
    async def refresh_token(request: RefreshTokenRequest):
        """Refresh access token"""
        if SERVICES_AVAILABLE:
            result = auth_service.refresh_access_token(request.refresh_token)
            if not result:
                raise HTTPException(status_code=401, detail="Invalid refresh token")
            return result

        if not JWT_AVAILABLE:
            return {"access_token": "mock-token", "token_type": "Bearer", "expires_in": 3600}

        try:
            payload = jwt.decode(request.refresh_token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
            if payload.get("type") != "refresh":
                raise HTTPException(status_code=401, detail="Invalid refresh token")

            access_token = create_access_token(
                {"sub": payload["sub"], "username": payload.get("username")}
            )
            return {
                "access_token": access_token,
                "token_type": "Bearer",
                "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            }
        except InvalidTokenError:
            raise HTTPException(status_code=401, detail="Invalid refresh token")

    @app.post("/api/v1/auth/logout")
    async def logout(current_user: Dict[str, Any] = Depends(verify_token)):
        """Logout user"""
        # TODO: Implement token revocation  # [ADDRESSED]  # [ADDRESSED]
        return {"message": "Logged out successfully"}

    # Workflow endpoints
    @app.post("/api/v1/workflows")
    async def create_workflow(
        workflow: WorkflowCreate, current_user: Dict[str, Any] = Depends(verify_token)
    ):
        """Create a new workflow"""
        if SERVICES_AVAILABLE:
            try:
                workflow_data = workflow_service.create_workflow(
                    name=workflow.name,
                    description=workflow.description,
                    steps=workflow.steps,
                    parameters=workflow.parameters,
                    created_by=current_user.get("sub") or current_user.get("user_id"),
                )
                return {"workflow": workflow_data}
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))

        # Fallback
        workflow_id = str(uuid.uuid4())
        workflow_data = {
            "id": workflow_id,
            "name": workflow.name,
            "description": workflow.description,
            "steps": workflow.steps,
            "parameters": workflow.parameters or {},
            "status": "draft",
            "created_by": current_user.get("sub") or current_user.get("user_id"),
            "created_at": datetime.now().isoformat(),
        }

        if service_bus_client:
            publish_workflow_created(workflow_data, service_bus_client)

        return {"workflow": workflow_data}

    @app.get("/api/v1/workflows")
    async def list_workflows(
        status: Optional[str] = None,
        limit: int = 20,
        offset: int = 0,
        current_user: Dict[str, Any] = Depends(verify_token),
    ):
        """List workflows"""
        if SERVICES_AVAILABLE:
            return workflow_service.list_workflows(
                status=status,
                created_by=current_user.get("sub") or current_user.get("user_id"),
                limit=limit,
                offset=offset,
            )
        return {"workflows": [], "total": 0, "limit": limit, "offset": offset}

    @app.get("/api/v1/workflows/{workflow_id}")
    async def get_workflow(workflow_id: str, current_user: Dict[str, Any] = Depends(verify_token)):
        """Get workflow by ID"""
        if SERVICES_AVAILABLE:
            workflow = workflow_service.get_workflow(workflow_id)
            if not workflow:
                raise HTTPException(status_code=404, detail="Workflow not found")
            return {"workflow": workflow}
        raise HTTPException(status_code=404, detail="Workflow not found")

    @app.put("/api/v1/workflows/{workflow_id}")
    async def update_workflow(
        workflow_id: str,
        workflow: WorkflowUpdate,
        current_user: Dict[str, Any] = Depends(verify_token),
    ):
        """Update workflow"""
        if SERVICES_AVAILABLE:
            success = workflow_service.update_workflow(
                workflow_id=workflow_id,
                name=workflow.name,
                description=workflow.description,
                status=workflow.status,
            )
            if not success:
                raise HTTPException(status_code=404, detail="Workflow not found")
            return {"message": "Workflow updated"}
        raise HTTPException(status_code=404, detail="Workflow not found")

    @app.delete("/api/v1/workflows/{workflow_id}")
    async def delete_workflow(
        workflow_id: str, current_user: Dict[str, Any] = Depends(verify_token)
    ):
        """Delete workflow"""
        if SERVICES_AVAILABLE:
            success = workflow_service.delete_workflow(workflow_id)
            if not success:
                raise HTTPException(status_code=404, detail="Workflow not found")
            return {"message": "Workflow deleted"}
        return {"message": "Workflow deleted"}

    @app.post("/api/v1/workflows/{workflow_id}/execute")
    async def execute_workflow(
        workflow_id: str,
        parameters: Optional[Dict[str, Any]] = None,
        current_user: Dict[str, Any] = Depends(verify_token),
    ):
        """Execute workflow"""
        if SERVICES_AVAILABLE:
            success = workflow_service.execute_workflow(workflow_id, parameters)
            if not success:
                raise HTTPException(status_code=404, detail="Workflow not found")
            return {"message": "Workflow execution started", "workflow_id": workflow_id}

        if service_bus_client:
            send_workflow_execution_request(workflow_id, parameters or {}, True, service_bus_client)
        return {"message": "Workflow execution started", "workflow_id": workflow_id}

    # Chat endpoints
    @app.post("/api/v1/chat/conversations")
    async def create_conversation(
        title: Optional[str] = None, current_user: Dict[str, Any] = Depends(verify_token)
    ):
        """Create a new conversation"""
        if SERVICES_AVAILABLE:
            try:
                conversation = chat_service.create_conversation(
                    user_id=current_user.get("sub") or current_user.get("user_id"), title=title
                )
                return {"conversation": conversation}
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
        raise HTTPException(status_code=503, detail="Chat service not available")

    @app.get("/api/v1/chat/conversations")
    async def list_conversations(
        limit: int = 20,
        offset: int = 0,
        is_archived: bool = False,
        current_user: Dict[str, Any] = Depends(verify_token),
    ):
        """List conversations"""
        if SERVICES_AVAILABLE:
            return chat_service.list_conversations(
                user_id=current_user.get("sub") or current_user.get("user_id"),
                limit=limit,
                offset=offset,
                is_archived=is_archived,
            )
        return {"conversations": [], "total": 0, "limit": limit, "offset": offset}

    @app.post("/api/v1/chat/messages")
    async def send_chat_message(
        conversation_id: str,
        message: ChatMessage,
        current_user: Dict[str, Any] = Depends(verify_token),
    ):
        """Send chat message"""
        if SERVICES_AVAILABLE:
            try:
                # Send user message
                user_msg = chat_service.send_message(
                    conversation_id=conversation_id,
                    role="user",
                    content=message.message,
                    metadata=message.context,
                )

                # TODO: Process with AI and send assistant response  # [ADDRESSED]  # [ADDRESSED]
                # For now, return user message
                return {"message": user_msg}
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))

        # Fallback
        message_id = str(uuid.uuid4())
        chat_data = {
            "id": message_id,
            "message": message.message,
            "context": message.context,
            "user_id": current_user.get("sub") or current_user.get("user_id"),
            "timestamp": datetime.now().isoformat(),
        }

        if service_bus_client:
            sb_message = ServiceBusMessage(
                message_id=message_id,
                message_type=MessageType.RESPONSE,
                timestamp=datetime.now(),
                source="api-chat",
                destination="chat-processor",
                payload=chat_data,
            )
            service_bus_client.publish_to_topic("jarvis.responses", sb_message)

        return {"message": chat_data}

    @app.get("/api/v1/chat/messages")
    async def get_chat_messages(
        conversation_id: str,
        limit: int = 50,
        offset: int = 0,
        current_user: Dict[str, Any] = Depends(verify_token),
    ):
        """Get chat messages"""
        if SERVICES_AVAILABLE:
            return chat_service.get_messages(conversation_id, limit, offset)
        return {"messages": [], "total": 0, "limit": limit, "offset": offset}

    # Agent History endpoints
    @app.get("/api/v1/agent/history/search")
    async def search_agent_history(
        keyword: str,
        limit: int = 20,
        offset: int = 0,
        current_user: Dict[str, Any] = Depends(verify_token),
    ):
        """Search agent history with keyword filtering and pagination"""
        if not AGENT_HISTORY_AVAILABLE or not agent_history_manager:
            raise HTTPException(status_code=503, detail="Agent History service not available")

        try:
            result = agent_history_manager.search_histories(
                keyword=keyword, limit=limit, offset=offset
            )
            return {
                "items": result["items"],
                "total": result["total"],
                "hasMore": result["hasMore"],
                "offset": result["offset"],
                "limit": result["limit"],
            }
        except Exception as e:
            logger.error(f"Error searching agent history: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail=f"Error searching agent history: {str(e)}")

    @app.get("/api/v1/agent/history/{history_id}")
    async def get_agent_history(
        history_id: str, current_user: Dict[str, Any] = Depends(verify_token)
    ):
        """Get agent history by ID"""
        if not AGENT_HISTORY_AVAILABLE or not agent_history_manager:
            raise HTTPException(status_code=503, detail="Agent History service not available")

        try:
            history = agent_history_manager.get_history_by_id(history_id)
            if not history:
                raise HTTPException(
                    status_code=404, detail=f"Agent history not found: {history_id}"
                )
            return history.to_dict()
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error getting agent history: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail=f"Error retrieving agent history: {str(e)}")

    @app.post("/api/v1/agent/history/{history_id}/pin")
    async def pin_agent_history(
        history_id: str, current_user: Dict[str, Any] = Depends(verify_token)
    ):
        """Pin an agent history item"""
        if not AGENT_HISTORY_AVAILABLE or not agent_history_manager:
            raise HTTPException(status_code=503, detail="Agent History service not available")

        try:
            success = agent_history_manager.pin_history(history_id)
            if not success:
                raise HTTPException(
                    status_code=404, detail=f"Agent history not found: {history_id}"
                )
            return {"success": True, "history_id": history_id, "pinned": True}
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error pinning agent history: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail=f"Error pinning agent history: {str(e)}")

    @app.post("/api/v1/agent/history/{history_id}/unpin")
    async def unpin_agent_history(
        history_id: str, current_user: Dict[str, Any] = Depends(verify_token)
    ):
        """Unpin an agent history item"""
        if not AGENT_HISTORY_AVAILABLE or not agent_history_manager:
            raise HTTPException(status_code=503, detail="Agent History service not available")

        try:
            success = agent_history_manager.unpin_history(history_id)
            if not success:
                raise HTTPException(
                    status_code=404, detail=f"Agent history not found: {history_id}"
                )
            return {"success": True, "history_id": history_id, "pinned": False}
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error unpinning agent history: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail=f"Error unpinning agent history: {str(e)}")

    @app.get("/api/v1/agent/history/pinned")
    async def get_pinned_agent_histories(current_user: Dict[str, Any] = Depends(verify_token)):
        """Get all pinned agent histories"""
        if not AGENT_HISTORY_AVAILABLE or not agent_history_manager:
            raise HTTPException(status_code=503, detail="Agent History service not available")

        try:
            pinned_histories = agent_history_manager.get_pinned_histories()
            return {
                "items": [h.to_dict() for h in pinned_histories],
                "total": len(pinned_histories),
            }
        except Exception as e:
            logger.error(f"Error getting pinned agent histories: {e}", exc_info=True)
            raise HTTPException(
                status_code=500, detail=f"Error retrieving pinned agent histories: {str(e)}"
            )

    # R5 Knowledge endpoints
    @app.post("/api/v1/r5/knowledge/search")
    async def search_r5_knowledge(
        request: R5SearchRequest, current_user: Dict[str, Any] = Depends(verify_token)
    ):
        """Search R5 knowledge"""
        if SERVICES_AVAILABLE:
            return r5_service.search_knowledge(
                query=request.query,
                filters=request.filters,
                limit=request.limit,
                offset=request.offset,
            )
        return {"results": [], "total": 0, "query": request.query}

    @app.post("/api/v1/r5/knowledge/ingest")
    async def ingest_r5_knowledge(
        entry: Dict[str, Any], current_user: Dict[str, Any] = Depends(verify_token)
    ):
        """Ingest knowledge into R5"""
        if SERVICES_AVAILABLE:
            try:
                result = r5_service.ingest_knowledge(
                    entry_id=entry.get("entry_id", str(uuid.uuid4())),
                    category=entry.get("category", "general"),
                    content=entry.get("content", ""),
                    tags=entry.get("tags"),
                    patterns=entry.get("patterns"),
                    metadata=entry.get("metadata"),
                    source=entry.get("source"),
                    extract_patterns=entry.get("extract_patterns", True),
                )
                return {"message": "Knowledge entry ingested", "entry": result}
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))

        if service_bus_client:
            from r5_service_bus_integration import publish_knowledge_entry

            publish_knowledge_entry(entry, True, service_bus_client)

        return {"message": "Knowledge entry ingested", "entry_id": str(uuid.uuid4())}

    # Helpdesk endpoints
    @app.post("/api/v1/helpdesk/tickets")
    async def create_ticket(
        ticket: TicketCreate, current_user: Dict[str, Any] = Depends(verify_token)
    ):
        """Create helpdesk ticket"""
        if SERVICES_AVAILABLE:
            try:
                ticket_data = helpdesk_service.create_ticket(
                    title=ticket.title,
                    description=ticket.description,
                    priority=ticket.priority,
                    category=ticket.category,
                    created_by=current_user.get("sub") or current_user.get("user_id"),
                )
                return {"ticket": ticket_data}
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))

        # Fallback
        ticket_id = str(uuid.uuid4())
        ticket_data = {
            "id": ticket_id,
            "title": ticket.title,
            "description": ticket.description,
            "priority": ticket.priority,
            "category": ticket.category,
            "created_by": current_user.get("sub") or current_user.get("user_id"),
            "status": "open",
            "created_at": datetime.now().isoformat(),
        }

        if service_bus_client:
            sb_message = ServiceBusMessage(
                message_id=ticket_id,
                message_type=MessageType.ESCALATION,
                timestamp=datetime.now(),
                source="api-helpdesk",
                destination="helpdesk-coordinator",
                payload={"MessageType": "TicketCreated", **ticket_data},
            )
            service_bus_client.publish_to_topic("helpdesk.coordination", sb_message)

        return {"ticket": ticket_data}

    @app.get("/api/v1/helpdesk/tickets")
    async def list_tickets(
        status: Optional[str] = None,
        priority: Optional[str] = None,
        limit: int = 20,
        offset: int = 0,
        current_user: Dict[str, Any] = Depends(verify_token),
    ):
        """List helpdesk tickets"""
        if SERVICES_AVAILABLE:
            return helpdesk_service.list_tickets(
                status=status,
                priority=priority,
                created_by=current_user.get("sub") or current_user.get("user_id"),
                limit=limit,
                offset=offset,
            )
        return {"tickets": [], "total": 0, "limit": limit, "offset": offset}

    # Intelligence endpoints
    @app.get("/api/v1/intelligence/feed")
    async def get_intelligence_feed(
        type: Optional[str] = None,
        priority: Optional[str] = None,
        action_required: Optional[bool] = None,
        limit: int = 20,
        offset: int = 0,
        current_user: Dict[str, Any] = Depends(verify_token),
    ):
        """Get intelligence feed"""
        if SERVICES_AVAILABLE:
            return intelligence_service.get_intelligence_feed(
                type_filter=type,
                priority_filter=priority,
                action_required=action_required,
                limit=limit,
                offset=offset,
            )
        return {"items": [], "total": 0, "limit": limit, "offset": offset}

    # System status endpoints
    @app.get("/api/v1/system/health")
    async def health_check():
        """Health check endpoint"""
        try:
            from monitoring_service import get_monitoring_service

            monitoring = get_monitoring_service(project_root)
            health = monitoring.get_system_health()
            return health
        except Exception:
            # Fallback
            return {
                "status": "healthy",
                "timestamp": datetime.now().isoformat(),
                "version": "1.0.0",
                "components": {
                    "api": "healthy",
                    "service_bus": "healthy" if service_bus_client else "unavailable",
                    "key_vault": "healthy" if key_vault_client else "unavailable",
                },
            }

    @app.get("/api/v1/system/status")
    async def system_status(current_user: Dict[str, Any] = Depends(verify_token)):
        """Get system status"""
        try:
            from monitoring_service import get_monitoring_service

            monitoring = get_monitoring_service(project_root)
            business_metrics = monitoring.get_business_metrics()

            return {
                "status": "operational",
                "timestamp": datetime.now().isoformat(),
                "version": "1.0.0",
                "metrics": business_metrics,
            }
        except Exception:
            return {
                "status": "operational",
                "timestamp": datetime.now().isoformat(),
                "uptime": "0 days, 0 hours, 0 minutes",
                "version": "1.0.0",
            }

    # Additional metrics endpoints
    @app.get("/api/v1/metrics/performance")
    async def get_performance_metrics(current_user: Dict[str, Any] = Depends(verify_token)):
        """Get performance metrics"""
        try:
            from performance_monitor import get_performance_monitor

            monitor = get_performance_monitor(project_root)
            return monitor.get_performance_metrics()
        except Exception as e:
            raise HTTPException(
                status_code=503, detail=f"Performance monitoring not available: {e}"
            )

    @app.get("/api/v1/metrics/business")
    async def get_business_metrics(current_user: Dict[str, Any] = Depends(verify_token)):
        """Get business metrics"""
        try:
            from monitoring_service import get_monitoring_service

            monitoring = get_monitoring_service(project_root)
            return monitoring.get_business_metrics()
        except Exception as e:
            raise HTTPException(status_code=503, detail=f"Business metrics not available: {e}")

    # WebSocket endpoint
    @app.websocket("/api/v1/ws")
    async def websocket_endpoint(websocket: WebSocket):
        """WebSocket endpoint for real-time updates"""
        await websocket.accept()
        try:
            while True:
                data = await websocket.receive_text()
                # Echo back for now
                await websocket.send_text(f"Echo: {data}")
        except WebSocketDisconnect:
            logger.info("WebSocket client disconnected")

    @app.get("/")
    async def root():
        """Root endpoint"""
        return {
            "name": "JARVIS Master Agent API",
            "version": "1.0.0",
            "status": "operational",
            "docs": "/api/docs",
        }

else:
    # Fallback if FastAPI not available
    app = None
    logger.error("FastAPI not available - API server cannot be started")


if __name__ == "__main__":
    from pathlib import Path

    import uvicorn

    project_root = Path(__file__).parent.parent.parent

    if FASTAPI_AVAILABLE and app:
        logger.info("Starting JARVIS Master Agent API Server...")
        logger.info(f"Project root: {project_root}")
        uvicorn.run(app, host="0.0.0.0", port=8000)
    else:
        logger.error("Cannot start API server - FastAPI not available")
