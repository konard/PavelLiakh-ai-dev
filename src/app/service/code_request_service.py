import json

from pydantic import BaseModel, Field
from src.infrastructure.ai.llm_client import LlmClient
from src.infrastructure.ai.prompt import Prompt
from src.infrastructure.db.story_storage import StoryStorage


class CodeFiles(BaseModel):
    files: dict[str, str] = Field(description="Generated code from LLM.")


class CodeRequestService:
    def __init__(self, llm_client: LlmClient, story_storage: StoryStorage, log):
        self.llm_client = llm_client
        self.story_storage = story_storage
        self.log = log

    def implement(self, story) -> dict[str, str]:
        system_prompt = Prompt(
            role="Senior software engineer",
            task="Implement the provided development plan into complete, production-ready code.",
            context=[
                "Provide only the code necessary to fulfill the provided plan.",
                "CI/CD steps, explanations, and code reviews are handled separately, do not include them.",
            ],
            instructions=[
                "Provide the complete source code for each file separately.",
                "Specify filenames explicitly.",
                "Default programming language is Python unless otherwise specified.",
            ],
        )

        user_request = f"Story: {story.name}\n\nPlan:\n" + "\n".join(story.plan)
        response = self.llm_client.generate_response(
            system_prompt.to_str(), user_request, CodeFiles
        )

        self.log.info(f"Code implementation response: {response}")

        code_files = response.files

        self.log.info(
            f"Generated code files for story #{story.number}: {list(code_files.keys())}"
        )

        story.code_files = code_files
        self.story_storage.save_story(story)

        return code_files
