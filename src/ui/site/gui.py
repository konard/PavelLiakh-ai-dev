from src.infrastructure.web_server import web_app

from nicegui import ui, app
from src.ioc import auth_service, log


def init_ui() -> None:

    @ui.page("/")
    def show():
        get_app_page()

    def get_app_page():
        with ui.card():
            ui.label("AI Dev")

    ui.run_with(
        web_app,
        title="modastat.ru",
    )
