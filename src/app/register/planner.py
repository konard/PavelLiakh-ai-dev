import json
from typing import List

from src.app.register.metadata import get_metadata
from src.infrastructure.ai.prompt import Prompt
from src.app.register.entities import UserRequest, DataCriteria
from src.infrastructure.db.glossary_store import GlossaryStore
from src.ioc import llm_client
from src.ioc import log


def plan_data_retrieve(user_request: UserRequest) -> DataCriteria:
    log.info("Plan data retrieve for user question: %s", user_request.user_question)
    metadata = get_metadata()

    # Get glossary context for relevant terms in the user's question
    glossary_context = build_context_glossary([user_request.user_question])
    prompt = Prompt(
        task="""
            1. Find if answer may be given using this data.
            2. Describe the selection criteria for answering to the user question. Do detect user question intent first.
            And if user question is ambiguous or unclear, do clearly write the assumptions you did to answer the question.
        """,
        role="You are data retriever planner. Data will be used in future for answering user question.",
        context=[
            f"UserData Metadata: {metadata}",
            f"Glossary Context: {glossary_context}" if glossary_context else "",
        ],
        instructions=[
            "Do double check every step.",
            "You work with any kind of data including financial, marketing, sales, etc."
            "Write the selection criteria as a numbered list of steps. E.g. \n1. Select all records by field X=x\n 2. Filter rows by condition Y=y etc.",
            "In case if there are more than one question, do write sequential instruction for getting all data to answer for each question one by one.",
            "Pay attention to the business nature of the question, because it may include complex financial relations.",
            "You have to analyze if it possible to answer the question using the data or your knowledge. "
            "Enough_data is negative only when it's implicitly clear. "
            "For example, if today is 2020 but user asked report for sales in 2030 year. Or he asks for illegal data e.g. poison creation.",
            "UserQuestion will be provided. This is most important what you need to use when preparing response.",
            "Do sort result by the main criteria (e.g. revenue, date, and so on), if applicable.",
        ],
        examples=[
            """
            Task: Group all success payments in 2024 year by owner.
            Example: \n1. Select all records by field Year=2024 and PaymentStatus=Success \n2. Group by Owner column.
            """
        ],
    )

    try:
        response = llm_client.generate_response(
            prompt.to_str(), user_request.user_question, DataCriteria
        )
        result = DataCriteria(**json.loads(response))
    except Exception as e:
        log.error("Failed to plan data retrieve: %s. One more attempt", e)
        response = llm_client.generate_response(
            prompt.to_str(), user_request.user_question, DataCriteria
        )
        result = DataCriteria(**json.loads(response))

    log.info("Plan data retrieve question: %s", response)
    return result


def build_context_glossary(topics: List[str]) -> str:
    """Build a glossary context string from relevant terms based on topics.

    Args:
        topics: List of topics from user request to find relevant glossary terms

    Returns:
        Formatted string with relevant glossary terms and definitions
    """
    glossary_store = GlossaryStore()
    glossary_text = glossary_store.get_formatted_glossary_text(topics)

    if not glossary_text:
        log.info("No glossary terms found for topics: %s", topics)
    return glossary_text
