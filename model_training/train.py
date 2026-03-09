from flask import Flask, request, jsonify
import pandas as pd
from sklearn.linear_model import LogisticRegression
import pickle
import os

app = Flask(__name__)

@app.route('/train', methods=['POST'])
def train_model():
    try:
        # Expect JSON payload with training data
        data = request.get_json()
        df = pd.DataFrame(data)

        # Features and target
        X = df.drop(columns=['Churn'])
        y = df['Churn'].map({'Yes': 1, 'No': 0})

        # Train model
        model = LogisticRegression()
        model.fit(X, y)

        # PVC mount path
        pvc_path = "/data/churn-model"

        # Save model to PVC
        model_path = os.path.join(pvc_path, "churn_model.pkl")
        with open(model_path, "wb") as f:
            pickle.dump(model, f)

        # Save reference distributions to PVC
        reference = {
            "feature_means": X.mean().to_dict(),
            "feature_stds": X.std().to_dict(),
            "label_distribution": y.value_counts(normalize=True).to_dict()
        }
        ref_path = os.path.join(pvc_path, "reference_distribution.pkl")
        with open(ref_path, "wb") as f:
            pickle.dump(reference, f)

        return jsonify({"status": "success", "message": "Model and reference saved to PVC"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)
