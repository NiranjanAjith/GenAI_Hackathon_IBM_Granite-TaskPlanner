import crewai
import openai
import json

# Load configuration
with open('config.json') as f:
    config = json.load(f)

openai.api_key = config['llm']['api_key']

# Initialize CrewAI platform
platform = crewai.Platform()

# Define system prompts for each agent (task definitions)
user_interaction_prompt = """
You are a helpful assistant. Given a user's request, extract the main task or goal and return a clear description of it. If the user gives multiple tasks, summarize them into one goal. For example, for 'Book a flight to New York and reserve a hotel', your response should be 'Plan a trip to New York.'
"""

subtask_generator_prompt = """
You are a task breakdown assistant. Given a task or goal, break it down into smaller, actionable subtasks. If a subtask can be broken down further, do so iteratively. For example, for 'Plan a birthday party', the subtasks might be:
1. Choose a venue
2. Send invitations
3. Arrange catering
If you can't break it down further, return the final subtasks.
"""

plan_evaluator_prompt = """
You are a plan evaluator. Given a list of subtasks, evaluate whether the plan is complete or needs improvement. Check for missing steps or incomplete tasks. If the plan is good, return 'Plan is ready'. If it needs improvement, suggest changes or refinements.
"""

# Define agents (using CrewAI's agent system)
user_interaction_agent = platform.create_agent("User Interaction Agent", role="Handles user input and output")
subtask_generator = platform.create_agent("Subtask Generator", role="Breaks down tasks into smaller subtasks iteratively")
plan_evaluator = platform.create_agent("Plan Evaluator", role="Evaluates and improves the generated plan")

# Assign the system prompts to the agents
user_interaction_agent.set_system_prompt(user_interaction_prompt)
subtask_generator.set_system_prompt(subtask_generator_prompt)
plan_evaluator.set_system_prompt(plan_evaluator_prompt)

# Define the Subtask Generator logic (iterative process)
class SubtaskGenerator:
    def __init__(self):
        self.model = config['agents']['subtask_generator']['model']
    
    def generate_subtasks(self, task):
        subtasks = []
        while True:
            response = openai.Completion.create(
                model=self.model,
                prompt=f"{subtask_generator_prompt}\nTask: {task}",
                max_tokens=150
            )
            new_subtask = response['choices'][0]['text'].strip()
            if new_subtask and new_subtask not in subtasks:
                subtasks.append(new_subtask)
                # If a new subtask is added, continue the process
                task = new_subtask
            else:
                break  # No further subtasks can be generated
        return subtasks

# Define the User Interaction Agent task logic
def process_user_input(user_input):
    # Send input to LLM and get response
    response = openai.Completion.create(
        model=config['agents']['user_interaction_agent']['model'],
        prompt=f"{user_interaction_prompt}\nUser request: {user_input}",
        max_tokens=100
    )
    return response['choices'][0]['text'].strip()

# Define Plan Evaluator task logic
def evaluate_plan(subtasks):
    subtasks_text = "\n".join(subtasks)
    response = openai.Completion.create(
        model=config['agents']['plan_evaluator']['model'],
        prompt=f"{plan_evaluator_prompt}\nSubtasks: {subtasks_text}",
        max_tokens=200
    )
    evaluation = response['choices'][0]['text'].strip()
    if "improvement" in evaluation.lower():
        return False  # Plan needs improvement
    return True  # Plan is ready to be delivered

# Assign the task of "Handling user input" to the User Interaction Agent
user_interaction_agent.add_task("Handle user input", process_user_input)

# Assign the task of "Breaking down tasks into subtasks" to the Subtask Generator
subtask_generator.add_task("Generate subtasks iteratively", SubtaskGenerator().generate_subtasks)

# Assign the task of "Evaluating the generated plan" to the Plan Evaluator
plan_evaluator.add_task("Evaluate generated plan", evaluate_plan)

# Orchestrate the tasks
def orchestrate_event(user_input):
    # Step 1: Handle user input
    user_input_result = user_interaction_agent.delegate_task(user_input)
    
    # Step 2: Generate subtasks based on user input
    subtasks = subtask_generator.delegate_task(user_input_result)
    
    # Step 3: Evaluate the generated subtasks (plan)
    plan_ready = plan_evaluator.delegate_task(subtasks)
    
    # Step 4: Return final result to the user if plan is ready
    if plan_ready:
        return f"Plan is complete and ready: {subtasks}"
    else:
        return f"Plan needs improvement: {subtasks}"

# Automatically delegate tasks and monitor progress
user_input = "Plan a birthday party"
final_plan = orchestrate_event(user_input)
print(final_plan)

# Run the event orchestration process through CrewAI
platform.run()
