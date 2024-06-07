FROM python:3.12-alpine

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY workdir ./workdir
COPY app ./app
COPY preseeded-data ./preseeded-data
COPY logging.json ./config/logging.json

CMD uvicorn app.main:app --port 8001 --log-config ./config/logging.json