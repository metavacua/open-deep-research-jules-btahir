import json
import os
import requests
from typing import Dict, Any
import argparse

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

def web_search(query: str, provider: str = CONFIG['search']['provider'], time_filter: str = "all") -> str:
    if provider == "google":
        return search_google(query, time_filter)
    elif provider == "bing":
        return search_bing(query, time_filter)
    elif provider == "exa":
        return search_exa(query)
    else:
        return json.dumps({"error": "Invalid search provider specified."})

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="A Python-native web search tool.")
    parser.add_argument("--query", required=True, help="The search query.")
    parser.add_argument("--provider", default=CONFIG['search']['provider'], help="The search provider to use (google, bing, exa).")
    parser.add_argument("--time_filter", default="all", help="The time filter for the search (24h, week, month, year, all).")

    args = parser.parse_args()

    result = web_search(query=args.query, provider=args.provider, time_filter=args.time_filter)
    print(result)