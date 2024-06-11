FROM python:3.12-alpine

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY app ./app
COPY appconfig.yaml ./appconfig.yaml
COPY preseeded-data ./preseeded-data
COPY logging.json ./config/logging.json

CMD uvicorn app.main:app --host 0.0.0.0 --port 8001 --log-config ./config/logging.json