import unittest
from unittest.mock import patch
from tooling.ported.optimize_research import optimize_research

class TestPortedOptimizeResearch(unittest.TestCase):

    def test_no_prompt_provided(self):
        """Test error handling when no prompt is provided."""
        result = optimize_research(prompt="", platform_model="openai__gpt-4")
        self.assertEqual(result["status"], 400)
        self.assertIn("error", result)
        self.assertEqual(result["error"], "Prompt is required")

    def test_is_test_query(self):
        """Test the handling of a 'test' prompt."""
        result = optimize_research(prompt="test", platform_model="openai__gpt-4")
        self.assertEqual(result["status"], 200)
        self.assertEqual(result["query"], "test")
        self.assertEqual(result["explanation"], "Test optimization strategy")
        self.assertEqual(len(result["suggestedStructure"]), 2)

    @patch('tooling.ported.optimize_research.generate_with_model')
    def test_optimization_success(self, mock_generate):
        """Test a successful optimization with a mocked LLM response."""
        mock_response_json = {
            "query": "optimized query",
            "optimizedPrompt": "optimized prompt",
            "explanation": "explanation",
            "suggestedStructure": ["structure 1"]
        }
        mock_generate.return_value = str(mock_response_json).replace("'", '"')

        result = optimize_research(prompt="original prompt", platform_model="openai__gpt-4")
        self.assertEqual(result["status"], 200)
        self.assertEqual(result["query"], "optimized query")
        self.assertEqual(len(result["suggestedStructure"]), 1)
        mock_generate.assert_called_once()

    @patch('tooling.ported.optimize_research.generate_with_model', side_effect=Exception("LLM is down"))
    def test_optimization_failure_model_error(self, mock_generate):
        """Test a failure when the LLM model raises an exception."""
        result = optimize_research(prompt="original prompt", platform_model="openai__gpt-4")
        self.assertEqual(result["status"], 500)
        self.assertIn("error", result)
        self.assertIn("Failed to optimize research", result["error"])

if __name__ == '__main__':
    unittest.main()