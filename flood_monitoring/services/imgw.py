"""
Serwis do pobierania danych z IMGW
"""
import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List

import aiohttp

from flood_monitoring.core.config import get_settings
from flood_monitoring.services.database import DatabaseService
from flood_monitoring.models.warnings import WarningArea, HydroWarning

logger = logging.getLogger(__name__)
settings = get_settings()


class IMGWService:
    """Serwis do obsługi danych z IMGW"""

    def __init__(self, db_service: DatabaseService):
        self.db_service = db_service
        self.base_url = settings.IMGW_API_URL
        self.warnings_url = settings.IMGW_WARNINGS_URL

    async def get_stations(self) -> List[Dict[str, Any]]:
        """Pobierz listę stacji pomiarowych i zaktualizuj bazę danych"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.base_url}") as response:
                    if response.status == 200:
                        stations = await response.json()
                        # Zapisz stacje w bazie danych
                        for station in stations:
                            try:
                                self.db_service.get_or_create_station(
                                    id_stacji=station["id_stacji"],
                                    stacja=station["stacja"],
                                    lat=float(station["lat"]),
                                    lon=float(station["lon"]),
                                    rzeka=station.get("rzeka"),
                                    wojewodztwo=station.get("wojewodztwo")
                                )
                            except Exception as e:
                                logger.error(
                                    f"Error saving station {station['id_stacji']}: {str(e)}"
                                )
                        return stations
                    else:
                        logger.error(f"IMGW API returned status {response.status}")
                        return []
        except Exception as e:
            logger.error(f"Error fetching stations: {str(e)}")
            return []

    def _parse_datetime(self, date_str: str) -> datetime:
        """Parsuje datę z różnych formatów"""
        if not date_str:
            return None

        try:
            # Najpierw próbujemy sparsować datę w formacie IMGW (bez strefy czasowej)
            try:
                parsed_date = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
            except ValueError:
                # Jeśli nie pasuje, próbujemy inne formaty
                formats = [
                    "%Y-%m-%dT%H:%M:%S",
                    "%Y-%m-%dT%H:%M:%S.%f",
                    "%Y-%m-%dT%H:%M:%S.%fZ",
                    "%Y-%m-%dT%H:%M:%SZ",
                ]

                for fmt in formats:
                    try:
                        parsed_date = datetime.strptime(
                            date_str.replace("+00:00", ""), fmt
                        )
                        break
                    except ValueError:
                        continue
                else:
                    # Jeśli żaden format nie pasuje
                    return None

            # Porównujemy daty bez stref czasowych
            now = datetime.now()
            if parsed_date.date() > now.date():
                logger.warning(f"Found future date: {date_str}, skipping")
                return None
            elif parsed_date.date() == now.date() and parsed_date.time() > now.time():
                logger.warning(
                    f"Found future time on current date: {date_str}, skipping"
                )
                return None

            return parsed_date
        except Exception as e:
            logger.error(f"Error parsing date {date_str}: {str(e)}")
            return None

    async def get_station_data_przelyw(self, station_id: str, days: int = 7) -> Dict[str, Any]:
        """Pobierz dane z konkretnej stacji i zaktualizuj bazę danych"""
        try:
            async with aiohttp.ClientSession() as session:
                logger.info(f"Fetching data for station {station_id} from IMGW API")
                async with session.get(f"{self.base_url}/id/{station_id}") as response:
                    if response.status == 200:
                        data = await response.json()
                        logger.info(
                            f"Received raw data from IMGW API for station {station_id}: {data}"
                        )

                        if not data or len(data) == 0:
                            logger.warning(f"No data received for station {station_id}")
                            return {"stan_wody": []}

                        # API zwraca listę z jednym elementem
                        measurement = data[0]

                        if (
                            "przeplyw_data" in measurement
                            and "przelyw" in measurement
                            and measurement["przelyw"] is not None
                        ):
                            przeplyw_data = self._parse_datetime(measurement["przeplyw_data"])
                            if przeplyw_data:
                                # Zapisujemy pomiar w bazie
                                if self.db_service.add_przeplyw_measurement(
                                    station_id=station_id,
                                    przeplyw_data=przeplyw_data,
                                    przelyw=float(measurement["przelyw"]),
                                ):
                                    logger.info(
                                        f"Dodano nowy pomiar dla stacji {station_id}"
                                    )
                                else:
                                    logger.info(
                                        f"Pomiar dla stacji {station_id} już istnieje w bazie"
                                    )

                                # Zwracamy pomiar
                                return {
                                    "przelyw": [
                                        {
                                            "przeplyw_data": measurement["przeplyw_data"],
                                            "przelyw": float(measurement["przelyw"]),
                                        }
                                    ]
                                }

                        logger.warning(
                            f"Invalid measurement data for station {station_id}"
                        )
                        return {"przeplyw_data": []}
                    else:
                        logger.error(
                            f"IMGW API returned status {response.status} for station {station_id}"
                        )
                        return {"przeplyw_data": []}
        except Exception as e:
            logger.error(f"Error fetching data for station {station_id}: {str(e)}")
            return {"przelyw": []}


    async def get_station_data_stan(self, station_id: str, days: int = 7) -> Dict[str, Any]:
        """Pobierz dane z konkretnej stacji i zaktualizuj bazę danych"""
        try:
            async with aiohttp.ClientSession() as session:
                logger.info(f"Fetching data for station {station_id} from IMGW API")
                async with session.get(f"{self.base_url}/id/{station_id}") as response:
                    if response.status == 200:
                        data = await response.json()
                        logger.info(
                            f"Received raw data from IMGW API for station {station_id}: {data}"
                        )

                        if not data or len(data) == 0:
                            logger.warning(f"No data received for station {station_id}")
                            return {"stan_wody": []}

                        # API zwraca listę z jednym elementem
                        measurement = data[0]

                        if (
                            "stan_wody_data_pomiaru" in measurement
                            and "stan_wody" in measurement
                            and measurement["stan_wody"] is not None
                        ):
                            stan_wody_data_pomiaru = self._parse_datetime(measurement["stan_wody_data_pomiaru"])
                            if stan_wody_data_pomiaru:
                                # Zapisujemy pomiar w bazie
                                if self.db_service.add_stan_measurement(
                                    station_id=station_id,
                                    stan_wody_data_pomiaru=stan_wody_data_pomiaru,
                                    stan_wody=float(measurement["stan_wody"]),
                                ):
                                    logger.info(
                                        f"Dodano nowy pomiar dla stacji {station_id}"
                                    )
                                else:
                                    logger.info(
                                        f"Pomiar dla stacji {station_id} już istnieje w bazie"
                                    )

                                # Zwracamy pomiar
                                return {
                                    "stan_wody": [
                                        {
                                            "stan_wody_data_pomiaru": measurement["stan_wody_data_pomiaru"],
                                            "stan_wody": float(measurement["stan_wody"]),
                                        }
                                    ]
                                }

                        logger.warning(
                            f"Invalid measurement data for station {station_id}"
                        )
                        return {"stan_wody_data_pomiaru": []}
                    else:
                        logger.error(
                            f"IMGW API returned status {response.status} for station {station_id}"
                        )
                        return {"stan_wody_data_pomiaru": []}
        except Exception as e:
            logger.error(f"Error fetching data for station {station_id}: {str(e)}")
            return {"stan_wody": []}

    async def get_warnings(self) -> List[Dict[str, Any]]:
        """Pobierz ostrzeżenia hydrologiczne z API IMGW"""
        url = f"{self.warnings_url}"
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    return data
                else:
                    raise Exception(f"Error fetching warnings: {response.status}")

    async def sync_warnings(self):
        """Synchronizuj ostrzeżenia hydrologiczne do bazy danych"""
        try:
            warnings = await self.get_warnings()
            for warning_data in warnings:
                # Parsuj daty
                warning_data['opublikowano'] = datetime.strptime(warning_data['opublikowano'], '%Y-%m-%d %H:%M:%S')
                warning_data['data_od'] = datetime.strptime(warning_data['data_od'], '%Y-%m-%d %H:%M:%S')
                warning_data['data_do'] = datetime.strptime(warning_data['data_do'], '%Y-%m-%d %H:%M:%S')

                # Sprawdź czy ostrzeżenie już istnieje (unikalne po numer + biuro + opublikowano)
                existing = self.db_service.db.query(HydroWarning).filter(
                    HydroWarning.numer == warning_data['numer'],
                    HydroWarning.biuro == warning_data['biuro'],
                    HydroWarning.opublikowano == warning_data['opublikowano']
                ).first()

                if not existing:
                    new_warning = HydroWarning(
                        opublikowano=warning_data['opublikowano'],
                        stopien=warning_data['stopień'],
                        data_od=warning_data['data_od'],
                        data_do=warning_data['data_do'],
                        prawdopodobienstwo=warning_data['prawdopodobienstwo'],
                        numer=warning_data['numer'],
                        biuro=warning_data['biuro'],
                        zdarzenie=warning_data['zdarzenie'],
                        przebieg=warning_data['przebieg'],
                        komentarz=warning_data['komentarz']
                    )
                    self.db_service.db.add(new_warning)
                    self.db_service.db.flush()  # Aby dostać ID

                    # Dodaj obszary
                    for area in warning_data['obszary']:
                        new_area = WarningArea(
                            warning_id=new_warning.id,
                            wojewodztwo=area['wojewodztwo'],
                            opis=area['opis'],
                            kod_zlewni=area['kod_zlewni']
                        )
                        self.db_service.db.add(new_area)

                self.db_service.db.commit()
                logger.info(f"Synchronized {len(warnings)} warnings")
        except Exception as e:
            self.db_service.db.rollback()
            logger.error(f"Error syncing warnings: {str(e)}")
            raise
