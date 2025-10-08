import unittest
from unittest.mock import patch, Mock
import os
from tooling.remote.search import search, get_bing_freshness, get_google_date_restrict

class TestPortedSearch(unittest.TestCase):

    # --- Test Helper Functions ---

    def test_get_bing_freshness(self):
        """Test the Bing freshness helper function."""
        self.assertEqual(get_bing_freshness('24h'), 'Day')
        self.assertEqual(get_bing_freshness('week'), 'Week')
        self.assertEqual(get_bing_freshness('month'), 'Month')
        self.assertEqual(get_bing_freshness('year'), 'Year')
        self.assertEqual(get_bing_freshness('all'), '')

    def test_get_google_date_restrict(self):
        """Test the Google date restrict helper function."""
        self.assertEqual(get_google_date_restrict('24h'), 'd1')
        self.assertEqual(get_google_date_restrict('week'), 'w1')
        self.assertEqual(get_google_date_restrict('month'), 'm1')
        self.assertEqual(get_google_date_restrict('year'), 'y1')
        self.assertIsNone(get_google_date_restrict('all'))

    # --- Test Main Search Functionality ---

    def test_no_query(self):
        """Test that an error is returned when the query is empty."""
        result = search(query="")
        self.assertIn("error", result)
        self.assertEqual(result["status"], 400)

    def test_is_test_query(self):
        """Test that dummy results are returned for a test query."""
        result = search(query="test", is_test_query=True)
        self.assertIn("webPages", result)
        self.assertEqual(len(result["webPages"]["value"]), 3)
        self.assertEqual(result["webPages"]["value"][0]["name"], "Test Result 1")

    # --- Mocked Provider Tests ---

    @patch('tooling.ported.search.requests.get')
    @patch.dict(os.environ, {"GOOGLE_SEARCH_API_KEY": "fake_key", "GOOGLE_SEARCH_CX": "fake_cx"})
    def test_search_google_success(self, mock_get):
        """Test a successful search with the Google provider."""
        mock_response = Mock()
        mock_response.ok = True
        mock_response.json.return_value = {
            "items": [{"title": "Google Result", "link": "http://google.com", "snippet": "A snippet"}]
        }
        mock_get.return_value = mock_response

        result = search(query="deep learning", provider="google")
        self.assertIn("webPages", result)
        self.assertEqual(result["webPages"]["value"][0]["name"], "Google Result")
        mock_get.assert_called_once()

    @patch('tooling.ported.search.requests.get')
    @patch.dict(os.environ, {"AZURE_SUB_KEY": "fake_key"})
    def test_search_bing_success(self, mock_get):
        """Test a successful search with the Bing provider."""
        mock_response = Mock()
        mock_response.ok = True
        mock_response.json.return_value = {
            "webPages": {"value": [{"name": "Bing Result"}]}
        }
        mock_get.return_value = mock_response

        result = search(query="machine learning", provider="bing")
        self.assertEqual(result["webPages"]["value"][0]["name"], "Bing Result")
        mock_get.assert_called_once()

    @patch('tooling.ported.search.requests.post')
    @patch.dict(os.environ, {"EXA_API_KEY": "fake_key"})
    def test_search_exa_success(self, mock_post):
        """Test a successful search with the Exa provider."""
        mock_response = Mock()
        mock_response.ok = True
        mock_response.json.return_value = {
            "results": [{"title": "Exa Result", "url": "http://exa.com", "text": "A snippet"}]
        }
        mock_post.return_value = mock_response

        result = search(query="AI research", provider="exa")
        self.assertIn("webPages", result)
        self.assertEqual(result["webPages"]["value"][0]["name"], "Exa Result")
        mock_post.assert_called_once()

    def test_search_google_no_keys(self):
        """Test Google search failure when API keys are missing."""
        with patch.dict(os.environ, {}, clear=True):
            result = search(query="real query", provider="google")
            self.assertIn("error", result)
            self.assertIn("not properly configured", result["error"])
            self.assertEqual(result["status"], 500)

    def test_search_bing_no_keys(self):
        """Test Bing search failure when API key is missing."""
        with patch.dict(os.environ, {}, clear=True):
            result = search(query="real query", provider="bing")
            self.assertIn("error", result)
            self.assertIn("not properly configured", result["error"])
            self.assertEqual(result["status"], 500)

    def test_search_exa_no_keys(self):
        """Test Exa search failure when API key is missing."""
        with patch.dict(os.environ, {}, clear=True):
            result = search(query="real query", provider="exa")
            self.assertIn("error", result)
            self.assertIn("not properly configured", result["error"])
            self.assertEqual(result["status"], 500)

if __name__ == '__main__':
    unittest.main()