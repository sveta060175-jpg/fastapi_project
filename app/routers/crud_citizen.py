from sqlmodel import Session
from models.models import Citizen


def create_cit(session: Session = None, data: dict = None):
    if session is None or data is None:
        raise ValueError("Сессия и данные необходимы")
    
    citizen = Citizen(**data)
    print(citizen)
    session.add(citizen)
    session.commit()
    session.refresh(citizen)
    return citizen

def get_cit(session:Session,cert_id:int):
    return session.get(Citizen,cert_id)


def update_cit(session:Session,cert_id:int,data:dict):
    citizen=session.get(Citizen,cert_id)
    if not citizen:
        return 
    for key,value in data.items():
        setattr(citizen,key,value)
    session.add(citizen)
    session.commit()
    session.refresh(citizen)
    return citizen