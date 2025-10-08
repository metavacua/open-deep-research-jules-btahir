import unittest
from unittest.mock import patch
from tooling.remote.analyze_results import analyze_results

class TestPortedAnalyzeResults(unittest.TestCase):

    def setUp(self):
        """Set up sample data for tests."""
        self.sample_prompt = "What are the latest advancements in AI?"
        self.sample_results = [
            {"url": "http://example.com/ai-news", "title": "AI News", "snippet": "Latest news in AI."},
            {"url": "http://example.com/ml-advances", "title": "ML Advances", "snippet": "Recent machine learning advances."}
        ]
        self.test_results = [
            {"url": "http://example.com/test-1", "title": "Test 1", "snippet": "This is a test."}
        ]

    def test_missing_prompt_or_results(self):
        """Test error handling when prompt or results are missing."""
        # Test missing prompt
        result_no_prompt = analyze_results(prompt="", results=self.sample_results, platform_model="openai__gpt-4")
        self.assertEqual(result_no_prompt["status"], 400)
        self.assertIn("error", result_no_prompt)

        # Test missing results
        result_no_results = analyze_results(prompt=self.sample_prompt, results=[], platform_model="openai__gpt-4")
        self.assertEqual(result_no_results["status"], 400)
        self.assertIn("error", result_no_results)

    def test_is_test_query(self):
        """Test the handling of a test query."""
        result = analyze_results(prompt=self.sample_prompt, results=self.sample_results, platform_model="openai__gpt-4", is_test_query=True)
        self.assertEqual(result["status"], 200)
        self.assertIn("rankings", result)
        self.assertEqual(len(result["rankings"]), 2)
        self.assertEqual(result["analysis"], "Test analysis of search results")

    def test_is_test_url(self):
        """Test that a URL containing 'example.com/test' triggers test mode."""
        result = analyze_results(prompt=self.sample_prompt, results=self.test_results, platform_model="openai__gpt-4")
        self.assertEqual(result["status"], 200)
        self.assertIn("rankings", result)
        self.assertEqual(result["analysis"], "Test analysis of search results")

    @patch('tooling.ported.analyze_results.generate_with_model')
    def test_analysis_success(self, mock_generate_with_model):
        """Test a successful analysis with a mocked LLM response."""
        mock_response_json = {
            "rankings": [{"url": "http://example.com/ai-news", "score": 0.9, "reasoning": "Highly relevant"}],
            "analysis": "The results are highly relevant."
        }
        # The deep_research tool's extract_and_parse_json expects a string, so we mock that.
        mock_generate_with_model.return_value = str(mock_response_json).replace("'", '"')

        result = analyze_results(prompt=self.sample_prompt, results=self.sample_results, platform_model="openai__gpt-4")

        # The result from analyze_results should already be a dictionary
        self.assertEqual(result["status"], 200)
        self.assertEqual(result["analysis"], "The results are highly relevant.")
        self.assertEqual(len(result["rankings"]), 1)
        mock_generate_with_model.assert_called_once()

    @patch('tooling.ported.analyze_results.generate_with_model', side_effect=Exception("LLM is down"))
    def test_analysis_failure_model_error(self, mock_generate_with_model):
        """Test a failure when the LLM model raises an exception."""
        result = analyze_results(prompt=self.sample_prompt, results=self.sample_results, platform_model="openai__gpt-4")
        self.assertEqual(result["status"], 500)
        self.assertIn("error", result)
        self.assertIn("Failed to analyze results", result["error"])

if __name__ == '__main__':
    unittest.main()