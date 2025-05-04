def process_input(value):
    try:
        number = float(value)
        return number * 2  # Example logic: double the input
    except (ValueError, TypeError):
        return 'Invalid input'
