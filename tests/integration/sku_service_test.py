import unittest

from datetime import date

from tests.helper.environemnt_helper import prepare_new_test_env
from tests.helper.file_helper import get_file_path
from tests.helper.assert_helper import assert_as_jsons
from src.ioc import sku_service
from src.ioc import sku_storage
from src.app.mp.mp_entities import SkuFilter, Sku


class SkuServiceIntegrationTest(unittest.TestCase):
    def setUp(self):
        """Prepare fresh test environment before each test"""
        prepare_new_test_env()

    def test_process_file_stores_skus(self):
        # given
        prepare_new_test_env()
        csv_path = get_file_path("files/test_skus.csv")

        # when
        sku_service.process_file(str(csv_path))

        # then
        stored_skus = sku_storage.get_all_skus()
        self.assertEqual(1, len(stored_skus))
        assert_as_jsons("files/expected_sku.json", stored_skus[0])

    def test_process_stores_only_unique_skus(self):
        # given
        prepare_new_test_env()
        csv_path = get_file_path("files/test_skus.csv")

        # when
        sku_service.process_file(str(csv_path))
        sku_service.process_file(str(csv_path))

        # then
        stored_skus = sku_storage.get_all_skus()
        self.assertEqual(1, len(stored_skus))

    def test_save_and_retrieve_sku_filter(self):
        # given
        prepare_new_test_env()
        test_filter = SkuFilter(
            category="Test Category", start_date=date(2025, 1, 1), end_date=date(2025, 12, 31)
        )

        # when
        sku_service.save_sku_filter(test_filter)

        # then
        actual_filter = sku_service.get_sku_filter()
        self.assertEqual(actual_filter.category, "Test Category")
        self.assertEqual(actual_filter.start_date, date(2025, 1, 1))
        self.assertEqual(actual_filter.end_date, date(2025, 12, 31))

    def test_filter_skus_by_category_and_date(self):
        # given - create test SKUs
        prepare_new_test_env()
        sku1 = Sku(
            number="SKU001", category="Electronics", revenue_by_day={date(2025, 1, 15): 100.0}
        )
        sku2 = Sku(number="SKU002", category="Clothing", revenue_by_day={date(2025, 2, 15): 200.0})
        sku3 = Sku(
            number="SKU003", category="Electronics", revenue_by_day={date(2025, 3, 15): 300.0}
        )

        # store test SKUs
        sku_storage.save(sku1)
        sku_storage.save(sku2)
        sku_storage.save(sku3)

        test_filter = SkuFilter(
            category="Electronics", start_date=date(2025, 3, 1), end_date=date(2025, 3, 31)
        )
        sku_service.save_sku_filter(test_filter)

        # when
        filtered_skus = sku_service.get_filtered_skus()

        # then
        self.assertEqual(1, len(filtered_skus))
        self.assertEqual("SKU003", filtered_skus[0].number)

    def test_merge_skus(self):
        # given
        prepare_new_test_env()
        sku1 = Sku(
            number="123",
            name="Product A",
            brand="Brand X",
            revenue_by_day={date(2024, 3, 1): 100, date(2024, 3, 5): 200},
            sales_by_day={date(2024, 3, 2): 5},
            price_by_day={date(2024, 3, 1): 20.0}
        )

        sku2 = Sku(
            number="123",
            name="Product A Updated",
            brand="Brand X",
            revenue_by_day={date(2024, 3, 2): 150, date(2024, 3, 10): 300},
            sales_by_day={date(2024, 3, 10): 8},
            price_by_day={date(2024, 3, 5): 22.0}
        )

        # when
        merged_sku = sku_service.merge_sku(sku1, sku2)

        # Check that single-value fields come from the latest SKU
        self.assertEqual(merged_sku.name, "Product A Updated")

        # Check merged dictionary fields
        expected_revenue = {
            date(2024, 3, 1): 100,
            date(2024, 3, 5): 200,
            date(2024, 3, 2): 150,
            date(2024, 3, 10): 300
        }
        self.assertEqual(merged_sku.revenue_by_day, expected_revenue)

        expected_sales = {date(2024, 3, 2): 5, date(2024, 3, 10): 8}
        self.assertEqual(merged_sku.sales_by_day, expected_sales)

        expected_prices = {date(2024, 3, 1): 20.0, date(2024, 3, 5): 22.0}
        self.assertEqual(merged_sku.price_by_day, expected_prices)

if __name__ == "__main__":
    unittest.main()
