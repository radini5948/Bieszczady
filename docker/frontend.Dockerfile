FROM python:3.11-slim

WORKDIR /app

# Install UV
RUN pip install uv

# Copy only dependency files first
COPY pyproject.toml .

# Create and activate virtual environment
RUN uv venv /app/.venv
ENV PATH="/app/.venv/bin:$PATH"

# Install dependencies using UV
RUN uv pip install -e ".[dev]"

# Copy the rest of the code (will be overridden by volume in dev)
COPY flood_monitoring/ui ./flood_monitoring/ui

ENV PYTHONPATH="/app"

CMD ["streamlit", "run", "flood_monitoring/ui/app.py", "--server.port=8501", "--server.address=0.0.0.0"]