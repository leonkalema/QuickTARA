from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Optional, Dict, Any
import hashlib
import logging
import os
import secrets
import stat

import jwt  # PyJWT
from passlib.context import CryptContext
from fastapi import HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# JWT secret — never hardcoded. Resolution order:
#   1. QUICKTARA_JWT_SECRET env var
#   2. ./.quicktara_jwt_secret file (auto-generated on first run, mode 0600)
# ---------------------------------------------------------------------------
_SECRET_FILE: Path = Path(os.getcwd()) / ".quicktara_jwt_secret"


def _load_or_create_jwt_secret() -> str:
    """Return a stable JWT signing secret, generating one on first run."""
    env_secret = os.environ.get("QUICKTARA_JWT_SECRET")
    if env_secret:
        return env_secret

    if _SECRET_FILE.exists():
        return _SECRET_FILE.read_text(encoding="utf-8").strip()

    logger.warning(
        "QUICKTARA_JWT_SECRET not set — generating a persistent random secret at %s. "
        "For production, set QUICKTARA_JWT_SECRET in the environment instead.",
        _SECRET_FILE,
    )
    new_secret = secrets.token_urlsafe(64)
    _SECRET_FILE.write_text(new_secret, encoding="utf-8")
    try:
        os.chmod(_SECRET_FILE, stat.S_IRUSR | stat.S_IWUSR)  # 0600
    except OSError:
        pass
    return new_secret


SECRET_KEY: str = _load_or_create_jwt_secret()
ALGORITHM: str = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
REFRESH_TOKEN_EXPIRE_DAYS: int = 7

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT Bearer token scheme
security = HTTPBearer()

class SecurityManager:
    def __init__(self):
        self.pwd_context = pwd_context
        
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash"""
        return self.pwd_context.verify(plain_password, hashed_password)
    
    def get_password_hash(self, password: str) -> str:
        """Hash a password"""
        return self.pwd_context.hash(password)
    
    def create_access_token(self, data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
        """Create JWT access token"""
        to_encode = data.copy()
        expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
        to_encode.update({"exp": expire, "type": "access"})
        return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    def create_refresh_token(self, data: Dict[str, Any]) -> str:
        """Create JWT refresh token"""
        to_encode = data.copy()
        expire = datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
        to_encode.update({"exp": expire, "type": "refresh"})
        return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    def verify_token(self, token: str, token_type: str = "access") -> Dict[str, Any]:
        """Verify and decode JWT token. PyJWT validates `exp` natively."""
        try:
            payload: Dict[str, Any] = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token expired",
            )
        except jwt.InvalidTokenError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
            )

        if payload.get("type") != token_type:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type",
            )
        return payload
    
    def generate_refresh_token_hash(self, user_id: str, device_info: str = "") -> tuple[str, str]:
        """Generate a secure refresh token and its hash"""
        # Create a random token
        raw_token = secrets.token_urlsafe(32)
        
        # Create hash for storage (includes user_id and device_info for security)
        token_data = f"{raw_token}:{user_id}:{device_info}"
        token_hash = hashlib.sha256(token_data.encode()).hexdigest()
        
        return raw_token, token_hash
    
    def verify_refresh_token_hash(self, raw_token: str, stored_hash: str, user_id: str, device_info: str = "") -> bool:
        """Verify refresh token against stored hash"""
        token_data = f"{raw_token}:{user_id}:{device_info}"
        computed_hash = hashlib.sha256(token_data.encode()).hexdigest()
        return secrets.compare_digest(computed_hash, stored_hash)

# Global security manager instance
security_manager = SecurityManager()

def create_user_token_data(user_id: str, email: str, roles: list, organizations: list) -> Dict[str, Any]:
    """Create token payload data for a user"""
    return {
        "sub": user_id,  # Subject (user ID)
        "email": email,
        "roles": roles,
        "organizations": organizations,
        "iat": datetime.utcnow().timestamp()  # Issued at
    }

def extract_user_from_token(token_payload: Dict[str, Any]) -> Dict[str, Any]:
    """Extract user information from token payload"""
    return {
        "user_id": token_payload.get("sub"),
        "email": token_payload.get("email"),
        "roles": token_payload.get("roles", []),
        "organizations": token_payload.get("organizations", [])
    }
