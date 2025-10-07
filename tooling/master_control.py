import json
import sys
import time
import subprocess

# Add tooling directory to path to import other tools
sys.path.insert(0, './tooling')
from state import AgentState
from research import execute_research_protocol
from research_planner import plan_deep_research
from environmental_probe import probe_filesystem, probe_network, probe_environment_variables

class MasterControlGraph:
    """
    A Finite State Machine (FSM) that enforces the agent's protocol.
    This graph reads a state definition and orchestrates the agent's workflow,
    ensuring that all protocol steps are followed in the correct order.
    """
    def __init__(self, fsm_path: str = "tooling/fsm.json"):
        with open(fsm_path, 'r') as f:
            self.fsm = json.load(f)
        self.current_state = self.fsm["initial_state"]

    def get_trigger(self, source_state: str, dest_state: str) -> str:
        """Finds the trigger for a transition between two states."""
        for transition in self.fsm["transitions"]:
            if transition["source"] == source_state and transition["dest"] == dest_state:
                return transition["trigger"]
        raise ValueError(f"No trigger found for transition from {source_state} to {dest_state}")

    def do_orientation(self, agent_state: AgentState) -> str:
        """Executes the L1, L2, and L3 orientation steps."""
        print("[MasterControl] State: ORIENTING")
        try:
            # L1: Self-Awareness
            print("  - Executing L1: Self-Awareness...")
            l1_constraints = {"target": "local_filesystem", "scope": "file", "path": "knowledge_core/agent_meta.json"}
            agent_meta = execute_research_protocol(l1_constraints)
            agent_state.messages.append({"role": "system", "content": f"L1 Orientation Complete. Agent Meta: {agent_meta[:100]}..."})

            # L2: Repo Sync
            print("  - Executing L2: Repository Sync...")
            l2_constraints = {"target": "local_filesystem", "scope": "directory", "path": "knowledge_core/"}
            repo_state = execute_research_protocol(l2_constraints)
            agent_state.messages.append({"role": "system", "content": f"L2 Orientation Complete. Repo State: {repo_state[:100]}..."})

            # L3: Environmental Probe
            print("  - Executing L3: Environmental Probe...")
            fs_status, fs_msg, fs_latency = probe_filesystem()
            net_status, net_msg, net_latency = probe_network()
            env_status, env_msg, _ = probe_environment_variables()

            report = f"Filesystem: {fs_status} ({fs_msg} - {fs_latency}) | Network: {net_status} ({net_msg} - {net_latency}) | Env Vars: {env_status} ({env_msg})"
            agent_state.vm_capability_report = report
            agent_state.messages.append({"role": "system", "content": f"L3 Orientation Complete. {report}"})

            agent_state.orientation_complete = True
            print("[MasterControl] Orientation Succeeded.")
            return self.get_trigger("ORIENTING", "PLANNING")
        except Exception as e:
            agent_state.error = f"Orientation failed: {e}"
            print(f"[MasterControl] Orientation Failed: {e}")
            return self.get_trigger("ORIENTING", "ERROR")

    def do_planning(self, agent_state: AgentState) -> str:
        """Generates a plan for the task."""
        print("[MasterControl] State: PLANNING")
        if not agent_state.plan:
            # This is where the agent would use the research planner
            agent_state.plan = plan_deep_research(agent_state.task)
            agent_state.messages.append({"role": "system", "content": f"Plan has been set:\n{agent_state.plan}"})
        print("[MasterControl] Planning Complete.")
        return self.get_trigger("PLANNING", "EXECUTING")

    def do_execution(self, agent_state: AgentState) -> str:
        """Executes the plan step by step."""
        print("[MasterControl] State: EXECUTING")

        try:
            plan_steps = [line for line in agent_state.plan.split('\n') if line.strip()]

            if agent_state.current_step_index < len(plan_steps):
                step = plan_steps[agent_state.current_step_index].strip()
                print(f"  - Executing step {agent_state.current_step_index + 1}: {step}")

                result = subprocess.run(step, shell=True, check=True, capture_output=True, text=True)

                output = result.stdout.strip()
                if result.stderr:
                    output += "\nStderr:\n" + result.stderr.strip()

                print(f"  - Output: {output}")

                agent_state.messages.append({
                    "role": "system",
                    "content": f"Successfully executed step: {step}\nOutput:\n{output}"
                })

                agent_state.current_step_index += 1
                return self.get_trigger("EXECUTING", "EXECUTING")
            else:
                print("[MasterControl] Execution Complete.")
                return self.get_trigger("EXECUTING", "POST_MORTEM")
        except subprocess.CalledProcessError as e:
            error_message = f"Execution failed at step {agent_state.current_step_index + 1}: {e.cmd}\nStderr: {e.stderr}"
            agent_state.error = error_message
            print(f"[MasterControl] {error_message}")
            return self.get_trigger("EXECUTING", "ERROR")
        except Exception as e:
            error_message = f"An unexpected error occurred during execution: {e}"
            agent_state.error = error_message
            print(f"[MasterControl] {error_message}")
            return self.get_trigger("EXECUTING", "ERROR")

    def do_post_mortem(self, agent_state: AgentState) -> str:
        """Creates a post-mortem report for the task."""
        print("[MasterControl] State: POST_MORTEM")
        try:
            # Create a summary of the execution to include in the report
            execution_summary = "\n".join([msg['content'] for msg in agent_state.messages if msg['role'] == 'system'])

            report_content = f"""
# Post-Mortem Report

## Task: {agent_state.task}

## Execution Summary
{execution_summary}

## Final Status: SUCCESS
"""
            # Create the postmortem file
            postmortem_path = f"postmortems/{agent_state.task.replace(' ', '_')}.md"
            with open(postmortem_path, "w") as f:
                f.write(report_content)

            agent_state.final_report = f"Post-mortem report created at {postmortem_path}"
            print(f"[MasterControl] Post-Mortem Complete. Report at {postmortem_path}")
            return self.get_trigger("POST_MORTEM", "DONE")
        except Exception as e:
            error_message = f"Failed to generate post-mortem report: {e}"
            agent_state.error = error_message
            print(f"[MasterControl] {error_message}")
            return self.get_trigger("POST_MORTEM", "ERROR")

    def run(self, initial_agent_state: AgentState):
        """Runs the agent's workflow through the FSM."""
        agent_state = initial_agent_state

        while self.current_state not in self.fsm["final_states"]:
            if self.current_state == "START":
                self.current_state = "ORIENTING"
                continue

            if self.current_state == "ORIENTING":
                trigger = self.do_orientation(agent_state)
            elif self.current_state == "PLANNING":
                trigger = self.do_planning(agent_state)
            elif self.current_state == "EXECUTING":
                trigger = self.do_execution(agent_state)
            elif self.current_state == "POST_MORTEM":
                trigger = self.do_post_mortem(agent_state)
            else:
                agent_state.error = f"Unknown state: {self.current_state}"
                self.current_state = "ERROR"
                break

            # Find the next state based on the trigger
            found_transition = False
            for transition in self.fsm["transitions"]:
                if transition["source"] == self.current_state and transition["trigger"] == trigger:
                    self.current_state = transition["dest"]
                    found_transition = True
                    break

            if not found_transition:
                agent_state.error = f"No transition found for state {self.current_state} with trigger {trigger}"
                self.current_state = "ERROR"

        print(f"[MasterControl] Workflow finished in state: {self.current_state}")
        if agent_state.error:
            print(f"  - Error: {agent_state.error}")
        return agent_state

if __name__ == '__main__':
    print("--- Initializing Master Control Graph Demonstration ---")
    # 1. Initialize the agent's state for a new task
    task = "Demonstrate the self-enforcing protocol."
    initial_state = AgentState(task=task)

    # 2. Initialize and run the master control graph
    graph = MasterControlGraph()
    final_state = graph.run(initial_state)

    # 3. Print the final report
    print("\n--- Final State ---")
    print(json.dumps(final_state.to_json(), indent=2))
    print("--- Demonstration Complete ---")