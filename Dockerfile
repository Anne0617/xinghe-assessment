 # ============================================
 # Dockerfile - 智善TIC人才测评系统
 # ============================================
 FROM python:3.12-slim-bookworm AS builder
 
 WORKDIR /app
 
 # Install build dependencies
 RUN apt-get update && apt-get install -y --no-install-recommends \
     gcc libpq-dev && \
     rm -rf /var/lib/apt/lists/*
 
 COPY requirements.txt .
 RUN pip install --no-cache-dir -r requirements.txt
 
 # ============================================
 FROM python:3.12-slim-bookworm
 
 WORKDIR /app
 
 # Only runtime deps
 RUN apt-get update && apt-get install -y --no-install-recommends \
     libpq5 && \
     rm -rf /var/lib/apt/lists/*
 
 COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
 COPY --from=builder /usr/local/bin /usr/local/bin
 
 # Project code
 COPY . .
 
 # Collect static files
 RUN python manage.py collectstatic --noinput
 
 EXPOSE 8000
 
 CMD ["sh", "-c", "python manage.py migrate --noinput && gunicorn config.wsgi --log-file - --bind 0.0.0.0:${PORT:-8000}"]
