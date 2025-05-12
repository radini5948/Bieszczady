"""
Serwis do pobierania danych z IMGW
"""
import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List

import aiohttp

from flood_monitoring.core.config import get_settings
from flood_monitoring.services.database import DatabaseService

logger = logging.getLogger(__name__)
settings = get_settings()


class IMGWService:
    """Serwis do obsługi danych z IMGW"""

    def __init__(self, db_service: DatabaseService):
        self.db_service = db_service
        self.base_url = settings.IMGW_API_URL

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
                                    kod_stacji=station["kod_stacji"],
                                    nazwa_stacji=station["nazwa_stacji"],
                                    lat=float(station["lat"]),
                                    lon=float(station["lon"]),
                                    rzeka=station.get("rzeka"),
                                )
                            except Exception as e:
                                logger.error(
                                    f"Error saving station {station['kod_stacji']}: {str(e)}"
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

    async def get_station_data(self, station_id: str, days: int = 7) -> Dict[str, Any]:
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
                            return {"stan": []}

                        # API zwraca listę z jednym elementem
                        measurement = data[0]

                        if (
                            "stan_data" in measurement
                            and "stan" in measurement
                            and measurement["stan"] is not None
                        ):
                            stan_data = self._parse_datetime(measurement["stan_data"])
                            if stan_data:
                                # Zapisujemy pomiar w bazie
                                if self.db_service.add_stan_measurement(
                                    station_id=station_id,
                                    stan_data=stan_data,
                                    stan=float(measurement["stan"]),
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
                                    "stan": [
                                        {
                                            "stan_data": measurement["stan_data"],
                                            "stan": float(measurement["stan"]),
                                        }
                                    ]
                                }

                        logger.warning(
                            f"Invalid measurement data for station {station_id}"
                        )
                        return {"stan": []}
                    else:
                        logger.error(
                            f"IMGW API returned status {response.status} for station {station_id}"
                        )
                        return {"stan": []}
        except Exception as e:
            logger.error(f"Error fetching data for station {station_id}: {str(e)}")
            return {"stan": []}
