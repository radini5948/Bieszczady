"""
Router dla synchronizacji danych z IMGW
"""
import logging
from typing import Dict

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException

from flood_monitoring.api.dependencies import get_imgw_service
from flood_monitoring.services.imgw import IMGWService

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/sync", tags=["sync"])


@router.post("/all")
async def sync_all_data(
    background_tasks: BackgroundTasks,
    imgw_service: IMGWService = Depends(get_imgw_service),
) -> Dict[str, str]:
    """
    Synchronizuj wszystkie dane z IMGW:
    1. Pobierz i zaktualizuj listę stacji
    2. Dla każdej stacji pobierz i zaktualizuj pomiary
    """
    try:
        # Pobierz i zaktualizuj stacje
        stations = await imgw_service.get_stations()
        if not stations:
            raise HTTPException(
                status_code=500, detail="Nie udało się pobrać listy stacji z IMGW"
            )

        # Uruchom w tle synchronizację pomiarów dla wszystkich stacji
        background_tasks.add_task(sync_all_measurements, imgw_service, stations)

        return {
            "message": f"Rozpoczęto synchronizację {len(stations)} stacji",
            "status": "started",
            "stations_count": str(len(stations)),
        }
    except Exception as e:
        logger.error(f"Błąd podczas synchronizacji: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Błąd podczas synchronizacji: {str(e)}"
        )


async def sync_all_measurements(imgw_service: IMGWService, stations: list):
    """Synchronizuj pomiary dla wszystkich stacji"""
    success_count = 0
    error_count = 0

    for station in stations:
        try:
            station_id = station["kod_stacji"]
            logger.info(f"Rozpoczynam synchronizację stacji {station_id}")

            data = await imgw_service.get_station_data(station_id)
            if data:
                success_count += 1
                logger.info(f"Zakończono synchronizację stacji {station_id}")
            else:
                error_count += 1
                logger.error(f"Brak danych dla stacji {station_id}")

        except Exception as e:
            error_count += 1
            logger.error(
                f"Błąd synchronizacji stacji {station['kod_stacji']}: {str(e)}"
            )
            continue

    logger.info(
        f"Zakończono synchronizację. Sukces: {success_count}, Błędy: {error_count}"
    )


@router.post("/stations")
async def sync_stations(imgw_service: IMGWService = Depends(get_imgw_service)):
    """Synchronizuj dane stacji z IMGW"""
    try:
        stations = await imgw_service.get_stations()
        return {"message": f"Zaktualizowano {len(stations)} stacji"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/station/{station_id}")
async def sync_station_data(
    station_id: str,
    days: int = 7,
    imgw_service: IMGWService = Depends(get_imgw_service),
):
    """Synchronizuj dane z konkretnej stacji"""
    try:
        await imgw_service.get_station_data(station_id, days)
        return {"message": f"Zaktualizowano dane dla stacji {station_id}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
