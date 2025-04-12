from pydantic import BaseModel

from src.infrastructure.ai.llm_client_mock import mock_llm_response
import openai
from openai import OpenAI

from src.config import config
from typing import Optional

client = OpenAI()

gpt_4o_mini = "gpt-4o-mini"
o1_mini = "o1-mini"
o3_mini = "o3-mini"


class LLMClient:
    def __init__(self, log, model: str = "gpt-4o-mini"):
        self.log = log
        self.model = model
        openai.api_key = config.openai_api_key

    def generate_reasoned_response(
        self, system_prompt: str = None, user_prompt: str = ""
    ) -> Optional[str]:
        """Generate a response using the o3-mini model with a reasoning-focused approach

        Args:
            user_prompt: The user's input message that requires reasoning

        Returns:
            The generated response or None if there was an error
        """
        if config.is_test():
            return mock_llm_response(
                "You are a helpful assistant that reasons step by step", user_prompt
            )

        question = user_prompt
        if system_prompt:
            question = f"Context: {system_prompt}. The question is: {user_prompt}"

        # Use the reasoning-focused prompt structure
        messages = [
            {"role": "user", "content": question},
            {"role": "assistant", "content": "Let's think step by step."},
        ]

        response = openai.chat.completions.create(model="o3-mini", messages=messages, temperature=1)
        return response.choices[0].message.content

    def generate_response(
        self,
        system_prompt: str,
        user_prompt: str,
        output_format: BaseModel = None,
        temperature: float = None,
        top_p: float = None,
    ) -> Optional[str]:
        """Generate a response using the configured LLM model or mock if in test environment

        Args:
            system_prompt: The system message that sets the behavior of the assistant
            user_prompt: The user's input message

        Returns:
            The generated response or None if there was an error
        """
        if config.is_test():
            return mock_llm_response(system_prompt, user_prompt)

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]

        if output_format:
            response = client.beta.chat.completions.parse(
                model=self.model, messages=messages, temperature=0.0, response_format=output_format
            )
        else:
            response = client.beta.chat.completions.parse(
                model=self.model, messages=messages, temperature=0.0
            )

        result = response.choices[0].message.content

        self.log.info(f"LLM request: {messages}\nLLM response: {result}")
        return result


# self-test
if __name__ == "__main__":
    import logging

    client = LLMClient(logging.getLogger("testllmclient"))
    # response = client.generate_response("Hello", "How are you?")
    # print(response)
    response = client.generate_reasoned_response("What is the capital of France?")
    print(response)
