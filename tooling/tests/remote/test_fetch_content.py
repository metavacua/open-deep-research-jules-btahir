import unittest
from unittest.mock import patch, Mock
import requests
from tooling.ported.fetch_content import fetch_content

class TestPortedFetchContent(unittest.TestCase):

    def test_no_url_provided(self):
        """Test that an error is returned when no URL is provided."""
        result = fetch_content(url="")
        self.assertIn("error", result)
        self.assertEqual(result["status"], 400)
        self.assertEqual(result["error"], "URL is required")

    @patch('tooling.ported.fetch_content.requests.get')
    def test_fetch_success(self, mock_get):
        """Test a successful content fetch."""
        mock_response = Mock()
        mock_response.ok = True
        mock_response.status_code = 200
        mock_response.text = "This is the fetched content."
        mock_get.return_value = mock_response

        test_url = "http://example.com"
        result = fetch_content(url=test_url)

        self.assertEqual(result["status"], 200)
        self.assertEqual(result["content"], "This is the fetched content.")
        mock_get.assert_called_once_with("https://r.jina.ai/http%3A%2F%2Fexample.com", timeout=30)

    @patch('tooling.ported.fetch_content.requests.get')
    def test_fetch_failure_http_error(self, mock_get):
        """Test a fetch failure due to a non-200 HTTP status."""
        mock_response = Mock()
        mock_response.ok = False
        mock_response.status_code = 404
        mock_response.text = "Not Found"
        mock_get.return_value = mock_response

        test_url = "http://example.com/notfound"
        result = fetch_content(url=test_url)

        self.assertEqual(result["status"], 404)
        self.assertIn("error", result)
        self.assertEqual(result["error"], "Failed to fetch content")

    @patch('tooling.ported.fetch_content.requests.get', side_effect=requests.exceptions.RequestException("Connection error"))
    def test_fetch_failure_request_exception(self, mock_get):
        """Test a fetch failure due to a request exception."""
        test_url = "http://example.com/timeout"
        result = fetch_content(url=test_url)

        self.assertEqual(result["status"], 500)
        self.assertIn("error", result)
        self.assertIn("An unexpected error occurred", result["error"])

if __name__ == '__main__':
    unittest.main()