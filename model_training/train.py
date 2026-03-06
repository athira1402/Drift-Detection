from flask import Flask, request, jsonify
import pandas as pd
from sklearn.linear_model import LogisticRegression
import pickle

app = Flask(__name__)

@app.route('/train', methods=['POST'])
def train_model():
    try:
        # Expect JSON payload with training data
        data = request.get_json()
        df = pd.DataFrame(data)

        # Features and target
        X = df.drop(columns=['Churn'])
        y = df['Churn'].map({'Yes':1, 'No':0})

        # Train model
        model = LogisticRegression()
        model.fit(X, y)

        # Save model
        with open("churn_model.pkl", "wb") as f:
            pickle.dump(model, f)

        return jsonify({"status": "success", "message": "Model trained and saved"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)
