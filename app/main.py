from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers.auth_router import router as auth_router
from routers.certificate_router import router as cert_router
from db.db import  init_db
import logging

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(), 
        logging.FileHandler('app.log') 
    ]
)

logger = logging.getLogger(__name__)

app = FastAPI(debug=True, title="Система учета льготных категорий граждан",
    description="API для учета льготных категорий граждан",
    version="1.0.0",
    contact={"email": "bLb3Y@example.com"},
    license_info={"name": "MIT License"},)



app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(cert_router)
app.include_router(auth_router)

@app.get("/db")
async def init_database():
    """Инициализация БД."""    
    init_db()
    return {"message": "Система учета льготных категорий граждан", "status": "работает", "version": "1.0.0",'база данных': 'создана'}


@app.get("/health")
async def health_check():
    """Healthcheck/проверка работоспособности.
    Returns:
        dict : статус
    """    
    return {"status": "healthy"}