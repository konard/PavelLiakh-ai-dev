from typing import Optional

from pydantic import BaseModel, Field


class UserRequest(BaseModel):
    format_requirements: str = Field(
        description="Optional. Requirements for response format IF ANY. Otherwise empty string."
    )
    user_question: str = Field(
        description="User question or questions in a strict format. Questions formatted as numbered list in BUT only in case of multiple questions."
    )
    language: str = Field(description="User language example: russian, example: english")
    topics: list[str] = Field(description="Topics mentioned")


class DataCriteria(BaseModel):
    enough_data: bool = Field(
        description="If data is enough to answer the question. Default is True. Only implicit lack of data can lead to the answer False.",
    )
    retrieve_plan: Optional[str] = Field(
        description="If enough data, the plan to retrieve it. Otherwise, the explanation what data is missing."
    )


class PostProcessorResponse(BaseModel):
    concrete_answer: str = Field(
        description="Contains an exact match to the requested data or approximation or interpretation. "
        "The most short and precise answer. "
        "Just one word(s) or number(s) that can answer the question. "
        "Use comma as a delimiter for multiple answers."
        "This field is required for strict assertion of the answer in tests. "
        "By-default value is 0, when its not possible to get concrete value (not 'nan')."
    )
    explanations_and_details: str = Field(
        description="The processed response text to be shown to the user"
    )
