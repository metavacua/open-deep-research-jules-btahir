import json
from typing import Dict, Any, List
from tooling.lib.remote_helpers import generate_with_model # Reusing the centralized LLM function

def _create_prompt(report: Dict[str, Any]) -> str:
    """Creates the prompt for the LLM to generate search terms."""

    # Safely access report fields
    title = report.get('title', 'N/A')
    summary = report.get('summary', 'N/A')

    # Safely process sections
    sections_str = "\n".join(
        [f"{section.get('title', 'Untitled')}: {section.get('content', '')}"
         for section in report.get('sections', [])]
    )

    return f"""Based on the following research report, generate 3 focused search terms or phrases for further research. These should be concise keywords or phrases that would help explore important aspects not fully covered in the current report.

Report Title: {title}
Summary: {summary}

Key Sections:
{sections_str}

Generate exactly 3 search terms and return them in the following JSON format:
{{
  "searchTerms": [
    "first search term",
    "second search term",
    "third search term"
  ]
}}

The search terms should be specific and focused on unexplored aspects of the topic."""

def _parse_llm_response(response: str) -> List[str]:
    """
    Parses the LLM response, attempting to decode JSON first,
    with a fallback to line-based parsing.
    """
    try:
        # Attempt to parse the full string as JSON
        data = json.loads(response)
        search_terms = data.get("searchTerms")

        if isinstance(search_terms, list) and len(search_terms) == 3:
            return search_terms
        else:
            raise ValueError("Invalid search terms format in JSON")

    except (json.JSONDecodeError, ValueError):
        # Fallback to simple line-based parsing if JSON fails
        return [
            term.strip().replace('"', '').replace(',', '')
            for term in response.split('\n')
            if term.strip() and not term.strip().startswith('{') and not term.strip().startswith('}')
        ][:3]

def generate_question(report: Dict[str, Any], platform_model: str) -> Dict[str, Any]:
    """
    Generates follow-up search questions based on a research report.
    This is a Python port of the logic in `app/api/generate-question/route.ts`.
    """
    if not report:
        return {"error": "Report is required", "status": 400}

    prompt = _create_prompt(report)

    try:
        # Call the LLM using the previously implemented function
        llm_response = generate_with_model(prompt, platform_model)

        if not llm_response:
            raise ValueError("No response from model")

        # Parse the response to extract search terms
        search_terms = _parse_llm_response(llm_response)

        return {"searchTerms": search_terms, "status": 200}

    except Exception as e:
        return {"error": f"Failed to generate search terms: {e}", "status": 500}