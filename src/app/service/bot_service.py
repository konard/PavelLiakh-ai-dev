from src.app.service.error_service import ErrorService
from src.infrastructure.ai.llm_client import LLMClient
from src.app.service.entities import Bot, ERROR_RESPONSE
from src.config import config


class BotService:
    def __init__(self, storage, log, llm_client: LLMClient, error_service: ErrorService):
        self.storage = storage
        self.log = log
        self.llm_client = llm_client
        self.error_service = error_service

    def find_bot_by_link(self, link) -> Bot:
        """Find the bot that received this message by its link"""
        bot = self.storage.find_bot_by_link(link)
        if bot:
            return bot
        self.log.error("No bot found for link: %s", link)
        raise ValueError("No bot found")

    def find_bot_for_message(self, message) -> Bot:
        """Find the bot that received this message by its link"""
        return self.find_bot_by_link(message.bot_link)

    def update_example_bot_behavior(self, behavior: str) -> str:
        """Update the example bot's behavior"""
        try:
            self.log.info("Updating example bot behavior with input: %s", behavior)

            # Pre-process the behavior with LLM
            system_prompt = """
            You are a system designed to create a well-structured system prompt for an AI assistant based on a users description of its behavior. Follow these guidelines:

            1. **Context**: Define the assistants purpose or intended use.
            2. **Role**: Specify the assistants role, including its expertise and behavior style.
            3. **Tone**: Set the tone and personality traits, if specified or implied.
            4. **Instructions**: Add specific rules, constraints, or examples provided by the user.

            Use the following format for the output:
            [Context: Brief overview of the assistant's purpose or function.]
            [Role: Description of the assistants role, expertise, and behavior style.]
            [Tone: Tone or personality traits, if applicable.]
            [Instructions: Detailed instructions or rules for the assistant to follow. Include any examples if provided.]

            Input: "{Users description of the assistants behavior}"
            Output: A system prompt formatted as specified.
            """
            processed_behavior = self.llm_client.generate_response(system_prompt, behavior)

            if not processed_behavior:
                raise ValueError("Failed to process behavior with LLM")

            example_bot = self.find_bot_by_link(config.example_bot_link)
            if not example_bot:
                raise ValueError("Example bot not found")

            example_bot.behaviour = processed_behavior
            self.storage.save_bot(example_bot)
            self.log.info("Example bot behavior updated successfully with processed behavior")
            return f"Bot is created. Follow @{config.example_bot_link}"
        except Exception as e:
            self.error_service.log_error(
                user_id="system",
                message=f"Behavior update attempt: {behavior}",
                error=e,
            )
            return ERROR_RESPONSE
