FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY drift_detection.py .

CMD ["python", "drift_detection.py"]
