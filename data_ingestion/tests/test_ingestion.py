import unittest
from unittest.mock import patch, MagicMock
from data_ingestion.app import app
import os

class FlaskIngestTestCase(unittest.TestCase):
    def setUp(self):
        # Set up environment variables that the app expects
        os.environ["SERVING_URL"] = "http://fake-serving-url.com"
        os.environ["DRIFT_URL"] = "http://fake-drift-url.com"
        
        # Configure the Flask test client
        self.app = app.test_client()
        self.app.testing = True

    @patch('requests.post')
    def test_ingest_success(self, mock_post):
        # 1. Setup Mock Responses
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"result": "success"}
        mock_post.return_value = mock_response

        # 2. Define valid payload
        payload = [
            {"customerID": "123", "Churn": "No", "tenure": 1},
            {"customerID": "456", "Churn": "Yes", "tenure": 24}
        ]

        # 3. Make the request
        response = self.app.post('/ingest', json=payload)
        data = response.get_json()

        # 4. Assertions
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['status'], 'ingested')
        self.assertEqual(data['rows'], 2)
        # Verify that requests.post was called twice (once for serving, once for drift)
        self.assertEqual(mock_post.call_count, 2)

    def test_ingest_invalid_schema(self):
        # Payload missing 'Churn'
        payload = [{"customerID": "123", "tenure": 1}]
        
        response = self.app.post('/ingest', json=payload)
        data = response.get_json()

        self.assertEqual(response.status_code, 400)
        self.assertIn("Invalid schema", data['error'])

if __name__ == '__main__':
    unittest.main()