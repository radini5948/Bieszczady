"""
Konfiguracja bazy danych
"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session, sessionmaker

from flood_monitoring.core.config import get_settings

settings = get_settings()

# Tworzymy silnik bazy danych
engine = create_engine(settings.DATABASE_URL)

# Tworzymy fabrykę sesji
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Tworzymy bazową klasę dla modeli
Base = declarative_base()


def get_db() -> Session:
    """Funkcja pomocnicza do pobierania sesji bazy danych"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
