"""
Główny plik aplikacji FastAPI
"""
import logging
import os
import sys
from typing import Dict

import aiohttp
from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from sqlalchemy.orm import Session

from flood_monitoring.api.dependencies import get_database_service, get_imgw_service
from flood_monitoring.api.routers import stations, sync
from flood_monitoring.core.config import get_settings
from flood_monitoring.core.database import get_db
from flood_monitoring.services.database import DatabaseService
from flood_monitoring.services.imgw import IMGWService

# Konfiguracja loggingu
log_level = os.getenv("LOG_LEVEL", "INFO")
logging.basicConfig(
    level=getattr(logging, log_level),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[logging.StreamHandler(sys.stdout)],
)

# Ustawienie poziomu logowania dla wszystkich loggerów
logging.getLogger("flood_monitoring").setLevel(logging.DEBUG)
logger = logging.getLogger(__name__)

settings = get_settings()
app = FastAPI(
    title=settings.PROJECT_NAME, openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(stations.router)
app.include_router(sync.router)


@app.get("/")
async def root():
    """Endpoint główny"""
    logger.info("Received request to root endpoint")
    return {"message": "Flood Monitoring System API"}


@app.get("/health", response_model=Dict[str, str])
async def health_check(
    db: Session = Depends(get_db), imgw_service: IMGWService = Depends(get_imgw_service)
):
    """Sprawdź stan aplikacji i połączenia z bazą danych"""
    logger.info("Performing health check")
    status = {
        "status": "healthy",
        "database": "connected",
        "api": "running",
        "imgw_api": "connected",
    }

    try:
        # Sprawdź połączenie z bazą danych
        db.execute(text("SELECT 1"))
        logger.debug("Database connection test successful")
    except Exception as e:
        logger.error(f"Database connection test failed: {str(e)}")
        status["status"] = "unhealthy"
        status["database"] = f"error: {str(e)}"
        raise HTTPException(status_code=503, detail=status)

    try:
        # Sprawdź połączenie z IMGW
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{imgw_service.base_url}/station") as response:
                if response.status != 200:
                    logger.error(f"IMGW API test failed with status {response.status}")
                    status["status"] = "unhealthy"
                    status["imgw_api"] = f"error: status {response.status}"
                    raise HTTPException(status_code=503, detail=status)
                logger.debug("IMGW API connection test successful")
    except Exception as e:
        logger.error(f"IMGW API connection test failed: {str(e)}")
        status["status"] = "unhealthy"
        status["imgw_api"] = f"error: {str(e)}"
        raise HTTPException(status_code=503, detail=status)

    logger.info("Health check completed successfully")
    return status
