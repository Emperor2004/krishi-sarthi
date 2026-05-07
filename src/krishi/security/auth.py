"""Enhanced authentication with JWT tokens and security."""
import os
import time
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import jwt
from passlib.context import CryptContext
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from ..database import UserCRUD, User

# JWT Configuration
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 1440  # 24 hours

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class SecurityManager:
    """Manages authentication, authorization, and security features."""
    
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash."""
        return pwd_context.verify(plain_password, hashed_password)
    
    @staticmethod
    def get_password_hash(password: str) -> str:
        """Hash a password."""
        return pwd_context.hash(password)
    
    @staticmethod
    def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
        """Create JWT access token."""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt
    
    @staticmethod
    def verify_token(token: str) -> Optional[Dict[str, Any]]:
        """Verify JWT token and return payload."""
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            return payload
        except jwt.PyJWTError:
            return None
    
    @staticmethod
    def authenticate_user(db: Session, phone: str, password: str) -> Optional[User]:
        """Authenticate user with phone and password."""
        user = UserCRUD.get_user_by_phone(db, phone)
        if not user or not user.is_active:
            return None
        
        if not SecurityManager.verify_password(password, user.password_hash):
            return None
        
        return user
    
    @staticmethod
    def get_current_user(token: str, db: Session) -> Optional[User]:
        """Get current user from JWT token."""
        payload = SecurityManager.verify_token(token)
        if payload is None:
            return None
        
        user_id: int = payload.get("sub")
        if user_id is None:
            return None
        
        user = UserCRUD.get_user_by_id(db, user_id)
        if user is None:
            return None
        
        return user


class RateLimiter:
    """Simple in-memory rate limiter."""
    
    def __init__(self):
        self.requests = {}
    
    def is_allowed(self, key: str, limit: int, window: int) -> bool:
        """Check if request is allowed based on rate limit."""
        now = time.time()
        
        if key not in self.requests:
            self.requests[key] = []
        
        # Remove old requests outside the window
        self.requests[key] = [req_time for req_time in self.requests[key] 
                            if now - req_time < window]
        
        # Check if under limit
        if len(self.requests[key]) >= limit:
            return False
        
        # Add current request
        self.requests[key].append(now)
        return True


# Rate limiting configuration
LOGIN_RATE_LIMIT = 5  # 5 login attempts
LOGIN_WINDOW = 300  # 5 minutes (300 seconds)

API_RATE_LIMIT = 100  # 100 requests per minute
API_WINDOW = 60  # 1 minute

# Global rate limiter instance
rate_limiter = RateLimiter()


def check_login_rate_limit(phone: str) -> bool:
    """Check login rate limit for a phone number."""
    return rate_limiter.is_allowed(f"login:{phone}", LOGIN_RATE_LIMIT, LOGIN_WINDOW)


def check_api_rate_limit(client_ip: str) -> bool:
    """Check API rate limit for a client IP."""
    return rate_limiter.is_allowed(f"api:{client_ip}", API_RATE_LIMIT, API_WINDOW)
