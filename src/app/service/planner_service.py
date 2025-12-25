import json

from pydantic import BaseModel, Field

from src.app.domain.story import PLANNING_STATE
from src.app.service.code_repo_service import CodeRepoServise
from src.infrastructure.ai.llm_client import LlmClient
from src.infrastructure.ai.prompt import Prompt
from src.infrastructure.db.story_storage import StoryStorage


class Plan(BaseModel):
    plan: list[str] = Field(description="Steps to implement story.")


class PlannerService:
    def __init__(
        self,
        llm_client: LlmClient,
        story_storage: StoryStorage,
        code_repo_service: CodeRepoServise,
        log,
    ):
        self.llm_client = llm_client
        self.story_storage = story_storage
        self.code_repo_service = code_repo_service
        self.log = log

    def plan(self, story) -> Plan:
        story.state = PLANNING_STATE

        # Get repository file tree for context
        try:
            repo_tree = self.code_repo_service.get_files_tree()
            self.log.info("Successfully retrieved repository file tree")
        except Exception as e:
            self.log.error(f"Failed to retrieve repository file tree: {e}")
            repo_tree = "Repository structure not available"

        system_prompt = Prompt(
            role="Technical planner",
            task="Create a detailed development plan for implementing user story.",
            context=[
                "Do only what was asked.",
                "FYI all the CI/CD steps will be done outside of this conversation, so you must not mention them.",
                f"Repository structure:\n{repo_tree}",
            ],
            instructions=[
                "Be specific about files that need to be modified.",
                "Do order items from less-dependent to more-dependent. Each step will be checked by CI/CD pipeline.",
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
        plan = self.llm_client.generate_response(
            system_prompt.to_str(), user_request, Plan
        )

        self.log.info(f"Response from planner: {plan}")
        self.log.info(f"Generated plan for story #{story.number}: {plan.plan}")

        story.build_plan = plan.plan
        self.story_storage.save_story(story)

        return plan
