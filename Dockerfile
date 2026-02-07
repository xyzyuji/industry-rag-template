FROM python:3.10-slim

WORKDIR /app
ENV PYTHONPATH=/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/public_api.py ./public_api.py
COPY public/ ./public/

ENV PORT=8080
EXPOSE 8080

CMD ["sh", "-c", "uvicorn public_api:app --host 0.0.0.0 --port $PORT"]
