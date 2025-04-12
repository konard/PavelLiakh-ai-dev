import time
from src.ioc import google_sheet_parser
from src.app.register.data_analyst import analyze_task

interval_seconds = 4  # Polling interval, seconds.
# Parameters

from src.ioc import log

parser = google_sheet_parser


def calculate_value(value_name: str) -> str:
    """Function to process the value."""
    log.info(f"Calculating value for {value_name}")
    task = f"Find the value for {value_name}. "
    value = analyze_task(task)
    log.info(f"Value for {value_name} is {value.concrete_answer}")
    return value.concrete_answer


def update_indicators():
    indicator_questions = parser.get_column_data()

    if indicator_questions:
        parser.update_indicators(indicator_questions, calculate_value)


def start_indicator_process():
    """
    Polls the spreadsheet for a given number of requests and writes updated values to the adjacent column.
    Also initializes and saves the source cell cache to a file.
    """
    while True:
        print("Polling spreadsheet...")
        try:
            update_indicators()
        except Exception as e:
            log.error(f"Failed to update table: %s", e)
        time.sleep(interval_seconds)


if __name__ == "__main__":
    start_indicator_process()
