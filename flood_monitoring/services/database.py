"""
Serwis do obsługi bazy danych
"""
import logging
from datetime import datetime

from geoalchemy2.shape import from_shape
from shapely.geometry import Point
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

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
        # Sprawdź czy pomiar już istnieje
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
        # Sprawdź czy pomiar już istnieje
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

    def get_station_measurements(self, station_id: str, days: int = 7):
        """Pobierz pomiary dla stacji z ostatnich n dni"""
        from datetime import timedelta

        start_date = datetime.now() - timedelta(days=days)

        logger.info(f"Fetching measurements for station {station_id} from {start_date}")

        stan_measurements = (
            self.db.query(StanMeasurement)
            .filter(
                StanMeasurement.station_id == station_id,
                StanMeasurement.stan_wody_data_pomiaru >= start_date,
            )
            .all()
        )

        przeplyw_measurements = (
            self.db.query(PrzeplywMeasurement)
            .filter(
                PrzeplywMeasurement.station_id == station_id,
                PrzeplywMeasurement.przeplyw_data >= start_date,
            )
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

        logger.info(f"Retrieved measurements for station {station_id}: {result}")

        return result
