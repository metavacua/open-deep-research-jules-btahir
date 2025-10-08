import json
from typing import Dict, Any

# --- Import all the ported tools ---
from tooling.ported import search as ported_search
from tooling.ported import fetch_content as ported_fetch_content
from tooling.ported import parse_document as ported_parse_document
from tooling.ported import optimize_research as ported_optimize_research
from tooling.ported import analyze_results as ported_analyze_results
from tooling.ported import consolidate_report as ported_consolidate_report
from tooling.ported import generate_final_report as ported_generate_final_report
from tooling.ported import download as ported_download

# A mapping from task names to their corresponding functions
TASK_DISPATCHER = {
    "search": ported_search.search,
    "fetch_content": ported_fetch_content.fetch_content,
    "parse_document": ported_parse_document.parse_document,
    "optimize_research": ported_optimize_research.optimize_research,
    "analyze_results": ported_analyze_results.analyze_results,
    "consolidate_report": ported_consolidate_report.consolidate_report,
    "generate_final_report": ported_generate_final_report.generate_final_report,
    "download_report": ported_download.download_report,
}

def execute_research_protocol(constraints: Dict[str, Any]) -> str:
    """
    Orchestrates the research workflow by dispatching tasks to the
    appropriate ported tools.

    The `constraints` dictionary must contain a 'task' key, which
    determines which tool to run. The rest of the keys in `constraints`
    are passed as keyword arguments to the selected tool.

    Args:
        constraints: A dictionary containing the task and its arguments.

    Returns:
        A JSON string representing the result from the executed tool.
    """
    task = constraints.get("task")
    if not task:
        return json.dumps({"error": "A 'task' must be specified in the constraints", "status": 400})

    if task not in TASK_DISPATCHER:
        return json.dumps({"error": f"Unknown task: {task}", "status": 400})

    task_function = TASK_DISPATCHER[task]
    task_args = {k: v for k, v in constraints.items() if k != 'task'}

    try:
        result = task_function(**task_args)
        return json.dumps(result)
    except Exception as e:
        return json.dumps({"error": f"An error occurred while executing task '{task}': {e}", "status": 500})