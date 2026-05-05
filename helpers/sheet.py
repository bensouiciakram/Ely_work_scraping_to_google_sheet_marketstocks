import re
from google.oauth2 import service_account
from googleapiclient.discovery import build
from pathlib import Path
from helpers.params import SHEET_NAME

class SheetManipulator():
    @staticmethod
    def get_credentials_and_service() -> set[any, any]:
        current_dir = Path(__file__).parent.absolute()
        config_folder = current_dir.parent / 'auth'
        credentials_file_path = config_folder / 'notification-88f1b-7105c5bbca71.json'
        credentials = service_account.Credentials.from_service_account_file(credentials_file_path, scopes=["https://www.googleapis.com/auth/spreadsheets"])
        service = build('sheets', 'v4', credentials=credentials)
        return credentials, service

    @staticmethod
    def get_spreadsheet_id(url) -> str:
        # https://docs.google.com/spreadsheets/d/1lvspePHKSD_dejnWUq1hkCNr29gq-D7kDyiVI7qpZBo/edit?gid=0#gid=0
        # must return 1lvspePHKSD_dejnWUq1hkCNr29gq-D7kDyiVI7qpZBo
        match = re.search(r'/d/([a-zA-Z0-9-_]+)', url)
        if match:
            return match.group(1)
        else:
            raise ValueError("Invalid url or id not found")

    @staticmethod
    def append_stock(spreadsheet_id: str, new_rows: list, service):
        body = { "values": new_rows }
        result = service.spreadsheets().values().append(
            spreadsheetId=spreadsheet_id,
            range= f"'{SHEET_NAME}'!A:A",
            valueInputOption="USER_ENTERED",
            insertDataOption="INSERT_ROWS", 
            body=body
        ).execute()
        return result
    
    @staticmethod
    def get_all_stocks(spreadsheet_id: str, service) -> dict[str, any]:
        # Read data from sheet
        range_name = f"'{SHEET_NAME}'!A:R"
        sheet = service.spreadsheets().values().get(
            spreadsheetId=spreadsheet_id,
            range=range_name
        ).execute()
        values = sheet.get('values', [])
        # Check existing data
        if not values:
            raise f"No data found in the sheet : {range_name}"
        headers = values[0]
        # Add line number for update after
        mapped_rows = [ row + [index + 1] for index, row in enumerate(values[1:]) ]
        # Add "row_index" in header
        return mapped_rows
    
    # Update line
    @staticmethod
    def update_line_items(spreadsheet_id: str, modified_rows: list, service):
        requests = []
        for row_data in modified_rows:
            row_index = row_data.pop()
            update_range = f"{SHEET_NAME}!A{row_index + 1}"
            # Each request
            requests.append({
                "range": update_range,
                "values": [row_data]
            })
        # Group all request in one batch
        body = {
            "valueInputOption": "USER_ENTERED",
            "data": requests
        }
        # Execute update
        result = service.spreadsheets().values().batchUpdate(
            spreadsheetId=spreadsheet_id,
            body=body
        ).execute()
        return result
    
    @staticmethod
    def clean_non_ascii(text):
        text = text.replace('\r', "")
        text = text.replace('\t', "")
        text = text.replace('\n', "")
        text = text.replace(' ', '')
        text = text.replace('$', '')
        text = text.replace('%', '')
        text = text.replace('USD', '')
        text = text.replace('N/A', '')
        text = text.replace('NotAvailable', '')
        text = re.sub(r'[^0-9.-]', '', text)  # Keep only digits and point
        return text