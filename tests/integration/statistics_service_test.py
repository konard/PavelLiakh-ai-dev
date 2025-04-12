import unittest
from datetime import date

from src.app.mp.mp_entities import SkuFilter
from tests.helper.assert_helper import assert_as_jsons
from tests.helper.environemnt_helper import prepare_new_test_env
from tests.helper.file_helper import get_file_path
from src.ioc import sku_service, statistics_service


class StatisticsServiceIntegrationTest(unittest.TestCase):
    def setUp(self):
        prepare_new_test_env()

    def test_get_min_date_returns_earliest_date(self):
        # given
        prepare_new_test_env()
        csv_path = get_file_path("files/test_skus.csv")
        sku_service.process_file(str(csv_path))

        # when
        min_date = statistics_service.git_min_date()

        # then
        self.assertEqual(min_date, date(2025, 2, 8))

    def test_find_top_by_revenue_returns_correct_order(self):
        # given
        prepare_new_test_env()
        csv_path = get_file_path("files/top_skus_test.csv")
        sku_service.process_file(str(csv_path))

        # when
        top_skus = statistics_service.find_top_by_revenue(top_n=1)

        # then
        self.assertEqual(1, len(top_skus))
        self.assertEqual("444444444", top_skus[0].number)

    def test_report_top_10_revenue_with_current_sku(self):
        # given
        prepare_new_test_env()
        csv_path = get_file_path("files/report_10_revenue_skus_test.csv")
        sku_service.process_file(str(csv_path))

        # when
        filter = SkuFilter(
            sku_number="61134", category="Electronics", start_date=date(2025, 2, 9), end_date=date(2025, 2, 28)
        )
        actual_report = statistics_service.report_top_market_share_with_current_sku(filter, top_n=10)

        # then
        assert_as_jsons("files/expected_report_10_revenue_skus_test.json", actual_report)

    def test_get_revenue_time_series_for_plot(self):
        # given
        prepare_new_test_env()
        csv_path = get_file_path("files/report_market_share_test.csv")
        sku_service.process_file(str(csv_path))

        # when
        filter = SkuFilter(
            sku_number="61134", 
            category="Electronics", 
            start_date=date(2024, 1, 1), 
            end_date=date(2024, 3, 28)
        )
        result = statistics_service.get_revenue_time_series_for_plot(filter)

        # then
        self.assertIn("dates", result)
        self.assertIn("current_sku", result)
        self.assertIn("top_sku", result)
        self.assertIn("total", result)
        self.assertEqual(result["current_sku"]["number"], "61134")
        self.assertEqual(len(result["dates"]), len(result["current_sku"]["values"]))
        self.assertEqual(len(result["dates"]), len(result["top_sku"]["values"]))
        self.assertEqual(len(result["dates"]), len(result["total"]["values"]))

    def test_report_market_share(self):
        # given
        prepare_new_test_env()
        csv_path = get_file_path("files/report_market_share_test.csv")
        sku_service.process_file(str(csv_path))

        # when
        filter = SkuFilter(
            sku_number="61134", category="Electronics", start_date=date(2024, 1, 1), end_date=date(2024, 3, 28)
        )
        actual_report = statistics_service.report_top_market_share_with_current_sku(filter, top_n=10)

        # then
        assert_as_jsons("files/report_market_share_test.json", actual_report)

    def test_get_revenue_time_series_with_report_10_data(self):
        # given
        prepare_new_test_env()
        csv_path = get_file_path("files/report_10_revenue_skus_test.csv")
        sku_service.process_file(str(csv_path))

        # when
        filter = SkuFilter(
            sku_number="61134",
            category="Electronics",
            start_date=date(2025, 2, 8),
            end_date=date(2025, 2, 10)
        )
        result = statistics_service.get_revenue_time_series_for_plot(filter)

        # then
        assert_as_jsons("files/expected_revenue_time_series.json", result)


if __name__ == "__main__":
    unittest.main()
