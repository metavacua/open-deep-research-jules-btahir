import time
import subprocess
import json
from tooling.state import AgentState
from tooling.aooda_cli import retrospect, adapt

class AoodaOrchestrator:
    """
    An orchestrator that implements the A-OODA protocol.
    This class replaces the rigid FSM-based MasterControlGraph with a continuous,
    hierarchical loop designed for emergent, adaptive behavior.
    """
    def __init__(self, agent_state: AgentState):
        self.agent_state = agent_state
        self.ooda_cycle_count = 0
        print("[AoodaOrchestrator] Initialized.")

    def run(self):
        """
        Main execution loop for the A-OODA protocol.
        This loop runs continuously, processing information and acting on it,
        while periodically triggering a meta-cognitive reflection cycle.
        """
        print("[AoodaOrchestrator] Starting A-OODA cognitive cycle...")
        # In a real-world scenario, this would be a long-running process.
        # For this demonstration, we'll limit the number of cycles.
        max_cycles = 5
        while self.ooda_cycle_count < max_cycles:
            self.observe()
            self.orient()
            self.decide()
            self.act()

            self.ooda_cycle_count += 1

            # Check for Agile Reflection trigger
            if self.should_trigger_reflection():
                self.agile_reflection_cycle()

            time.sleep(0.1) # Small delay for readability

        print(f"\n[AoodaOrchestrator] Halting after {max_cycles} cycles for demonstration.")
        self.agent_state.final_report = "Demonstration of A-OODA protocol complete. See logs for cycle details."
        return self.agent_state

    def observe(self):
        """
        [Observe Phase]
        Gathers raw data from all available sources, including internal state,
        environmental sensors, and the outcome of previous actions.
        """
        print(f"\n--- OODA Cycle {self.ooda_cycle_count + 1}: Observe ---")
        last_message = self.agent_state.messages[-1] if self.agent_state.messages else {"content": "None"}
        print(f"  - Observing current state. Task: '{self.agent_state.task}'")
        print(f"  - Reviewing last system message: '{last_message['content'][:100]}...'")

    def orient(self):
        """
        [Orient Phase]
        The cognitive engine. Synthesizes observations, cultural heritage (core programming),
        and past experiences (memory) to form a coherent mental model of the situation.
        """
        print("--- OODA Cycle: Orient ---")
        orientation_summary = "Situation normal. Continuing with standard procedure."
        if self.agent_state.error:
            orientation_summary = f"A failure was observed: '{self.agent_state.error}'. Re-orienting to address the issue."
            # Clear the error after acknowledging it
            self.agent_state.error = None

        self.agent_state.messages.append({"role": "system", "content": f"[Orient] {orientation_summary}"})
        print(f"  - Orientation: {orientation_summary}")

    def decide(self):
        """
        [Decide Phase]
        Formulates a hypothesis or plan of action based on the current orientation.
        This is not about finding a perfect plan, but the best available option.
        """
        print("--- OODA Cycle: Decide ---")
        if not self.agent_state.plan:
            # If there's no plan, the default decision is to do a simple self-check.
            self.agent_state.plan = 'echo "Status OK. No active plan."'
            print("  - Decision: No plan exists. Formulating a default self-check action.")
        else:
            print(f"  - Decision: Proceeding with existing plan: '{self.agent_state.plan}'")

        self.agent_state.messages.append({"role": "system", "content": f"[Decide] Decided to execute: {self.agent_state.plan}"})

    def act(self):
        """
        [Act Phase]
        Executes the decided action. Actions are treated as experiments to test
        the current hypothesis, and their outcomes are the primary input for the
        next Observe phase.
        """
        print("--- OODA Cycle: Act ---")
        command = self.agent_state.plan
        try:
            print(f"  - Executing command: `{command}`")
            result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
            output = result.stdout.strip() or "(No output)"
            message = f"[Act] Successfully executed command. Output: {output}"
            print(f"  - Action successful. Output: {output}")
            self.agent_state.messages.append({"role": "system", "content": message})
            # For this demo, create a new dummy plan for the next cycle
            self.agent_state.plan = f'echo "This is the plan for cycle {self.ooda_cycle_count + 2}."'
        except Exception as e:
            error_message = f"Action failed: {e}"
            print(f"  - {error_message}")
            self.agent_state.error = str(e)
            self.agent_state.messages.append({"role": "system", "content": f"[Act][FAILURE] {error_message}"})
            # In case of failure, the plan is cleared to force re-evaluation
            self.agent_state.plan = None

    def should_trigger_reflection(self):
        """
        Checks if the conditions are met to trigger the Agile Reflection Cycle.
        This is a key part of the agent's meta-cognition.
        """
        # For this demo, trigger every 3 cycles.
        return self.ooda_cycle_count > 0 and self.ooda_cycle_count % 3 == 0

    def agile_reflection_cycle(self):
        """
        [Outer Loop]
        Performs the Agile Reflection Cycle for self-improvement.
        This is a lower-frequency, deliberative process.
        """
        print("\n\n===== TRIGGERING AGILE REFLECTION CYCLE =====")

        # 1. Retrospect: Analyze performance data.
        print("\n--- Agile Cycle: Retrospect ---")
        # Here we would call the CLI function to analyze the real episodic memory log.
        # retrospect(EPISODIC_MEMORY_PATH)
        print("  - Analyzing performance logs... (mocked for demo)")

        # 2. Hypothesize: Generate ideas for improvement.
        print("\n--- Agile Cycle: Hypothesize ---")
        print("  - Generating hypotheses for improvement... (mocked for demo)")
        hypothesis = "Hypothesis: The default 'echo' plan is not sufficiently complex. A new heuristic should be developed to generate more meaningful plans based on the task description."

        # 3. Adapt: Commit a change to the agent's "source code".
        print("\n--- Agile Cycle: Adapt ---")
        print("  - Adapting internal heuristics... (mocked for demo)")
        # In a real system, this would modify a file in tooling/heuristics/ or log a formal proposal.
        # For the demo, we use the adapt function to log this to the reflection log.
        adapt(f"### Reflection\nAnalyzed {self.ooda_cycle_count} OODA cycles and found performance to be nominal but simplistic.\n\n### Hypothesis\n{hypothesis}\n\n### Adaptation\nNo code was changed, but this reflection was logged as a proof-of-concept for future, more advanced self-modification.")

        self.agent_state.messages.append({"role": "system", "content": f"[Adapt] {hypothesis}"})
        print("\n=============================================\n")