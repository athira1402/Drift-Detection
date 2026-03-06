from flask import Flask, request, jsonify
import pandas as pd
import pickle

app = Flask(__name__)

# Load the trained model at startup
with open("churn_model.pkl", "rb") as f:
    model = pickle.load(f)

@app.route('/predict', methods=['POST'])
def predict():
    try:
        # Expect JSON payload with customer data
        data = request.get_json()
        df = pd.DataFrame(data)

        # Predict churn
        predictions = model.predict(df)
        results = ["Yes" if p == 1 else "No" for p in predictions]

        return jsonify({"predictions": results})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002)
