from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from datetime import date
from models.models import User
from sqlmodel import Session
from db.db import get_session
from routers.auth import get_current_user
from routers.crud_certificate import create_cert,update_certificate,get_certificate
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix='/api/v1/certificate', tags=['certificate'])

class CertificateCreate(BaseModel):
    citizen_id: int
    number_certificate: str 
    issue_date: date
    issued_by: str
    purpose: str
class CertificateRead(BaseModel):
    id: int
    citizen_id: int
    number_certificate: str 
    issue_date: date
    issued_by: str
    purpose: str
@router.post("/create_certificate",response_model=CertificateRead,description="""
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
def create_certificate(data:CertificateCreate,session:Session=Depends(get_session),_: User=Depends(get_current_user),):
    return create_cert(session,data.model_dump())

@router.get("/{cert_id}",response_model=CertificateRead,description="""
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
def get_cert(cert_id:int,session:Session=Depends(get_session),_: User=Depends(get_current_user)):
    cert=get_certificate(session,cert_id)
    if not cert:
        raise HTTPException(404,"Справка не найдена")
    return cert

@router.put("/{cert_id}",response_model=CertificateRead,description="""
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
def update_cert(data:CertificateRead,cert_id:int,session:Session=Depends(get_session),_: User=Depends(get_current_user)):
    update=update_certificate(session,cert_id,data.model_dump())
    if not update:
        raise HTTPException(404,"Не удалось обновить справочник")
    return update