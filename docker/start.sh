#!/bin/bash

# Czekamy na inicjalizację bazy danych
echo "Inicjalizacja bazy danych..."
python -m flood_monitoring.scripts.init_db

# Uruchamiamy aplikację
echo "Uruchamianie aplikacji..."
uvicorn flood_monitoring.api.main:app --host 0.0.0.0 --port 8000 --reload 