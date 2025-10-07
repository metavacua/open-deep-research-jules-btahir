import sys
from typing import Literal

# Ensure the tooling directory is in the path to import the research tool
sys.path.insert(0, './tooling')
from research import execute_research_protocol

def plan_deep_research(topic: str, repository: Literal['local', 'external'] = 'local') -> str:
    """
    Generates a concrete, executable plan for the demonstration task.
    """

    # For the demonstration, we will generate a specific, executable plan
    # instead of a generic template.
    executable_plan = """
python3 tooling/research.py --target external_web --scope narrow --query "React Hooks best practices 2025"
# The above command will perform the research and save the results.
# A real agent would then parse these results and use them to inform
# the next steps of the plan. For this demonstration, we will simply
# print a message indicating the next logical step.
echo "Next step: Analyze the research findings and refactor the search component."
"""
    return executable_plan.strip()

if __name__ == '__main__':
    # Example usage for testing
    print("--- Generating Executable Research Plan ---")
    executable_plan = plan_deep_research("Demonstration Task")
    print(executable_plan)