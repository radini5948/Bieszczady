"""
Router dla endpointów związanych z ostrzeżeniami hydrologicznymi
"""
from fastapi import APIRouter, Depends, HTTPException
from typing import List, Dict, Any
from pydantic import BaseModel  # Add this import
from datetime import datetime

from flood_monitoring.api.dependencies import get_database_service
from flood_monitoring.services.database import DatabaseService
from flood_monitoring.models.warnings import HydroWarning, WarningArea

router = APIRouter(prefix="/warnings", tags=["warnings"])


class WarningAreaResponse(BaseModel):
    wojewodztwo: str
    opis: str
    kod_zlewni: List[str]


class WarningResponse(BaseModel):
    id: int
    opublikowano: datetime
    stopien: str
    data_od: datetime
    data_do: datetime
    prawdopodobienstwo: str
    numer: str
    biuro: str
    zdarzenie: str
    przebieg: str
    komentarz: str
    obszary: List[WarningAreaResponse]


@router.get("/", response_model=List[WarningResponse])
async def get_warnings(db_service: DatabaseService = Depends(get_database_service)):
    """Pobierz listę ostrzeżeń hydrologicznych"""
    try:
        warnings = db_service.get_all_warnings()
        response = []
        for warning in warnings:
            areas = [
                WarningAreaResponse(
                    wojewodztwo=area.wojewodztwo,
                    opis=area.opis,
                    kod_zlewni=area.kod_zlewni
                ) for area in warning.areas
            ]
            response.append(
                WarningResponse(
                    id=warning.id,
                    opublikowano=warning.opublikowano,
                    stopien=warning.stopien,
                    data_od=warning.data_od,
                    data_do=warning.data_do,
                    prawdopodobienstwo=warning.prawdopodobienstwo,
                    numer=warning.numer,
                    biuro=warning.biuro,
                    zdarzenie=warning.zdarzenie,
                    przebieg=warning.przebieg,
                    komentarz=warning.komentarz,
                    obszary=areas
                )
            )
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{warning_id}", response_model=WarningResponse)
async def get_warning(
    warning_id: int,
    db_service: DatabaseService = Depends(get_database_service),
):
    """Pobierz konkretne ostrzeżenie"""
    try:
        warning = db_service.get_warning_by_id(warning_id)
        if not warning:
            raise HTTPException(status_code=404, detail="Warning not found")
        areas = [
            WarningAreaResponse(
                wojewodztwo=area.wojewodztwo,
                opis=area.opis,
                kod_zlewni=area.kod_zlewni
            ) for area in warning.areas
        ]
        return WarningResponse(
            id=warning.id,
            opublikowano=warning.opublikowano,
            stopien=warning.stopien,
            data_od=warning.data_od,
            data_do=warning.data_do,
            prawdopodobienstwo=warning.prawdopodobienstwo,
            numer=warning.numer,
            biuro=warning.biuro,
            zdarzenie=warning.zdarzenie,
            przebieg=warning.przebieg,
            komentarz=warning.komentarz,
            obszary=areas
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))