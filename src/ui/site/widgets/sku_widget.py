from nicegui import ui
from src.app.mp.mp_entities import Sku


def render_sku_card(sku: Sku, container: ui.row):
    total_revenue = sum(sku.revenue_by_day.values())
    with container:
        with ui.card().classes("w-72 p-4 shadow-lg hover:shadow-xl transition-shadow duration-300"):
            with ui.column().classes("items-center gap-2"):
                print("SKU photo link:", sku.photo_link)
                if sku.photo_link:
                    ui.image(sku.photo_link).classes("w-full h-48 object-cover rounded-lg")

                ui.label(f"Артикул: {sku.number}").classes("text-lg font-bold text-center")

            with ui.column().classes("mt-4 gap-2"):
                ui.label("Категория:").classes("text-sm font-medium")
                ui.label(sku.category or "Не указана").classes("text-sm text-gray-600")

                ui.label("Общая выручка:").classes("text-sm font-medium mt-2")
                ui.label(f"{total_revenue:.2f} ₽").classes("text-sm text-gray-600")

            if sku.wb_link:
                with ui.row().classes("items-center gap-2 mt-4 justify-center"):
                    ui.icon("link").classes("text-blue-500")
                    ui.link("Ссылка на WB", sku.wb_link, new_tab=True).classes(
                        "text-sm text-blue-500 hover:text-blue-700"
                    )
