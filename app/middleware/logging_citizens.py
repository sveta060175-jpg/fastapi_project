from fastapi import Request
from typing import Optional
from db.db import Session
from models.models import EventLog, User


def log_event(
    session: Session,
    user_id: Optional[int],
    action: str,
    object_type: Optional[str] = None,
    object_id: Optional[str] = None
):
    """Основная функция для логирования событий"""
    event = EventLog(
        user_id=user_id,
        action=action,
        object_type=object_type,
        object_id=object_id
    )
    session.add(event)
    session.commit()
    session.refresh(event)
    return event

def log_api_call(
    session: Session,
    user: Optional[User],
    request: Request,
    action: str,
    object_type: Optional[str] = None,
    object_id: Optional[str] = None
):
    """Логирование вызовов API"""
    user_id = user.id if user else None
    return log_event(
        session=session,
        user_id=user_id,
        action=f"API_{request.method}_{action}",
        object_type=object_type,
        object_id=object_id
    )

