from src.infrastructure.ai.llm_client import LLMClient


class PlannerService:
    def __init__(self, llm_client: LLMClient, log):
        self.llm_client = llm_client
        self.log = log

    def plan(self, story) -> str:
        # TODO implement
        # It must read the story description and ask the LLM to create a plan
        # It may use a tree of the repository as a context
        # Branch with a name of story number must be created
        # PR with a name of story number must be created
        # Plan must be saved to a plan.md in the root of the repository, commited and pushed to GH
        # Commit hash of the commit with a plan must be returned
        return ""