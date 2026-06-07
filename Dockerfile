FROM python:3.12-slim

WORKDIR /app

COPY backend/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt httpx tiktoken python-dotenv fastembed

COPY backend/app ./app
COPY data ./data
COPY scripts ./scripts

ENV PYTHONPATH=/app
ENV REPO_ROOT=/app
ENV RUN_INGEST_ON_START=1

RUN chmod +x /app/scripts/docker-entrypoint.sh

EXPOSE 8000

CMD ["/app/scripts/docker-entrypoint.sh"]
