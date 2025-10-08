# Knowledge Base: Tractable Exponentiality and Fixed-Parameter Analysis

This document defines the protocol for evaluating and accepting algorithms with exponential time complexity, ensuring they are "tractable" within our specific problem domains.

## 1. The Need for Nuance: Beyond P vs. NP

While our core protocol mandates Polynomial-Time (PTIME) complexity as the ideal, some problems are inherently exponential. However, not all exponential algorithms are created equal. An algorithm with a runtime of `O(2^n)` is intractable for even small `n`, but an algorithm with a runtime of `O(n^2 * 2^k)` can be highly efficient if the parameter `k` is small and bounded.

This is the core idea behind **Fixed-Parameter Tractability (FPT)**, which provides a formal framework for identifying and accepting such "tractably exponential" algorithms.

## 2. Defining Tractable Exponentiality via FPT

An algorithm is considered **Fixed-Parameter Tractable**, and therefore **Tractably Exponential** for our purposes, if its runtime complexity can be expressed as:

`f(k) * poly(|x|)`

Where:
-   `|x|` is the size of the main input (e.g., the size of a file, the length of a report).
-   `k` is a specific, well-defined **parameter** of the input that is independent of the main input size.
-   `poly()` is any function that is polynomial in the size of the main input `|x|`.
-   `f()` is an arbitrary function (which can be exponential) that depends *only* on the parameter `k`.

The key insight is that if we can identify a parameter `k` that is small and bounded in our specific use case, the `f(k)` part of the equation becomes a large but manageable constant, and the algorithm's runtime scales polynomially with the main input size.

## 3. The Heuristic for Evaluating Tractable Exponentiality

When designing or evaluating a tool that may have exponential complexity, the following heuristic must be applied:

1.  **Identify the Parameter `k`**: What is the specific, small, and bounded parameter that isolates the exponential complexity? This could be the number of reports to consolidate, the number of search results to analyze, or the depth of a recursion. The value of `k` must be independent of the size of the data itself.

2.  **Identify the Main Input `|x|`**: What is the primary input whose size the algorithm should scale polynomially with? This is typically the size of the text content, file buffers, or other large data structures.

3.  **Analyze the Algorithm**: Can the proposed algorithm's runtime be formally expressed in the FPT form `f(k) * poly(|x|)`?

4.  **Bound the Parameter `k`**: Can we establish a practical and enforced upper bound on `k` for our use case? For example, "The `consolidate_report` tool will never be called with more than `k=5` reports." This bound must be justified and, where possible, enforced by the calling logic.

### Example Application: `consolidate_report`

-   **Problem**: Consolidating `k` reports. The naive approach of combining all text and sending it to an LLM scales with the total size of all reports, which is not polynomially bounded.
-   **Applying the Heuristic**:
    1.  **Parameter `k`**: The number of reports to be consolidated.
    2.  **Main Input `|x|`**: The size of the *summaries* of the reports.
    3.  **Algorithm Analysis**: A refactored algorithm that only uses report summaries has a prompt size that scales as `O(k * avg_summary_size)`. This fits the FPT model.
    4.  **Bound `k`**: We can enforce a system-wide limit, such as `k <= 5`, for any single consolidation task.

An algorithm that satisfies this heuristic is considered "tractably exponential" and is acceptable for implementation within our toolchain, as its resource usage is predictable and bounded in practice.