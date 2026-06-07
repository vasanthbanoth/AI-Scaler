# Stage 1: Build frontend
FROM node:20-slim AS builder
WORKDIR /app/frontend
COPY frontend/package.json frontend/package-lock.json* ./
RUN npm install
COPY frontend .
RUN npm run build

# Stage 2: Python backend
FROM python:3.12-slim
WORKDIR /app

COPY backend/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt httpx tiktoken python-dotenv fastembed

COPY backend/app ./app
COPY data ./data
COPY scripts ./scripts
COPY --from=builder /app/frontend/out /app/frontend/out

ENV PYTHONPATH=/app
ENV REPO_ROOT=/app
ENV RUN_INGEST_ON_START=0

RUN chmod +x /app/scripts/docker-entrypoint.sh

EXPOSE 8000

CMD ["/app/scripts/docker-entrypoint.sh"]
