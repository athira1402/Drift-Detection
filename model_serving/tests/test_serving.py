import unittest
from unittest.mock import patch, MagicMock
import pandas as pd
import os

# Adjust this import to match your folder/file name
from model_serving.serve import app 

class TestModelServing(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    @patch('model_serving.serve.model') # Mock the global 'model' object
    def test_predict_success(self, mock_model):
        # 1. Setup Mock Model behavior
        # Simulate the model returning [1, 0] for two inputs
        mock_model.predict.return_value = [1, 0]

        # 2. Define Payload
        payload = [
            {"customerID": "123", "Age": 30, "Tenure": 5, "Balance": 5000},
            {"customerID": "456", "Age": 45, "Tenure": 10, "Balance": 12000}
        ]

        # 3. Make Request
        response = self.app.post('/predict', json=payload)
        data = response.get_json()

        # 4. Assertions
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(data['predictions']), 2)
        self.assertEqual(data['predictions'][0]['prediction'], "Yes")
        self.assertEqual(data['predictions'][1]['prediction'], "No")
        
        # Verify that the model's predict method was called
        mock_model.predict.assert_called_once()

    def test_no_model_error(self):
        # Simulate the scenario where the model failed to load (model is None)
        with patch('model_serving.serve.model', None):
            payload = [{"Age": 30, "Tenure": 5, "Balance": 5000}]
            response = self.app.post('/predict', json=payload)
            data = response.get_json()

            self.assertEqual(response.status_code, 500)
            self.assertIn("No model found", data['error'])

if __name__ == '__main__':
    unittest.main()