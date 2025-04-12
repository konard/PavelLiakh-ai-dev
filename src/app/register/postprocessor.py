import json

from src.infrastructure import file_helper
from src.infrastructure.ai.prompt import Prompt
from src.app.register.entities import UserRequest, PostProcessorResponse
from src.ioc import llm_client, log
from datetime import datetime


default_format_instructions = """
"Use default format for answer, when nothing requested by user:"
            "1. Start with the answer."
            "2. Describe the way (and/or data if needed) how this result achieved."
            "*. Follow user-friendly warm very professional response style."
            "*. You MUST NOT analyze the data: provide ONLY exact answer and exact way how it was achieved."
"""


def postprocess_answer(
    user_data: str, user_request: UserRequest, data_plan: str
) -> PostProcessorResponse:
    example = file_helper.get_content("files/data_analyst_example.txt")
    example2 = file_helper.get_content("files/data_analyst_example_2.txt")
    prompt = Prompt(
        role="User response builder.",
        task="Analyze provided details and build an response adequate for the user question. "
        "Softly engage user into conversation.",
        context=[
            f"Data-retriever response: {user_data}",
            f"Data Planner findings: {data_plan}",
            f"User-defined response requirements: {user_request.format_requirements}",
            "User is a business person, not a technician.",
        ],
        instructions=[
            "Do double check.",
            "Strictly follow user-defined response requirements.",
            (
                default_format_instructions
                if not user_request.format_requirements
                else user_request.format_requirements
            ),
            "Response is always formed in a user language.",
            """
            Be honest when preparing the response: it means use only the provided data must be used and data must not be imagined or generated.
            """,
            "Do not include technical stuff like code, or technical messages.",
            "If there is list, then do format it as a list - not like a plain text. Same for table data.",
        ],
        examples=[
            example,
            """
                  Example of the short response. Context: { format requirements: shortest answer possible, no explanations needed; question: средний чек; Total sum: 145655512; Amount: 100; Средний чек: 1456555.12; (other details...) }
                  User response builder: 1456555.12
                  """,
            example2,
        ],
    )
    response = llm_client.generate_response(
        prompt.to_str(), user_request.user_question, PostProcessorResponse
    )

    result = PostProcessorResponse(**json.loads(response))
    if result.concrete_answer and "nan" == result.concrete_answer:
        result.concrete_answer = "0"
    return result


# FIXME move to separate guardrails module
def is_good_answer(user_request: str, response: str) -> bool:
    prompt = Prompt(
        role="You are guardian of the User answer quality.",
        task="Check if the answer is good enough for sending to the user.",
        context=[
            f"User Request: {user_request}",
            f"Response: {response}",
            f"Current datetime: {datetime.now()}",
        ],
        instructions=[
            "Do double check.",
            "Check if response answers user question.",
            "Check that response does not contain weird not-human friendly stuff.",
            "Check that response is not too technical.",
        ],
        examples=[
            """
            Case# Good answer.
            Question: процент отмененных продаж.
            Answer: Процент отмененных продаж составляет 51.00%.
            Result: True 
            """,
            """
            Case# Bad answer contains technical code.
            Question: процент отмененных продаж.
            Answer: Формула для расчета выглядит следующим образом: \[ \text{Процент отмененных продаж} = \left( \frac{\text{Количество отмененных заказов}}{\text{Количество отмененных заказов} + \text{Количество выполненных заказов}} \right) \times 100 \]
            Result: False
            """,
            """
            Case# Bad answer contains contradictive information.
            Answer: К сожалению, у меня нет данных о продажах за 2 января. Однако я могу предоставить информацию о продажах за 2 января.
            Result: False
            """,
            """
            Case# Bad answer does not answer the question.
            Question: процент отмененных продаж за 2 января.
            Answer: К сожалению у меня нет данных о продажах за 2 января.
            Result: False
            """,
            """
            Case# Bad answer because reply syntax is not logical: number instead of noun
            Question: best employee of the month.
            Answer: 1012312
            Result: False
            Comment: Actual answer is an answer for question "what is the amount of money earned by the best employee of the month?" but not directly to the question.
            """,
        ],
        output="strictly True or False",
    )

    try:
        result = llm_client.generate_response(prompt.to_str(), response)
        return bool(result)
    except Exception as e:
        log.error(f"Failed to check answer quality: %s", e)
        try:
            result = llm_client.generate_response(prompt.to_str(), response)
            return bool(result)
        except Exception as e:
            log.error(f"Again failed to check answer quality: %s", e)
            return True
