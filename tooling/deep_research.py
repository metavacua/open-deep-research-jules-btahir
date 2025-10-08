import json
import os
import requests
from typing import Dict, Any
import google.generativeai as genai
from openai import OpenAI
import anthropic
import ollama
import re

# --- Configuration (ported from lib/config.ts) ---
CONFIG = {
    "search": {
        "resultsPerPage": 10,
        "provider": 'google',
        "safeSearch": {
            "google": 'active',
            "bing": 'moderate',
        },
        "market": 'en-US',
    },
}

# --- Search Endpoints ---
BING_ENDPOINT = 'https://api.bing.microsoft.com/v7.0/search'
GOOGLE_ENDPOINT = 'https://customsearch.googleapis.com/customsearch/v1'
EXA_ENDPOINT = 'https://api.exa.ai/search'

# --- Helper Functions ---
def get_bing_freshness(time_filter: str) -> str:
    if time_filter == '24h': return 'Day'
    if time_filter == 'week': return 'Week'
    if time_filter == 'month': return 'Month'
    if time_filter == 'year': return 'Year'
    return ''

def get_google_date_restrict(time_filter: str) -> str:
    if time_filter == '24h': return 'd1'
    if time_filter == 'week': return 'w1'
    if time_filter == 'month': return 'm1'
    if time_filter == 'year': return 'y1'
    return ''

# --- Provider-Specific Search Functions ---
def search_google(query: str, time_filter: str) -> str:
    api_key = os.environ.get("GOOGLE_SEARCH_API_KEY")
    cx = os.environ.get("GOOGLE_SEARCH_CX")
    if not api_key or not cx:
        return json.dumps({"error": "Google search API is not properly configured."})

    params = {
        'q': query,
        'key': api_key,
        'cx': cx,
        'num': CONFIG['search']['resultsPerPage'],
        'safe': CONFIG['search']['safeSearch']['google']
    }
    date_restrict = get_google_date_restrict(time_filter)
    if date_restrict:
        params['dateRestrict'] = date_restrict

    try:
        response = requests.get(GOOGLE_ENDPOINT, params=params)
        response.raise_for_status()
        return json.dumps(response.json())
    except requests.exceptions.RequestException as e:
        return json.dumps({"error": f"Error during Google search: {e}"})

def search_bing(query: str, time_filter: str) -> str:
    api_key = os.environ.get("AZURE_SUB_KEY")
    if not api_key:
        return json.dumps({"error": "Bing search API is not properly configured."})

    params = {
        'q': query,
        'count': CONFIG['search']['resultsPerPage'],
        'mkt': CONFIG['search']['market'],
        'safeSearch': CONFIG['search']['safeSearch']['bing'],
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
        return json.dumps({"error": f"Error during Bing search: {e}"})

def search_exa(query: str) -> str:
    api_key = os.environ.get("EXA_API_KEY")
    if not api_key:
        return json.dumps({"error": "Exa search API is not properly configured."})

    headers = {
        'Content-Type': 'application/json',
        'x-api-key': api_key
    }
    payload = {
        'query': query,
        'numResults': CONFIG['search']['resultsPerPage'],
        'useAutoprompt': True
    }

    try:
        response = requests.post(EXA_ENDPOINT, headers=headers, json=payload)
        response.raise_for_status()
        return json.dumps(response.json())
    except requests.exceptions.RequestException as e:
        return json.dumps({"error": f"Error during Exa search: {e}"})

# --- Report Generation Functions ---
def generate_system_prompt(articles, user_prompt):
    """Generates a detailed system prompt for the research assistant."""
    article_str = "\n\n".join([f"Source {i+1}:\n{art['body']}" for i, art in enumerate(articles)])
    return f"""You are a world-class research assistant. Your goal is to provide a comprehensive, unbiased, and well-structured report based on the provided articles.

Here are the articles for your review:
{article_str}

Based on these articles, please answer the following user prompt: "{user_prompt}"

Your response MUST be a JSON object with the following schema:
{{
  "title": "A concise and informative title for the report",
  "introduction": "A brief overview of the topic and the scope of the report.",
  "key_findings": [
    "A list of the most important facts, conclusions, or insights from the articles."
  ],
  "synthesis": "A detailed analysis that connects the findings from different articles, highlighting agreements, disagreements, and potential gaps in information.",
  "conclusion": "A summary of the main points and potential implications or areas for further research.",
  "sources": [
    "A list of the source URLs or identifiers for the articles used."
  ]
}}

Ensure your report is neutral, well-supported by the provided text, and does not introduce outside information.
"""

def extract_and_parse_json(response: str) -> Dict:
    try:
        return json.loads(response)
    except json.JSONDecodeError:
        pass

    code_block_match = re.search(r"```(?:json)?\s*([\s\S]*?)```", response)
    if code_block_match:
        try:
            return json.loads(code_block_match.group(1))
        except json.JSONDecodeError:
            pass

    try:
        start_index = response.index("{")
        end_index = response.rindex("}") + 1
        return json.loads(response[start_index:end_index])
    except (ValueError, json.JSONDecodeError):
        pass

    raise ValueError("No valid JSON found in response")

def generate_with_gemini(system_prompt: str, model_name: str) -> str:
    """Generates a research report using a model from Google Gemini."""
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY environment variable not set.")

    genai.configure(api_key=api_key)
    model = genai.GenerativeModel(model_name)
    response = model.generate_content(system_prompt)
    return response.text

def generate_with_openai(system_prompt: str, model_name: str) -> str:
    """Generates a research report using a model from OpenAI."""
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY environment variable not set.")

    client = OpenAI(api_key=api_key)
    response = client.chat.completions.create(
        model=model_name,
        messages=[
            {"role": "system", "content": system_prompt},
        ],
        temperature=0.2,
        max_tokens=4096,
        response_format={"type": "json_object"},
    )
    return response.choices[0].message.content

def generate_with_anthropic(system_prompt: str, model_name: str) -> str:
    """Generates a research report using a model from Anthropic."""
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        raise ValueError("ANTHROPIC_API_KEY environment variable not set.")

    client = anthropic.Anthropic(api_key=api_key)
    response = client.messages.create(
        model=model_name,
        max_tokens=4096,
        temperature=0.2,
        system=system_prompt,
        messages=[
            {
                "role": "user",
                "content": "Please generate the report based on the provided articles."
            }
        ]
    )
    return response.content[0].text

def generate_with_ollama(system_prompt: str, model_name: str) -> str:
    """Generates a research report using a local model from Ollama."""
    try:
        response = ollama.chat(
            model=model_name,
            messages=[{'role': 'system', 'content': system_prompt}],
            format='json'
        )
        return response['message']['content']
    except Exception as e:
        # Catch potential connection errors or other issues
        raise RuntimeError(f"Failed to connect to Ollama: {e}")

def generate_with_model(system_prompt: str, platform_model: str) -> str:
    platform, model = platform_model.split('__')
    if platform == "google": return generate_with_gemini(system_prompt, model)
    if platform == "openai": return generate_with_openai(system_prompt, model)
    if platform == "anthropic": return generate_with_anthropic(system_prompt, model)
    if platform == "ollama": return generate_with_ollama(system_prompt, model)
    raise ValueError("Invalid platform specified")

# --- Main Execution Logic ---
def execute_research_protocol(constraints: Dict[str, Any]) -> str:
    target = constraints.get("target")
    scope = constraints.get("scope")
    path = constraints.get("path")
    query = constraints.get("query")
    results_for_report = constraints.get("results")
    prompt = constraints.get("prompt")
    model = constraints.get("model")
    provider = constraints.get("provider", CONFIG['search']['provider'])
    time_filter = constraints.get("time_filter", "all")

    if target == "local_filesystem" and scope == "file":
        if path and os.path.exists(path):
            try:
                with open(path, 'r') as f:
                    return f.read()
            except Exception as e:
                return f"Error reading file {path}: {e}"
        return f"Error: Path '{path}' not specified or does not exist for L1 research."

    elif target == "local_filesystem" and scope == "directory":
        if path and os.path.isdir(path):
            try:
                files = os.listdir(path)
                return f"Directory listing for '{path}':\n" + "\n".join(files)
            except Exception as e:
                return f"Error listing directory {path}: {e}"
        return f"Error: Path '{path}' not specified or is not a directory for L2 research."

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