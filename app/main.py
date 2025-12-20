from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from middleware.logging_middleware import LoggingMiddleware
from routers.auth_router import router as auth_router
from routers.certificate_router import router as cert_router
from db.db import  init_db
import logging
from routers.citizen_router import router as citizen_router
from routers.privilege_router import router as privilege_router
from routers.excel_routers import router as excel_router
from utils.utils import read_readme
from routers.log_router import router as event_router

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(), 
        logging.FileHandler('app.log') 
    ]
)

routers = (auth_router,cert_router,citizen_router,excel_router,privilege_router,event_router)


logger = logging.getLogger(__name__)

app = FastAPI(debug=True, title="Система учета льготных категорий граждан",
    description=read_readme(),
    version="1.0.0",
    contact={"email": "bLb3Y@example.com"},
    license_info={"name": "MIT License"},)

app.add_middleware(LoggingMiddleware)
list(map(app.include_router, routers))

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



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