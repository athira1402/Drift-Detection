import json
import os
import tempfile
import unittest
import model_training.train as training_app

class TestTraining(unittest.TestCase):
    def setUp(self):
        self.client = training_app.app.test_client()

    def test_train_model_success(self):
        tmpdir = tempfile.mkdtemp()
        training_app.pvc_path = tmpdir

        payload = [
            {"feature1": 0.1, "feature2": 0.5, "Churn": "Yes"},
            {"feature1": 0.2, "feature2": 0.3, "Churn": "No"},
            {"feature1": 0.4, "feature2": 0.7, "Churn": "Yes"}
        ]

        response = self.client.post("/train", json=payload)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data["status"], "success")
        self.assertIn("Model and reference saved", data["message"])
        self.assertTrue(os.path.exists(os.path.join(tmpdir, "churn_model.pkl")))
        self.assertTrue(os.path.exists(os.path.join(tmpdir, "reference_distribution.pkl")))

    def test_train_model_invalid_payload(self):
        payload = [
            {"feature1": 0.1, "feature2": 0.5},
            {"feature1": 0.2, "feature2": 0.3}
        ]
        response = self.client.post("/train", json=payload)
        self.assertEqual(response.status_code, 500)
        data = json.loads(response.data)
        self.assertIn("error", data)

if __name__ == '__main__':
    unittest.main()
