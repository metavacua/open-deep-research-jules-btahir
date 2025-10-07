import json
import os
import requests
from typing import Dict, Any

# The Next.js app runs on port 3000
BASE_URL = "http://localhost:3000/api"

def execute_research_protocol(constraints: Dict[str, Any]) -> str:
    """
    A unified, constraint-based research tool that integrates with the
    Open Deep Research Next.js application.

    Args:
        constraints: A dictionary specifying the operational parameters for the
                     research task.

    Returns:
        A string representing the result of the research operation.
    """
    target = constraints.get("target")
    scope = constraints.get("scope")
    path = constraints.get("path")
    query = constraints.get("query")
    results_for_report = constraints.get("results")
    prompt = constraints.get("prompt")
    model = constraints.get("model")


    # Level 1: Self-Awareness & Identity Verification (Local Filesystem)
    if target == "local_filesystem" and scope == "file":
        if path and os.path.exists(path):
            try:
                with open(path, 'r') as f:
                    return f.read()
            except Exception as e:
                return f"Error reading file {path}: {e}"
        return f"Error: Path '{path}' not specified or does not exist for L1 research."

    # Level 2: Repository State Synchronization (Local Filesystem)
    elif target == "local_filesystem" and scope == "directory":
        if path and os.path.isdir(path):
            try:
                files = os.listdir(path)
                return f"Directory listing for '{path}':\n" + "\n".join(files)
            except Exception as e:
                return f"Error listing directory {path}: {e}"
        return f"Error: Path '{path}' not specified or is not a directory for L2 research."

    # Level 3: Targeted RAG (Web Search via Next.js API)
    elif target == "external_web" and scope == "narrow":
        if not query:
            return "Error: Query not specified for L3 research."
        try:
            response = requests.post(f"{BASE_URL}/search", json={"query": query})
            response.raise_for_status()
            return response.text
        except requests.exceptions.RequestException as e:
            return f"Error during L3 web search: {e}"

    # Level 4: Deep Research (Report Generation via Next.js API)
    elif target == "external_web" and scope == "broad":
        if not results_for_report or not prompt or not model:
            return "Error: 'results', 'prompt', and 'model' must be provided for L4 deep research."
        try:
            payload = {
                "results": results_for_report,
                "prompt": prompt,
                "model": model
            }
            response = requests.post(f"{BASE_URL}/report", json=payload)
            response.raise_for_status()
            return response.text
        except requests.exceptions.RequestException as e:
            return f"Error during L4 deep research: {e}"

    else:
        return "Error: The provided constraints do not map to a recognized research level."