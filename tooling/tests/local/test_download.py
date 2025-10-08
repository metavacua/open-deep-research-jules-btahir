import unittest
from unittest.mock import patch
from tooling.local.download import download_report

class TestPortedDownload(unittest.TestCase):

    def setUp(self):
        """Set up a sample report for all tests."""
        self.sample_report = {
            "title": "Test Report",
            "summary": "A summary.",
            "sections": [{"title": "Section 1", "content": "Content 1."}]
        }

    @patch('tooling.ported.download.generate_pdf')
    def test_download_pdf(self, mock_generate_pdf):
        """Test PDF download calls the correct generator."""
        mock_generate_pdf.return_value = b"pdf_content"
        result = download_report(self.sample_report, 'pdf')

        mock_generate_pdf.assert_called_once_with(self.sample_report)
        self.assertEqual(result["status"], 200)
        self.assertEqual(result["content"], b"pdf_content")
        self.assertEqual(result["content_type"], 'application/pdf')
        self.assertEqual(result["filename"], 'report.pdf')

    @patch('tooling.ported.download.generate_docx')
    def test_download_docx(self, mock_generate_docx):
        """Test DOCX download calls the correct generator."""
        mock_generate_docx.return_value = b"docx_content"
        result = download_report(self.sample_report, 'docx')

        mock_generate_docx.assert_called_once_with(self.sample_report)
        self.assertEqual(result["status"], 200)
        self.assertEqual(result["content"], b"docx_content")
        self.assertEqual(result["content_type"], 'application/vnd.openxmlformats-officedocument.wordprocessingml.document')
        self.assertEqual(result["filename"], 'report.docx')

    def test_download_txt(self):
        """Test TXT download uses the internal text generator."""
        result = download_report(self.sample_report, 'txt')

        self.assertEqual(result["status"], 200)
        self.assertIn(b"Test Report", result["content"])
        self.assertIn(b"A summary.", result["content"])
        self.assertEqual(result["content_type"], 'text/plain')
        self.assertEqual(result["filename"], 'report.txt')

    def test_unsupported_format(self):
        """Test that an unsupported format returns an error."""
        result = download_report(self.sample_report, 'unsupported')
        self.assertEqual(result["status"], 400)
        self.assertIn("error", result)
        self.assertIn("Unsupported format", result["error"])

    @patch('tooling.ported.download.generate_pdf', side_effect=Exception("PDF generation failed"))
    def test_download_failure_propagates_exception(self, mock_generate_pdf):
        """Test that exceptions from generators are caught and handled."""
        result = download_report(self.sample_report, 'pdf')
        self.assertEqual(result["status"], 500)
        self.assertIn("error", result)
        self.assertIn("Failed to generate download", result["error"])

if __name__ == '__main__':
    unittest.main()