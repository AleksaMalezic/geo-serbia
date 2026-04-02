FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN addgroup --system geoserbia && adduser --system --ingroup geoserbia geoserbia \
    && mkdir -p /app/src/static/uploads/locations \
    && chown -R geoserbia:geoserbia /app

USER geoserbia

EXPOSE 8000

CMD ["uvicorn", "src.boot.main:app", "--host", "0.0.0.0", "--port", "8000"]
