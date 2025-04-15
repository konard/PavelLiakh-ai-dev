import json
from tkinter.scrolledtext import example

from pydantic import BaseModel, Field

from src.infrastructure.ai.llm_client import LlmClient
from src.infrastructure.ai.prompt import Prompt


class Plan(BaseModel):
    plan: list[str] = Field(description="Steps to implement story.")


class PlannerService:
    def __init__(self, llm_client: LlmClient, log):
        self.llm_client = llm_client
        self.log = log

    def plan(self, story) -> Plan:
        system_prompt = Prompt(
            role="Technical planner",
            task="Create a detailed development plan for implementing user story.",
            context=[
                "Do only what was asked."
                "FYI all the CI/CD steps will be done by the outside of this conversation, so you must not mention them."
            ],
            instructions=[
                "Be specific about files that need to be modified."
                "Do order items from less-dependent to more-dependent. Each step will be checked by CI/CD pipeline."
                "Use python if not said otherwise. It means default language is python.",
            ],
            examples=[
                """
                User story: 
                I want to refactor my code to remove not used functions.
                file service.py: <service logic follows. It calls z() function from myfuncs>. 
                file myfuncs.py: <file content follows with x(), y(), z()>.
                Response:
                1. Remove function x() from file `myfuncs.py`
                2. Remove function y() from file `myfuncs.py`
                """
            ],
        )
        user_request = f"Story: {story.name}\n\nDescription: {story.description}"
        response = self.llm_client.generate_response(system_prompt.to_str(), user_request, Plan)

        self.log.info(f"Response from planner: {response}")
        plan = Plan(**json.loads(response))
        self.log.info(f"Generated plan for story {story.number}: {plan.plan}")

        return plan
