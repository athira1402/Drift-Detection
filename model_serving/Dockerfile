FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy code and model
COPY serve.py .
COPY churn_model.pkl .

EXPOSE 5002

CMD ["python", "serve.py"]
