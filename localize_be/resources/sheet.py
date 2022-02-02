"""
Wrapper for Google API to update the spreadsheet
"""
import os
import os.path
from typing import List

from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

# If modifying these scopes, delete the file token.json.
from localize_be.config import config

SCOPES = ['https://www.googleapis.com/auth/spreadsheets']


def build_service(conf_dir):
    """
    Retrieve reference to Google spreadsheet service, initializing the authentication tokens if they are not
    present or need to be refreshed
    """
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    token_json = os.path.join(conf_dir, "token.json")
    credentials_json = os.path.join(conf_dir, "credentials.json")
    if os.path.exists(token_json):
        creds = Credentials.from_authorized_user_file(token_json, SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                credentials_json, SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open(token_json, 'w') as token:
            token.write(creds.to_json())

    service = build('sheets', 'v4', credentials=creds)

    # Call the Sheets API
    return service.spreadsheets()


class Sheet:
    def __init__(self, spreadsheet_id, spreadsheet_gid, conf_dir="."):
        print("BUILDING SERVICE")
        self.sheets = build_service(conf_dir)
        print("DONE")
        self.sheet_id = spreadsheet_id
        self.sheet_gid = spreadsheet_gid

    def _get_headers(self):
        result = self.sheets.values().get(spreadsheetId=self.sheet_id,
                                          range="Houses!A1:ZZ1").execute()
        values = result.get('values', [])
        return values[0]

    def get_homes(self):
        request = self.sheets.values().get(
            spreadsheetId=self.sheet_id,
            range="Houses!A2:E",
        ).execute()
        result = []
        for i, row_values in enumerate(request['values']):
            result.append((i, {
                "id": int(row_values[0]),
                "postal_code": row_values[1],
                "price": int(row_values[2]),
                "city": row_values[3],
                "property_type": row_values[4] if len(row_values) > 4 else None,
            }))
        return result

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

    def set_home_filter(self, exclude_ids: List[int]):
        self.sheets.batchUpdate(
            spreadsheetId=self.sheet_id,
            body={
                "requests": [
                    {
                        "setBasicFilter": {
                            "filter": {
                                "range": {
                                    "sheetId": self.sheet_gid,
                                    "startColumnIndex": 0,
                                    "endColumnIndex": 1
                                },
                                "filterSpecs": [
                                    {
                                        "columnIndex": 0,
                                        "filterCriteria": {
                                            # "condition": {
                                            #     "type": "ONE_OF_LIST",
                                            #     "values": [
                                            #         {
                                            #             "userEnteredValue": "9477738"
                                            #         }
                                            #     ]
                                            # }
                                            "hiddenValues": list(map(str, exclude_ids))
                                        }
                                    }
                                ]
                            }
                        }
                    }
                ]
            }
        ).execute()


def get_sheet():
    return Sheet(config["SHEET"]["SPREADSHEET_ID"], config["SHEET"]["SPREADSHEET_GID"])
