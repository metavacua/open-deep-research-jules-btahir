import requests
from typing import Dict, Any
from urllib.parse import quote

JINA_READER_ENDPOINT = "https://r.jina.ai/"

def fetch_content(url: str) -> Dict[str, Any]:
    """
    Fetches the primary content from a given URL using the Jina AI reader service.
    This is a Python port of the logic in `app/api/fetch-content/route.ts`.
    """
    if not url:
        return {"error": "URL is required", "status": 400}

    try:
        # URL-encode the target URL to safely pass it as a parameter
        encoded_url = quote(url, safe='')
        fetch_url = f"{JINA_READER_ENDPOINT}{encoded_url}"

        response = requests.get(fetch_url, timeout=30)

        # Check if the request was successful
        if not response.ok:
            return {
                "error": "Failed to fetch content",
                "status": response.status_code,
                "details": response.text
            }

        # Return the content if successful
        return {"content": response.text, "status": 200}

    except requests.exceptions.RequestException as e:
        return {"error": f"An unexpected error occurred: {e}", "status": 500}

if __name__ == '__main__':
    # Example usage:
    test_url = "https://www.forbes.com/sites/gilpress/2024/07/21/the-story-of-openais-story/"
    result = fetch_content(test_url)

    if "error" in result:
        print(f"Error fetching content: {result['error']} (Status: {result['status']})")
    else:
        print("Successfully fetched content:")
        print(result["content"][:1000] + "...") # Print the first 1000 characters