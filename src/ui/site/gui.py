from src.infrastructure.db.credentials_storage import Credentials
from src.app.service.session_service import load_sessions, save_sessions
from src.infrastructure.web_server import web_app
from src.ui.site.home_tab import home_tab
from src.ui.site.data_tab import data_tab
from nicegui import ui, app
from src.ioc import auth_service, log
import asyncio

MAIN_TAB_NAME = "Главная"
DATA_TAB_NAME = "Данные"
#
# def try_login(login, password):
#     log.info(f"Signin pressed: {login},pwd={password}")
#     if auth_service.authenticate(login, password):
#         app.storage.user['authenticated'] = True
#         app.storage.user['login'] = login
#         sessions = load_sessions()
#         sessions[app.storage.user.get('id')] = True
#         save_sessions(sessions)
#         ui.navigate.to('/')
#     else:
#         ui.notify('Invalid credentials', type='negative')

def init_ui() -> None:

    @ui.page("/")
    def show():
        # if not is_authenticated():
        #     return login_page()
        get_app_page()

    # def is_authenticated() -> bool:
    #     return app.storage.user.get('authenticated', False)
    #
    # def login_page():
    #     with ui.card().classes('absolute-center'):
    #         login_button = ui.input('Login').classes('w-64')
    #         password_button = ui.input('Password', password=True).classes('w-64')
    #         try_login_lambda = lambda: try_login(login_button.value, password_button.value)
    #         ui.button('Login', on_click=try_login_lambda).classes('w-full')

    def get_app_page():
        # def logout():
        #     app.storage.user['authenticated'] = False
        #     sessions = load_sessions()
        #     sessions.pop(app.storage.user.get('id'), None)
        #     save_sessions(sessions)
        #     ui.navigate.to('/')

        # ui.button('Logout', on_click=logout).classes('absolute top-4 right-4')
        #
        # with ui.tabs() as tabs:
        #     tab1 = ui.tab(MAIN_TAB_NAME)
        #     tab2 = ui.tab(DATA_TAB_NAME)
        #
        # with ui.tab_panels(tabs, value=MAIN_TAB_NAME, keep_alive=True):
        #     with ui.tab_panel(tab1):
        home_tab()
            #
            # with ui.tab_panel(tab2):
            #     data_tab()


    ui.run_with(
        web_app,
        title='modastat.ru',
    )
