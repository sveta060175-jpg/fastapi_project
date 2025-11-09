from sqlmodel import create_engine, Session, SQLModel
import os
import logging
from sqlalchemy import inspect


logger = logging.getLogger(__name__)
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./dev.db")
engine = create_engine(DATABASE_URL, echo=True)

def init_db():
    """Создание всех таблиц в базе данных с проверкой"""
    try:
        inspector = inspect(engine)
        existing_tables = inspector.get_table_names()
        if existing_tables:
            logger.info(f"База данных уже существует. Таблицы: {existing_tables}")
            return
        SQLModel.metadata.create_all(engine)
        logger.info("Таблицы базы данных успешно созданы")
    except Exception as e:
        logger.error(f"Ошибка при создании базы данных: {e}")
        raise
    
def get_session():
    """Контекстный менеджер для работы с сессией БД"""
    session = Session(engine)
    try:
        yield session
        session.commit() 
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()