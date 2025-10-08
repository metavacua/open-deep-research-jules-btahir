import unittest
import json
from unittest.mock import patch, MagicMock

# The function we are testing
from tooling.deep_research import execute_research_protocol, TASK_DISPATCHER

class TestDeepResearchOrchestrator(unittest.TestCase):

    def test_no_task_specified(self):
        """Test that an error is returned if no task is specified."""
        constraints = {"some_arg": "some_value"}
        result_json = execute_research_protocol(constraints)
        result = json.loads(result_json)

        self.assertEqual(result["status"], 400)
        self.assertIn("A 'task' must be specified", result["error"])

    def test_unknown_task(self):
        """Test that an error is returned for an unknown task."""
        constraints = {"task": "non_existent_task"}
        result_json = execute_research_protocol(constraints)
        result = json.loads(result_json)

        self.assertEqual(result["status"], 400)
        self.assertIn("Unknown task", result["error"])

    @patch.dict(TASK_DISPATCHER, {'search': MagicMock()})
    def test_dispatch_search_task_success(self):
        """Test successful dispatch to the search tool."""
        # Arrange: The mocked tool returns a dictionary
        mock_search = TASK_DISPATCHER['search']
        mock_return_value = {"status": 200, "data": "search results"}
        mock_search.return_value = mock_return_value

        constraints = {
            "task": "search",
            "query": "test query",
            "provider": "google"
        }

        # Act
        result_json = execute_research_protocol(constraints)
        result = json.loads(result_json)

        # Assert
        mock_search.assert_called_once()
        expected_args = {"query": "test query", "provider": "google"}
        mock_search.assert_called_with(**expected_args)
        self.assertEqual(result, mock_return_value)

    @patch.dict(TASK_DISPATCHER, {'fetch_content': MagicMock(side_effect=Exception("Tool failed unexpectedly"))})
    def test_dispatch_task_exception(self):
        """Test that the orchestrator handles exceptions from tools."""
        constraints = {
            "task": "fetch_content",
            "url": "http://example.com"
        }

        # Act
        result_json = execute_research_protocol(constraints)
        result = json.loads(result_json)

        # Assert
        mock_fetch = TASK_DISPATCHER['fetch_content']
        mock_fetch.assert_called_once()
        self.assertEqual(result["status"], 500)
        self.assertIn("An error occurred while executing task 'fetch_content'", result["error"])
        self.assertIn("Tool failed unexpectedly", result["error"])

    @patch.dict(TASK_DISPATCHER, {'download_report': MagicMock()})
    def test_dispatch_download_task(self):
        """Test dispatch to another tool to ensure the dispatcher is generic."""
        mock_download = TASK_DISPATCHER['download_report']
        mock_return_value = {"status": 200, "content": "file bytes"}
        mock_download.return_value = mock_return_value

        constraints = {
            "task": "download_report",
            "report": {"title": "My Report"},
            "file_format": "pdf"
        }

        execute_research_protocol(constraints)

        expected_args = {"report": {"title": "My Report"}, "file_format": "pdf"}
        mock_download.assert_called_once_with(**expected_args)


if __name__ == '__main__':
    unittest.main()