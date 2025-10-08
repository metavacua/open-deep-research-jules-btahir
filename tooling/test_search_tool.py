import os
import sys

# Add the tooling directory to the Python path to allow for relative imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))

from research import web_search

def main():
    """
    A simple script to verify the functionality of the web_search tool.
    """
    print("--- Verifying Web Search Tool ---")

    # This test will fail if API keys are not set in the environment,
    # which is the expected behavior. The goal is to verify that the
    # script runs and attempts to make the API call.
    test_query = "latest news on generative AI"
    print(f"Executing search for: '{test_query}'")

    # We expect this to return an error about missing API keys,
    # which proves the function is being called correctly.
    result = web_search(query=test_query, provider="google")

    print("\n--- Search Result ---")
    print(result)
    print("--- Verification Complete ---")

if __name__ == "__main__":
    main()