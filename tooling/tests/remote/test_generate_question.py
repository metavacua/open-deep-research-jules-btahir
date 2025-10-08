import unittest
from unittest.mock import patch
from tooling.remote.generate_question import generate_question

class TestPortedGenerateQuestion(unittest.TestCase):

    def setUp(self):
        """Set up a sample report for testing."""
        self.sample_report = {
            "title": "Test Report",
            "summary": "A summary of the report.",
            "sections": [
                {"title": "Intro", "content": "This is the introduction."},
                {"title": "Conclusion", "content": "This is the conclusion."}
            ]
        }

    def test_no_report_provided(self):
        """Test that an error is returned when no report is provided."""
        result = generate_question(report=None, platform_model="openai__gpt-4")
        self.assertIn("error", result)
        self.assertEqual(result["status"], 400)
        self.assertEqual(result["error"], "Report is required")

    @patch('tooling.ported.generate_question.generate_with_model')
    def test_generation_success_json_response(self, mock_generate):
        """Test successful generation with a valid JSON response from the LLM."""
        mock_response = '{"searchTerms": ["term 1", "term 2", "term 3"]}'
        mock_generate.return_value = mock_response

        result = generate_question(report=self.sample_report, platform_model="openai__gpt-4")

        self.assertEqual(result["status"], 200)
        self.assertEqual(len(result["searchTerms"]), 3)
        self.assertEqual(result["searchTerms"], ["term 1", "term 2", "term 3"])
        mock_generate.assert_called_once()

    @patch('tooling.ported.generate_question.generate_with_model')
    def test_generation_success_fallback_parsing(self, mock_generate):
        """Test the fallback line-based parsing when the LLM response is not valid JSON."""
        mock_response = 'Here are the terms:\n"term one"\n"term two"\n"term three"'
        mock_generate.return_value = mock_response

        result = generate_question(report=self.sample_report, platform_model="openai__gpt-4")

        self.assertEqual(result["status"], 200)
        self.assertEqual(len(result["searchTerms"]), 3)
        self.assertEqual(result["searchTerms"], ['Here are the terms:', 'term one', 'term two'])

    @patch('tooling.ported.generate_question.generate_with_model', side_effect=Exception("Model unavailable"))
    def test_generation_failure_model_error(self, mock_generate):
        """Test a generation failure when the model raises an exception."""
        result = generate_question(report=self.sample_report, platform_model="openai__gpt-4")

        self.assertEqual(result["status"], 500)
        self.assertIn("error", result)
        self.assertIn("Failed to generate search terms", result["error"])

if __name__ == '__main__':
    unittest.main()