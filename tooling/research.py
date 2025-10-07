import json
import os
import requests
from typing import Dict, Any

# The Next.js app runs on port 3000
BASE_URL = "http://localhost:3000/api"

BING_ENDPOINT = 'https://api.bing.microsoft.com/v7.0/search'
GOOGLE_ENDPOINT = 'https://customsearch.googleapis.com/customsearch/v1'
EXA_ENDPOINT = 'https://api.exa.ai/search'

def get_bing_freshness(time_filter: str) -> str:
    if time_filter == '24h':
        return 'Day'
    if time_filter == 'week':
        return 'Week'
    if time_filter == 'month':
        return 'Month'
    if time_filter == 'year':
        return 'Year'
    return ''

def get_google_date_restrict(time_filter: str) -> str:
    if time_filter == '24h':
        return 'd1'
    if time_filter == 'week':
        return 'w1'
    if time_filter == 'month':
        return 'm1'
    if time_filter == 'year':
        return 'y1'
    return ''

def search_google(query: str, time_filter: str) -> str:
    api_key = os.environ.get("GOOGLE_SEARCH_API_KEY")
    cx = os.environ.get("GOOGLE_SEARCH_CX")
    if not api_key or not cx:
        return "Error: Google search API is not properly configured."

    params = {
        'q': query,
        'key': api_key,
        'cx': cx,
        'num': 10
    }
    date_restrict = get_google_date_restrict(time_filter)
    if date_restrict:
        params['dateRestrict'] = date_restrict

    try:
        response = requests.get(GOOGLE_ENDPOINT, params=params)
        response.raise_for_status()
        return json.dumps(response.json())
    except requests.exceptions.RequestException as e:
        return f"Error during Google search: {e}"

def search_bing(query: str, time_filter: str) -> str:
    api_key = os.environ.get("AZURE_SUB_KEY")
    if not api_key:
        return "Error: Bing search API is not properly configured."

    params = {
        'q': query,
        'count': 10,
        'mkt': 'en-US',
        'safeSearch': 'Moderate',
        'textFormat': 'HTML',
        'textDecorations': 'true'
    }
    freshness = get_bing_freshness(time_filter)
    if freshness:
        params['freshness'] = freshness

    headers = {'Ocp-Apim-Subscription-Key': api_key}

    try:
        response = requests.get(BING_ENDPOINT, params=params, headers=headers)
        response.raise_for_status()
        return json.dumps(response.json())
    except requests.exceptions.RequestException as e:
        return f"Error during Bing search: {e}"

def search_exa(query: str) -> str:
    api_key = os.environ.get("EXA_API_KEY")
    if not api_key:
        return "Error: Exa search API is not properly configured."

    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {api_key}'
    }
    payload = {
        'query': query,
        'type': 'auto',
        'numResults': 10,
        'contents': {
            'text': {
                'maxCharacters': 500
            }
        }
    }

    try:
        response = requests.post(EXA_ENDPOINT, headers=headers, json=payload)
        response.raise_for_status()
        return json.dumps(response.json())
    except requests.exceptions.RequestException as e:
        return f"Error during Exa search: {e}"

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
    provider = constraints.get("provider", "google")
    time_filter = constraints.get("time_filter", "all")


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

    # Level 3: Targeted RAG (Web Search via Python native functions)
    elif target == "external_web" and scope == "narrow":
        if not query:
            return "Error: Query not specified for L3 research."

        if provider == "google":
            return search_google(query, time_filter)
        elif provider == "bing":
            return search_bing(query, time_filter)
        elif provider == "exa":
            return search_exa(query)
        else:
            return "Error: Invalid search provider specified."

    # Level 4: Deep Research (Report Generation via Python native functions)
    elif target == "external_web" and scope == "broad":
        if not results_for_report or not prompt or not model:
            return "Error: 'results', 'prompt', and 'model' must be provided for L4 deep research."

        system_prompt = generate_system_prompt(results_for_report, prompt)

        try:
            response = generate_with_model(system_prompt, model)
            parsed_response = extract_and_parse_json(response)
            return json.dumps(parsed_response)
        except Exception as e:
            return f"Error during L4 deep research: {e}"

    else:
        return "Error: The provided constraints do not map to a recognized research level."

def generate_system_prompt(articles, user_prompt):
    return f"""You are a research assistant tasked with creating a comprehensive report based on multiple sources.
The report should specifically address this request: "{user_prompt}"

Your report should:
1. Have a clear title that reflects the specific analysis requested
2. Begin with a concise executive summary
3. Be organized into relevant sections based on the analysis requested
4. Use markdown formatting for emphasis, lists, and structure
5. Use citations ONLY when necessary for specific claims, statistics, direct quotes, or important facts
6. Maintain objectivity while addressing the specific aspects requested in the prompt
7. Compare and contrast the information from sources, noting areas of consensus or points of contention
8. Showcase key insights, important data, or innovative ideas

Here are the source articles to analyze (numbered for citation purposes):

{chr(10).join([f"[{index + 1}] Title: {article['title']}{chr(10)}URL: {article['url']}{chr(10)}Content: {article['content']}{chr(10)}---" for index, article in enumerate(articles)])}

Format the report as a JSON object with the following structure:
{{
  "title": "Report title",
  "summary": "Executive summary (can include markdown)",
  "sections": [
    {{
      "title": "Section title",
      "content": "Section content with markdown formatting and selective citations"
    }}
  ],
  "usedSources": [1, 2]
}}

Use markdown formatting in the content to improve readability.
Be judicious and selective with citations.
You DO NOT need to cite every source provided.
"""

def extract_and_parse_json(response: str) -> Dict:
    # Attempt 1: Full parse
    try:
        return json.loads(response)
    except json.JSONDecodeError:
        pass

    # Attempt 2: Code block
    import re
    code_block_match = re.search(r"```(?:json)?\s*([\s\S]*?)```", response)
    if code_block_match:
        try:
            return json.loads(code_block_match.group(1))
        except json.JSONDecodeError:
            pass

    # Attempt 3: Bracket matching
    try:
        start_index = response.index("{")
        end_index = response.rindex("}") + 1
        return json.loads(response[start_index:end_index])
    except (ValueError, json.JSONDecodeError):
        pass

    raise ValueError("No valid JSON found in response")

import google.generativeai as genai
from openai import OpenAI
import anthropic
import ollama

def generate_with_model(system_prompt: str, platform_model: str) -> str:
    platform, model = platform_model.split('__')

    if platform == "google":
        return generate_with_gemini(system_prompt, model)
    elif platform == "openai":
        return generate_with_openai(system_prompt, model)
    elif platform == "anthropic":
        return generate_with_anthropic(system_prompt, model)
    elif platform == "ollama":
        return generate_with_ollama(system_prompt, model)
    else:
        raise ValueError("Invalid platform specified")

def generate_with_gemini(system_prompt: str, model_name: str) -> str:
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY not set")
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel(model_name)
    response = model.generate_content(system_prompt)
    return response.text

def generate_with_openai(system_prompt: str, model_name: str) -> str:
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY not set")
    client = OpenAI(api_key=api_key)
    response = client.chat.completions.create(
        model=model_name,
        messages=[{"role": "user", "content": system_prompt}]
    )
    return response.choices[0].message.content

def generate_with_anthropic(system_prompt: str, model_name: str) -> str:
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        raise ValueError("ANTHROPIC_API_KEY not set")
    client = anthropic.Anthropic(api_key=api_key)
    response = client.messages.create(
        model=model_name,
        max_tokens=3500,
        messages=[{"role": "user", "content": system_prompt}]
    )
    return response.content[0].text

def generate_with_ollama(system_prompt: str, model_name: str) -> str:
    response = ollama.chat(
        model=model_name,
        messages=[{"role": "user", "content": system_prompt}]
    )
    return response['message']['content']

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description="A unified, constraint-based research tool.")
    parser.add_argument("--target", required=True, help="The target for the research (e.g., local_filesystem, external_web).")
    parser.add_argument("--scope", required=True, help="The scope of the research (e.g., file, directory, narrow, broad).")
    parser.add_argument("--path", help="The file or directory path for local filesystem research.")
    parser.add_argument("--query", help="The search query for web research.")
    parser.add_argument("--results", help="A JSON string of search results for report generation.")
    parser.add_argument("--prompt", help="The prompt for report generation.")
    parser.add_argument("--model", help="The model to use for report generation.")
    parser.add_argument("--provider", default="google", help="The search provider to use.")
    parser.add_argument("--time_filter", default="all", help="The time filter for web search.")

    args = parser.parse_args()

    constraints = {
        "target": args.target,
        "scope": args.scope,
        "path": args.path,
        "query": args.query,
        "results": json.loads(args.results) if args.results else None,
        "prompt": args.prompt,
        "model": args.model,
        "provider": args.provider,
        "time_filter": args.time_filter,
    }

    result = execute_research_protocol(constraints)
    print(result)