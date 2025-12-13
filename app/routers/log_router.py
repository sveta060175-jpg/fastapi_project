from sqlmodel import Session,select
from models.models import EventLog
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from datetime import date,datetime
from models.models import User
from sqlmodel import Session
from db.db import get_session
from routers.auth import get_current_user

router=APIRouter(prefix='/api/v1/logs', tags=['logs'])

class EventlogData(BaseModel):
     
    user_id: int
    action: str
    object_type: str
    object_id: str
    created_at: datetime 
    model_config={"from_attributes":True}

    
@router.get("/",response_model=list[EventlogData],description="")

def get_all_logs(session:Session=Depends(get_session),_: User=Depends(get_current_user)):
    log=select(EventLog)
    return session.exec(log).all()
 
