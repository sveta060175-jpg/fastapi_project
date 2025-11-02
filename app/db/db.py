from sqlmodel import create_engine,Session
from contextlib import contextmanager
import os

DATABASEURL=os.getenv("DATABASEURL","sqllite:///./dev.db")
engine=create_engine(DATABASEURL,echo=False)
def init_db():
    from app.models.models import SQLModel
    SQLModel.metadata.create_all(engine)

@contextmanager
def get_session():
    with Session(engine) as session:
        yield session 