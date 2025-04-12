import unittest

from src.app.register.entities import UserRequest
from src.app.register.planner import plan_data_retrieve
from src.infrastructure.ai.llm_client_mock import (
    set_predefined_llm_response,
)
from tests.helper.assert_helper import assert_equals
from tests.helper.environemnt_helper import prepare_new_test_env


class PlannerIntegrationTest(unittest.TestCase):

    def test_planner(self):
        # given
        prepare_new_test_env()
        set_predefined_llm_response(
            '{"enough_data": true, "retrieve_plan": "Retrieve sales data for 2023 and sum total sales."}'
        )

        user_request = UserRequest(
            user_question="Get total sales for 2023",
            format_requirements="",
            language="english",
            topics=["Когортный анализ"],
        )

        # when
        actual_result = plan_data_retrieve(user_request=user_request)
        actual_result = actual_result.retrieve_plan

        # then
        assert_equals("Retrieve sales data for 2023 and sum total sales.", actual_result)
