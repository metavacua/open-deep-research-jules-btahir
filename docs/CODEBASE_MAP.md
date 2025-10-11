# Codebase Map and Toolchain Analysis

This document provides a high-level map of the repository's toolchain architecture. It outlines the primary control flows, identifies all known toolsets, and highlights disconnected or underutilized components.

## 1. Primary Control Flows

The repository currently contains two parallel, conflicting control-flow systems for agent operations.

### System A: The `MasterControlGraph` (Executed)

This is the system that is actively run when `run.py` is executed.

*   **Entry Point:** `run.py`
*   **Orchestrator:** `tooling/master_control.py` (`MasterControlGraph` class)
*   **State Machine:** Defined in `tooling/fsm.json`
*   **Workflow:**
    1.  `START`: The script is initiated.
    2.  `ORIENTING`: Performs a hardcoded set of orientation tasks (L1-L4 self-awareness, repo sync, environmental probe, temporal orientation).
    3.  `PLANNING`: Calls `tooling/research_planner.py` to generate a plan. **(Note: This is a placeholder that returns a static plan).**
    4.  `EXECUTING`: Executes the plan's steps using `subprocess.run`.
    5.  `POST_MORTEM`: Generates a simple post-mortem report.
*   **Dependencies:**
    *   `tooling/state.py`
    *   `tooling/deep_research.py` (which in turn uses `tooling/remote/search.py` and `tooling/remote/fetch_content.py`)
    *   `tooling/research_planner.py`
    *   `tooling/environmental_probe.py`
    *   `tooling/lib/filesystem.py`

### System B: The FDC/AORP Protocol (Documented)

This is the system described in `AGENTS.md` and is the mandated protocol for the agent to follow. It is currently **not** executed by the `run.py` entry point.

*   **Entry Point:** `AGENTS.md` (instructions for the agent)
*   **Orchestrator:** `tooling/fdc_cli.py` (Finite Development Cycle Command-Line Interface)
*   **State Machine:** Defined in `tooling/fdc_fsm.json`
*   **Workflow:** A more flexible, state-based model where the agent is expected to use CLI commands (`validate`, `analyze`, `close`) to manage the task lifecycle. It is designed to work with agent-generated plans.
*   **Dependencies:**
    *   Relies on the agent (me) to generate and execute plans based on the FSM.

**Conclusion:** The primary architectural issue is that the documented, mandated `FDC/AORP` protocol is completely bypassed by the `run.py` script, which uses the simpler, more rigid `MasterControlGraph` system.

## 2. Disconnected Components

These are tools and utilities that are not currently integrated into either of the primary control flows.

### Standalone Tools
*   **`tooling/dependency_graph_generator.py`**: A script intended to generate a repository-wide dependency graph. It is only used by its own test file.
*   **`tooling/symbol_map_generator.py`**: A script to generate a map of code symbols (classes, functions). It is only used by its own test file.
*   **`tooling/self_improvement_cli.py`**: A script containing functions to analyze agent planning efficiency. It is only used by its own test file.

### Ported Tool Suites

The `tooling/local` and `tooling/remote` directories contain Python ports of the original TypeScript application's API routes. While `deep_research.py` uses two of these, the majority are unused, and there is no high-level orchestrator to manage them effectively.

*   **`tooling/local/`**:
    *   `documents.py`: To generate DOCX and PDF files.
    *   `download.py`: To orchestrate file downloads.
    *   `parse_document.py`: To extract text from office documents.
*   **`tooling/remote/`**:
    *   `analyze_results.py`: To score and rank search results.
    *   `consolidate_report.py`: To synthesize multiple reports.
    *   `fetch_content.py`: **(Partially used)** To get content from URLs.
    *   `generate_final_report.py`: To generate a detailed report from sources.
    *   `generate_question.py`: **(Partially used)** To generate search terms from a report.
    *   `optimize_research.py`: To refine a research topic.
    *   `search.py`: **(Partially used)** To handle web searches.