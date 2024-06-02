FROM python:3.12-alpine

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY app /app/

# CMD uvicorn app.main:app --port 8001
CMD uvicorn app.main:app --port 8001 --reload --log-config logging.json