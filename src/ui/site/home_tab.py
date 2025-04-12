import asyncio
import plotly.graph_objects as go

from datetime import date, timedelta, datetime
from nicegui import ui

from src.app.mp.mp_entities import TableView
from src.ioc import sku_service, statistics_service, log
from src.app.mp.mp_entities import Sku, SkuFilter
from src.ui.site.widgets.sku_widget import render_sku_card

found_sku_container: ui.row = None
revenue_chart_container: ui.row = None
top_skus_container: ui.row = None
revenue_report_container: ui.row = None
market_share_report_container: ui.row = None
total_period_skus_container: ui.row = None



def home_tab():
    with ui.column().classes("items-center w-full"):
        _render_analysis_section()
        ui.space().classes("h-8")

        _add_revenue_chart()
        _add_top_3_skus_section()
        _add_revenue_report()
        _add_market_share_report()
        _add_total()


def _render_analysis_section():
    current_filter = sku_service.get_sku_filter()
    min_date = statistics_service.git_min_date()
    today = date.today()

    ui.label("Анализ артикулов").classes("text-2xl font-bold text-left")
    with ui.column().classes("items-center w-full"):

        with ui.row().classes("items-center w-full gap-8"):
            # Filter controls column
            with ui.column().classes("items-center"):
                sku_input = ui.input("Артикул").classes("w-96")

                with ui.row().classes("items-center gap-4"):
                    start_date = current_filter.start_date or min_date
                    start_date = max(min_date, min(start_date, today))
                    with ui.input("Начальная дата", value=start_date.isoformat()) as start_input:
                        with ui.menu().props("no-parent-event") as menu:
                            ui.date().bind_value(start_input)
                        with start_input.add_slot("append"):
                            ui.icon("edit_calendar").on("click", menu.open).classes("cursor-pointer")

                    end_date = current_filter.end_date or today
                    end_date = max(start_date, min(end_date, today))
                    with ui.input("Конечная дата", value=end_date.isoformat()) as end_input:
                        with ui.menu().props("no-parent-event") as menu:
                            ui.date().bind_value(end_input)
                        with end_input.add_slot("append"):
                            ui.icon("edit_calendar").on("click", menu.open).classes("cursor-pointer")

                ui.button(
                    "Проанализировать период",
                    on_click=lambda: _search_and_filter(
                        sku_input.value, start_input.value, end_input.value
                    ),
                ).classes("w-96")

            # SKU display area (empty initially)
            global found_sku_container
            found_sku_container = ui.column().classes("w-96")


async def _search_and_filter(sku_number: str, start_date_str: str, end_date_str: str):
    sku_number = sku_number.strip()
    log.info("home_tab: search_and_filter: %s", sku_number)
    if not sku_number:
        ui.notify("Введите артикул", type="warning")
        return

    sku = sku_service.find_by_number(sku_number)
    if not sku:
        ui.notify("Артикул не найден", type="negative")
        return

    # Check if SKU is in the database
    # category = sku_service.get_sku_category(sku_number)

    min_date = statistics_service.git_min_date()
    today = date.today()
    start_date, end_date = _validate_dates(start_date_str, end_date_str, min_date, today)

    sku_filter = SkuFilter(sku_number=sku_number,
                  # category=category,
                  start_date=start_date,
                  end_date=end_date)
    sku_service.save_sku_filter(
        sku_filter
    )

    skus = sku_service.get_filtered_skus(sku_filter)
    if not skus:
        ui.notify("Для SKU нет данных в выбранном периоде", type="warning")
        return

    # Display found SKU
    global found_sku_container
    found_sku_container.clear()
    with found_sku_container:
        render_sku_card(sku, found_sku_container)

    log.info("load_revenue_chart")
    await _load_revenue_chart()
    log.info("load_top_3_skus")
    await _load_top_3_skus()
    log.info("load_revenue_report")
    await _load_revenue_report()
    log.info("load_market_share_report")
    await _load_market_share_report()
    log.info("load_total_period_skus")
    await _load_total_period_skus()
    log.info("home_tab: search_and_filter: done")

def _validate_dates(start_date_str: str, end_date_str: str, min_date: date, today: date):
    """Validate date ranges and return parsed dates"""
    from datetime import datetime

    try:
        start_date = (
            datetime.strptime(start_date_str, "%Y-%m-%d").date() if start_date_str else min_date
        )
        end_date = datetime.strptime(end_date_str, "%Y-%m-%d").date() if end_date_str else today

        start_date = max(min_date, min(start_date, today))
        end_date = max(start_date, min(end_date, today))

        return start_date, end_date
    except ValueError:
        return min_date, today


def _add_revenue_chart():
    global revenue_chart_container
    with ui.column().classes("items-center w-full mb-8"):
        revenue_chart_container = ui.row().classes("w-full gap-8")

def _add_top_3_skus_section():
    global top_skus_container
    with ui.column().classes("items-center w-full mb-8"):
        top_skus_container = ui.row().classes("w-full gap-8")

def _add_revenue_report():
    global revenue_report_container
    with ui.column().classes("items-center w-full mb-8"):
        revenue_report_container = ui.row().classes("w-full gap-8")

def _add_market_share_report():
    global market_share_report_container
    with ui.column().classes("items-center w-full mb-8"):
        market_share_report_container = ui.row().classes("w-full gap-8")

def _add_total():
    global total_period_skus_container
    with ui.column().classes("items-center w-full mb-8"):
        total_period_skus_container = ui.row().classes("w-full gap-8")

async def _load_revenue_chart():
    global revenue_chart_container
    revenue_chart_container.clear()
    with revenue_chart_container:
        ui.label("Загрузка данных... ")

    current_filter = sku_service.get_sku_filter()
    
    # Get time series data
    time_series = await asyncio.to_thread(
        statistics_service.get_revenue_time_series_for_plot,
        sku_filter=current_filter
    )

    revenue_chart_container.clear()

    if not time_series:
        with revenue_chart_container:
            ui.label("Нет данных для графика")
        return

    # Add title and create Plotly figure
    with revenue_chart_container:
        ui.label("График выручки").classes("text-2xl font-bold w-full")
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=time_series['dates'],
        y=time_series['current_sku']['values'],
        mode='lines',
        name=f"Текущий SKU: {time_series['current_sku']['number']}",
        line=dict(color='blue'),
        line_shape='spline'
    ))
    fig.add_trace(go.Scatter(
        x=time_series['dates'],
        y=time_series['top_sku']['values'],
        mode='lines',
        name=f"Топ SKU: {time_series['top_sku']['number']}",
        line=dict(color='green'),
        line_shape='spline'
    ))
    fig.add_trace(go.Scatter(
        x=time_series['dates'],
        y=time_series['total']['values'],
        mode='lines',
        name="Общая выручка",
        line=dict(color='red'),
        line_shape='spline'
    ))

    fig.update_layout(
        title='Выручка по дням',
        xaxis_title='Дата',
        yaxis_title='Выручка',
        legend_title='Легенда'
    )

    with revenue_chart_container:
        ui.plotly(fig)


async def _load_revenue_report():
    global revenue_report_container
    revenue_report_container.clear()

    with revenue_report_container:
        ui.label("Загрузка данных...  ")

    current_filter = sku_service.get_sku_filter()

    print("before getting report")
    # Run long-running task in a background thread
    revenue_report: TableView = await asyncio.to_thread(
        statistics_service.report_top_revenue_with_current_sku,
        sku_filter=current_filter,
        top_n=15
    )
    print("after getting report")

    revenue_report_container.clear()

    if not revenue_report:
        with revenue_report_container:
            ui.label("Нет данных о выручке")
        return

    with revenue_report_container:
        ui.label("TOP-15 по Выручке").classes("text-2xl font-bold w-full")
        rows = [dict(zip(revenue_report.columns, row)) for row in revenue_report.data]
        table = ui.table(
            columns=[{'name': col, 'label': col, 'field': col} for col in revenue_report.columns],
            rows=rows,
            row_key='#'
        )
        table.selected = [rows[revenue_report.highlighted_row]]

async def _load_market_share_report():
    global market_share_report_container
    market_share_report_container.clear()

    with market_share_report_container:
        ui.label("Загрузка данных...   ")

    current_filter = sku_service.get_sku_filter()

    print("before getting report")
    # Run long-running task in a background thread
    market_share_report: TableView = await asyncio.to_thread(
        statistics_service.report_top_market_share_with_current_sku,
        sku_filter=current_filter,
        top_n=10
    )
    print("after getting report")

    market_share_report_container.clear()

    if not market_share_report:
        with market_share_report_container:
            ui.label("Нет данных о доле рынка")
        return

    with market_share_report_container:
        ui.label("TOP-10 по Росту доли рынка").classes("text-2xl font-bold w-full")
        rows = [
            dict(zip(market_share_report.columns, row), class_="bg-green-300" if i == market_share_report.highlighted_row else "")
            for i, row in enumerate(market_share_report.data)
        ]
        table = ui.table(
            columns=[{'name': col, 'label': col, 'field': col} for col in market_share_report.columns],
            rows=rows,
            row_key='#',
        )
        table.selected = [rows[market_share_report.highlighted_row]]


async def _load_top_3_skus():
    global top_skus_container

    top_skus_container.clear()
    with top_skus_container:
        ui.label("Загрузка данных...    ")

    current_filter = sku_service.get_sku_filter()

    top_skus = await asyncio.to_thread(
        statistics_service.find_top_by_revenue,
        sku_filter=current_filter
    )

    top_skus_container.clear()
    if not top_skus:
        with top_skus_container:
            ui.label("Нет данных о выручке")
        return

    with top_skus_container:
        ui.label("TOP-3 по Выручке").classes("text-2xl font-bold w-full")
    for sku in top_skus:
        render_sku_card(sku, top_skus_container)

async def _load_total_period_skus():
    global total_period_skus_container

    total_period_skus_container.clear()
    current_filter = sku_service.get_sku_filter()
    with total_period_skus_container:
        ui.label(f"Всего в выбранном периоде: {len(sku_service.get_filtered_skus(current_filter))}")
        ui.label(f"Всего в категории: {sku_service.count_all_skus()}")
