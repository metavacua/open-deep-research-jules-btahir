import argparse
import json
import os
from collections import defaultdict
import datetime
import uuid

# --- Configuration ---
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
EPISODIC_MEMORY_PATH = os.path.join(ROOT_DIR, 'logs', 'episodic_memory.jsonl')
REFLECTION_LOG_PATH = os.path.join(ROOT_DIR, 'knowledge_core', 'reflection_log.md')
HEURISTICS_DIR = os.path.join(ROOT_DIR, 'tooling', 'heuristics')

# --- Agile Reflection Cycle Commands ---

def retrospect(log_file):
    """
    Analyzes the episodic memory log to identify patterns for improvement.
    This is the "Retrospect" phase of the Agile Outer Loop.
    """
    print(f"--- Running Retrospection Analysis on {log_file} ---")

    tool_failures = defaultdict(int)
    tool_successes = defaultdict(int)
    all_tools = set()
    total_actions = 0

    try:
        with open(log_file, 'r') as f:
            for line in f:
                try:
                    entry = json.loads(line)
                    total_actions += 1
                    outcome = entry.get('outcome', {})
                    action_details = entry.get('action', {}).get('details', {})

                    tool_name = action_details.get('tool_name', 'unknown_tool')
                    all_tools.add(tool_name)

                    if outcome.get('status') == 'FAILURE':
                        tool_failures[tool_name] += 1
                    else:
                        tool_successes[tool_name] += 1

                except json.JSONDecodeError:
                    print(f"Warning: Skipping malformed JSON line: {line.strip()}")
                    continue
    except FileNotFoundError:
        print(f"Error: Log file not found at {log_file}. No analysis can be performed.")
        print("This may be expected if the agent has not yet recorded any actions.")
        return

    print(f"\nAnalysis Complete. Total actions analyzed: {total_actions}")

    if not total_actions:
        print("\nNo actions recorded in the log.")
        return

    print("\nTool Performance Summary:")
    for tool in sorted(list(all_tools)):
        failures = tool_failures.get(tool, 0)
        successes = tool_successes.get(tool, 0)
        total_uses = failures + successes
        failure_rate = (failures / total_uses) * 100 if total_uses > 0 else 0
        print(f"  - Tool: {tool:<30} | Failures: {failures:<5} | Successes: {successes:<5} | Failure Rate: {failure_rate:.2f}%")

    print("\nRetrospection finished. Use these insights to 'hypothesize' improvements.")


def hypothesize():
    """
    Placeholder for the "Hypothesize" phase.
    In a real implementation, this would involve using an LLM to generate
    concrete, testable hypotheses for improving performance based on
    the output of the 'retrospect' phase.
    """
    print("\n--- Hypothesize Phase (Placeholder) ---")
    print("This phase would take the analysis from 'retrospect' and generate suggestions.")
    print("Example Hypothesis: 'The `scrape_static_html` tool has a high failure rate. A new tool, `render_dynamic_webpage`, should be proposed and implemented.'")


def adapt(reflection_text):
    """
    Records the outcome of a reflection cycle into the reflection log.
    This is the "Adapt" phase of the Agile Outer Loop.
    """
    if not reflection_text:
        print("Error: --reflection-text is required to log an adaptation.")
        return

    print("\n--- Adapt Phase ---")

    header = f"""
---
timestamp: "{datetime.datetime.now(datetime.timezone.utc).isoformat()}"
trigger: "Manual CLI Invocation"
---
"""

    entry = header + "\n" + reflection_text + "\n"

    try:
        with open(REFLECTION_LOG_PATH, 'a') as f:
            f.write(entry)
        print(f"Successfully appended new entry to {REFLECTION_LOG_PATH}")
    except Exception as e:
        print(f"Error writing to reflection log: {e}")


def main():
    """
    Main function to run the A-OODA protocol CLI.
    """
    parser = argparse.ArgumentParser(
        description="A command-line tool to interact with the A-OODA protocol's Agile Reflection Cycle."
    )
    subparsers = parser.add_subparsers(dest="command", help="Available subcommands", required=True)

    # Retrospect command
    retro_parser = subparsers.add_parser("retrospect", help="Analyze episodic memory to find patterns for improvement.")
    retro_parser.add_argument(
        '--log-file',
        default=EPISODIC_MEMORY_PATH,
        help=f"Path to the episodic memory log file. Defaults to {EPISODIC_MEMORY_PATH}"
    )

    # Hypothesize command
    subparsers.add_parser("hypothesize", help="Generate hypotheses for improvement based on analysis (Placeholder).")

    # Adapt command
    adapt_parser = subparsers.add_parser("adapt", help="Log a new reflection and adaptation into the agent's constitution.")
    adapt_parser.add_argument(
        "--reflection-text",
        required=True,
        help="A string containing the full reflection entry (Reflection, Hypothesis, Adaptation)."
    )

    args = parser.parse_args()
    if args.command == "retrospect":
        retrospect(args.log_file)
    elif args.command == "hypothesize":
        hypothesize()
    elif args.command == "adapt":
        adapt(args.reflection_text)

if __name__ == "__main__":
    main()