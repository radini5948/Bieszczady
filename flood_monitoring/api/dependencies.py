"""
Definicje zależności dla FastAPI
"""
from fastapi import Depends
from sqlalchemy.orm import Session

from flood_monitoring.core.database import get_db
from flood_monitoring.services.database import DatabaseService
from flood_monitoring.services.imgw import IMGWService


def get_database_service(db: Session = Depends(get_db)) -> DatabaseService:
    return DatabaseService(db)


def get_imgw_service(
    db_service: DatabaseService = Depends(get_database_service),
) -> IMGWService:
    return IMGWService(db_service)
