import unittest
from unittest.mock import patch
from tooling.local.parse_document import parse_document

class TestPortedParseDocument(unittest.TestCase):

    def test_no_file_content(self):
        """Test that an error is returned when no file content is provided."""
        result = parse_document(file_content=b"")
        self.assertIn("error", result)
        self.assertEqual(result["status"], 400)
        self.assertEqual(result["error"], "No file content provided")

    @patch('tooling.ported.parse_document.parse_office')
    def test_parse_success(self, mock_parse_office):
        """Test a successful document parse."""
        expected_content = "This is the content of the document."
        mock_parse_office.return_value = expected_content

        sample_bytes = b"some-binary-document-content"
        result = parse_document(file_content=sample_bytes)

        self.assertEqual(result["status"], 200)
        self.assertEqual(result["content"], expected_content)
        mock_parse_office.assert_called_once_with(sample_bytes, unittest.mock.ANY)

    @patch('tooling.ported.parse_document.parse_office', side_effect=Exception("Invalid file format"))
    def test_parse_failure_parser_error(self, mock_parse_office):
        """Test a failure due to a parsing exception."""
        sample_bytes = b"invalid-document-content"
        result = parse_document(file_content=sample_bytes)

        self.assertEqual(result["status"], 500)
        self.assertIn("error", result)
        self.assertIn("Failed to extract content from document", result["error"])
        self.assertIn("Invalid file format", result["error"])

if __name__ == '__main__':
    unittest.main()