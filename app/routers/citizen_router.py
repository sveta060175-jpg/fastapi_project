from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from datetime import date
from models.models import User
from sqlmodel import Session, select
from db.db import get_session
from routers.auth import get_current_user
from routers.crud_citizen import create_citizen,get_citizen,update_citizen
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix='/api/v1/citizen', tags=['citizen'])

class CitizenCreate(BaseModel):
    id: int
    lastname: str
    firstname: str
class CitizenRead(BaseModel):
    id: int
    lastname: str
    firstname: str
    middlename: str
    id_snils: str
@router.post("/create_citizen",response_model=CitizenRead,description="""
# Создание льгот
Этот эндпоинт позволяет создавать новые льгот в системе.
## Процесс создания:
1. Проверка jwt токена
2. Создание льгот в бд
## Параметры:
- **citizen_id**: Идентификатор гражданина 
- **number_certificate**: Номер льгот
- **issue_date**: Пороговая дата
- **purpose**: Предназначение льготы
## Ответ:
- **citizen_id**: Идентификатор гражданина 
- **number_certificate**: Номер льгот
- **issue_date**: Пороговая дата
- **purpose**: Предназначение льготы
- **id**: Номер
- **issued_by**: Пользователь создавший пороговую дату
## Ошибки:
- `500 Internal Server Error` - внутренняя ошибка сервера
""",)
def create_citizen(data:CitizenCreate,session:Session=Depends(get_session)):
    return create_citizen(data,session)

@router.get("/{cert_id}",response_model=CitizenRead,description="""
# Получение льгот
Этот эндпоинт позволяет получать льготы которые есть в системе.
## Процесс получения:
1. Проверка jwt токена
2. Получение льгот из бд
## Параметры:
- **citizen_id**: Идентификатор гражданина 
- **number_certificate**: Номер льгот
- **issue_date**: Пороговая дата
- **purpose**: Предназначение льготы
## Ответ:
- **citizen_id**: Идентификатор гражданина 
- **number_certificate**: Номер льгот
- **issue_date**: Пороговая дата
- **purpose**: Предназначение льготы
- **id**: Номер
- **issued_by**: Пользователь создавший пороговую дату
## Ошибки:
- `500 Internal Server Error` - внутренняя ошибка сервера
""",)
def get_citizen(cert_id:int,session:Session=Depends(get_session),current_user: User = Depends(get_current_user)):
    citizen=get_citizen(session,cert_id)
    if not citizen:
        raise HTTPException(404,"Справка не найдена")
    return citizen

@router.put("/{cert_id}",response_model=CitizenRead,description="""
# Обновление льгот
Этот эндпоинт позволяет обновлять льготы которые есть в системе.
## Процесс создания:
1. Проверка jwt токена
2. Обновление льгот в бд
## Параметры:
- **citizen_id**: Идентификатор гражданина 
- **number_certificate**: Номер льгот
- **issue_date**: Пороговая дата
- **purpose**: Предназначение льготы
## Ответ:
- **citizen_id**: Идентификатор гражданина 
- **number_certificate**: Номер льгот
- **issue_date**: Пороговая дата
- **purpose**: Предназначение льготы
- **id**: Номер
- **issued_by**: Пользователь создавший пороговую дату
## Ошибки:
- `500 Internal Server Error` - внутренняя ошибка сервера
""",)
def update_citizen(data:CitizenRead,cert_id:int,session:Session=Depends(get_session),current_user: User = Depends(get_current_user)):
    update=update_citizen(data,cert_id,session)
    if not update:
        raise HTTPException(404,"Не удалось обновить справочник")
    return update
