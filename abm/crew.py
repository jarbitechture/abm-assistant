from crewai import Crew, Agent, Task
from langchain_openai import ChatOpenAI
from abm.sales_copilot import summarize_deal_context
from dotenv import load_dotenv
import os

load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")

llm = ChatOpenAI(api_key=openai_api_key, model="gpt-4-turbo", temperature=0.3)

class TargetAccountCrew:
    def __init__(self, contact: dict):
        self.contact = contact

    def build(self):
        context_str = summarize_deal_context(self.contact)

        strategist = Agent(
            role="Sales Strategist",
            goal="Craft persuasive summaries for top ABM targets.",
            backstory="Expert in B2B positioning and ABM strategies.",
            verbose=True,
            llm=llm
        )

        analyst = Agent(
            role="Account Analyst",
            goal="Create structured contact and firmographic briefs.",
            backstory="Skilled in preparing detailed outreach data.",
            verbose=True,
            llm=llm
        )

        task1 = Task(
            description="Write a compelling ABM summary highlighting key advantages.",
            agent=strategist,
            expected_output="Detailed, persuasive ABM target summary.",
            context=[
                {
                    "description": "Enriched contact data",
                    "input": context_str,
                    "expected_output": "Clear understanding of the business advantages and positioning strategy for outreach."
                }
            ]
        )

        task2 = Task(
            description="Prepare a JSON brief with structured firmographic and contact details.",
            agent=analyst,
            expected_output="JSON brief with contact details and firmographics.",
            context=[
                {
                    "description": "Output from the ABM summary task",
                    "input": task1,
                    "expected_output": "Detailed ABM summary from the previous task."
                }
            ]
        )

        crew = Crew(
            agents=[strategist, analyst],
            tasks=[task1, task2],
            verbose=True
        )

        return crew, [task1, task2]
