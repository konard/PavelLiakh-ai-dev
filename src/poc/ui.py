from nicegui import ui
from logic import plan

def create_ui():
    ui.label('Enter your task:')
    
    # Input field with default value
    task_input = ui.input('Task description', value='Implement user login feature')
    
    # Output textarea that's read-only
    output_area = ui.textarea('Plan').props('readonly outlined').classes('w-full')
    
    def on_plan():
        """Handle plan button click"""
        task = task_input.value
        if task:
            plan_result = plan(task)
            output_area.value = plan_result
    
    # Plan button
    ui.button('Plan', on_click=on_plan)
    
    # Trigger planning automatically on first load
    on_plan()
