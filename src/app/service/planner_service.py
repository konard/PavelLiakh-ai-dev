from src.infrastructure.ai.llm_client import LlmClient


class PlannerService:
    def __init__(self, llm_client: LlmClient, log):
        self.llm_client = llm_client
        self.log = log

    def plan(self, story) -> str:
        """Generate and commit a development plan for the story"""
        try:
            # Generate plan using LLM
            system_prompt = """You are a technical planner. Create a detailed development plan 
                            for implementing this story. Include steps for implementation, testing, 
                            and deployment. Be specific about files that need to be modified."""

            # plan_content = self.llm_client.generate_reasoned_response(
            #     system_prompt=system_prompt,
            #     user_prompt=f"Story: {story.name}\n\nDescription: {story.description}",
            # )
            plan_content = "Mocked plan"

            # Create branch
            branch_name = f"story-{story.number}"
            self.log.info(f"Creating branch {branch_name}")

            # Save plan to file
            plan_path = "plan.md"
            with open(plan_path, "w") as f:
                f.write(f"# Development Plan for Story {story.number}\n\n")
                f.write(plan_content)

            # Commit plan
            commit_message = f"Add development plan for story {story.number}"
            self.log.info(f"Committing plan for story {story.number}")

            # In a real implementation, we would use GitHandler from examples
            # For now returning mock commit hash
            return "mock_commit_hash"

        except Exception as e:
            self.log.error(f"Failed to create plan for story {story.number}: {str(e)}")
            raise
