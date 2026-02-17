#!/usr/bin/env python3
"""
API Authentication Service
Handles user authentication, token management, and authorization

Integrates with database and Azure Key Vault for secrets.
"""

import sys
import uuid
import hashlib
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, Tuple

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

logger = get_logger("APIAuthentication")

# Password hashing
try:
    import bcrypt
    BCRYPT_AVAILABLE = True
except ImportError:
    BCRYPT_AVAILABLE = False
    logger.warning("bcrypt not available. Install with: pip install bcrypt")

# JWT
try:
    import jwt
    from jwt.exceptions import InvalidTokenError
    JWT_AVAILABLE = True
except ImportError:
    JWT_AVAILABLE = False
    logger.warning("PyJWT not available. Install with: pip install pyjwt")

# Database
try:
    from database_connection_manager import get_db_manager
    DB_AVAILABLE = True
except ImportError:
    DB_AVAILABLE = False
    logger.warning("Database connection manager not available")

# Azure Key Vault
try:
    from azure_service_bus_integration import get_key_vault_client
    AZURE_AVAILABLE = True
except ImportError:
    AZURE_AVAILABLE = False
    logger.warning("Azure Key Vault integration not available")


class AuthenticationService:
    """Handles authentication and authorization"""

    def __init__(self, project_root: Optional[Path] = None):
        self.project_root = Path(project_root) if project_root else Path(__file__).parent.parent.parent

        # Initialize database
        if DB_AVAILABLE:
            self.db_manager = get_db_manager(project_root)
        else:
            self.db_manager = None

        # Initialize Key Vault for JWT secret
        self.jwt_secret = self._get_jwt_secret()
        self.jwt_algorithm = "HS256"
        self.access_token_expire_minutes = 60
        self.refresh_token_expire_days = 30

    def _get_jwt_secret(self) -> str:
        """Get JWT secret from Key Vault"""
        if AZURE_AVAILABLE:
            try:
                kv_client = get_key_vault_client()
                return kv_client.get_secret("jwt-secret-key")
            except Exception as e:
                logger.warning(f"Failed to get JWT secret from Key Vault: {e}")

        # Fallback to environment variable
        import os
        return os.getenv("JWT_SECRET", "default-secret-key-change-in-production")

    def hash_password(self, password: str) -> str:
        """Hash password using bcrypt"""
        if BCRYPT_AVAILABLE:
            salt = bcrypt.gensalt()
            return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
        else:
            # Fallback to SHA256 (not secure, but functional)
            return hashlib.sha256(password.encode('utf-8')).hexdigest()

    def verify_password(self, password: str, password_hash: str) -> bool:
        """Verify password against hash"""
        if BCRYPT_AVAILABLE:
            return bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8'))
        else:
            # Fallback to SHA256
            return hashlib.sha256(password.encode('utf-8')).hexdigest() == password_hash

    def create_user(self, username: str, email: str, password: str, permissions: Optional[list] = None) -> Dict[str, Any]:
        """Create a new user"""
        if not self.db_manager:
            raise RuntimeError("Database manager not available")

        user_id = str(uuid.uuid4())
        password_hash = self.hash_password(password)

        query = """
        INSERT INTO users (id, username, email, password_hash, permissions, created_at, updated_at)
        VALUES (%s, %s, %s, %s, %s, NOW(), NOW())
        RETURNING id, username, email, permissions, created_at
        """

        try:
            results = self.db_manager.execute_query(
                query,
                (user_id, username, email, password_hash, permissions or [])
            )
            if results:
                return results[0]
            raise Exception("User creation failed")
        except Exception as e:
            logger.error(f"Error creating user: {e}")
            raise

    def authenticate_user(self, username: str, password: str) -> Optional[Dict[str, Any]]:
        """Authenticate user and return user data"""
        if not self.db_manager:
            return None

        query = """
        SELECT id, username, email, password_hash, permissions, is_active
        FROM users
        WHERE username = %s OR email = %s
        """

        try:
            results = self.db_manager.execute_query(query, (username, username))
            if not results:
                return None

            user = results[0]

            # Check if user is active
            if not user.get('is_active', True):
                logger.warning(f"Authentication attempt for inactive user: {username}")
                return None

            # Verify password
            if not self.verify_password(password, user['password_hash']):
                logger.warning(f"Invalid password for user: {username}")
                return None

            # Update last login
            update_query = "UPDATE users SET last_login = NOW() WHERE id = %s"
            self.db_manager.execute_update(update_query, (user['id'],))

            # Return user data (without password hash)
            return {
                "id": str(user['id']),
                "username": user['username'],
                "email": user['email'],
                "permissions": user.get('permissions', [])
            }
        except Exception as e:
            logger.error(f"Error authenticating user: {e}")
            return None

    def create_access_token(self, user_data: Dict[str, Any]) -> str:
        """Create JWT access token"""
        if not JWT_AVAILABLE:
            return "mock-access-token"

        payload = {
            "sub": user_data["id"],
            "username": user_data["username"],
            "email": user_data.get("email"),
            "permissions": user_data.get("permissions", []),
            "type": "access",
            "iat": datetime.utcnow(),
            "exp": datetime.utcnow() + timedelta(minutes=self.access_token_expire_minutes)
        }

        return jwt.encode(payload, self.jwt_secret, algorithm=self.jwt_algorithm)

    def create_refresh_token(self, user_data: Dict[str, Any], device_id: Optional[str] = None) -> Tuple[str, str]:
        """Create refresh token and store in database"""
        if not JWT_AVAILABLE:
            return "mock-refresh-token", "mock-token-id"

        token_id = str(uuid.uuid4())
        payload = {
            "sub": user_data["id"],
            "jti": token_id,
            "type": "refresh",
            "iat": datetime.utcnow(),
            "exp": datetime.utcnow() + timedelta(days=self.refresh_token_expire_days)
        }

        refresh_token = jwt.encode(payload, self.jwt_secret, algorithm=self.jwt_algorithm)

        # Store refresh token in database
        if self.db_manager:
            try:
                # Get device_id if provided
                device_uuid = None
                if device_id:
                    device_query = "SELECT id FROM devices WHERE device_id = %s"
                    device_results = self.db_manager.execute_query(device_query, (device_id,))
                    if device_results:
                        device_uuid = device_results[0]['id']

                # Hash token for storage
                token_hash = hashlib.sha256(refresh_token.encode('utf-8')).hexdigest()

                insert_query = """
                INSERT INTO refresh_tokens (id, user_id, device_id, token_hash, expires_at, created_at)
                VALUES (%s, %s, %s, %s, %s, NOW())
                """
                expires_at = datetime.utcnow() + timedelta(days=self.refresh_token_expire_days)
                self.db_manager.execute_update(
                    insert_query,
                    (token_id, user_data["id"], device_uuid, token_hash, expires_at)
                )
            except Exception as e:
                logger.error(f"Error storing refresh token: {e}")

        return refresh_token, token_id

    def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Verify JWT token"""
        if not JWT_AVAILABLE:
            return {"user_id": "mock-user", "username": "mock"}

        try:
            payload = jwt.decode(token, self.jwt_secret, algorithms=[self.jwt_algorithm])
            return payload
        except InvalidTokenError as e:
            logger.warning(f"Invalid token: {e}")
            return None

    def refresh_access_token(self, refresh_token: str) -> Optional[Dict[str, Any]]:
        """Refresh access token using refresh token"""
        if not JWT_AVAILABLE:
            return {"access_token": "mock-token", "token_type": "Bearer", "expires_in": 3600}

        try:
            payload = self.verify_token(refresh_token)
            if not payload or payload.get("type") != "refresh":
                return None

            # Verify refresh token exists in database
            if self.db_manager:
                token_hash = hashlib.sha256(refresh_token.encode('utf-8')).hexdigest()
                query = """
                SELECT id, user_id, is_revoked, expires_at
                FROM refresh_tokens
                WHERE token_hash = %s
                """
                results = self.db_manager.execute_query(query, (token_hash,))
                if not results or results[0]['is_revoked']:
                    return None

                # Check expiration
                if results[0]['expires_at'] < datetime.utcnow():
                    return None

                # Get user data
                user_query = "SELECT id, username, email, permissions FROM users WHERE id = %s"
                user_results = self.db_manager.execute_query(user_query, (results[0]['user_id'],))
                if not user_results:
                    return None

                user_data = {
                    "id": str(user_results[0]['id']),
                    "username": user_results[0]['username'],
                    "email": user_results[0]['email'],
                    "permissions": user_results[0].get('permissions', [])
                }
            else:
                # Fallback if no database
                user_data = {
                    "id": payload["sub"],
                    "username": payload.get("username", "unknown"),
                    "email": payload.get("email"),
                    "permissions": payload.get("permissions", [])
                }

            # Create new access token
            access_token = self.create_access_token(user_data)

            return {
                "access_token": access_token,
                "token_type": "Bearer",
                "expires_in": self.access_token_expire_minutes * 60
            }
        except Exception as e:
            logger.error(f"Error refreshing token: {e}")
            return None

    def revoke_token(self, token: str) -> bool:
        """Revoke a refresh token"""
        if not self.db_manager:
            return False

        try:
            token_hash = hashlib.sha256(token.encode('utf-8')).hexdigest()
            query = """
            UPDATE refresh_tokens
            SET is_revoked = TRUE, revoked_at = NOW()
            WHERE token_hash = %s AND is_revoked = FALSE
            """
            rows_affected = self.db_manager.execute_update(query, (token_hash,))
            return rows_affected > 0
        except Exception as e:
            logger.error(f"Error revoking token: {e}")
            return False


def get_auth_service(project_root: Optional[Path] = None) -> AuthenticationService:
    """Get global authentication service"""
    return AuthenticationService(project_root)
