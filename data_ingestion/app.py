from flask import Flask, request, jsonify
import pandas as pd
import requests
import os

app = Flask(__name__)

@app.route('/ingest', methods=['POST'])
def ingest_data():
    try:
        data = request.get_json()
        df = pd.DataFrame([data])

        if 'customerID' not in df.columns or 'Churn' not in df.columns:
            return jsonify({"error": "Invalid schema"}), 400

        # Forward to serving for predictions
        serving_url = os.getenv("SERVING_URL")
        print(f"Attempting to reach Serving at: {serving_url}")

        # Add a 5 second timeout
        serving_response = requests.post(serving_url, json=data, timeout=5)

        # Forward to drift detection
        drift_url = os.getenv("DRIFT_URL")
        drift_response = requests.post(drift_url, json=data)

        return jsonify({
            "status": "ingested",
            "rows": len(df),
            "serving_response": serving_response.json(),
            "drift_response": drift_response.json()
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
