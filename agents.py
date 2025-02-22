import crewai
import openai
import json
import os
from dotenv import load_dotenv
from crewai import Agent, Task, Crew, LLM

# Load environment variables (Ensure your .env contains OpenAI API keys)
load_dotenv()

# Initialize LLM using Groq (Ensure your API key is set in the environment)
llm = LLM(model="groq/llama-3.1-8b-instant")

# Define system prompts
user_interaction_prompt = """
You are a helpful assistant. Given a user's request, extract the main task or goal and return a clear description of it.
If the user gives multiple tasks, summarize them into one goal.
"""

subtask_generator_prompt = """
You are a task breakdown assistant. Given a task or goal, break it down into smaller, actionable subtasks.
If a subtask can be broken down further, do so iteratively. Stop if no further breakdown is needed.
"""

plan_evaluator_prompt = """
You are a plan evaluator. Given a list of subtasks, evaluate whether the plan is complete or needs improvement.
Check for missing steps. If the plan is good, return 'Plan is ready'. If not, suggest improvements.
"""

# Define Agents
user_interaction_agent = Agent(
    name="User Interaction Agent",
    role="Handles user input and extracts primary task",
    goal="Extract the main task from user input",
    backstory="An AI assistant designed to simplify user requests into clear tasks.",
    llm=llm,
    allow_delegation=True
)

subtask_generator = Agent(
    name="Subtask Generator",
    role="Breaks down main tasks into subtasks",
    goal="Generate clear and actionable subtasks iteratively",
    backstory="A highly efficient assistant for decomposing tasks",
    llm=llm,
    allow_delegation=True
)

plan_evaluator = Agent(
    name="Plan Evaluator",
    role="Evaluates the completeness of a task plan",
    goal="Ensure task plans are complete and ready for execution",
    backstory="An AI designed to check task plans for completeness and improvements.",
    llm=llm
)

# Define Tasks
user_interaction_task = Task(
    description="Extract the primary task from the user's input.",
    expected_output="A concise summary of the user's goal.",
    agent=user_interaction_agent,
    llm=llm,
    prompt=user_interaction_prompt
)

subtask_generator_task = Task(
    description="Break down the primary task into smaller subtasks iteratively.",
    expected_output="A detailed list of subtasks.",
    agent=subtask_generator,
    llm=llm,
    prompt=subtask_generator_prompt
)

plan_evaluator_task = Task(
    description="Evaluate the generated subtasks and suggest improvements if necessary.",
    expected_output="Either 'Plan is ready' or a list of improvements.",
    agent=plan_evaluator,
    llm=llm,
    prompt=plan_evaluator_prompt
)

# Create a Crew
crew = Crew(
    agents=[user_interaction_agent, subtask_generator, plan_evaluator],
    tasks=[user_interaction_task, subtask_generator_task, plan_evaluator_task],
    manager_llm=llm
)

# Orchestrate the process
def orchestrate_event(user_input):
    print(f"Processing User Input: {user_input}")

    # Step 1: Handle user input
    primary_task = user_interaction_agent.execute_task(user_interaction_task)
    print(f"Primary Task Identified: {primary_task}")

    # Step 2: Generate subtasks
    subtasks = subtask_generator.execute_task(subtask_generator_task)
    print(f"Generated Subtasks: {subtasks}")

    # Step 3: Evaluate the plan
    evaluation = plan_evaluator.execute_task(plan_evaluator_task)
    print(f"Plan Evaluation: {evaluation}")

    # Step 4: Final output
    if "Plan is ready" in evaluation:
        return f"Plan is complete and ready: {subtasks}"
    else:
        return f"Plan needs improvement: {evaluation}"

# Example User Input
user_input = "Plan a birthday party"
final_plan = orchestrate_event(user_input)
print(final_plan)

# Run CrewAI execution
crew.kickoff()
