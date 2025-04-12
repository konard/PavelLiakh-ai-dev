from google.oauth2 import service_account
from googleapiclient.discovery import build
from src.config import config

SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
credentials_file = config.get_resource("files/google_credentials.json")


class GoogleSheetsAuth:
    """Class for authentication with the Google Sheets API."""

    def __init__(self):
        populated_credentials_file = config.populate_template(credentials_file)
        self.credentials = service_account.Credentials.from_service_account_file(
            populated_credentials_file, scopes=SCOPES
        )

    def get_service(self):
        """Returns the service object for working with the Google Sheets API."""
        return build("sheets", "v4", credentials=self.credentials)
