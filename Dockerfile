FROM python:3.12-alpine

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY app .

CMD uvicorn app.main:app --port 8001