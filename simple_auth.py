"""
Simple Authentication System with Demo Account
Based on proven patterns from FastAPI docs
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from datetime import datetime, timedelta
from typing import Optional
import jwt
import hashlib

# Demo credentials - hardcoded for simplicity
DEMO_USERS = {
    "demo@auravest.com": {
        "email": "demo@auravest.com", 
        "password_hash": "demo123",  # In production, this would be hashed
        "name": "Demo User",
        "id": 1
    },
    "admin@auravest.com": {
        "email": "admin@auravest.com",
        "password_hash": "admin123",
        "name": "Admin User", 
        "id": 2
    }
}

# Configuration
SECRET_KEY = "demo-secret-key-change-in-production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24 hours for demo

security = HTTPBearer(auto_error=False)

# Models
class UserLogin(BaseModel):
    email: str
    password: str

class UserRegister(BaseModel):
    email: str
    password: str
    name: Optional[str] = None

class Token(BaseModel):
    access_token: str
    token_type: str

class User(BaseModel):
    id: int
    email: str
    name: str

# Helper functions
def verify_password(plain_password: str, stored_password: str) -> bool:
    """Simple password verification - for demo purposes only"""
    return plain_password == stored_password

def create_access_token(data: dict) -> str:
    """Create JWT token"""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def authenticate_user(email: str, password: str) -> Optional[dict]:
    """Authenticate user credentials"""
    user = DEMO_USERS.get(email)
    if not user or not verify_password(password, user["password_hash"]):
        return None
    return user

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> User:
    """Get current user from JWT token"""
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=401, detail="Invalid authentication credentials")
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid authentication credentials")
    
    user = DEMO_USERS.get(email)
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")
    
    return User(
        id=user["id"],
        email=user["email"], 
        name=user["name"]
    )

def add_demo_user(email: str, password: str, name: str = None) -> bool:
    """Add a new demo user (for registration)"""
    if email in DEMO_USERS:
        return False
    
    DEMO_USERS[email] = {
        "email": email,
        "password_hash": password,  # In production, hash this
        "name": name or email.split("@")[0],
        "id": len(DEMO_USERS) + 1
    }
    return True

# Initialize empty data for fresh start
def init_demo_data():
    """Initialize empty data structures for fresh start"""
    return {}, {}, {}