import json
from typing import Dict, Any

# --- Import all the ported tools from their new locations ---
from tooling.local import parse_document as local_parse_document
from tooling.local import documents as local_documents
from tooling.local import download as local_download
from tooling.remote import search as remote_search
from tooling.remote import fetch_content as remote_fetch_content
from tooling.remote import optimize_research as remote_optimize_research
from tooling.remote import analyze_results as remote_analyze_results
from tooling.remote import consolidate_report as remote_consolidate_report
from tooling.remote import generate_final_report as remote_generate_final_report
from tooling.remote import generate_question as remote_generate_question

# A mapping from task names to their corresponding functions, now clearly separated
TASK_DISPATCHER = {
    # --- Local Tools ---
    "parse_document": local_parse_document.parse_document,
    "generate_docx": local_documents.generate_docx,
    "generate_pdf": local_documents.generate_pdf,
    "download_report": local_download.download_report,

    # --- Remote Tools ---
    "search": remote_search.search,
    "fetch_content": remote_fetch_content.fetch_content,
    "optimize_research": remote_optimize_research.optimize_research,
    "analyze_results": remote_analyze_results.analyze_results,
    "consolidate_report": remote_consolidate_report.consolidate_report,
    "generate_final_report": remote_generate_final_report.generate_final_report,
    "generate_question": remote_generate_question.generate_question,
}

def execute_research_protocol(constraints: Dict[str, Any]) -> str:
    """
    Orchestrates the research workflow by dispatching tasks to the
    appropriate local or remote tools.

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
        # The download tool returns bytes, which are not directly JSON serializable.
        # We handle this by not double-encoding the result if it's already a dict with bytes.
        if task == "download_report" and isinstance(result.get("content"), bytes):
            # For simplicity in the toolchain, we'll encode bytes to a string for the JSON wrapper.
            # A more robust system might handle binary data differently.
            result["content"] = result["content"].decode('latin1')
        return json.dumps(result)
    except Exception as e:
        return json.dumps({"error": f"An error occurred while executing task '{task}': {e}", "status": 500})