from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from models.models import User
from sqlmodel import Session
from db.db import get_session
from routers.auth import get_current_user
from routers.crud_citizen import create_cit,get_cit,update_cit,delete_cit
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix='/api/v1/citizen', tags=['citizen'])


    
class CitizenRead(BaseModel):
    lastname: str
    firstname: str
    middlename: str
    id_snils: str
class CitizenData(BaseModel):
    lastname: str
    firstname: str
    middlename: str
    id_snils: str
    privilege_id: int

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
def create_citizen(data:CitizenData,session:Session=Depends(get_session),_: User=Depends(get_current_user)):
    data_dict = data.model_dump()
    return create_cit(session,data_dict)

@router.get("/{citizen_id}",response_model=CitizenRead,description="""
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
def get_citizen(citizen_id:int,session:Session=Depends(get_session),_: User = Depends(get_current_user)):
    citizen=get_cit(session,citizen_id)
    if not citizen:
        raise HTTPException(404,"Запрашиваемый льготник не найден")
    return citizen

@router.put("/{citizen_id}",response_model=CitizenRead,description="""
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
def update_citizen(data:CitizenData,citizen_id:int,session:Session=Depends(get_session),_: User = Depends(get_current_user)):
    update=update_cit(session,citizen_id,data.model_dump())
    if not update:
        raise HTTPException(404,"Не удалось обновить справочник")
    return update

@router.delete("/{citizen_id}",response_model=CitizenRead,description="")
def del_citizen(citizen_id:int,session:Session=Depends(get_session),_: User = Depends(get_current_user)):
    delete=delete_cit(session,citizen_id)
    if not delete:
        raise HTTPException(404,"Не найден гражданин для удаления")
    return delete