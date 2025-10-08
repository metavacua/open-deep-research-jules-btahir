import unittest
import os
import json
import io
from contextlib import redirect_stdout
from tooling.aooda_cli import retrospect, adapt

class TestAoodaCLI(unittest.TestCase):

    def setUp(self):
        """Set up temporary files for testing."""
        self.test_episodic_log_path = "temp_test_episodic.log.jsonl"
        self.test_reflection_log_path = "temp_test_reflection.md"

        # Create sample episodic log data
        log_entries = [
            {"action": {"details": {"tool_name": "read_file"}}, "outcome": {"status": "SUCCESS"}},
            {"action": {"details": {"tool_name": "run_in_bash_session"}}, "outcome": {"status": "SUCCESS"}},
            {"action": {"details": {"tool_name": "run_in_bash_session"}}, "outcome": {"status": "FAILURE"}},
            {"action": {"details": {"tool_name": "run_in_bash_session"}}, "outcome": {"status": "FAILURE"}},
            {"action": {"details": {"tool_name": "run_in_bash_session"}}, "outcome": {"status": "SUCCESS"}},
            {"action": {"details": {"tool_name": "non_existent_tool"}}, "outcome": {"status": "FAILURE"}},
        ]
        with open(self.test_episodic_log_path, 'w') as f:
            for entry in log_entries:
                full_entry = {
                    "log_id": "test-id", "session_id": "test-session", "timestamp": "now",
                    "phase": "Act", "task": {"id": "test-task"}
                }
                full_entry.update(entry)
                f.write(json.dumps(full_entry) + '\n')

        # Create a dummy reflection log
        with open(self.test_reflection_log_path, 'w') as f:
            f.write("# Reflection Log\n\n")

    def tearDown(self):
        """Clean up the temporary files."""
        if os.path.exists(self.test_episodic_log_path):
            os.remove(self.test_episodic_log_path)
        if os.path.exists(self.test_reflection_log_path):
            os.remove(self.test_reflection_log_path)

    def test_retrospect_analysis(self):
        """Test that the retrospect function correctly analyzes failure rates."""
        f = io.StringIO()
        with redirect_stdout(f):
            # Temporarily override the default path to use our test file
            from tooling import aooda_cli
            aooda_cli.EPISODIC_MEMORY_PATH = self.test_episodic_log_path
            retrospect(self.test_episodic_log_path)

        output = f.getvalue()

        # Check for correct failure rate calculations.
        # Adjusted spacing to be less brittle.
        self.assertIn("Tool: run_in_bash_session", output)
        self.assertIn("Failures: 2", output)
        self.assertIn("Successes: 2", output)
        self.assertIn("Failure Rate: 50.00%", output)

        self.assertIn("Tool: non_existent_tool", output)
        self.assertIn("Failures: 1", output)
        self.assertIn("Successes: 0", output)
        self.assertIn("Failure Rate: 100.00%", output)

        self.assertIn("Tool: read_file", output)
        self.assertIn("Failures: 0", output)
        self.assertIn("Successes: 1", output)
        self.assertIn("Failure Rate: 0.00%", output)

        self.assertIn("Total actions analyzed: 6", output)

    def test_adapt_logging(self):
        """Test that the adapt function correctly appends to the reflection log."""
        reflection_entry = "### Reflection\nThis is a test reflection."

        # Temporarily override the default path to use our test file
        from tooling import aooda_cli
        aooda_cli.REFLECTION_LOG_PATH = self.test_reflection_log_path
        adapt(reflection_entry)

        with open(self.test_reflection_log_path, 'r') as f:
            content = f.read()

        self.assertIn("This is a test reflection.", content)
        self.assertIn("timestamp", content)
        self.assertIn("trigger: \"Manual CLI Invocation\"", content)

if __name__ == '__main__':
    unittest.main()