from datetime import date
from typing import Optional

from src.infrastructure.db.json_storage import MongoStorage
from src.app.mp.mp_entities import Sku, SkuFilter, DEFAULT_CATEGORY
from tinydb import Query


class SkuStorage:
    def __init__(self, storage: MongoStorage, log):
        self.storage = storage
        self.sku_db = self.storage.get_db("skus")
        self.filter_db = self.storage.get_db("sku_filters")
        self.log = log

    def insert_new_skus(self, new_skus: list[Sku]) -> None:
        """Inserts a collection of new SKUs in bulk."""
        if not new_skus:
            return
        self.sku_db.insert_multiple([sku.as_dict() for sku in new_skus])
        self.log.info(f"Inserted {len(new_skus)} new SKUs.")

    def save_updated_skus(self, updated_skus: list[Sku]) -> None:
        """Clears the existing collection and inserts updated SKUs in bulk, preserving IDs."""
        if not updated_skus:
            return
        self.sku_db.truncate()  # Remove all existing SKUs
        self.sku_db.insert_multiple([sku.as_dict() for sku in updated_skus])
        self.log.info(f"Updated {len(updated_skus)} SKUs.")

    def save(self, sku: Sku) -> Sku:
        saved_sku = self.storage.save_entity(
            db=self.sku_db, query=Query().number == sku.number, entity=sku, entity_class=Sku
        )

        return saved_sku

    def find_by_number(self, sku_number: str) -> Sku | None:
        query = Query()
        return self.storage._find_entity(
            db=self.sku_db, query=query.number == sku_number, entity_class=Sku
        )

    def count_all_skus(self) -> int:
        """Returns the total count of SKUs in the database."""
        return self.sku_db.count(Query().number.exists())

    def get_all_skus(self) -> list[Sku]:
        skus = []
        for sku_data in self.sku_db.all():
            # Convert time series data
            revenue_data = {
                date.fromisoformat(date_str): amount
                for date_str, amount in sku_data.get("revenue_by_day", {}).items()
            }
            sales_data = {
                date.fromisoformat(date_str): amount
                for date_str, amount in sku_data.get("sales_by_day", {}).items()
            }
            price_data = {
                date.fromisoformat(date_str): amount
                for date_str, amount in sku_data.get("price_by_day", {}).items()
            }

            sku = Sku(
                number=sku_data.get("number", ""),
                name=sku_data.get("name"),
                brand=sku_data.get("brand"),
                category=DEFAULT_CATEGORY,
                seller=sku_data.get("seller"),
                color=sku_data.get("color"),
                sales_number=sku_data.get("sales_number"),
                revenue=sku_data.get("revenue"),
                price=sku_data.get("price"),
                wb_link=sku_data.get("wb_link"),
                photo_link=sku_data.get("photo_link"),
                revenue_by_day=revenue_data,
                sales_by_day=sales_data,
                price_by_day=price_data,
                _id=sku_data.get("_id"),
            )
            skus.append(sku)

        return skus

    def clear_all_skus(self) -> None:
        self.sku_db.truncate()
        self.filter_db.truncate()
        self.log.info("Cleared all SKUs from storage")

    def get_sku_filter(self) -> Optional[SkuFilter]:
        """Get the first SKU filter from storage"""
        filters = self.filter_db.all()
        if filters:
            filter_data = filters[0]
            return SkuFilter(
                sku_number=filter_data.get("sku_number"),
                category=filter_data.get("category"),
                start_date=(
                    date.fromisoformat(filter_data["start_date"])
                    if filter_data.get("start_date")
                    else None
                ),
                end_date=(
                    date.fromisoformat(filter_data["end_date"])
                    if filter_data.get("end_date")
                    else None
                ),
            )
        return None

    def save_sku_filter(self, sku_filter: SkuFilter) -> None:
        """Save SKU filter to storage, replacing any existing filter"""
        self.filter_db.truncate()

        filter_data = {
            "sku_number": sku_filter.sku_number,
            "category": sku_filter.category,
            "start_date": sku_filter.start_date.isoformat() if sku_filter.start_date else None,
            "end_date": sku_filter.end_date.isoformat() if sku_filter.end_date else None,
        }
        self.filter_db.insert(filter_data)
        self.log.info("Saved SKU filter to storage")
