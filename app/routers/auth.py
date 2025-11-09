from dotenv import load_dotenv
import os
from passlib.context import CryptContext
from typing import Optional
from jose import JWTError,jwt

from app.models.models import User
from app.db.db import Session, get_session
from fastapi import Depends,HTTPException,status
from fastapi.security import OAuth2PasswordBearer
from datetime import timedelta, datetime, timezone
from sqlmodel import select
import logging

logger=logging.getLogger(__name__)
load_dotenv()
SECRET_KEY=os.getenv("SECRET_KEY")
ALGORITHM=os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES=int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))

pwd_context=CryptContext(schemes=["bcrypt"],deprecated="auto")
oauth2_schem=OAuth2PasswordBearer(tokenUrl="token")

def verify_password(planed_password:str,hashed_password:str) ->bool:
    return pwd_context.verify(planed_password,hashed_password)

def get_password_hash(password:str)->str:
    logger.debug(f"hashing password: {password}")
    return pwd_context.hash(password)

def create_access_token(data:dict,expires_delta:Optional[timedelta]=None)->str:
    to_encode=data.copy()
    expire=datetime.now(timezone.utc)+(expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp":expire})
    return jwt.encode(to_encode,SECRET_KEY,ALGORITHM)

def get_current_user(token:str=Depends(oauth2_schem),session:Session=Depends(get_session))->User:
    credentials_exception=HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="this user is not found",headers={"WWW-Authenticate": "Bearer"})
    try:
        payload=jwt.decode(token,SECRET_KEY,algorithms=[ALGORITHM])
        username=payload.get("sub")
        if not username:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user=session.exec(select(User).where(User.username==username).one_or_one())
    if not user:
        raise credentials_exception
    return user

def require_admin(user:User=Depends(get_current_user)):
    if user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail="admin only")
    return user

