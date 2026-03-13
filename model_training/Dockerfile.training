FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY train.py .

EXPOSE 5001

CMD ["python", "train.py"]
