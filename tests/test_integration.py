import pytest
import requests
import time

# URLs (Assuming Docker Compose service names or localhost for local testing)
INGEST_URL = "http://localhost:5000/ingest"
TRAIN_URL = "http://localhost:5001/train"
PREDICT_URL = "http://localhost:5002/predict"
DRIFT_URL = "http://localhost:5003/drift"

@pytest.fixture(scope="module", autouse=True)
def setup_initial_model():
    """Ensure a model exists before testing ingestion/prediction."""
    sample_data = [
        {"Age": 30, "Tenure": 5, "Balance": 1000, "Churn": "No", "customerID": "1"},
        {"Age": 45, "Tenure": 1, "Balance": 5000, "Churn": "Yes", "customerID": "2"}
    ]
    requests.post(TRAIN_URL, json=sample_data)

def test_full_pipeline_flow():
    # 1. Test Ingestion (which triggers Predict and Drift)
    payload = [
        {"Age": 35, "Tenure": 3, "Balance": 2500, "Churn": "No", "customerID": "101"}
    ]
    response = requests.post(INGEST_URL, json=payload)
    
    assert response.status_code == 200
    data = response.json()
    assert "serving_response" in data
    assert "drift_response" in data

def test_drift_triggers_retraining():
    # 2. Simulate Drift (Drastic change in Age/Balance)
    drift_payload = [
        {"Age": 99, "Tenure": 50, "Balance": 999999, "Churn": "Yes", "customerID": "999"}
    ]
    
    # We call the Drift service directly to check its logic
    response = requests.post(DRIFT_URL, json=drift_payload)
    assert response.status_code == 200
    
    # If drift is detected, it should return training_response
    if response.json().get("drift_detected"):
        assert "training_response" in response.json()
        assert response.json()["training_response"]["status"] == "success"