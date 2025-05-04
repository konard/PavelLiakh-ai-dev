from nicegui import ui
from logic import process_input

def create_ui():
    ui.label('Enter a number:')

    input_field = ui.number('Number')

    result_label = ui.label()

    def on_click():
        value = input_field.value
        result = process_input(value)
        result_label.text = f'Result: {result}'

    ui.button('Calculate', on_click=on_click)
