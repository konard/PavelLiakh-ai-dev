from dataclasses import dataclass, field, asdict
from datetime import date
import json
from typing import Optional, Dict

DEFAULT_CATEGORY = "Одежда / Лонгсливы"

@dataclass
class SkuFilter:
    """Filter criteria for SKU queries"""

    _id: Optional[str] = None  # DB ID
    category: Optional[str] = DEFAULT_CATEGORY  # Category
    start_date: Optional[date] = None  # Start date
    end_date: Optional[date] = None  # End date
    sku_number: Optional[str] = None  # SKU number

    def __hash__(self):
        """Generate a unique hash using all attributes"""
        return hash((self._id, self.category, self.start_date, self.end_date, self.sku_number))


@dataclass
class Sku:
    number: Optional[str]  # SKU number
    name: Optional[str] = None  # Name
    brand: Optional[str] = None  # Brand
    category: Optional[str] = DEFAULT_CATEGORY  # Category
    seller: Optional[str] = None  # Seller
    color: Optional[str] = None  # Color
    sales_number: Optional[int] = None  # Sales Number
    revenue: Optional[float] = None  # Revenue
    price: Optional[float] = None  # Price
    wb_link: Optional[str] = None  # Wildberries link
    photo_link: Optional[str] = None  # Photo link
    revenue_by_day: Dict[date, float] = field(default_factory=dict)
    sales_by_day: Dict[date, int] = field(default_factory=dict)
    price_by_day: Dict[date, float] = field(default_factory=dict)
    _id: str = None  # DB ID - will be populated by DB

    def __hash__(self):
        return hash((self._id, self.number, self.wb_link, self.photo_link))

    def as_dict(self):
        data = asdict(self)
        data["revenue_by_day"] = {d.isoformat(): r for d, r in self.revenue_by_day.items()}
        data["sales_by_day"] = {d.isoformat(): r for d, r in self.sales_by_day.items()}
        data["price_by_day"] = {d.isoformat(): r for d, r in self.price_by_day.items()}

        return data


@dataclass
class TableView:
    columns: list
    data: list
    highlighted_row: Optional[int] = None

    def to_json(self):
        result = {
            "columns": self.columns,
            "data": self.data,
            "highlighted_row": self.highlighted_row,
        }
        return json.dumps(result, ensure_ascii=False, ident=2)
