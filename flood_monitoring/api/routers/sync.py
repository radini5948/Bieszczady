"""
Router dla endpointów synchronizacji danych z IMGW
"""
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from flood_monitoring.services.imgw import IMGWService
from flood_monitoring.api.dependencies import get_imgw_service
import logging
from typing import Dict, Any

router = APIRouter(prefix="/sync", tags=["sync"])
logger = logging.getLogger(__name__)

async def sync_all_measurements(imgw_service: IMGWService, days: int = 7):
    """Synchronizuj pomiary dla wszystkich stacji w tle"""
    try:
        stations = await imgw_service.get_stations()
        for station in stations:
            try:
                await imgw_service.get_station_data(station["id_stacji"], days=days)
            except Exception as e:
                logger.error(f"Błąd synchronizacji stacji {station['id_stacji']}: {str(e)}")
    except Exception as e:
        logger.error(f"Błąd podczas pobierania listy stacji: {str(e)}")

@router.post("/all")
async def sync_all_data(background_tasks: BackgroundTasks, days: int = 7, imgw_service: IMGWService = Depends(get_imgw_service)):
    """Synchronizuj wszystkie dane z IMGW"""
    try:
        background_tasks.add_task(sync_all_measurements, imgw_service, days)
        return {"message": "Rozpoczęto synchronizację wszystkich danych w tle"}
    except Exception as e:
        logger.error(f"Error syncing all data: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/stations")
async def sync_stations(imgw_service: IMGWService = Depends(get_imgw_service)):
    """Synchronizuj dane stacji z IMGW oraz ich pomiary"""
    try:
        stations = await imgw_service.get_stations()
        stan_count = 0
        przeplyw_count = 0
        for station in stations:
            try:
                # Synchronizuj pomiary dla każdej stacji
                measurement_stan = await imgw_service.get_station_data_stan(station["id_stacji"], days=7)
                measurement_przelyw = await imgw_service.get_station_data_przelyw(station["id_stacji"], days=7)
                stan_count += len(measurement_stan["stan_wody"])
                przeplyw_count += len(measurement_przelyw["przelyw"])
                logger.info(f"Synchronizowano pomiary dla stacji {station['id_stacji']}: {len(measurement_stan['stan_wody'])} stan, {len(measurement_przelyw['przelyw'])} przelyw")
            except Exception as e:
                logger.error(f"Błąd synchronizacji pomiarów dla stacji {station['id_stacji']}: {str(e)}")
        return {
            "message": f"Zaktualizowano {len(stations)} stacji, {stan_count} pomiarów stanu wody, {przeplyw_count} pomiarów przepływu"
        }
    except Exception as e:
        logger.error(f"Error syncing stations: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/station/{station_id}")
async def sync_station_data(station_id: str, days: int = 7, imgw_service: IMGWService = Depends(get_imgw_service)):
    """Synchronizuj dane dla konkretnej stacji"""
    try:
        measurements = await imgw_service.get_station_data(station_id, days)
        return {"message": f"Zaktualizowano dane dla stacji {station_id}"}
    except Exception as e:
        logger.error(f"Error syncing station {station_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/warnings")
async def sync_warnings(imgw_service: IMGWService = Depends(get_imgw_service)):
    """Synchronizuj ostrzeżenia hydrologiczne z IMGW"""
    try:
        await imgw_service.sync_warnings()
        return {"message": "Ostrzeżenia hydrologiczne zsynchronizowane"}
    except Exception as e:
        logger.error(f"Error syncing warnings: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))