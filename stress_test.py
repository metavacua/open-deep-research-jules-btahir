import json
import time
import os
from tooling.deep_research import execute_research_protocol

def log_step(title, start_time, data_size=None):
    """Logs the completion of a step, its duration, and optional data size."""
    duration = time.time() - start_time
    size_log = f"| Data Size: {data_size / 1024:.2f} KB" if data_size is not None else ""
    print(f"--- Step Complete: {title} | Duration: {duration:.2f}s {size_log} ---")

def run_stress_test():
    """
    Orchestrates a comprehensive, multi-step research task to stress test
    the entire ported toolchain.

    Note: To run this test with real results, ensure all necessary
    environment variables (e.g., OPENAI_API_KEY, GOOGLE_SEARCH_API_KEY) are set.
    The script is designed to fail gracefully if keys are missing.
    """
    print("--- Initializing Toolchain Stress Test ---")

    research_task = "Conduct a comprehensive analysis of the current state of autonomous AI software engineering agents, their core architectural patterns, and the primary challenges they face."
    print(f"\nResearch Task: {research_task}")

    start_time = time.time()

    # --- Step 1: Optimize Research (L5) ---
    print("\n--- Step 1: Optimizing Research Prompt (L5) ---")
    optimize_constraints = {
        "task": "optimize_research",
        "prompt": research_task,
        "platform_model": "openai__gpt-4" # Using a powerful model for optimization
    }
    optimized_json = execute_research_protocol(optimize_constraints)
    optimized_data = json.loads(optimized_json)

    if "error" in optimized_data:
        print(f"Error in Step 1: {optimized_data['error']}. Aborting.")
        return

    optimized_query = optimized_data.get("query", research_task)
    final_report_prompt = optimized_data.get("optimizedPrompt", research_task)
    log_step("Optimize Research", start_time)
    print(f"Optimized Query: {optimized_query}")

    # --- Step 2: Web Search (L3) ---
    start_time = time.time()
    print("\n--- Step 2: Performing Web Search (L3) ---")
    search_constraints = {
        "task": "search",
        "query": optimized_query,
        "provider": "google"
    }
    search_results_json = execute_research_protocol(search_constraints)
    search_results = json.loads(search_results_json)

    if "error" in search_results:
        print(f"Error in Step 2: {search_results['error']}. Aborting.")
        return

    web_pages = search_results.get("webPages", {}).get("value", [])
    log_step("Web Search", start_time, len(search_results_json.encode('utf-8')))
    print(f"Found {len(web_pages)} search results.")

    # --- Step 3: Fetch Content (L4) ---
    start_time = time.time()
    print(f"\n--- Step 3: Fetching Content for Top {min(3, len(web_pages))} Results (L4) ---")
    fetched_content = []
    total_fetched_size = 0
    for result in web_pages[:3]: # Limit to top 3 for the stress test
        url = result.get("url")
        if not url:
            continue
        print(f"Fetching: {url}")
        fetch_constraints = {"task": "fetch_content", "url": url}
        content_json = execute_research_protocol(fetch_constraints)
        content_data = json.loads(content_json)

        if "content" in content_data:
            content = content_data["content"]
            fetched_content.append({"url": url, "title": result.get("name"), "content": content})
            total_fetched_size += len(content.encode('utf-8'))
        else:
            print(f"Warning: Could not fetch content for {url}. Reason: {content_data.get('error')}")

    log_step("Fetch Content", start_time, total_fetched_size)
    print(f"Fetched content for {len(fetched_content)} sources.")

    # --- Step 4: Analyze Results (L5) ---
    start_time = time.time()
    print("\n--- Step 4: Analyzing Results (L5) ---")
    analysis_constraints = {
        "task": "analyze_results",
        "prompt": final_report_prompt,
        "results": fetched_content,
        "platform_model": "openai__gpt-4"
    }
    analysis_json = execute_research_protocol(analysis_constraints)
    analysis_data = json.loads(analysis_json)

    if "error" in analysis_data:
        print(f"Error in Step 4: {analysis_data['error']}. Aborting.")
        return

    log_step("Analyze Results", start_time, len(analysis_json.encode('utf-8')))
    print("Analysis complete. Top ranked source:", analysis_data.get("rankings", [{}])[0].get("url"))

    # --- Step 5: Generate Final Report (L5) ---
    start_time = time.time()
    print("\n--- Step 5: Generating Final Report (L5) ---")
    report_constraints = {
        "task": "generate_final_report",
        "selected_results": fetched_content,
        "sources": web_pages, # Pass original search results for citation
        "prompt": final_report_prompt,
        "platform_model": "openai__gpt-4"
    }
    final_report_json = execute_research_protocol(report_constraints)
    final_report_data = json.loads(final_report_json)

    if "error" in final_report_data:
        print(f"Error in Step 5: {final_report_data['error']}. Aborting.")
        return

    log_step("Generate Final Report", start_time, len(final_report_json.encode('utf-8')))
    print("Final report generated successfully.")

    # --- Step 6: Save Report as DOCX (L1) ---
    start_time = time.time()
    print("\n--- Step 6: Saving Report as DOCX (L1) ---")
    download_constraints = {
        "task": "download_report",
        "report": final_report_data,
        "file_format": "docx"
    }
    download_json = execute_research_protocol(download_constraints)
    download_data = json.loads(download_json)

    if "error" in download_data:
        print(f"Error in Step 6: {download_data['error']}. Aborting.")
        return

    output_filename = "stress_test_report.docx"
    docx_content = download_data["content"].encode('latin1') # Content is returned as a string, must be encoded back to bytes
    with open(output_filename, 'wb') as f:
        f.write(docx_content)

    log_step("Save Report", start_time, len(docx_content))
    print(f"Report saved to '{output_filename}'")

    print("\n--- Stress Test Complete ---")

if __name__ == "__main__":
    run_stress_test()