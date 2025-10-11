import os
import re
import ast
import json

# Configuration
REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
TOOLING_DIR = os.path.join(REPO_ROOT, 'tooling')
ENTRY_POINTS = [
    os.path.join(REPO_ROOT, 'run.py'),
    os.path.join(TOOLING_DIR, 'fdc_cli.py')
]
IGNORED_DIRS = ['.git', '.next', 'node_modules', 'docs']
TECH_DEBT_MARKERS = ['TODO', 'FIXME', 'XXX']

def get_all_python_files(root_dir):
    """Recursively finds all Python files in the repository."""
    py_files = set()
    for root, dirs, files in os.walk(root_dir):
        # Prune ignored directories
        dirs[:] = [d for d in dirs if d not in IGNORED_DIRS]
        for file in files:
            if file.endswith('.py'):
                py_files.add(os.path.join(root, file))
    return py_files

def find_imports(filepath):
    """Extracts all imported modules from a Python file."""
    imports = set()
    with open(filepath, 'r', encoding='utf-8') as f:
        try:
            tree = ast.parse(f.read(), filename=filepath)
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        imports.add(alias.name.split('.')[0])
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        imports.add(node.module.split('.')[0])
        except Exception as e:
            print(f"Warning: Could not parse {filepath}. Reason: {e}")
    return imports

def build_dependency_graph(all_files):
    """Builds a graph of all imports between Python files."""
    graph = {f: set() for f in all_files}
    file_to_module = {os.path.splitext(os.path.basename(f))[0]: f for f in all_files}

    for file in all_files:
        imported_modules = find_imports(file)
        for mod in imported_modules:
            if mod in file_to_module:
                graph[file].add(file_to_module[mod])
    return graph

def find_reachable_files(graph, entry_points):
    """Performs a graph traversal (DFS) to find all files reachable from entry points."""
    reachable = set()
    stack = list(entry_points)
    while stack:
        node = stack.pop()
        if node not in reachable:
            reachable.add(node)
            # Also add dependencies that are not in the graph (e.g. non-python files)
            # This is a simplification; a more robust solution would handle this better.
            if node in graph:
                for neighbor in graph[node]:
                    stack.append(neighbor)
    return reachable

def find_tech_debt(all_files):
    """Searches for technical debt markers in all files."""
    debt = []
    for file in all_files:
        try:
            with open(file, 'r', encoding='utf-8') as f:
                for i, line in enumerate(f, 1):
                    for marker in TECH_DEBT_MARKERS:
                        if re.search(f'#.*{marker}', line, re.IGNORECASE):
                            debt.append({
                                "file": os.path.relpath(file, REPO_ROOT),
                                "line": i,
                                "marker": marker,
                                "content": line.strip()
                            })
        except Exception:
            # Ignore files that can't be read as text
            continue
    return debt

def main():
    """
    Main function to run the context check and generate a report.
    """
    print("--- Starting Repository Context Check ---")

    all_py_files = get_all_python_files(REPO_ROOT)
    graph = build_dependency_graph(all_py_files)
    reachable_files = find_reachable_files(graph, ENTRY_POINTS)

    all_repo_files = set()
    for root, dirs, files in os.walk(REPO_ROOT):
        dirs[:] = [d for d in dirs if d not in IGNORED_DIRS]
        for file in files:
            all_repo_files.add(os.path.join(root, file))

    # We only care about python files for disconnected check
    unreachable_py_files = all_py_files - reachable_files

    # Filter out test files that only import the file they are testing
    truly_disconnected = []
    for f in unreachable_py_files:
        is_test_file = 'test_' in os.path.basename(f)
        tested_file = os.path.basename(f).replace('test_', '').replace('.py', '')

        # Simple heuristic: if a test file's only purpose is to test a single,
        # otherwise disconnected file, then the source file is truly disconnected.
        if not is_test_file:
             truly_disconnected.append(os.path.relpath(f, REPO_ROOT))


    tech_debt = find_tech_debt(all_repo_files)

    report = {
        "disconnected_tools": sorted(list(truly_disconnected)),
        "technical_debt": tech_debt
    }

    print("\n--- Context Check Report ---")
    print(json.dumps(report, indent=2))
    print("\n--- Context Check Complete ---")

    # Save report to a file
    report_path = os.path.join(REPO_ROOT, 'docs', 'governance_report.json')
    with open(report_path, 'w') as f:
        json.dump(report, f, indent=2)

    print(f"Report saved to {report_path}")

if __name__ == "__main__":
    main()