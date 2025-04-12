from dataclasses import dataclass
from datetime import datetime
from typing import Any

from src.app.register.entities import UserRequest, DataCriteria
from src.infrastructure.ai.prompt import Prompt
from src.infrastructure.pandas_executor import PandasScriptExecutor
from src.ioc import llm_client, log

pandas_executor = PandasScriptExecutor()
attempts = 6


@dataclass
class RetrieveAttempt:
    success: bool
    response: str
    error: str
    code: str

    def to_dict(self):
        return {
            "success": self.success,
            "response": self.response,
            "error": self.error,
            "code": self.code,
        }


pandas_script_header = """
import pandas as pd

file_path = r"{FILEPATH}"
df = pd.read_csv(file_path)
"""


def retrieve_data(
    file_path: str, metadata: str, user_request: UserRequest, data_criteria: DataCriteria
) -> tuple[str, Any]:
    """
    Retrieve data from a file and returns data OR error.
    """
    # FIXME metadata must be retrieved here
    debug_info = []

    now = datetime.now()
    log.info(f"Retrieving data from file: {file_path}")

    prompt = Prompt(
        role="You are a Python developer who is tasked with writing Pands code to retrieve and analyze data.",
        context=[
            f"Current datetime: {now}. This is the real current date and time. Use it, or imagine today that Current datetime is an actual one.",
            f"Metadata: {metadata}",
            f"Data Criteria: {data_criteria.retrieve_plan}",
            f"First lines of code already here: pandas import, file read to dataframe. So that don't add them.",
            f"Dataframe variable: df",
        ],
        task="Build pandas script to retrieve user data from the data file.",
        instructions=[
            "Do double check.",
            "If result is a data dataframe, then return it in a table format.",
            "Return ONLY THE CODE. Do put comments if any explanation is needed.",
            "Use Data frame as a single possible data source. It is already available in `df` variable. You must trust me and no need to do any assumption on that - it is true by-default.",
            "Use data plan as plan for data retrieval.",
            "Start and end date must always be printed after main result print",
            "Add the whole record itself with field names as a map, if result is one concrete data record.",
        ],
        examples=[
            """
            myvar = df["A"].mean()
            print(f"Average A: {myvar}")
            """,
            """
            Фильтрация по значениям скидки
            Пример: Выбрать заказы, где скидка больше 20%.
            high_discount_orders = df[df['discount'] > 20]
            print(high_discount_orders)
            """,
        ],
    )

    last_attempt = None
    for i in range(attempts):
        attempt = retrieve_attempt(prompt, file_path, last_attempt)
        debug_info.append(attempt.to_dict())
        last_attempt = attempt
        if attempt.success:
            log.info(f"User data retrieve attempt#{i} succeeded. Result={attempt.response}")
            return attempt.response, debug_info
        else:
            log.error(f"Attempt#{i}  failed: {attempt.error}")
    log.warn(f"Failed to retrieve data after {attempts} attempts.")
    return (
        f"Failed to retrieve user data. Error: {last_attempt.error}"
        if last_attempt
        else "Failed to retrieve user data."
    ), debug_info


def retrieve_attempt(
    prompt: Prompt, file_path: str, previous_attempt: RetrieveAttempt = None
) -> RetrieveAttempt:
    """
    Attempts to retrieve data based on a prompt.
    Returns:
        success: bool - True if successful, False otherwise.
        response: str - The output of the attempt.
        error: str - The error message if any.
    """

    if previous_attempt:
        current_situation = (
            f"\nImportant: Previous attempt failed. "
            f"\nCurrently, code execution fails with an error: {previous_attempt.error}. "
            f"\nThe code: {previous_attempt.code}"
            f"\nPlease give only new code with errors fixed."
        )
    else:
        current_situation = "Give me the code"

    pandas_code = llm_client.generate_response(prompt.to_str(), current_situation)

    log.info(f"Generated code: {pandas_code}")
    out, err = pandas_executor.execute(
        pandas_script_header.replace("{FILEPATH}", file_path) + pandas_code
    )
    success = not err
    log.info(f"Success: {success}, stdout: {out}, stderr: {err}")

    return RetrieveAttempt(success=success, response=out, error=err, code=pandas_code)
