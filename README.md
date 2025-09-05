# 🌊 System Monitorowania Powodzi

System monitorowania powodzi w Polsce oparty na danych IMGW-PIB.

## 🚀 Szybki start

### Uruchomienie aplikacji

```bash
# Uruchom całą aplikację (backend + frontend)
make start

# Sprawdź status aplikacji
make status

# Zatrzymaj aplikację
make stop
```

### Dostępne komendy Makefile

| Komenda | Opis |
|---------|------|
| `make start` | Uruchom całą aplikację (backend + frontend) |
| `make stop` | Zatrzymaj całą aplikację |
| `make status` | Sprawdź status aplikacji |
| `make dev` | Uruchom w trybie deweloperskim z hot-reload |
| `make install` | Zainstaluj zależności |
| `make clean` | Wyczyść cache i pliki tymczasowe |
| `make restart` | Zrestartuj aplikację |
| `make logs` | Pokaż logi backendu |
| `make test` | Przetestuj działanie aplikacji |
| `make help` | Pokaż pomoc |

### Adresy aplikacji

- **Frontend (Streamlit)**: http://localhost:8501
- **Backend API**: http://localhost:8000
- **Dokumentacja API**: http://localhost:8000/docs

System do monitorowania i wizualizacji zagrożeń powodziowych w Polsce, wykorzystujący dane z IMGW. Aplikacja umożliwia śledzenie stanu wód w stacjach pomiarowych, wizualizację danych na interaktywnej mapie oraz analizę historycznych pomiarów.

## Funkcjonalności

- 🌊 Monitorowanie stanu wód w czasie rzeczywistym
- 🗺️ Interaktywna mapa stacji pomiarowych
- 📊 Wykresy historycznych pomiarów
- 🔄 Automatyczna synchronizacja danych z IMGW
- 📱 Responsywny interfejs użytkownika

## Architektura Systemu

System składa się z następujących komponentów:

- **Frontend (Streamlit)**: Interaktywny interfejs użytkownika
- **Backend (FastAPI)**: REST API do obsługi danych
- **Baza danych (PostgreSQL + PostGIS)**: Przechowywanie danych przestrzennych

## Struktura Projektu

```
flood_monitoring/
├── flood_monitoring/          # Główny pakiet
│   ├── api/                  # Backend FastAPI
│   │   ├── routers/         # Endpointy API
│   │   └── dependencies/    # Zależności FastAPI
│   ├── core/                # Konfiguracja i podstawowe komponenty
│   ├── models/              # Modele SQLAlchemy
│   ├── services/            # Logika biznesowa
│   └── ui/                  # Frontend Streamlit
│       ├── pages/          # Strony aplikacji
│       └── components/     # Komponenty UI
├── docker/                  # Konfiguracja Docker
└── tests/                  # Testy
```

## Wymagania Systemowe

- Python 3.11+
- Docker i Docker Compose (dla wersji konteneryzowanej)
- PostgreSQL 17+ z PostGIS 3.4+ (dla lokalnej instalacji)
- uv (opcjonalnie, dla szybszej instalacji zależności)

## Uruchomienie z Docker Compose

1. Uruchom aplikację:
```bash
docker-compose up -d
```

2. Sprawdź status kontenerów:
```bash
docker-compose ps
```

3. Zatrzymanie aplikacji:
```bash
docker-compose down
```

Aplikacja będzie dostępna pod następującymi adresami:
- Frontend: http://localhost:8501
- Backend API: http://localhost:8000
- Dokumentacja API: http://localhost:8000/docs

## Lokalna Instalacja z uv

1. Zainstaluj uv (jeśli nie jest zainstalowany):
```bash
pip install uv
```

2. Utwórz i aktywuj wirtualne środowisko:
```bash
uv venv
source .venv/bin/activate  # Linux/Mac
.venv\Scripts\activate     # Windows
```

3. Zainstaluj zależności:
```bash
uv pip install -e ".[dev]"
```

## Rozwój i Testowanie

1. Formatowanie kodu:
```bash
black .
isort .
```

2. Sprawdzanie jakości kodu:
```bash
flake8
```

3. Uruchomienie testów:
```bash
pytest
```

## Rozwiązywanie Problemów

### Docker Compose

1. Problem z połączeniem do bazy danych:
```bash
docker-compose logs db
```

2. Problem z backendem:
```bash
docker-compose logs backend
```

3. Reset kontenerów:
```bash
docker-compose down -v
docker-compose up -d
```
