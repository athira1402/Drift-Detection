from flask import Flask, request, jsonify
import pandas as pd

app = Flask(__name__)

@app.route('/ingest', methods=['POST'])
def ingest_data():
    try:
        # Expect JSON payload
        data = request.get_json()
        df = pd.DataFrame(data)

        # Simple validation
        if 'customerID' not in df.columns or 'Churn' not in df.columns:
            return jsonify({"error": "Invalid schema"}), 400

        # For now, just log the data (later: push to DB or Kafka)
        print("Received batch:", df.head())

        return jsonify({"status": "success", "rows": len(df)})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
