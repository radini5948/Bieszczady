import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any

from geoalchemy2.shape import from_shape
from shapely.geometry import Point
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from sqlalchemy import func, and_

from flood_monitoring.models.measurements import PrzeplywMeasurement, StanMeasurement
from flood_monitoring.models.station import Station
from flood_monitoring.models.warnings import HydroWarning, WarningArea
logger = logging.getLogger(__name__)


class DatabaseService:
    def __init__(self, db_session: Session):
        self.db = db_session

    def get_all_stations(self) -> list[Station]:
        """Pobierz wszystkie stacje z bazy danych"""
        return self.db.query(Station).all()

    def get_all_warnings(self):
        """Pobierz wszystkie ostrzeżenia"""
        return self.db.query(HydroWarning).all()

    def get_warning_by_id(self, warning_id: int):
        """Pobierz ostrzeżenie po ID"""
        return self.db.query(HydroWarning).filter(HydroWarning.id == warning_id).first()
    def get_or_create_station(
        self,
        id_stacji: str,
        stacja: str,
        lat: float,
        lon: float,
        rzeka: str,
        wojewodztwo: str

    ) -> Station:
        """Pobierz lub utwórz stację"""
        station = self.db.query(Station).filter_by(id_stacji=id_stacji).first()
        if not station:
            # Tworzymy punkt geometryczny
            point = Point(lon, lat)
            geom = from_shape(point, srid=4326)

            station = Station(
                id_stacji=id_stacji,
                stacja=stacja,
                lat=lat,
                lon=lon,
                rzeka=rzeka,
                geom=geom,
                wojewodztwo=wojewodztwo
            )
            self.db.add(station)
            try:
                self.db.commit()
            except IntegrityError:
                self.db.rollback()
                raise
        return station

    def add_stan_measurement(
        self, station_id: str, stan_wody_data_pomiaru: datetime, stan_wody: float
    ) -> bool:
        """Dodaj pomiar stanu wody. Zwraca True jeśli dodano nowy pomiar, False jeśli już istniał."""
        existing = (
            self.db.query(StanMeasurement)
            .filter_by(station_id=station_id, stan_wody_data_pomiaru=stan_wody_data_pomiaru)
            .first()
        )

        if existing:
            return False

        measurement_id = f"{station_id}_{stan_wody_data_pomiaru.isoformat()}"
        measurement = StanMeasurement(
            id=measurement_id, station_id=station_id, stan_wody_data_pomiaru=stan_wody_data_pomiaru, stan_wody=stan_wody
        )
        self.db.add(measurement)
        try:
            self.db.commit()
            return True
        except IntegrityError:
            self.db.rollback()
            return False

    def add_przeplyw_measurement(
        self, station_id: str, przeplyw_data: datetime, przelyw: float
    ) -> bool:
        """Dodaj pomiar przepływu. Zwraca True jeśli dodano nowy pomiar, False jeśli już istniał."""
        existing = (
            self.db.query(PrzeplywMeasurement)
            .filter_by(station_id=station_id, przeplyw_data=przeplyw_data)
            .first()
        )

        if existing:
            return False

        measurement_id = f"{station_id}_{przeplyw_data.isoformat()}"
        measurement = PrzeplywMeasurement(
            id=measurement_id,
            station_id=station_id,
            przeplyw_data=przeplyw_data,
            przelyw=przelyw
        )
        self.db.add(measurement)
        try:
            self.db.commit()
            return True
        except IntegrityError:
            self.db.rollback()
            return False

    def get_station_measurements(self, station_id: str, days: int = 1):
        """Pobierz pomiary z konkretnej stacji z ostatnich X dni"""
        from datetime import timedelta

        start_date = datetime.now() - timedelta(days=days)

        logger.info(f"Fetching measurements for station {station_id} from {start_date}")

        stan_measurements = (
            self.db.query(StanMeasurement)
            .filter(
                StanMeasurement.station_id == station_id,
                StanMeasurement.stan_wody_data_pomiaru >= start_date,
            )
            .order_by(StanMeasurement.stan_wody_data_pomiaru.asc())
            .all()
        )

        przeplyw_measurements = (
            self.db.query(PrzeplywMeasurement)
            .filter(
                PrzeplywMeasurement.station_id == station_id,
                PrzeplywMeasurement.przeplyw_data >= start_date,
            )
            .order_by(PrzeplywMeasurement.przeplyw_data.asc())
            .all()
        )

        result = {
            "stan": [
                {"stan_wody_data_pomiaru": m.stan_wody_data_pomiaru, "stan_wody": m.stan_wody} for m in stan_measurements
            ],
            "przelyw": [
                {"przeplyw_data": m.przeplyw_data, "przelyw": m.przelyw}
                for m in przeplyw_measurements
            ],
        }

        logger.info(f"Retrieved {len(stan_measurements)} water level and {len(przeplyw_measurements)} flow measurements for station {station_id} from last {days} days")

        return result

    def get_station_measurements_extended(self, station_id: str, days: int = 1, limit: int = 100) -> Dict[str, List[Dict[str, Any]]]:
        """Pobierz rozszerzone pomiary z konkretnej stacji z większą ilością punktów danych dla wykresów"""
        start_date = datetime.now() - timedelta(days=days)

        stan_measurements = (
            self.db.query(StanMeasurement)
            .filter(
                StanMeasurement.station_id == station_id,
                StanMeasurement.stan_wody_data_pomiaru >= start_date,
            )
            .order_by(StanMeasurement.stan_wody_data_pomiaru.desc())
            .limit(limit)
            .all()
        )

        przeplyw_measurements = (
            self.db.query(PrzeplywMeasurement)
            .filter(
                PrzeplywMeasurement.station_id == station_id,
                PrzeplywMeasurement.przeplyw_data >= start_date,
            )
            .order_by(PrzeplywMeasurement.przeplyw_data.desc())
            .limit(limit)
            .all()
        )

        stan_measurements.reverse()
        przeplyw_measurements.reverse()

        result = {
            "stan": [
                {"stan_wody_data_pomiaru": m.stan_wody_data_pomiaru, "stan_wody": m.stan_wody} for m in stan_measurements
            ],
            "przelyw": [
                {"przeplyw_data": m.przeplyw_data, "przelyw": m.przelyw}
                for m in przeplyw_measurements
            ],
        }

        logger.info(f"Retrieved extended data: {len(stan_measurements)} water level and {len(przeplyw_measurements)} flow measurements for station {station_id} from last {days} days (limit: {limit})")

        return result

    def get_station_measurements_batch(self, station_id: str, days: int = 1, batch_size: int = 50, offset: int = 0) -> Dict[str, List[Dict[str, Any]]]:
        """Pobierz pomiary w partiach dla lepszej wydajności przy dużych zbiorach danych"""
        start_date = datetime.now() - timedelta(days=days)

        stan_measurements = (
            self.db.query(StanMeasurement)
            .filter(
                StanMeasurement.station_id == station_id,
                StanMeasurement.stan_wody_data_pomiaru >= start_date,
            )
            .order_by(StanMeasurement.stan_wody_data_pomiaru.desc())
            .offset(offset)
            .limit(batch_size)
            .all()
        )

        przeplyw_measurements = (
            self.db.query(PrzeplywMeasurement)
            .filter(
                PrzeplywMeasurement.station_id == station_id,
                PrzeplywMeasurement.przeplyw_data >= start_date,
            )
            .order_by(PrzeplywMeasurement.przeplyw_data.desc())
            .offset(offset)
            .limit(batch_size)
            .all()
        )

        stan_measurements.reverse()
        przeplyw_measurements.reverse()

        result = {
            "stan": [
                {"stan_wody_data_pomiaru": m.stan_wody_data_pomiaru, "stan_wody": m.stan_wody} for m in stan_measurements
            ],
            "przelyw": [
                {"przeplyw_data": m.przeplyw_data, "przelyw": m.przelyw}
                for m in przeplyw_measurements
            ],
            "has_more": len(stan_measurements) == batch_size or len(przeplyw_measurements) == batch_size,
            "next_offset": offset + batch_size
        }

        logger.info(f"Retrieved batch data: {len(stan_measurements)} water level and {len(przeplyw_measurements)} flow measurements for station {station_id} (batch_size: {batch_size}, offset: {offset})")

        return result

    def get_latest_measurements_for_all_stations(self) -> Dict[str, Dict[str, Any]]:
        """Pobierz najnowsze pomiary dla wszystkich stacji"""
        latest_stan_subquery = (
            self.db.query(
                StanMeasurement.station_id,
                func.max(StanMeasurement.stan_wody_data_pomiaru).label('max_date')
            )
            .group_by(StanMeasurement.station_id)
            .subquery()
        )
        
        latest_stan_measurements = (
            self.db.query(StanMeasurement)
            .join(
                latest_stan_subquery,
                and_(
                    StanMeasurement.station_id == latest_stan_subquery.c.station_id,
                    StanMeasurement.stan_wody_data_pomiaru == latest_stan_subquery.c.max_date
                )
            )
            .all()
        )

        latest_przeplyw_subquery = (
            self.db.query(
                PrzeplywMeasurement.station_id,
                func.max(PrzeplywMeasurement.przeplyw_data).label('max_date')
            )
            .group_by(PrzeplywMeasurement.station_id)
            .subquery()
        )
        
        latest_przeplyw_measurements = (
            self.db.query(PrzeplywMeasurement)
            .join(
                latest_przeplyw_subquery,
                and_(
                    PrzeplywMeasurement.station_id == latest_przeplyw_subquery.c.station_id,
                    PrzeplywMeasurement.przeplyw_data == latest_przeplyw_subquery.c.max_date
                )
            )
            .all()
        )

        result = {}

        for measurement in latest_stan_measurements:
            if measurement.station_id not in result:
                result[measurement.station_id] = {}
            result[measurement.station_id]['stan_wody'] = measurement.stan_wody
            result[measurement.station_id]['stan_wody_data_pomiaru'] = measurement.stan_wody_data_pomiaru

        for measurement in latest_przeplyw_measurements:
            if measurement.station_id not in result:
                result[measurement.station_id] = {}
            result[measurement.station_id]['przeplyw'] = measurement.przelyw
            result[measurement.station_id]['przeplyw_data'] = measurement.przeplyw_data
        
        logger.info(f"Retrieved latest measurements for {len(result)} stations")
        return result
