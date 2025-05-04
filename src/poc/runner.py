from nicegui import ui
from ui import create_ui


def main():
    create_ui()
    ui.run(title="My NiceGUI App", host="localhost", port=80)


if __name__ in {"__main__", "__mp_main__"}:
    main()
