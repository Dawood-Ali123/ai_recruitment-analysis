from fastapi import FastAPI
from sqlalchemy import text
from app.core.config import settings
from app.db.database import engine
from app.routers.auth import router as auth_router
from app.routers.jobs import router as jobs_router
from app.routers.applications import router as applications_router
from app.routers import email
from fastapi.middleware.cors import CORSMiddleware
from app.routers import audit_logs
app=FastAPI(
    title=settings.APP_NAME,
    debug=settings.DEBUG,
    version="1.0.0"
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(auth_router)
app.include_router(jobs_router)
app.include_router(applications_router)
app.include_router(email.router)
app.include_router(audit_logs.router)
@app.get("/")
def home():
        return {
        "message": "Welcome to AI Recruitment Platform API",
        "status": "Running"
    }

@app.get("/health/db")
def database_health():
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        return{
             "status":"sucess",
             "database":"Postgresql Connected"
        }
    except Exception as e:
         
        print("DATABASE ERROR:", repr(e))
        return{
                "status": "error",
            "database": "Connection Failed"
         }
                
