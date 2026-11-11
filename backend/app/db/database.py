"""
Hamare AI recruitment platform mein postgresql database already bana hua hai 
jisme 11 tables han Jab HR kisi candidate ki applications dekhega Fastapi database sae information reterive karega 
ye filedatabase connection aur sessions manage kry gi

"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker,DeclarativeBase
from app.core.config import settings

engine=create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
    echo=settings.DEBUG
)

SessionLocal=sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False
)

class Base(DeclarativeBase):
    pass

def get_db():
    db=SessionLocal()
    try:
        yield db
    finally:
        db.close()

#create engine postgresql ky sath conection manage krta ha
#session maker Database sessions create krta ha
#Declarativebase SQLAlchemy models banana ky liya base class provide krta ha
