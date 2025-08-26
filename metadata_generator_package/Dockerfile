FROM python:3.11-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    FLASK_APP=app.py

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc g++ libffi-dev libssl-dev curl git \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install packages globally (NOT --user)
RUN pip install --no-cache-dir -r requirements.txt

# Verify imports
RUN python -c "import supabase; print('✅ Supabase verified')" && \
    python -c "import flask; print('✅ Flask verified')" && \
    python -c "import pandas; print('✅ Pandas verified')" && \
    gunicorn --version

# Copy app code
COPY . .

# Create app user and assign ownership
RUN useradd --create-home --shell /bin/bash appuser && \
    mkdir -p /app/uploads /app/temp /app/backups /app/logs && \
    chown -R appuser:appuser /app

# USER appuser

EXPOSE 5000

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5000/health || exit 1

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]
