import time
import streamlit as st
from dotenv import load_dotenv
from crewai import Agent, Task, Crew, LLM
import graphviz

# Load environment variables
load_dotenv()

# Initialize LLMs
user_handling = LLM(model="groq/gemma2-9b-it")
subtasks = LLM(model="groq/llama-3.3-70b-versatile")
evaluate = LLM(model="groq/llama-3.1-8b-instant")
flowchart_generator = LLM(model="groq/llama-3.3-70b-versatile")

# Define system prompts
user_interaction_prompt = """
You are an AI agent tasked with helping users create an actionable plan for achieving their objectives.

1. **Verifying User Input**: Ensure the query is legally and ethically acceptable. Flag and reject any harmful, illegal, or unethical requests.
2. **Extracting Relevant Information**: Identify and extract the core objective, any constraints, resources, timelines, or additional details provided.
"""

subtask_generator_prompt = """
Your task is to break down the main objective into structured, manageable subtasks:

1. **Break Down the Objective**: Divide the primary goal into smaller, distinct subtasks.
2. **Iterate Until Tasks Are Non-Divisible**: Keep breaking tasks down until each is highly specific and actionable.
3. **Ensure Clarity and Feasibility**: Each subtask must be understandable, achievable, and relevant.
"""

plan_evaluator_prompt = """
Your task is to evaluate the action plan to ensure its effectiveness:

1. **Assess Task Relevance & Completeness**: Ensure all necessary steps are included, without unnecessary distractions.
2. **Evaluate Feasibility & Resources**: Confirm that steps are realistic within given constraints.
3. **Verify Task Order & Structure**: Ensure dependencies are correctly ordered.
"""

flowchart_generator_prompt = """
Your task is to generate a Graphviz DOT format flowchart representation of the task breakdown:

1. **Analyze Subtasks**: Convert the structured list of subtasks into a DOT format directed graph.
2. **Ensure Logical Progression**: Each subtask should be a node with connections indicating dependencies.
3. **Format Correctly**: Output should be valid DOT syntax that Graphviz can render.
"""
# Define Agents with 'backstory' added
user_interaction_agent = Agent(
    name="User Interaction Agent",
    role="Extracts primary task",
    goal="Understand user intent and summarize the task.",
    backstory="An expert in extracting and structuring user intent into a clear objective.",
    llm=user_handling
)

subtask_generator = Agent(
    name="Subtask Generator",
    role="Creates a step-by-step breakdown",
    goal="Generate structured subtasks iteratively.",
    backstory="A specialist in breaking down complex objectives into manageable subtasks.",
    llm=subtasks
)

plan_evaluator = Agent(
    name="Plan Evaluator",
    role="Checks completeness of the plan",
    goal="Ensure task plans are optimized and complete.",
    backstory="An AI focused on evaluating the feasibility and effectiveness of structured plans.",
    llm=evaluate
)

flowchart_generator = Agent(
    name="Flowchart Generator",
    role="Generates a Graphviz DOT flowchart",
    goal="Convert structured task breakdown into DOT format for visualization.",
    backstory="An expert in structuring workflows and representing them as flowcharts.",
    llm=flowchart_generator
)

# Define Agents
# user_interaction_agent = Agent(name="User Interaction Agent", role="Extracts primary task", goal="Understand user intent and summarize the task.", llm=user_handling)
# subtask_generator = Agent(name="Subtask Generator", role="Creates a step-by-step breakdown", goal="Generate structured subtasks iteratively.", llm=subtasks)
# plan_evaluator = Agent(name="Plan Evaluator", role="Checks completeness of the plan", goal="Ensure task plans are optimized and complete.", llm=evaluate)
# flowchart_generator = Agent(name="Flowchart Generator", role="Generates a Graphviz DOT flowchart", goal="Convert structured task breakdown into DOT format for visualization", llm=flowchart_generator)

# Define Tasks
user_interaction_task = Task(description="Extract the core task from user input.", expected_output="A clear and concise primary task.", agent=user_interaction_agent, llm=user_handling, prompt=user_interaction_prompt)
subtask_generator_task = Task(description="Break down the primary task into smaller steps.", expected_output="A structured list of subtasks.", agent=subtask_generator, llm=subtasks, prompt=subtask_generator_prompt)
plan_evaluator_task = Task(description="Evaluate the quality and completeness of the subtasks.", expected_output="Feedback on task breakdown and necessary improvements.", agent=plan_evaluator, llm=evaluate, prompt=plan_evaluator_prompt)
flowchart_generator_task = Task(description="Generate a Graphviz DOT flowchart representation of the task breakdown.", expected_output="A valid DOT formatted flowchart.", agent=flowchart_generator, llm=flowchart_generator, prompt=flowchart_generator_prompt)

# Create a Crew
crew = Crew(agents=[user_interaction_agent, subtask_generator, plan_evaluator, flowchart_generator], tasks=[user_interaction_task, subtask_generator_task, plan_evaluator_task, flowchart_generator_task], manager_llm=subtasks)

# Streamlit UI
st.title("Task Planner with Graphviz Flowchart Visualization")
user_input = st.text_area("Enter your task:")

if st.button("Generate Flowchart"):
    if user_input:
         # Execute User Interaction Agent to get primary task
        primary_task = user_interaction_agent.execute_task(user_interaction_task, context={"user_input": user_input})

        # Modify Subtask Generator Prompt with Primary Task Result
        subtasks_result = subtask_generator.execute_task(subtask_generator_task, context={"primary_task": primary_task})

        # Modify Plan Evaluator Prompt with Subtask Generator Result
        plan_evaluation_result = plan_evaluator.execute_task(plan_evaluator_task, context={"subtasks_result": subtasks_result})

        # Generate Flowchart with Subtask Generator and Plan Evaluator Results
        dot_flowchart = flowchart_generator.execute_task(flowchart_generator_task, context={"subtasks_result": subtasks_result, "plan_evaluation_result": plan_evaluation_result})

        # Show subtasks result in a text box
        st.text_area("Subtasks Breakdown", value=str(subtasks_result), height=200)

         # Display Flowchart
        st.write("📊 Flowchart Visualization:")
        st.graphviz_chart(dot_flowchart)
    else:
        st.warning("⚠️ Please enter a valid task.")
