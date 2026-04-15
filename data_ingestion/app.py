from flask import Flask, request, jsonify
import pandas as pd
import requests
import os
import logging
import json
import sys

app = Flask(__name__)

# --- Structured Logging Setup ---
# We use a custom format to ensure ONLY the JSON string is printed
logging.basicConfig(
    level=logging.INFO,
    format='%(message)s',
    stream=sys.stdout
)

def log_event(service, status, extra=None):
    # Emit ECS-compatible fields to avoid collisions with reserved mappings.
    event = {
        "service": {"name": service},
        "event": {"outcome": "success" if status == "success" else "failure"},
        "app": {"status": status}
    }
    if extra:
        event.update(extra)
    logging.info(json.dumps(event))

@app.route('/ingest', methods=['POST'])
def ingest_data():
    try:
        df = None
        data_for_forwarding = None

        # 1. Handle File Upload (CSV)
        if 'file' in request.files:
            file = request.files['file']
            if file.filename != '':
                df = pd.read_csv(file)
                # Convert to dict for forwarding to other services
                data_for_forwarding = df.to_dict(orient='records')
        
        # 2. Handle JSON Body (Fallback)
        elif request.is_json:
            data_for_forwarding = request.get_json()
            df = pd.DataFrame(data_for_forwarding)

        # 3. Check if we actually got data
        if df is None:
            return jsonify({"error": "No valid file or JSON data provided"}), 400

        # Bank Churn dataset schema validation
        required_columns = [
            'CustomerId', 'CreditScore', 'Geography', 'Gender',
            'Age', 'Tenure', 'Balance', 'NumOfProducts',
            'HasCrCard', 'IsActiveMember', 'EstimatedSalary', 'Exited'
        ]
        
        missing = [col for col in required_columns if col not in df.columns]
        if missing:
            log_event("ingest", "validation_failed", {"missing": missing})
            return jsonify({"error": f"Missing columns: {missing}"}), 400

        # --- Forwarding Logic ---
        # Note: We use data_for_forwarding (list of dicts) for the POST requests
        
        serving_url = os.getenv("SERVING_URL")
        drift_url = os.getenv("DRIFT_URL")
        
        responses = {}

        if serving_url:
            s_res = requests.post(serving_url, json=data_for_forwarding, timeout=5)
            responses["serving"] = s_res.json()

        if drift_url:
            d_res = requests.post(drift_url, json=data_for_forwarding, timeout=5)
            responses["drift"] = d_res.json()

        log_event("ingest", "success", {"rows": len(df)})

        return jsonify({
            "status": "ingested",
            "rows": len(df),
            "responses": responses
        })

    except Exception as e:
        log_event("ingest", "error", {"error": str(e)})
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)