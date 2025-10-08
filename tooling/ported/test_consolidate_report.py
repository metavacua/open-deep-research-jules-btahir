import unittest
from unittest.mock import patch
from tooling.ported.consolidate_report import consolidate_report

class TestPortedConsolidateReport(unittest.TestCase):

    def setUp(self):
        """Set up sample data for tests."""
        self.sample_reports = [
            {
                "title": "Report 1",
                "summary": "Summary of report 1.",
                "sections": [{"title": "Finding 1", "content": "Content 1."}],
                "sources": [{"id": "src1", "name": "Source 1", "url": "http://example.com/1"}]
            },
            {
                "title": "Report 2",
                "summary": "Summary of report 2.",
                "sections": [{"title": "Finding 2", "content": "Content 2."}],
                "sources": [
                    {"id": "src1", "name": "Source 1", "url": "http://example.com/1"},
                    {"id": "src2", "name": "Source 2", "url": "http://example.com/2"}
                ]
            }
        ]

    def test_no_reports_provided(self):
        """Test error handling when the reports list is empty."""
        result = consolidate_report(reports=[], platform_model="openai__gpt-4")
        self.assertEqual(result["status"], 400)
        self.assertIn("error", result)
        self.assertEqual(result["error"], "Reports are required")

    @patch('tooling.ported.consolidate_report.generate_with_model')
    def test_consolidation_success_json_response(self, mock_generate):
        """Test a successful consolidation with a valid JSON response."""
        mock_response_json = {
            "title": "Consolidated Report",
            "summary": "This is the consolidated summary.",
            "sections": [{"title": "Theme 1", "content": "Analysis of themes."}],
            "usedSources": [1, 2]
        }
        mock_generate.return_value = str(mock_response_json).replace("'", '"')

        result = consolidate_report(reports=self.sample_reports, platform_model="openai__gpt-4")

        self.assertEqual(result["status"], 200)
        self.assertEqual(result["title"], "Consolidated Report")
        # Test that sources were de-duplicated correctly
        self.assertEqual(len(result["sources"]), 2)
        self.assertEqual(result["sources"][0]["id"], "src1")
        self.assertEqual(result["sources"][1]["id"], "src2")
        mock_generate.assert_called_once()

    @patch('tooling.ported.consolidate_report.generate_with_model')
    def test_consolidation_fallback_parsing(self, mock_generate):
        """Test the fallback parsing when the LLM response is not valid JSON."""
        mock_response_text = "This is a plain text report.\n\nIt has multiple paragraphs."
        mock_generate.return_value = mock_response_text

        result = consolidate_report(reports=self.sample_reports, platform_model="openai__gpt-4")

        self.assertEqual(result["status"], 200)
        self.assertEqual(result["title"], "Consolidated Research Report")
        self.assertIn("plain text report", result["sections"][0]["content"])
        # Check that sources are still added correctly
        self.assertEqual(len(result["sources"]), 2)

    @patch('tooling.ported.consolidate_report.generate_with_model', side_effect=Exception("LLM is down"))
    def test_consolidation_failure_model_error(self, mock_generate):
        """Test a failure when the LLM model raises an exception."""
        result = consolidate_report(reports=self.sample_reports, platform_model="openai__gpt-4")
        self.assertEqual(result["status"], 500)
        self.assertIn("error", result)
        self.assertIn("Failed to consolidate reports", result["error"])

if __name__ == '__main__':
    unittest.main()