from functools import lru_cache
from typing import List, Optional
from datetime import date
from src.app.mp.mp_entities import Sku, SkuFilter
from src.infrastructure.db.sku_storage import SkuStorage
from src.app.mp.csv_parser import CsvParser
from src.config import config
from copy import deepcopy


class SkuService:
    def __init__(self, storage: SkuStorage, log):
        self.storage = storage
        self.log = log

    def get_sku_category(self, sku_number: str) -> Optional[str]:
        sku = self.storage.find_by_number(sku_number)
        if sku:
            return sku.category

        return None

    def read_file(self, filepath: str) -> List[Sku]:
        csv_parser = CsvParser()
        skus = csv_parser.parse_skus(filepath)
        return skus

    def process_file(self, filepath: str) -> List[Sku]:
        """Process a CSV file of SKUs with progress logging"""
        skus = self.read_file(filepath)
        total = len(skus)
        saved_skus_count = 0

        self.log.info(f"Start storing SKUs to database. Count={len(skus)}")
        for i, sku in enumerate(skus, 1):
            self.storage.save(sku)
            saved_skus_count += 1

            # Log progress every 100 SKUs or on last item
            if i % 100 == 0 or i == total:
                progress = f"Stored {i}/{total} SKUs"
                # Use carriage return to overwrite previous line
                self.log.info(f"\r{progress}", extra={"end": "" if i < total else "\n"})

        self.log.info(f"Successfully processed {saved_skus_count}/{total} SKUs")

    def get_all_skus(self):
        return self.storage.get_all_skus()

    def count_all_skus(self):
        """Returns the total count of SKUs in the database."""
        return self.storage.count_all_skus()

    def get_sku_filter(self) -> SkuFilter:
        """Get the current SKU filter from storage"""
        return self.storage.get_sku_filter() or SkuFilter()

    def save_sku_filter(self, sku_filter: SkuFilter) -> SkuFilter:
        """Save SKU filter to storage"""
        self.storage.save_sku_filter(sku_filter)
        return sku_filter

    def find_by_number(self, sku_number: str) -> Optional[Sku]:
        """Find SKU by its number"""
        return self.storage.find_by_number(sku_number)

    def process_all_files(self) -> str:
        """Process all files in upload folder"""
        upload_folder = config.get_folder("uploads")
        files = sorted(upload_folder.glob("*"), key=lambda f: f.stat().st_mtime, reverse=True)
        if not files:
            return "No files to process"


        skus = []
        self.log.info(f"Found {len(files)} files to process in {upload_folder}")
        for i, file_path in enumerate(files):
            self.log.info(f"Processing file {i} of {len(files)}: {file_path.name} ")
            new_skus = self.read_file(str(file_path.resolve()))
            self.log.info(f"Found {len(new_skus)} SKUs in {file_path.name}")
            skus = self.merge_skus(skus, new_skus)
            self.log.info(f"Merged SKUs from {file_path.name}: {len(skus)} total SKUs")

        self.process_skus(skus)

    def process_skus(self, new_skus: list[Sku]) -> None:
        """Merges new SKUs with stored ones, splits them into new and updated SKUs, and inserts or updates them accordingly."""
        if not new_skus:
            self.log.info("No new SKUs to process.")
            return

        self.log.info(f"Processing {len(new_skus)} new SKUs...")
        new_skus_list, updated_skus_list = self.merge_and_split_skus(new_skus)
        self.log.info(f"New SKUs: {len(new_skus_list)}, Updated SKUs: {len(updated_skus_list)}")


        if updated_skus_list:
            self.storage.save_updated_skus(updated_skus_list)
            self.log.info(f"Updated  {len(updated_skus_list)} SKUs.")
        if new_skus_list:
            self.storage.insert_new_skus(new_skus_list)
            self.log.info(f"Inserted {len(new_skus_list)} new SKUs.")

    def merge_and_split_skus(self, new_skus: list[Sku]) -> tuple[list[Sku], list[Sku]]:
        """Reads stored SKUs, merges them with new_skus, and returns two lists: new and updated SKUs."""
        stored_skus = list(self.storage.get_all_skus())
        merged_skus = self.merge_skus(stored_skus, new_skus)

        new_skus_list = []
        updated_skus_list = []

        for sku in merged_skus:
            if sku.number not in stored_skus:
                new_skus_list.append(sku)
            else:
                updated_skus_list.append(sku)

        return new_skus_list, updated_skus_list

    def merge_skus(self, skus1: list[Sku], skus2: list[Sku]) -> list[Sku]:
        if not skus1 and not skus2:
            return []
        if not skus1:
            return skus2
        if not skus2:
            return skus1

        merged_skus = []
        sku_map = {sku.number: sku for sku in skus1 + skus2}

        for sku_number, sku in sku_map.items():
            other_sku = next((s for s in skus1 + skus2 if s.number == sku_number and s != sku), None)
            if other_sku:
                merged_skus.append(self.merge_sku(sku, other_sku))
            else:
                merged_skus.append(sku)

        return merged_skus

    def merge_sku(self, sku1: Sku, sku2: Sku) -> Sku:
        """Merge two SKUs, taking the latest SKU's values for single fields and merging dictionaries."""

        latest_sku = self.get_latest_sku(sku1, sku2)
        other_sku = sku1 if latest_sku == sku2 else sku2

        merged_sku = deepcopy(latest_sku)
        if (other_sku._id and not latest_sku._id):
            merged_sku._id = other_sku._id

        merged_sku.revenue_by_day = {**other_sku.revenue_by_day, **latest_sku.revenue_by_day}
        merged_sku.sales_by_day = {**other_sku.sales_by_day, **latest_sku.sales_by_day}
        merged_sku.price_by_day = {**other_sku.price_by_day, **latest_sku.price_by_day}

        return merged_sku

    def get_latest_sku(self, sku1: Sku, sku2: Sku) -> Sku:
        """Returns the SKU which has the latest data available."""

        def latest_date(sku: Sku) -> Optional[date]:
            """Finds the latest date present in revenue, sales, or price data."""
            all_dates = set(sku.revenue_by_day.keys()) | set(sku.sales_by_day.keys()) | set(sku.price_by_day.keys())
            return max(all_dates) if all_dates else None

        latest_date_1 = latest_date(sku1)
        latest_date_2 = latest_date(sku2)

        if latest_date_1 and latest_date_2:
            return sku1 if latest_date_1 > latest_date_2 else sku2
        elif latest_date_1:
            return sku1
        elif latest_date_2:
            return sku2
        else:
            return None  # Both SKUs have no date-based data

    @lru_cache(maxsize=1)
    def get_filtered_skus(self, sku_filter: Optional[SkuFilter] = None) -> List[Sku]:
        """Get SKUs filtered by current filter settings"""
        filter = sku_filter or self.get_sku_filter()
        all_skus = self.get_all_skus()

        filtered_skus = []
        for sku in all_skus:
            # Filter by date range if specified
            if filter.start_date or filter.end_date:
                min_date = filter.start_date or date.min
                max_date = filter.end_date or date.max

                # Only include SKUs with revenue data in the date range
                if any(min_date <= d <= max_date for d in sku.revenue_by_day.keys()):
                    filtered_skus.append(sku)
            else:
                filtered_skus.append(sku)

        return filtered_skus
