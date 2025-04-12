from datetime import timedelta
from decimal import ROUND_HALF_UP, Decimal
from functools import lru_cache
from typing import List, Optional

from dateutil.utils import today
from datetime import date
from src.app.mp.sku_service import SkuService
from src.app.mp.mp_entities import Sku, SkuFilter, TableView


class StatisticsService:
    def __init__(self, sku_service: SkuService, log):
        self.sku_service = sku_service
        self.log = log

    @lru_cache(maxsize=1)
    def git_min_date(self):
        skus = self.sku_service.get_all_skus()
        minimum_date = today().date()
        for sku in skus:
            if sku.revenue_by_day and list(sku.revenue_by_day.keys())[0] < minimum_date:
                minimum_date = list(sku.revenue_by_day.keys())[0]

        if minimum_date:
            return minimum_date

        return today

    def get_sku_revenue(self, sku: Sku, min_date, max_date):
        total_revenue = sum(
            revenue for d, revenue in sku.revenue_by_day.items() if min_date <= d <= max_date
        )
        return total_revenue

    def _get_date_range(self, sku_filter: Optional[SkuFilter] = None) -> tuple[date, date]:
        """Get min and max dates from filter or use defaults"""
        min_date = sku_filter.start_date if sku_filter and sku_filter.start_date else self.git_min_date()
        max_date = sku_filter.end_date if sku_filter and sku_filter.end_date else today().date()
        return min_date, max_date

    @lru_cache(maxsize=4)
    def find_top_by_revenue(
        self, top_n: int = 3, sku_filter: Optional[SkuFilter] = None
    ) -> List[Sku]:
        sorted_by_revenue = self._get_total_revenue(sku_filter)[:top_n]
        return [item["sku"] for item in sorted_by_revenue]

    @lru_cache(maxsize=1)
    def _get_total_revenue(self, sku_filter: Optional[SkuFilter] = None):
        sku_revenue = []
        skus = self.sku_service.get_filtered_skus(sku_filter)
        min_date, max_date = self._get_date_range(sku_filter)
        for sku in skus:
            total_revenue = self.get_sku_revenue(sku, min_date, max_date)
            sku_revenue.append({"sku": sku, "total_revenue": total_revenue})
        sorted_skus = sorted(sku_revenue, key=lambda x: x["total_revenue"], reverse=True)
        return sorted_skus

    @lru_cache(maxsize=1)
    def report_top_revenue_with_current_sku(self, sku_filter: SkuFilter, top_n: int = 15) -> TableView:
        self.log.info("before getting report")
        top_skus = self.find_top_by_revenue(sku_filter=sku_filter, top_n=top_n)

        min_date, max_date = self._get_date_range(sku_filter)

        columns = ["#", "SKU", "Название", "Бренд", "Категория", "Выручка"]
        data = [
            [i + 1, sku.number, sku.name, sku.brand, sku.category, self.get_sku_revenue(sku, min_date, max_date)]
            for i, sku in enumerate(top_skus)
        ]

        # find place of this concrete sku in the list of top items
        top_skus = self._get_total_revenue(sku_filter)[:top_n]

        # find number of our concrete sku in this list
        place = None
        for i, item in enumerate(top_skus):
            if item["sku"].number == sku_filter.sku_number:
                place = i + 1
                break

        if not place:
            self.log.info("after getting report")
            return TableView(columns, data, 1)

        if place <= top_n:
            self.log.info("after getting report")
            return TableView(columns, data, place)

        selected_sku = top_skus[place-1]
        data.append([
            place,
            selected_sku["sku"].number,
            selected_sku["sku"].name,
            selected_sku["sku"].brand,
            selected_sku["sku"].category,
            selected_sku["total_revenue"]
        ])

        self.log.info("after getting report and position")
        return TableView(columns, data, top_n)

    def get_revenue_time_series_for_plot(self, sku_filter: SkuFilter) -> dict:
        """Returns revenue time series data for plotting:
        - Current SKU (from filter)
        - Top performing SKU
        - Sum of all SKUs
        Returns dict with dates and values for each series.
        """
        if not sku_filter.sku_number:
            raise ValueError("SKU number must be provided in filter")

        # Get all relevant SKUs
        skus = self.sku_service.get_filtered_skus(sku_filter)
        
        # Find current SKU
        current_sku = next((s for s in skus if s.number == sku_filter.sku_number), None)
        if not current_sku:
            raise ValueError(f"SKU {sku_filter.sku_number} not found")

        # Find top SKU
        top_sku = self.find_top_by_revenue(top_n=1, sku_filter=sku_filter)[0]
        
        # Get all dates in range
        min_date, max_date = self._get_date_range(sku_filter)
        dates = sorted(set().union(
            *(sku.revenue_by_day.keys() for sku in skus)
        ))
        dates = [d for d in dates if min_date <= d <= max_date]

        # Prepare data series
        current_series = []
        top_series = []
        total_series = []
        
        for date in dates:
            # Current SKU revenue
            current_rev = current_sku.revenue_by_day.get(date, 0)
            current_series.append(current_rev)
            
            # Top SKU revenue
            top_rev = top_sku.revenue_by_day.get(date, 0)
            top_series.append(top_rev)
            
            # Total revenue
            total_rev = sum(sku.revenue_by_day.get(date, 0) for sku in skus)
            total_series.append(total_rev)

        return {
            "dates": dates,
            "current_sku": {
                "number": current_sku.number,
                "name": current_sku.name,
                "values": current_series
            },
            "top_sku": {
                "number": top_sku.number,
                "name": top_sku.name,
                "values": top_series
            },
            "total": {
                "values": total_series
            }
        }

    def report_top_market_share_with_current_sku(self, sku_filter: SkuFilter, top_n: int = 10) -> TableView:
        self.log.info("before getting report")
        skus = self.sku_service.get_filtered_skus(sku_filter)

        sku_market_shares = []
        min_date, max_date = self._get_date_range(sku_filter)
        total_revenue_at_start = 0
        total_revenue_at_end = 0
        for sku in skus:
            # sum of revenue for 30 days starting from start date
            revenue_at_start = self.get_sku_revenue(sku, min_date, min_date + timedelta(days=7))
            total_revenue_at_start += revenue_at_start
            revenue_at_end = self.get_sku_revenue(sku, max_date - timedelta(days=7), max_date)
            total_revenue_at_end += revenue_at_end
            sku_market_shares.append({"sku": sku,
                                      "start_revenue": revenue_at_start,
                                      "end_revenue": revenue_at_end})

        for sku_share in sku_market_shares:
            sku_share['start_market_share'] = Decimal(100 * sku_share['start_revenue'] / total_revenue_at_start).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP) if total_revenue_at_start > 0 else 0
            sku_share['end_market_share'] = Decimal(100 * sku_share['end_revenue'] / total_revenue_at_end).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP) if total_revenue_at_end > 0 else 0
            sku_share['market_share_diff'] = sku_share['end_market_share'] - sku_share['start_market_share']
            sku_share['revenue_diff'] = sku_share['end_revenue'] - sku_share['start_revenue']

        sku_market_shares = sorted(sku_market_shares, key=lambda x: x["market_share_diff"], reverse=True)

        top_n_market_shares = sku_market_shares[:top_n]
        current_position, current_market_share = None, None
        for i, item in enumerate(sku_market_shares):
            if item["sku"].number == sku_filter.sku_number:
                current_market_share, current_position = item, i
                break


        columns = ["#",
                   "SKU",
                   "Название",
                   "Бренд",
                   "Категория",
                   "Разница доли рынка (%)",
                   "Разница выручки"]
        data = [
            [i + 1,
             sku['sku'].number,
             sku['sku'].name,
             sku['sku'].brand,
             sku['sku'].category,
             sku['market_share_diff'],
             sku['revenue_diff']]
            for i, sku in enumerate(top_n_market_shares)
        ]

        if not current_position:
            self.log.info("after getting report")
            return TableView(columns, data, 1)

        if current_position <= top_n:
            self.log.info("after getting report")
            return TableView(columns, data, current_position)

        data.append([
            current_position,
            current_market_share["sku"].number,
            current_market_share["sku"].name,
            current_market_share["sku"].brand,
            current_market_share["sku"].category,
            current_market_share['market_share_diff'],
            current_market_share['revenue_diff']
        ])
        return TableView(columns, data, top_n)

