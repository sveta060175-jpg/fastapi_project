from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from app.models.models import User
from sqlmodel import Session, select
from app.db.db import get_session
from .auth import get_password_hash, verify_password, create_access_token
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix='/api/v1/auth', tags=['auth'])

class UserCreate(BaseModel):
    username: str
    password: str

class UserResponse(BaseModel):
    id: int
    username: str

class TokenResp(BaseModel):
    access_token: str
    token_type: str = 'bearer'

class LoginRequest(BaseModel):
    username: str
    password: str

def raise_http_exeception(status_code, detail):
    raise HTTPException(
        status_code=status_code,
        detail=detail
    )

@router.post('/register', response_model=UserResponse, status_code=status.HTTP_201_CREATED,description="""
# Регистрация нового пользователя
Этот эндпоинт позволяет зарегистрировать нового пользователя в системе.
## Процесс регистрации:
1. Проверка уникальности имени пользователя
2. Хеширование пароля
3. Сохранение пользователя в базе данных
## Параметры:
- **username**: Уникальное имя пользователя (3-50 символов)
- **password**: Пароль пользователя (минимум 6 символов)
## Ответ:
- **id**: ID созданного пользователя
- **username**: Имя пользователя
## Ошибки:
- `400 Bad Request` - пользователь уже существует
- `500 Internal Server Error` - внутренняя ошибка сервера
""",)
async def register(payload: UserCreate, session: Session = Depends(get_session)):
    exists = session.exec(select(User).where(User.username == payload.username)).first()
    if exists:
        raise raise_http_exeception(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User already exists"
        )
    user = User(
        username=payload.username,
        hashed_password=get_password_hash(payload.password)
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    logging.info(f"User {user.username} registered")
    return UserResponse(id=user.id, username=user.username)

@router.post('/login', response_model=TokenResp)
async def login_json(
    login_data: LoginRequest,
    session: Session = Depends(get_session)
):
    user = session.exec(select(User).where(User.username == login_data.username)).first()
    if not user:
        raise raise_http_exeception(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password"
        )
    
    if not verify_password(login_data.password, user.hashed_password):

        raise raise_http_exeception(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password"
        )
    
    access_token = create_access_token(
        data={"sub": user.username, "role": user.role}
    )
    logging.info(f"User {user.username} registered")

    return TokenResp(access_token=access_token, token_type="bearer")