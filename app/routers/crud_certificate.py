from sqlmodel import Session,select
from models.models import Certificates

def create_cert(session:Session,data:dict):
    certificate=Certificates(**data)
    session.add(certificate)
    session.commit()
    session.refresh(certificate)
    return certificate
def get_certificate(session:Session,cert_id:int):
    return session.get(Certificates,cert_id)
def update_certificate(session:Session,cert_id:int,data:dict):
    certificate=session.get(Certificates,cert_id)
    if not certificate:
        return 
    for key,value in data.items():
        setattr(certificate,key,value)
    session.add(certificate)
    session.commit()
    session.refresh(certificate)
    return certificate
