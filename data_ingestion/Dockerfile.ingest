# Use Python base image
FROM python:3.9-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy code
COPY app.py .

# Expose port
EXPOSE 5000

# Run service
CMD ["python", "app.py"]
