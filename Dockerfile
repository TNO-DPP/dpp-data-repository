FROM python:3.12-alpine

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY app /app/

# CMD uvicorn app.main:app --port 8001
COPY logging.json ./config/logging.json
CMD uvicorn app.main:app --port 8001 --reload --log-config ./config/logging.json