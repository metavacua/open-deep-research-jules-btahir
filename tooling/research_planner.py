import sys
import json
from typing import Literal

# Ensure the tooling directory is in the path to import the research tool
sys.path.insert(0, './tooling')
from research import execute_research_protocol

def plan_deep_research(topic: str, repository: Literal['local', 'external'] = 'local') -> str:
    """
    Generates a structured, executable JSON plan for the demonstration task.
    """

    plan = {
        "title": "Demonstration Task: Analyze and Refactor React Hooks",
        "steps": [
            {
                "description": "Perform research on the latest best practices for React Hooks in 2025.",
                "command": "python3 tooling/research.py --target external_web --scope narrow --query \"React Hooks best practices 2025\""
            },
            {
                "description": "Analyze the research findings and identify areas for improvement in the search component.",
                "command": "echo \"Next step would be to analyze the output of the previous step and refactor the code.\""
            }
        ]
    }

    return json.dumps(plan, indent=2)

if __name__ == '__main__':
    # Example usage for testing
    print("--- Generating Structured JSON Research Plan ---")
    json_plan = plan_deep_research("Demonstration Task")
    print(json_plan)