import json

from src.infrastructure.ai.prompt import Prompt
from src.app.register.entities import UserRequest
from src.ioc import llm_client, glossary
from src.ioc import log


def preprocess_question(user_question_text: str) -> UserRequest:
    log.info(f"Analyzing user question: %s", user_question_text)
    prompt = Prompt(
        role="User question pre-processor.",
        task="1. Analyze user question. "
        "2. Populate topics mentioned by user from the Available Topics list. "
        "3. Detect user language.",
        context=[f"Available Topics: {glossary.get_all_terms()}"],
        instructions=[
            "Always do double check.",
            """
            Extract required information from user question. No need to imagine or guess any details.
            - Reduce not meaningful information like e.g. language-specific words 'please' or 'kindly'.
            """,
        ],
        examples=[
            """
            "user_question": "хочу знать какой cредний чек И маржу И погоду. "
            "Available Topics": ["Средний чек", "Маржа"]."
            {
            "preprocess": {
                "format_requirements": "",
                "user_question": "Какой средний чек? Какая маржа? Какая погода?",
                "language": "russian",
                "topics": ["Средний чек", "Маржа"]
                }
            }
            """
        ],
    )

    try:
        response = llm_client.generate_response(prompt.to_str(), user_question_text, UserRequest)
        result = UserRequest(**json.loads(response))
    except Exception as e:
        log.error("Failed to preprocess user question: %s. One more attempt", e)
        response = llm_client.generate_response(prompt.to_str(), user_question_text, UserRequest)
        result = UserRequest(**json.loads(response))

    log.info("Preprocessed user question: %s", response)
    return result


if __name__ == "__main__":
    user_question_text = "What is the capital of France?"
    result = preprocess_question(user_question_text)
    print(f"Request: {user_question_text},\n Response: {result}")
