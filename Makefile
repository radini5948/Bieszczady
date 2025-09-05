.PHONY: help start stop status clean install dev

# Domyślny target
help:
	@echo "🌊 System Monitorowania Powodzi - Makefile"
	@echo "==========================================="
	@echo "Dostępne komendy:"
	@echo "  make start    - Uruchom całą aplikację (backend + frontend)"
	@echo "  make stop     - Zatrzymaj całą aplikację"
	@echo "  make status   - Sprawdź status aplikacji"
	@echo "  make dev      - Uruchom w trybie deweloperskim"
	@echo "  make install  - Zainstaluj zależności"
	@echo "  make clean    - Wyczyść cache i pliki tymczasowe"
	@echo "  make help     - Pokaż tę pomoc"

# Uruchom całą aplikację
start:
	@echo "🚀 Uruchamianie systemu monitorowania powodzi..."
	@echo "📦 Uruchamianie backendu (Docker)..."
	docker-compose up -d
	@echo "⏳ Czekanie na uruchomienie backendu..."
	sleep 5
	@echo "🌐 Uruchamianie frontendu (Streamlit)..."
	@echo "Frontend będzie dostępny na: http://localhost:8501"
	@echo "Backend API będzie dostępny na: http://localhost:8000"
	streamlit run flood_monitoring/ui/app.py --server.port 8501 --server.headless true &
	@echo "✅ Aplikacja uruchomiona pomyślnie!"
	@echo "📱 Otwórz przeglądarkę i przejdź do: http://localhost:8501"

# Zatrzymaj całą aplikację
stop:
	@echo "🛑 Zatrzymywanie systemu monitorowania powodzi..."
	@echo "🔌 Zatrzymywanie frontendu..."
	-pkill -f "streamlit run flood_monitoring/ui/app.py"
	@echo "📦 Zatrzymywanie backendu (Docker)..."
	docker-compose down
	@echo "✅ Aplikacja zatrzymana pomyślnie!"

# Sprawdź status aplikacji
status:
	@echo "📊 Status systemu monitorowania powodzi:"
	@echo "========================================"
	@echo "🐳 Status Docker containers:"
	@docker-compose ps || echo "❌ Docker nie jest uruchomiony"
	@echo ""
	@echo "🌐 Status Streamlit:"
	@pgrep -f "streamlit run" > /dev/null && echo "✅ Streamlit działa" || echo "❌ Streamlit nie działa"
	@echo ""
	@echo "🔗 Sprawdzanie połączeń:"
	@curl -s http://localhost:8000/health > /dev/null && echo "✅ Backend API (port 8000) - OK" || echo "❌ Backend API (port 8000) - BŁĄD"
	@curl -s http://localhost:8501 > /dev/null && echo "✅ Frontend (port 8501) - OK" || echo "❌ Frontend (port 8501) - BŁĄD"

# Tryb deweloperski
dev:
	@echo "🔧 Uruchamianie w trybie deweloperskim..."
	@echo "📦 Uruchamianie backendu z hot-reload..."
	docker-compose up -d
	@echo "⏳ Czekanie na uruchomienie backendu..."
	sleep 5
	@echo "🌐 Uruchamianie frontendu z hot-reload..."
	streamlit run flood_monitoring/ui/app.py --server.port 8501 --server.runOnSave true

# Instalacja zależności
install:
	@echo "📦 Instalowanie zależności..."
	pip install -e .
	@echo "🐳 Budowanie obrazów Docker..."
	docker-compose build
	@echo "✅ Instalacja zakończona!"

# Czyszczenie
clean:
	@echo "🧹 Czyszczenie cache i plików tymczasowych..."
	@echo "🗑️ Usuwanie cache Streamlit..."
	-rm -rf ~/.streamlit
	@echo "🗑️ Usuwanie plików __pycache__..."
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -name "*.pyc" -delete 2>/dev/null || true
	@echo "🐳 Czyszczenie obrazów Docker..."
	docker system prune -f
	@echo "✅ Czyszczenie zakończone!"

# Restart aplikacji
restart: stop start
	@echo "🔄 Aplikacja została zrestartowana!"

# Logi aplikacji
logs:
	@echo "📋 Logi backendu (Docker):"
	docker-compose logs -f

# Test aplikacji
test:
	@echo "🧪 Testowanie aplikacji..."
	@echo "🔍 Test backendu..."
	curl -f http://localhost:8000/stations/ > /dev/null && echo "✅ Backend API działa" || echo "❌ Backend API nie działa"
	@echo "🔍 Test frontendu..."
	curl -f http://localhost:8501 > /dev/null && echo "✅ Frontend działa" || echo "❌ Frontend nie działa"

# Backup danych
backup:
	@echo "💾 Tworzenie kopii zapasowej..."
	mkdir -p backups
	docker-compose exec -T db pg_dump -U postgres flood_monitoring > backups/backup_$(shell date +%Y%m%d_%H%M%S).sql
	@echo "✅ Kopia zapasowa utworzona w folderze backups/"
