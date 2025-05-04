from nicegui import ui
from logic import build_plan

DEFAULT_TASK = 'Implement user login feature'
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

    ui.label('Enter your task:')
    task_input = ui.input('Task description', value=DEFAULT_TASK)
    ui.button('Plan', on_click=on_plan)
    output_area = ui.textarea('Plan').props('readonly outlined').classes('w-full')

    # Trigger planning automatically on first load
    on_plan()
