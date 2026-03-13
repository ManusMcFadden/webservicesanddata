import os
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status, Header
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
import models, database
from database import get_db
from models import User

# Configuration
SECRET_KEY = "YOUR_SUPER_SECRET_RANDOM_STRING_HERE" 
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

MCP_SECRET_KEY = "tennis_manager_dev_key_2024" 
USER_TO_IMPERSONATE = "admin"

# Password hashing setup
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

# --- UTILS ---
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password[:71])

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

# --- DEPENDENCY ---
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db), x_mcp_token: Optional[str] = Header(None)):
    if x_mcp_token == MCP_SECRET_KEY:
        user = db.query(models.User).filter(models.User.username == USER_TO_IMPERSONATE).first()
        if user:
            return user
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
        
    user = db.query(models.User).filter(models.User.username == username).first()
    if user is None:
        raise credentials_exception
    return user

def get_current_admin(current_user: models.User = Depends(get_current_user)):

    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Operation not permitted. Admin rights required."
        )
    return current_user