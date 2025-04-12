import csv
import re
from datetime import datetime, date
from pathlib import Path
from typing import List, Dict

from src.infrastructure.logger import get_logger
from src.app.mp.mp_entities import Sku

log = get_logger(__name__)
# Basic fields
SKU_NUMBER_COLUMN = "SKU"
NAME_COLUMN = "Название"
NAME_COLUMN_2 = "Name"
BRAND_COLUMN = "Бренд"
BRAND_COLUMN_2 = "Brand"
CATEGORY_COLUMN = "Категория"
SELLER_COLUMN = "Продавец"
SELLER_COLUMN_2 = "Seller"
COLOR_COLUMN = "Цвет"
COLOR_COLUMN_2 = "Color"
SALES_NUMBER_COLUMN = "Продажи, кол-во"
SALES_NUMBER_COLUMN_2 = "Sales"
REVENUE_COLUMN = "Выручка"
REVENUE_COLUMN_2 = "Revenue"
PRICE_COLUMN = "Цена"
PRICE_COLUMN_2 = "Price"
WB_LINK_COLUMN = "Ссылка"
WB_LINK_COLUMN_2 = "URL"
PHOTO_LINK_COLUMN = "Фото"

# Time series patterns
DATE_PATTERN = re.compile(r"(\d{2}\.\d{2}\.\d{4})")
REVENUE_PATTERN = re.compile(DATE_PATTERN.pattern + r" Выручка")
REVENUE_PATTERN_2 = re.compile(DATE_PATTERN.pattern + r" Revenue")
SALES_PATTERN = re.compile(DATE_PATTERN.pattern + r" Продажи")
SALES_PATTERN_2 = re.compile(DATE_PATTERN.pattern + r" Sales")
PRICE_PATTERN = re.compile(DATE_PATTERN.pattern + r" Цена")
PRICE_PATTERN_2 = re.compile(DATE_PATTERN.pattern + r" Price")


class CsvParser:
    @staticmethod
    def parse_skus(filepath: str) -> List[Sku]:
        filepath = Path(filepath)
        if not filepath.exists():
            log.error(f"CSV file not found: {filepath}")
            raise FileNotFoundError(f"CSV file not found: {filepath}")

        skus = []
        with open(filepath, "r", newline="", encoding="utf-8-sig") as csvfile:
            lines = csvfile.readlines()
            total_lines = len(lines)
            log.info(f"Starting to parse {total_lines} lines from {filepath}")
            csvfile.seek(0)
            reader = csv.DictReader(csvfile, delimiter=";")

            fieldnames = reader.fieldnames
            if SKU_NUMBER_COLUMN not in fieldnames:
                raise ValueError(
                    f"CSV file must contain a '{SKU_NUMBER_COLUMN}' column. Actual headers: {fieldnames}"
                )

            # Get all time series columns
            revenue_columns = CsvParser._get_time_series_columns(fieldnames, REVENUE_PATTERN, REVENUE_PATTERN_2)
            sales_columns = CsvParser._get_time_series_columns(fieldnames, SALES_PATTERN, SALES_PATTERN_2)
            price_columns = CsvParser._get_time_series_columns(fieldnames, PRICE_PATTERN, PRICE_PATTERN_2)

            for i, row in enumerate(reader, 1):
                if i % 1000 == 0 or i == total_lines:
                    log.info(f"Processing row {i} of {total_lines}...")
                sku = CsvParser._row_to_sku(row, revenue_columns, sales_columns, price_columns)
                if sku:
                    skus.append(sku)

        log.info(f"Successfully parsed {len(skus)} SKUs from {filepath}")
        return skus

    @staticmethod
    def _extract_time_series(row: dict, columns: dict) -> Dict[date, float]:
        """Extract time series data from row using pattern"""
        series_data = {}
        for col, date_key in columns.items():
            value = row.get(col, "").replace(",", ".").strip()
            if value:
                try:
                    series_data[date_key] = float(value)
                except ValueError:
                    continue
        return series_data

    @staticmethod
    def _get_time_series_columns(fieldnames: list, *patterns: re.Pattern) -> Dict[str, date]:
        """Find all columns matching any of the given date patterns."""
        columns = {}
        for pattern in patterns:
            for col in fieldnames:
                if (match := pattern.match(col)):
                    date_key = datetime.strptime(match.group(1), "%d.%m.%Y").date()
                    columns[col] = date_key
        return columns

    @staticmethod
    def _row_to_sku(
            row: dict, revenue_columns: dict, sales_columns: dict, price_columns: dict
    ) -> Sku | None:
        """Convert CSV row to Sku object with all available fields, supporting column aliases."""
        sku_number = row.get(SKU_NUMBER_COLUMN, "").strip()
        if not sku_number:
            return None

        def get_first_non_empty(*keys: str) -> str | None:
            for key in keys:
                val = row.get(key, "").strip()
                if val:
                    return val
            return None

        sku = Sku(number=sku_number)

        # Basic info fields with aliases
        sku.name = get_first_non_empty(NAME_COLUMN, NAME_COLUMN_2)
        sku.brand = get_first_non_empty(BRAND_COLUMN, BRAND_COLUMN_2)
        sku.category = row.get(CATEGORY_COLUMN, "").strip() or None
        sku.seller = get_first_non_empty(SELLER_COLUMN, SELLER_COLUMN_2)
        sku.color = get_first_non_empty(COLOR_COLUMN, COLOR_COLUMN_2)

        # Numeric fields with type conversion and aliases
        try:
            sales_val = get_first_non_empty(SALES_NUMBER_COLUMN, SALES_NUMBER_COLUMN_2)
            sku.sales_number = int(sales_val) if sales_val else None
        except (ValueError, TypeError):
            sku.sales_number = None

        try:
            revenue_val = get_first_non_empty(REVENUE_COLUMN, REVENUE_COLUMN_2)
            sku.revenue = float(revenue_val.replace(",", ".")) if revenue_val else None
        except (ValueError, TypeError):
            sku.revenue = None

        try:
            price_val = get_first_non_empty(PRICE_COLUMN, PRICE_COLUMN_2)
            sku.price = float(price_val.replace(",", ".")) if price_val else None
        except (ValueError, TypeError):
            sku.price = None

        # Links
        sku.wb_link = get_first_non_empty(WB_LINK_COLUMN, WB_LINK_COLUMN_2)
        sku.photo_link = row.get(PHOTO_LINK_COLUMN, "").strip() or None

        # Time series data
        sku.revenue_by_day = CsvParser._extract_time_series(row, revenue_columns)
        sku.sales_by_day = {}
        sku.price_by_day = {}

        return sku
