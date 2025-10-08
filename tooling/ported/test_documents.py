import unittest
from unittest.mock import patch, MagicMock
from tooling.ported.documents import generate_docx, generate_pdf

class TestPortedDocuments(unittest.TestCase):

    def setUp(self):
        """Set up a sample report for all tests."""
        self.sample_report = {
            "title": "Comprehensive AI Report",
            "summary": "This is a summary of the report on AI.",
            "sections": [
                {"title": "Introduction", "content": "The introduction to AI."},
                {"title": "Conclusion", "content": "The conclusion on AI."}
            ]
        }

    @patch('tooling.ported.documents.Document')
    def test_generate_docx_success(self, mock_document_cls):
        """Test successful DOCX generation."""
        # Arrange: mock the Document class and its methods
        mock_doc_instance = MagicMock()
        mock_document_cls.return_value = mock_doc_instance

        # Act
        result = generate_docx(self.sample_report)

        # Assert
        mock_document_cls.assert_called_once() # Check if Document() was called
        self.assertTrue(mock_doc_instance.add_paragraph.called)
        self.assertTrue(mock_doc_instance.add_heading.called)
        # Check that save was called on a BytesIO-like object
        mock_doc_instance.save.assert_called_once()
        self.assertIsInstance(result, bytes)

    @patch('tooling.ported.documents.MarkdownPdf')
    @patch('tooling.ported.documents.Section')
    def test_generate_pdf_success(self, mock_section_cls, mock_markdown_pdf_cls):
        """Test successful PDF generation."""
        # Arrange
        mock_pdf_instance = MagicMock()
        mock_markdown_pdf_cls.return_value = mock_pdf_instance

        # Act
        result = generate_pdf(self.sample_report)

        # Assert
        mock_markdown_pdf_cls.assert_called_once_with(toc_level=2)
        mock_section_cls.assert_called_once() # Check that Section() was called with markdown
        mock_pdf_instance.add_section.assert_called_once()
        mock_pdf_instance.save.assert_called_once()
        self.assertIsInstance(result, bytes)

    @patch('tooling.ported.documents.Document', side_effect=Exception("DOCX library error"))
    def test_generate_docx_failure(self, mock_document_cls):
        """Test that DOCX generation propagates exceptions."""
        with self.assertRaisesRegex(Exception, "DOCX library error"):
            generate_docx(self.sample_report)

    @patch('tooling.ported.documents.MarkdownPdf', side_effect=Exception("PDF library error"))
    def test_generate_pdf_failure(self, mock_markdown_pdf_cls):
        """Test that PDF generation propagates exceptions."""
        with self.assertRaisesRegex(Exception, "PDF library error"):
            generate_pdf(self.sample_report)

if __name__ == '__main__':
    unittest.main()