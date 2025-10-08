import unittest
from unittest.mock import patch, mock_open
import os
import json
from tooling.deep_research import execute_research_protocol, extract_and_parse_json

class TestDeepResearch(unittest.TestCase):

    def setUp(self):
        """Set up a temporary directory for filesystem tests."""
        self.test_dir = "temp_research_test"
        os.makedirs(self.test_dir, exist_ok=True)
        self.test_file_path = os.path.join(self.test_dir, "test_file.txt")
        with open(self.test_file_path, "w") as f:
            f.write("This is a test file.")

    def tearDown(self):
        """Clean up the temporary directory."""
        if os.path.exists(self.test_dir):
            import shutil
            shutil.rmtree(self.test_dir)

    # --- Filesystem Tests ---

    def test_read_file_success(self):
        """Test reading an existing file from the local filesystem."""
        constraints = {
            "target": "local_filesystem",
            "scope": "file",
            "path": self.test_file_path
        }
        result = execute_research_protocol(constraints)
        self.assertEqual(result, "This is a test file.")

    def test_read_file_not_found(self):
        """Test reading a non-existent file."""
        constraints = {
            "target": "local_filesystem",
            "scope": "file",
            "path": "non_existent_file.txt"
        }
        result = execute_research_protocol(constraints)
        self.assertIn("Error: Path 'non_existent_file.txt' not specified or does not exist", result)

    def test_list_directory_success(self):
        """Test listing contents of a directory."""
        constraints = {
            "target": "local_filesystem",
            "scope": "directory",
            "path": self.test_dir
        }
        result = execute_research_protocol(constraints)
        self.assertIn("test_file.txt", result)

    # --- External Web Search Tests (with mocks) ---

    @patch.dict(os.environ, {"GOOGLE_SEARCH_API_KEY": "test_key", "GOOGLE_SEARCH_CX": "test_cx"})
    @patch('requests.get')
    def test_search_google_success(self, mock_get):
        """Test a successful Google search."""
        mock_response = unittest.mock.Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"items": [{"title": "Test Result"}]}
        mock_get.return_value = mock_response

        constraints = {
            "target": "external_web",
            "scope": "narrow",
            "provider": "google",
            "query": "test query"
        }
        result = execute_research_protocol(constraints)
        data = json.loads(result)
        self.assertEqual(data["items"][0]["title"], "Test Result")

    def test_search_google_no_api_key(self):
        """Test Google search when API key is not configured."""
        constraints = {
            "target": "external_web",
            "scope": "narrow",
            "provider": "google",
            "query": "test query"
        }
        result = execute_research_protocol(constraints)
        data = json.loads(result)
        self.assertIn("error", data)
        self.assertIn("not properly configured", data["error"])

    # --- JSON Parsing Tests ---

    def test_extract_json_plain(self):
        """Test extracting a plain JSON string."""
        json_string = '{"key": "value"}'
        self.assertEqual(extract_and_parse_json(json_string), {"key": "value"})

    def test_extract_json_in_code_block(self):
        """Test extracting JSON from a markdown code block."""
        response = "Some text before... ```json\n{\"key\": \"value\"}\n``` ...and after."
        self.assertEqual(extract_and_parse_json(response), {"key": "value"})

    def test_extract_json_in_text(self):
        """Test extracting the first valid JSON object from a messy string."""
        response = "Here is the data: { \"key\": \"value\" } some other text"
        self.assertEqual(extract_and_parse_json(response), {"key": "value"})

    def test_extract_json_no_json(self):
        """Test that an error is raised when no JSON is found."""
        with self.assertRaises(ValueError):
            extract_and_parse_json("This string has no JSON.")

    # --- LLM Generation Tests (with mocks) ---

    @patch.dict(os.environ, {"OPENAI_API_KEY": "fake_key"})
    @patch('tooling.deep_research.OpenAI')
    def test_generate_with_openai_success(self, mock_openai):
        """Test successful generation with OpenAI."""
        # Mock the client and its response
        mock_client = unittest.mock.Mock()
        mock_response = unittest.mock.Mock()
        mock_choice = unittest.mock.Mock()
        mock_message = unittest.mock.Mock()
        mock_message.content = '{"report": "openai"}'
        mock_choice.message = mock_message
        mock_response.choices = [mock_choice]
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client

        from tooling.deep_research import generate_with_openai
        result = generate_with_openai("test prompt", "gpt-4")
        self.assertEqual(result, '{"report": "openai"}')
        mock_openai.assert_called_with(api_key="fake_key")
        mock_client.chat.completions.create.assert_called_once()

    @patch.dict(os.environ, {"ANTHROPIC_API_KEY": "fake_key"})
    @patch('tooling.deep_research.anthropic.Anthropic')
    def test_generate_with_anthropic_success(self, mock_anthropic):
        """Test successful generation with Anthropic."""
        # Mock the client and its response
        mock_client = unittest.mock.Mock()
        mock_response = unittest.mock.Mock()
        mock_content = unittest.mock.Mock()
        mock_content.text = '{"report": "anthropic"}'
        mock_response.content = [mock_content]
        mock_client.messages.create.return_value = mock_response
        mock_anthropic.return_value = mock_client

        from tooling.deep_research import generate_with_anthropic
        result = generate_with_anthropic("test prompt", "claude-3")
        self.assertEqual(result, '{"report": "anthropic"}')
        mock_anthropic.assert_called_with(api_key="fake_key")
        mock_client.messages.create.assert_called_once()

    def test_generate_with_openai_no_key(self):
        """Test that OpenAI generation raises an error if the key is missing."""
        with patch.dict(os.environ, clear=True):
            from tooling.deep_research import generate_with_openai
            with self.assertRaisesRegex(ValueError, "OPENAI_API_KEY"):
                generate_with_openai("prompt", "model")

    def test_generate_with_anthropic_no_key(self):
        """Test that Anthropic generation raises an error if the key is missing."""
        with patch.dict(os.environ, clear=True):
            from tooling.deep_research import generate_with_anthropic
            with self.assertRaisesRegex(ValueError, "ANTHROPIC_API_KEY"):
                generate_with_anthropic("prompt", "model")

    @patch.dict(os.environ, {"GEMINI_API_KEY": "fake_key"})
    @patch('tooling.deep_research.genai')
    def test_generate_with_gemini_success(self, mock_genai):
        """Test successful generation with Gemini."""
        mock_model = unittest.mock.Mock()
        mock_response = unittest.mock.Mock()
        mock_response.text = '{"report": "gemini"}'
        mock_model.generate_content.return_value = mock_response
        mock_genai.GenerativeModel.return_value = mock_model

        from tooling.deep_research import generate_with_gemini
        result = generate_with_gemini("test prompt", "gemini-pro")
        self.assertEqual(result, '{"report": "gemini"}')
        mock_genai.configure.assert_called_with(api_key="fake_key")
        mock_model.generate_content.assert_called_once()

    @patch('tooling.deep_research.ollama')
    def test_generate_with_ollama_success(self, mock_ollama):
        """Test successful generation with Ollama."""
        mock_ollama.chat.return_value = {
            "message": {"content": '{"report": "ollama"}'}
        }
        from tooling.deep_research import generate_with_ollama
        result = generate_with_ollama("test prompt", "llama2")
        self.assertEqual(result, '{"report": "ollama"}')
        mock_ollama.chat.assert_called_once()

    def test_generate_with_gemini_no_key(self):
        """Test that Gemini generation raises an error if the key is missing."""
        with patch.dict(os.environ, clear=True):
            from tooling.deep_research import generate_with_gemini
            with self.assertRaisesRegex(ValueError, "GEMINI_API_KEY"):
                generate_with_gemini("prompt", "model")

    @patch('tooling.deep_research.ollama.chat', side_effect=RuntimeError("Connection failed"))
    def test_generate_with_ollama_connection_error(self, mock_chat):
        """Test that Ollama generation raises an error on connection failure."""
        from tooling.deep_research import generate_with_ollama
        with self.assertRaisesRegex(RuntimeError, "Failed to connect to Ollama"):
            generate_with_ollama("prompt", "model")


if __name__ == '__main__':
    unittest.main()