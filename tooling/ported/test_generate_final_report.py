import unittest
import json
from unittest.mock import patch
from tooling.ported.generate_final_report import generate_final_report

class TestPortedGenerateFinalReport(unittest.TestCase):

    def setUp(self):
        """Set up sample data for tests."""
        self.sample_prompt = "Analyze the impact of AI on modern art."
        self.sample_results = [
            {"url": "http://example.com/ai-art", "title": "AI in Art", "content": "AI is changing art."},
        ]
        self.sample_sources = [
            {"id": "src1", "url": "http://example.com/ai-art", "name": "AI in Art"}
        ]

    def test_missing_prompt_or_results(self):
        """Test error handling when prompt or results are missing."""
        # Test missing prompt
        result_no_prompt = generate_final_report(
            prompt="",
            selected_results=self.sample_results,
            sources=self.sample_sources,
            platform_model="openai__gpt-4"
        )
        self.assertEqual(result_no_prompt["status"], 400)
        self.assertIn("error", result_no_prompt)

        # Test missing results
        result_no_results = generate_final_report(
            prompt=self.sample_prompt,
            selected_results=[],
            sources=self.sample_sources,
            platform_model="openai__gpt-4"
        )
        self.assertEqual(result_no_results["status"], 400)
        self.assertIn("error", result_no_results)

    @patch('tooling.ported.generate_final_report.generate_with_model')
    def test_report_generation_success(self, mock_generate):
        """Test a successful report generation with a mocked LLM response."""
        mock_response_json = {
            "title": "AI's Impact on Art",
            "summary": "A summary of the impact.",
            "sections": [{"title": "Analysis", "content": "Detailed analysis."}],
            "usedSources": [1]
        }
        # Use json.dumps() to correctly serialize the dictionary to a JSON string
        mock_generate.return_value = json.dumps(mock_response_json)

        result = generate_final_report(
            prompt=self.sample_prompt,
            selected_results=self.sample_results,
            sources=self.sample_sources,
            platform_model="openai__gpt-4"
        )

        self.assertEqual(result["status"], 200)
        self.assertEqual(result["title"], "AI's Impact on Art")
        self.assertEqual(len(result["sections"]), 1)
        # Check that the original sources were added to the final report
        self.assertEqual(result["sources"], self.sample_sources)
        mock_generate.assert_called_once()

    @patch('tooling.ported.generate_final_report.generate_with_model', side_effect=Exception("LLM is down"))
    def test_report_generation_failure_model_error(self, mock_generate):
        """Test a failure when the LLM model raises an exception."""
        result = generate_final_report(
            prompt=self.sample_prompt,
            selected_results=self.sample_results,
            sources=self.sample_sources,
            platform_model="openai__gpt-4"
        )
        self.assertEqual(result["status"], 500)
        self.assertIn("error", result)
        self.assertIn("Failed to generate final report", result["error"])

if __name__ == '__main__':
    unittest.main()