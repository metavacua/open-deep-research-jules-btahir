# Open Deep Research - Python Toolchain

<div align="center">
  <p>A powerful open-source research toolchain, ported from a Next.js application to a modular, backend-focused Python system.</p>
</div>

This project is a comprehensive, Python-based research toolchain that generates in-depth reports from web searches and local documents. It provides a suite of modular tools that can be orchestrated to perform a complete research workflow, from initial query optimization to final report generation in various formats (PDF, DOCX, TXT).

The toolchain is designed to be used as a backend system or as a library for an AI agent. It supports multiple AI platforms (Google, OpenAI, Anthropic, Ollama) and search providers (Google, Bing, Exa), giving you the freedom to choose the perfect model and data source for your research requirements.

## Core Features

- 🔍 **Multi-Provider Web Search**: Flexible web search using Google, Bing, or Exa APIs.
- 📄 **Content Extraction**: Retrieves and processes the full content of web pages using the JinaAI reader service.
- 📂 **Local Document Parsing**: Extracts text from local DOCX, PDF, and other office documents.
- 🤖 **Multi-Platform LLM Support**: Integrates with Google Gemini, OpenAI GPT, Anthropic Claude, and local models via Ollama.
- 🧠 **AI-Powered Workflow**:
    - **Query Optimization**: Refines a basic topic into an optimized search query and report structure.
    - **Results Analysis**: Scores and ranks search results for relevance and quality.
    - **Report Generation**: Creates detailed, structured reports from curated sources.
    - **Report Consolidation**: Synthesizes multiple reports into a single, comprehensive document.
- 📤 **Multiple Export Formats**: Generates downloadable reports in PDF, DOCX, and TXT formats.

## Architecture: The Python Toolchain

The original Next.js application has been ported to a powerful, modular Python toolchain located in the `tooling/` directory. This new architecture is designed for backend use and agent-based workflows.

### Key Components:

- **`tooling/deep_research.py`**: The main entry point and orchestrator for the entire toolchain. The `execute_research_protocol` function acts as a high-level dispatcher that calls the appropriate specialized tool.

- **`tooling/ported/`**: This directory contains the individual, specialized tools that were ported from the original application's API routes. Each module handles a specific part of the research workflow:
    - `search.py`: Performs web searches.
    - `fetch_content.py`: Fetches content from URLs.
    - `parse_document.py`: Parses local documents.
    - `optimize_research.py`: Optimizes the initial research prompt.
    - `analyze_results.py`: Ranks and analyzes search results.
    - `consolidate_report.py`: Merges multiple reports.
    - `generate_final_report.py`: Creates the final, polished report.
    - `documents.py`: Generates DOCX and PDF files.
    - `download.py`: Orchestrates the file download process.

- **`tooling/lib/`**: Contains shared library code:
    - `helpers.py`: Centralized functions for interacting with LLMs and parsing JSON.
    - `filesystem.py`: Simple helpers for local file I/O.

## Getting Started

### Prerequisites

- Python 3.9+
- `pip` for installing packages

### Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/btahir/open-deep-research
    cd open-deep-research
    ```

2.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Set up Environment Variables:**
    Create a `.env` file in the root directory and add the necessary API keys for the services you intend to use. You can copy the contents of `env.example` as a template.

    ```env
    # --- LLM Provider API Keys ---
    GEMINI_API_KEY="your_gemini_api_key"
    OPENAI_API_KEY="your_openai_api_key"
    ANTHROPIC_API_KEY="your_anthropic_api_key"

    # --- Search Provider API Keys ---
    AZURE_SUB_KEY="your_azure_bing_subscription_key"
    GOOGLE_SEARCH_API_KEY="your_google_search_api_key"
    GOOGLE_SEARCH_CX="your_google_search_cx_id"
    EXA_API_KEY="your_exa_api_key"
    ```
    **Note**: You only need to provide API keys for the platforms you plan to use.

### Usage: The Research Orchestrator

The entire toolchain is accessed through the `execute_research_protocol` function in `tooling/deep_research.py`. This function takes a single dictionary argument, `constraints`, which must contain a `task` key. The value of `task` determines which tool is run, and the other keys in the dictionary are passed as arguments to that tool.

**Example: Performing a web search**

```python
from tooling.deep_research import execute_research_protocol
import json

search_constraints = {
    "task": "search",
    "query": "latest advancements in artificial intelligence",
    "provider": "google" # or "bing", "exa"
}

result_json = execute_research_protocol(search_constraints)
result = json.loads(result_json)

print(result)
```

**Example: Generating a final report**

```python
from tooling.deep_research import execute_research_protocol
import json

report_constraints = {
    "task": "generate_final_report",
    "selected_results": [
        {"url": "http://example.com/ai-news", "title": "AI News", "content": "..."}
    ],
    "sources": [
        {"id": "src1", "url": "http://example.com/ai-news", "name": "AI News"}
    ],
    "prompt": "Create a detailed report on the future of AI.",
    "platform_model": "openai__gpt-4" # or "google__gemini-flash", etc.
}

result_json = execute_research_protocol(report_constraints)
report = json.loads(result_json)

print(report['title'])
print(report['summary'])
```

## Agent-Centric Development

This repository is a controlled environment for the self-experimentation and autonomous operation of an AI agent. The primary objective is to observe, measure, and improve the agent's ability to perform complex software engineering tasks.

The core of the agent's capabilities now resides in the **Python toolchain**. The agent's workflow is orchestrated by `tooling/master_control.py`, which uses the `execute_research_protocol` function as its primary interface for interacting with the world and performing research tasks.

### Repository Structure

-   **AGENTS.md**: The master protocol document that dictates all agent behavior.
-   **knowledge_core/**: The agent's internal knowledge base.
-   **logs/**: Contains operational logs.
-   **postmortems/**: Contains post-task self-analysis reports.
-   **tooling/**: Contains the Python-based toolchain, including the FSM and ported tools.
-   **run.py**: The main entry point for initiating agent tasks.

To initiate a task for the agent, use the following command:
```bash
python run.py "Your task description here"
```

## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

## License

[MIT](https://github.com/btahir/open-deep-research/blob/main/LICENSE)