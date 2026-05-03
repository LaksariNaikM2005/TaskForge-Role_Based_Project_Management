# ── Stage 1: Build Frontend ──────────────────────────────────────────
FROM node:20-slim AS frontend-build
WORKDIR /frontend
COPY frontend/package*.json ./
RUN npm install
COPY frontend/ .
# Vite build variables
ENV VITE_API_URL=""
RUN npm run build

# ── Stage 2: Build Backend ───────────────────────────────────────────
FROM python:3.10-slim
WORKDIR /app

# Prevent python from buffering logs
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# System deps for asyncpg / scikit-learn
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy backend source
COPY backend/ .

# Copy built frontend from Stage 1
COPY --from=frontend-build /frontend/dist ./dist

# Ensure the app listens on the PORT provided by Railway
EXPOSE 8000
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]