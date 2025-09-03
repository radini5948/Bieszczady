FROM --platform=linux/amd64 python:3.11

WORKDIR /app

# Install system dependencies including build tools
RUN apt-get update && apt-get install -y \
    gdal-bin \
    libgdal-dev \
    curl \
    build-essential \
    g++ \
    gcc \
    pkg-config \
    cmake \
    && rm -rf /var/lib/apt/lists/*

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
COPY flood_monitoring ./flood_monitoring

# Create startup script
COPY docker/start.sh /start.sh
RUN chmod +x /start.sh

CMD ["/start.sh"]