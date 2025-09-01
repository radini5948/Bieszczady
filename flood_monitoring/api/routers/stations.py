"""
Router dla endpointów związanych ze stacjami pomiarowymi
"""
import logging
from datetime import datetime
from typing import List, Optional, Dict, Any

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from geojson import Feature, FeatureCollection, Point

from flood_monitoring.api.dependencies import get_database_service
from flood_monitoring.services.database import DatabaseService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/stations", tags=["stations"])


class Station(BaseModel):
    id_stacji: str
    stacja: str
    lat: float
    lon: float
    rzeka: Optional[str] = None
    wojewodztwo: str


class StanMeasurement(BaseModel):
    stan_wody_data_pomiaru: datetime
    stan_wody: float


class PrzeplywMeasurement(BaseModel):
    przeplyw_data: datetime
    przelyw: float


class StationMeasurements(BaseModel):
    stan: List[StanMeasurement]
    przelyw: List[PrzeplywMeasurement]


@router.get("/", response_model=Dict[str, Any])
async def get_stations(db_service: DatabaseService = Depends(get_database_service)):
    """Pobierz listę stacji pomiarowych z bazy danych w formacie GeoJSON"""
    try:
        stations = db_service.get_all_stations()
        features = []

        for station in stations:
            feature = Feature(
                geometry=Point((float(station.lon), float(station.lat))),
                properties={
                    "id_stacji": station.id_stacji,
                    "stacja": station.stacja,
                    "rzeka": station.rzeka,
                    "wojewodztwo:": station.wojewodztwo
                }
            )
            features.append(feature)

        geojson = FeatureCollection(features)
        return geojson

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{station_id}", response_model=StationMeasurements)
async def get_station_data(
    station_id: str,
    days: int = 7,
    db_service: DatabaseService = Depends(get_database_service),
):
    """Pobierz dane z konkretnej stacji z bazy danych"""
    try:
        logger.info(f"Received request for station {station_id} data")
        measurements = db_service.get_station_measurements(station_id, days)
        logger.info(f"Sending response for station {station_id}: {measurements}")
        return measurements
    except Exception as e:
        logger.error(f"Error getting data for station {station_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
