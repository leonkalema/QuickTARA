from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import secrets
import hashlib

# Security configuration
SECRET_KEY = "your-secret-key-change-in-production"  # Change this in production!
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7

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
        
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        
        to_encode.update({"exp": expire, "type": "access"})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt
    
    def create_refresh_token(self, data: Dict[str, Any]) -> str:
        """Create JWT refresh token"""
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
        to_encode.update({"exp": expire, "type": "refresh"})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt
    
    def verify_token(self, token: str, token_type: str = "access") -> Dict[str, Any]:
        """Verify and decode JWT token"""
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            
            # Check token type
            if payload.get("type") != token_type:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token type"
                )
            
            # Check expiration
            exp = payload.get("exp")
            if exp is None or datetime.utcnow() > datetime.fromtimestamp(exp):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Token expired"
                )
            
            return payload
            
        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials"
            )
    
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
