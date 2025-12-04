from sqlmodel import Session
from models.models import Privilege

def create_privileges(session: Session = None, data: dict = None):
    if session is None or data is None:
        raise ValueError("Сессия и данные необходимы")
    
    privilege = Privilege(**data)
    session.add(privilege)
    session.commit()
    session.refresh(privilege)
    return privilege

def get_privileges(session:Session,privilege_id:int):
    return session.get(Privilege,privilege_id)

def update_privileges(session:Session,privilege_id:int,data:dict):
    privilege=session.get(Privilege,privilege_id)
    if not privilege:
        return 
    for key,value in data.items():
        setattr(privilege,key,value)
    session.add(privilege)
    session.commit()
    session.refresh(privilege)
    return privilege
