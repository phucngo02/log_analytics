FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app

# Lệnh chạy collector
CMD ["python", "realtime_processor.py"]
