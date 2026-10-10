FROM python:3.11-slim

WORKDIR /app

# Prevent Python from writing bytecode and enable unbuffered logging
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy and install python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source and synthetic PDF storage
COPY app/ ./app
COPY storage/ ./storage

# Default port environment variable
ENV PORT=8010
EXPOSE 8010

# Run Uvicorn ASGI server using environment PORT
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8010}"]
