# Formal Research Protocol v2.0

This document defines a tiered research protocol where each level corresponds to a formal computational complexity class. This framework ensures all agent operations are predictable, resource-aware, and bounded by Polynomial-Time (PTIME) complexity, in accordance with the core development protocol.

## Research Tiers

### L0: Constant Time Operations - O(1)

-   **Description**: Operations with a fixed, constant time complexity, independent of input size. This tier represents the most efficient and predictable actions.
-   **Resources**: Internal memory (CPU registers, state flags).
-   **Complexity**: **O(1)**. The operation takes the same amount of time regardless of the agent's state or task.
-   **Example**: Accessing a pre-configured value, checking an agent status flag, initiating a pre-defined state transition.

### L1: Linear Time File I/O - O(n)

-   **Description**: Operations whose complexity scales linearly with the size of the data being processed. This primarily involves reading from or writing to a single file.
-   **Resources**: Local disk I/O, file buffers.
-   **Complexity**: **O(n)**, where `n` is the size of the file.
-   **Example**: `read_file('path/to/file.py')`, saving a generated report to disk.

### L2: Linear Time Directory I/O - O(k)

-   **Description**: Operations involving scanning a directory. The complexity scales linearly with the number of entries in the directory.
-   **Resources**: Local disk I/O.
-   **Complexity**: **O(k)**, where `k` is the number of files and subdirectories in the target directory.
-   **Example**: `list_files('tooling/ported/')`.

### L3: Bounded External Call (Search)

-   **Description**: Performing a single, targeted query to an external API (e.g., a web search). While subject to network latency, the operation itself is a single, bounded transaction from the agent's perspective.
-   **Resources**: Network I/O, Search API endpoint.
-   **Complexity**: Considered a **bounded, atomic operation**. The complexity is external and does not scale with a local input variable `n`.
-   **Example**: Using the `search` tool to query an API.

### L4: Linear Time External Call (Content Fetch)

-   **Description**: Fetching the full content of a web page or document from a URL. The complexity is dominated by the size of the content being downloaded.
-   **Resources**: Network I/O, Content Fetching Service.
-   **Complexity**: **O(n)**, where `n` is the size of the content being fetched.
-   **Example**: Using the `fetch_content` tool on a specific URL.

### L5: Polynomial Time Cognitive Operations (LLM)

-   **Description**: Utilizing a large language model (LLM) for a cognitive task (e.g., analysis, synthesis, generation). The agent's logic for preparing the prompt and parsing the response MUST be a polynomial-time algorithm. The external LLM call is treated as a PTIME oracle.
-   **Resources**: LLM API, significant computational resources (local or remote).
-   **Complexity**: **PTIME**. The agent's own processing logic is polynomially bounded.
-   **Example**: Using the `analyze_results` or `generate_final_report` tools.

### L6: PTIME-Bounded Orchestration

-   **Description**: A meta-level task that orchestrates a sequence of lower-level tasks (L0-L5) to achieve a complex goal.
-   **Resources**: Combines all resources from the lower tiers.
-   **Complexity**: **PTIME**. The entire workflow is guaranteed to be polynomially bounded, as it is a polynomial sequence of PTIME-bounded operations.
-   **Example**: The `stress_test.py` workflow, which combines prompt optimization (L5), search (L3), content fetching (L4), and report generation (L5) in a structured, polynomial sequence.