import json
from dataclasses import dataclass
from typing import Optional

from pydantic import BaseModel, Field

from src.infrastructure.ai.llm_client import LlmClient

class Plan(BaseModel):
    plan: list[str] = Field(
        description="Steps to implement story."
    )


class PlannerService:
    def __init__(self, llm_client: LlmClient, log):
        self.llm_client = llm_client
        self.log = log

    def plan(self, story) -> Plan:
        system_prompt = """You are a technical planner. Create a detailed development plan 
                        for implementing this story. Include steps for implementation, testing, 
                        and deployment. Be specific about files that need to be modified."""
        user_prompt = f"Story: {story.name}\n\nDescription: {story.description}"
        response = self.llm_client.generate_response(system_prompt, user_prompt, Plan)
        plan = Plan(**json.loads(response))

        self.log.info(f"Generated plan for story {story.number}: {plan.plan}")
        return plan