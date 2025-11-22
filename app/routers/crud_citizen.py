from sqlmodel import Session,select
from models.models import Citizen

def create_citizen(session:Session,data:dict):
    citizen=Citizen(**data)
    session.add(citizen)
    session.commit()
    session.refresh(citizen)
    return citizen
def get_citizen(session:Session,cert_id:int):
    return session.get(Citizen,cert_id)
def update_citizen(session:Session,cert_id:int,data:dict):
    citizen=session.get(Citizen,cert_id)
    if not citizen:
        return 
    for key,value in data.items():
        setattr(citizen,key,value)
    session.add(citizen)
    session.commit()
    session.refresh(citizen)
    return citizen