from src.infrastructure.google.sheets_auth import GoogleSheetsAuth
from src.infrastructure.google.sheets_cache import load_cache_from_file, save_cache_to_file

# Parameters
spreadsheet_id = "1uWz93e_xGyCl9-QPcU5Lpqk2MyC29hAiJXWEtz9KX2o"  # Focus table
worksheet_name = "Настройки"
column_letter = "B"
num_rows = 100
google_service = GoogleSheetsAuth().get_service()


class GoogleSheetsParser:
    """Class for working with Google Sheets: reading data and writing to the adjacent column."""

    def __init__(self, log):
        self.log = log
        self.last_column_data = self.initialize_parser()

    def initialize_parser(self):
        cached_data = load_cache_from_file()
        if cached_data:
            self.log.info("Using cached data: %s", cached_data)
            self.last_column_data = cached_data.copy()
        else:
            self.log.info("No cached data found. Fetching initial data.")
            initial_data = self.get_column_data()
            self.last_column_data = initial_data.copy()
            save_cache_to_file(self.last_column_data)
            self.log.info("Initial data fetched and cached: %s", initial_data)

        return cached_data

    def get_cell_color(self, cell):
        """Extracts text color from a cell, returns (r, g, b) or (-1, -1, -1) if not found."""
        color = cell.get("effectiveFormat", {}).get("textFormat", {}).get("foregroundColor", {})
        return color.get("red", -1), color.get("green", -1), color.get("blue", -1)

    def get_column_values_and_formats(self):
        """
        Returns a tuple of (values_data, format_data), where:
        - values_data is a list of cell values.
        - format_data is a list of row data containing formatting information.
        """
        range_name = f"{worksheet_name}!{column_letter}1:{column_letter}{num_rows}"

        # Fetch values
        values_response = (
            google_service.spreadsheets()
            .values()
            .get(spreadsheetId=spreadsheet_id, range=range_name)
            .execute()
        )
        values_data = values_response.get("values", [])

        # Fetch formatting
        format_response = (
            google_service.spreadsheets()
            .get(
                spreadsheetId=spreadsheet_id,
                ranges=[range_name],
                fields="sheets.data.rowData.values.effectiveFormat.textFormat.foregroundColor",
            )
            .execute()
        )
        format_data = format_response.get("sheets", [{}])[0].get("data", [{}])[0].get("rowData", [])

        return values_data, format_data

    def get_column_data(self):
        """
        Returns a dictionary {A1: "Text"} for cells where the font is NOT white.
        """
        values_data, format_data = self.get_column_values_and_formats()

        result = {}
        for i, row in enumerate(format_data):
            r, g, b = self.get_cell_color(row.get("values", [{}])[0])

            # If the color is not white (RGB 1,1,1) and there is a value in values_data
            if (r, g, b) != (1, 1, 1) and i < len(values_data):
                cell_id = f"{column_letter}{i + 1}"
                if len(values_data[i]) > 0:
                    result[cell_id] = values_data[i][0]
                else:
                    result[cell_id] = ""
        return result

    def update_indicators(self, indicator_questions, get_value_for_cell):
        """
        Updates cells in the adjacent column only if the value of the source cell has changed.
        """
        next_column_letter = chr(ord(column_letter) + 1)
        updates = []

        for cell, value in indicator_questions.items():
            # Skip if value hasn't changed
            if self.last_column_data.get(cell) == value:
                continue

            try:
                update = self.update_one_cell(cell, value, next_column_letter, get_value_for_cell)
            except Exception as e:
                self.log.error(f"Failed to update cell {cell}: %s", e)
                continue
            updates.append(update)

        if updates:
            self.write_to_google_sheet(updates)
            self.last_column_data = indicator_questions.copy()
            save_cache_to_file(self.last_column_data)

    def write_to_google_sheet(self, updates):
        google_service.spreadsheets().values().batchUpdate(
            spreadsheetId=spreadsheet_id, body={"valueInputOption": "RAW", "data": updates}
        ).execute()

    def update_one_cell(self, cell, value, next_column_letter, get_value_for_cell):
        print(f"Updating cell {cell} with text '{value}'")
        row_number = "".join(filter(str.isdigit, cell))
        new_cell = f"{worksheet_name}!{next_column_letter}{row_number}"
        new_value = get_value_for_cell(value)  # Get transformed value
        return {"range": new_cell, "values": [[new_value]]}
