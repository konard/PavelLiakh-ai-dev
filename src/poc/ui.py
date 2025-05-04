from nicegui import ui
from src.poc.logic import build_plan

DEFAULT_TASK = "Implement user login feature"
task_input = None
output_area = None


def on_plan():
    """Handle plan button click"""
    task = task_input.value
    if task:
        plan_result = build_plan(task)
        output_area.value = plan_result


def create_ui():
    global task_input
    global output_area

    ui.label("Enter your task:")

    with ui.row().classes("w-full"):
        task_input_component = ui.input("Task description", value=DEFAULT_TASK)
        task_input_component.props("autogrow").classes("w-full")
        task_input_component.on("keydown.enter", lambda e: on_plan())
        task_input = task_input_component

    ui.button("Plan", on_click=on_plan)

    output_area = ui.textarea("Plan").props("readonly outlined autogrow").classes("w-full")

    # Trigger planning automatically on first load
    on_plan()
