import unittest
from unittest.mock import patch

from src.app.register.data_analyst import analyze_task
from src.app.register.postprocessor import PostProcessorResponse
from tests.helper.environemnt_helper import prepare_new_test_env


class DataAnalystTest(unittest.TestCase):

    def test_analyze_task_success(self):
        # given
        prepare_new_test_env()
        user_question = "Get total sales for 2023"

        # when
        actual_result = analyze_task(user_question)

        expected_response = PostProcessorResponse.model_construct(
            explanations_and_details="Mocked business analyst response"
        )

        # then
        assert actual_result == expected_response

    @patch("src.config.config.is_test", return_value=False)
    @patch(
        "src.app.register.data_analyst.do_analyze_task",
        side_effect=[
            (PostProcessorResponse.model_construct(explanations_and_details="Bad answer"), []),
            (PostProcessorResponse.model_construct(explanations_and_details="Good answer"), []),
        ],
    )
    @patch("src.app.register.data_analyst.is_good_answer", side_effect=[False, True])
    def test_analyze_task_retries_if_answer_bad(
        self, mock_is_good_answer, mock_do_analyze_task, mock_is_test
    ):
        # given
        user_question = "Unclear question?"

        # when
        actual_result = analyze_task(user_question)

        # then
        self.assertIsNotNone(actual_result)
        self.assertEqual(actual_result.explanations_and_details, "Good answer")

        self.assertEqual(mock_do_analyze_task.call_count, 2)

    @patch("src.config.config.is_test", return_value=False)
    @patch("src.app.register.data_analyst.do_analyze_task", side_effect=Exception("Test error"))
    def test_handles_exception(self, mock_do_analyze_task, mock_is_test):
        # given
        user_question = "Invalid input causing failure"

        # when
        actual_result = analyze_task(user_question)

        # then
        self.assertEqual(actual_result.explanations_and_details, "Failed to answer")
