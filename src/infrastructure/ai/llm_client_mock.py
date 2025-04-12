from typing import Optional, NoReturn

actual_system_prompt = None
actual_user_prompt = None
predefined_response = None


def set_predefined_llm_response(response) -> NoReturn:
    """Set a predefined response to be returned by the mock."""
    global predefined_response
    predefined_response = response


def mock_llm_response(system_prompt: str, user_prompt: str) -> Optional[str]:
    global actual_system_prompt, actual_user_prompt, predefined_response
    actual_system_prompt = system_prompt
    actual_user_prompt = user_prompt
    if not predefined_response:
        raise AssertionError(
            "No predefined response for LLM set, but request expected. SystemPrompt=%s, UserPrompt=%s",
            system_prompt,
            user_prompt,
        )
    return predefined_response


def get_actual_system_prompt() -> str:
    """Get the actual system prompt."""
    return actual_system_prompt


def get_actual_user_prompt() -> str:
    """Get the actual user prompt."""
    return actual_user_prompt
