"""
Skrypt do inicjalizacji bazy danych
"""
import time

from sqlalchemy import create_engine
from sqlalchemy.exc import OperationalError

from flood_monitoring.core.database import Base, engine
from flood_monitoring.models.measurements import PrzeplywMeasurement, StanMeasurement
from flood_monitoring.models.station import Station


def wait_for_db(max_retries=5, retry_interval=5):
    """Czeka na gotowość bazy danych"""
    for i in range(max_retries):
        try:
            # Próbujemy połączyć się z bazą
            engine.connect()
            print("Połączono z bazą danych!")
            return True
        except OperationalError:
            if i < max_retries - 1:
                print(
                    f"Baza danych nie jest jeszcze gotowa. Próba {i+1}/{max_retries}. Czekam {retry_interval} sekund..."
                )
                time.sleep(retry_interval)
            else:
                print("Nie udało się połączyć z bazą danych po wszystkich próbach.")
                return False


def init_db():
    """Inicjalizacja bazy danych"""
    if not wait_for_db():
        return False

    try:
        # Tworzymy wszystkie tabele
        Base.metadata.create_all(bind=engine)
        print("Tabele zostały pomyślnie utworzone!")
        return True
    except Exception as e:
        print(f"Wystąpił błąd podczas tworzenia tabel: {str(e)}")
        return False


if __name__ == "__main__":
    print("Inicjalizacja bazy danych...")
    if init_db():
        print("Inicjalizacja zakończona sukcesem!")
    else:
        print("Inicjalizacja nie powiodła się!")
