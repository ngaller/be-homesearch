"""
Wrapper for Google API to update the spreadsheet
"""
import os

from dagster import resource, StringSource

from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']


def build_service():
    """
    Retrieve reference to Google spreadsheet service, initializing the authentication tokens if they are not
    present or need to be refreshed
    """
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    service = build('sheets', 'v4', credentials=creds)

    # Call the Sheets API
    return service.spreadsheets()


class Sheet:
    def __init__(self, spreadsheet_id, spreadsheet_gid):
        self.sheets = build_service()
        self.sheet_id = spreadsheet_id
        self.sheet_gid = spreadsheet_gid

    def _get_headers(self):
        result = self.sheets.values().get(spreadsheetId=self.sheet_id,
                                          range="Houses!A1:ZZ1").execute()
        values = result.get('values', [])
        return values[0]

    def add_homes(self, homes):
        for home in homes:
            # fix formulas
            home["Image"] = '=IMAGE(INDIRECT("RC[-1]", false), 4, 100, 120)'
            home["Link"] = '=HYPERLINK(INDIRECT("RC[-1]", false))'
            home["Address"] = f"{home['Street']}, {home['City']}" if home['Street'] else ''
        headers = self._get_headers()
        new_rows = [
            [home.get(key, "") for key in headers]
            for home in homes]
        result = self.sheets.values().append(
            spreadsheetId=self.sheet_id,
            range="Houses!A1",
            valueInputOption="USER_ENTERED",
            body={
                "values": new_rows
            }
        ).execute()
        updated_range = result["updates"]["updatedRange"]
        # extract start index from: Houses!A103:Z130
        start_index = int(updated_range.split("!")[1].split(":")[0][1:]) - 1
        updated_rows = result["updates"]["updatedRows"]
        self.sheets.batchUpdate(
            spreadsheetId=self.sheet_id,
            body={
                "requests": [
                    {
                        "updateDimensionProperties": {
                            "range": {
                                "sheetId": self.sheet_gid,
                                "dimension": "ROWS",
                                "startIndex": start_index,
                                "endIndex": start_index + updated_rows
                            },
                            "properties": {
                                "pixelSize": 100
                            },
                            "fields": "pixelSize"
                        }
                    }
                ]
            }).execute()

    def set_home_filter(self):
        pass


@resource(config_schema={"spreadsheet_id": StringSource, "spreadsheet_gid": StringSource})
def sheet(context):
    return Sheet(context.resource_config["spreadsheet_id"], context.resource_config["spreadsheet_gid"])
