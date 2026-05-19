# ─────────────────────────────────────────────────────────────────────────────
# Stage 1: Build React frontend (no local Node required)
# ─────────────────────────────────────────────────────────────────────────────
FROM node:20-alpine AS frontend-builder

WORKDIR /app/frontend
COPY frontend/package.json ./
RUN npm install --legacy-peer-deps

COPY frontend/ ./
RUN npm run build

# ─────────────────────────────────────────────────────────────────────────────
# Stage 2: Python runtime with FastAPI
# ─────────────────────────────────────────────────────────────────────────────
FROM python:3.12-slim

WORKDIR /app

# System deps for lxml / beautifulsoup
RUN apt-get update && apt-get install -y --no-install-recommends \
    libxml2 libxslt1.1 gcc \
    && rm -rf /var/lib/apt/lists/*

# Python deps
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt fastapi "uvicorn[standard]"

# Application code
COPY . .

# Pre-built frontend from stage 1
COPY --from=frontend-builder /app/frontend/dist /app/frontend/dist

# SQLite data directory
RUN mkdir -p /app/data

EXPOSE 8080

CMD ["uvicorn", "api.server:app", "--host", "0.0.0.0", "--port", "8080", "--workers", "1"]
