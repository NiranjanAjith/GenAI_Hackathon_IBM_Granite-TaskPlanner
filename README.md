1. User Interaction Agent
  Role: Handle input and output, serve as the point of communication between the user and the system.

    - Responsibilities:
	- Accept high-level goals from the user in natural language.
	- Process and forward the goals to the Subtask Generator Agent.
	- Display the final action plan to the user.

    - Flow:
	- Receives the user’s high-level goal (e.g., "Build a mobile app").
	- Passes the input to the Subtask Generator Agent for decomposition.
	- Once the plan is generated and evaluated, the agent presents it to the user in a readable format (e.g., list of tasks, timeline).

---

2. Subtask Generator Agent
  Role: Decompose the high-level goal into actionable tasks, recursively breaking down tasks until they can't be broken down further.

    - Responsibilities:
	- Main Task Decomposition: Break down high-level objectives (e.g., "Build a mobile app") into major tasks (e.g., "Design UI", "Develop Backend").
	- Recursive Breakdown: Continuously break each task down into smaller subtasks, until the task becomes granular enough to be executed independently.

    - Flow:
	- Receives a high-level goal from the **User Interaction Agent** and starts breaking it down into primary tasks.
	- For each primary task, it recursively calls itself to decompose the tasks further.
	- When a task can no longer be broken down (e.g., "Research app design trends"), it becomes a concrete subtask.
	- Outputs the final set of actionable tasks.

    - Key Decisions:
	- Granularity: Ensure that each task is actionable but doesn’t overwhelm the system with too many sub-levels. Tasks should be clear and measurable (e.g., "Create wireframes" instead of "Work on UI design").
	- Completion Condition: Stop recursion when a task can be considered complete on its own.

---

3. Plan Evaluator Agent
  Role: Evaluate the generated plan for feasibility and quality, providing a feedback loop for refinements.

    - Responsibilities:
	- Evaluation: Assess the quality and completeness of the plan based on certain criteria (e.g., clarity, feasibility, dependencies).
	- Scoring: Provide a score to the plan, ensuring it is actionable, realistic, and well-structured.
	- Refinement: If the plan doesn't meet the quality standards, send it back to the Subtask Generator Agent for refinements or additional detail.

    - Flow:
	- Receives the action plan from the Subtask Generator Agent.
	- Evaluates the plan's completeness, ensuring no tasks are left too vague or unfeasible (e.g., checking for task dependencies and logical flow).
	- If the plan is incomplete or poorly structured, the evaluator sends feedback and triggers rework by calling the **Subtask Generator Agent** again for refinement.
	- If the plan passes evaluation, it returns the refined action plan to the **User Interaction Agent** for display.

    - Criteria for Evaluation:
	- Feasibility: Can the tasks be realistically completed?
	- Completeness: Are all necessary steps included for task execution?
	- Task Structure: Is each task granular enough to be actionable? Are there dependencies that are clear?
	- Timeline: Are tasks scheduled properly, or are there missing time estimates?

---

Simplified Workflow

  1. User Input (via User Interaction Agent):
     - The user provides the high-level goal (e.g., "Build a mobile app").
     - The **User Interaction Agent** processes this input.

  2. Subtask Breakdown (via Subtask Generator Agent):
     - The Subtask Generator Agent starts breaking down the high-level goal into tasks and sub-tasks.
     - This recursive breakdown continues until the tasks cannot be further decomposed.

  3. Plan Evaluation (via Plan Evaluator Agent):
     - The generated plan is then sent to the Plan Evaluator Agent.
     - The evaluator checks the plan for completeness, feasibility, and proper structuring.
     - If the plan fails evaluation (e.g., missing tasks or too vague), it gets sent back to the Subtask Generator Agent for refinement.

  4. Final Output (via User Interaction Agent):
     - Once the plan is evaluated and meets the criteria, the User Interaction Agent presents the completed action plan to the user.

---



```
  User Input
       |
       v
  User Interaction Agent
       |
       v
  Subtask Generator Agent  --> Plan Refinement --> Subtask Generator Agent (if needed)
       |
       v
  Plan Evaluator Agent
       |
       v
  Final Plan
       |
       v
  User Interaction Agent
```
