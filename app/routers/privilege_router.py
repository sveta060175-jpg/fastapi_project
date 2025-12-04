from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from datetime import date,datetime
from models.models import User
from sqlmodel import Session
from db.db import get_session
from routers.auth import get_current_user
from routers.crud_privileges import create_privileges,update_privileges,get_privileges

router = APIRouter(prefix='/api/v1/privileges', tags=['privileges'])

class PrivilegesCreate(BaseModel):
    name: str
    description: str
    code: str

class PrivilegesRead(BaseModel):
    id: int
    created_at: datetime

class PrivilegesAll(BaseModel):
    id: int
    name: str
    description: str
    code: str

@router.post("/create_privilege",response_model=PrivilegesAll,description="""Создание сертификатов
Этот эндпоинт позволяет создавать привилегии которые есть в системе.
## Процесс создания:
1. Проверка jwt токена
2. Обновление привилегий в бд
## Параметры:
- **id**: Идентификатор гражданина 
- **name**: Название привилегии
- **description**: Описание
- **purpose**: Предназначение сертификата
## Ответ:

- **name**: Название сертификата
- **purpose**: Предназначение сертификата
- **id**: Номер
- **description**:Описание
## Ошибки:
- `500 Internal Server Error` - внутренняя ошибка сервера
""")
def create_privileg(data:PrivilegesCreate,session:Session=Depends(get_session),_: User=Depends(get_current_user)):
    data_dict = data.model_dump()
    return create_privileges(session,data_dict)

@router.get("/{id}",response_model=PrivilegesRead,description="""Получение сертификатов
Этот эндпоинт позволяет получать привилегии которые есть в системе.
## Процесс получения:
1. Проверка jwt токена
2. Обновление привилегий в бд
## Параметры:
- **id**: Идентификатор гражданина 
- **created_at**: Когда был создан

## Ответ:

- **name**: Название сертификата
- **purpose**: Предназначение сертификата
- **id**: Номер
- **description**:Описание
## Ошибки:
- `500 Internal Server Error` - внутренняя ошибка сервера
""")
def get_privileg(data:PrivilegesAll,id:int,session:Session=Depends(get_session),_: User = Depends(get_current_user)):
    privi=get_privileges(session,id)
    if not privi:
        raise HTTPException(404,"Запрашиваемая привилегия не найдена")
    return privi

@router.put("/{id}",response_model=PrivilegesRead,description="""Обновление сертификатов
Этот эндпоинт позволяет обновлять привилегии которые есть в системе.
## Процесс обновления:
1. Проверка jwt токена
2. Обновление привилегий в бд
## Параметры:
- **id**: Идентификатор гражданина 
- **name**: Название привилегии
- **description**: Описание
- **purpose**: Предназначение сертификата
## Ответ:

- **name**: Название сертификата
- **purpose**: Предназначение сертификата
- **id**: Номер
- **description**:Описание
## Ошибки:
- `500 Internal Server Error` - внутренняя ошибка сервера
""")
def update_privilege(data:PrivilegesRead,id:int,session:Session=Depends(get_session),_: User = Depends(get_current_user)):
    updatepriv=update_privileges(session,id,data.model_dump())
    if not updatepriv:
        raise HTTPException(404,"Не удалось обновить привилегию")
    return updatepriv

def get_all_privileg(id:int,session:Session=Depends(get_session),_: User = Depends(get_current_user)):
    privi=get_all_privileg(session,id)
    session.get(PrivilegesAll)

