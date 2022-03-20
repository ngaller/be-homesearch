"""
Wrapper for Google API to update the spreadsheet
"""
import os
import os.path
from typing import List
from typing import Tuple

from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

# If modifying these scopes, delete the file token.json.
from localize_be.config import config, logger

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
        self.sheets = build_service(conf_dir)
        self.sheet_id = spreadsheet_id
        self.sheet_gid = spreadsheet_gid

    def _get_headers(self):
        result = self.sheets.values().get(spreadsheetId=self.sheet_id,
                                          range="Houses!A1:ZZ1").execute()
        values = result.get('values', [])
        return values[0]

    def get_homes(self):
        """
        Retrieve existing homes from the spreadsheet.

        :returns: an array of tuple with (sheet index, home data)
        """
        request = self.sheets.values().get(
            spreadsheetId=self.sheet_id,
            range="Houses!A2:E",
        ).execute()
        result = []
        for i, row_values in enumerate(request['values']):
            if not row_values[2]:
                continue
            result.append((i, {
                "id": int(row_values[0]),
                "postal_code": row_values[1],
                "price": int(row_values[2]),
                "city": row_values[3],
                "property_type": row_values[4] if len(row_values) > 4 else None,
            }))
        logger.debug(f"Found {len(result)} home(s) in spreadsheet")
        return result

    def upsert_homes(self, homes: List):
        """
        Update values for existing homes, and append new homes
        """
        existing = self.get_homes()
        existing_ids = {d[1]["id"] for d in existing}
        new_homes = [h for h in homes if h["Code #"] not in existing_ids]
        inserted = 0
        logger.debug(f"Add {len(new_homes)} home(s) in spreadsheet")
        if new_homes:
            inserted = self.add_homes(new_homes)
        updated_homes = [h for h in homes if h["Code #"] in existing_ids]
        logger.debug(f"Update {len(updated_homes)} home(s) in spreadsheet")
        updated = 0
        if updated_homes:
            updated = self.update_homes(existing, updated_homes)
        return (inserted, updated)

    def update_homes(self, existing: List[Tuple], homes: List):
        """
        :param existing: an array of tuples (sheet index, home data)
        :param homes: list of homes to add
        """
        headers = self._get_headers()
        homes_by_id = {h["Code #"]: h for h in homes}
        skip_headers = {"Image", "Link", "Address"}

        def make_row(id_):
            # Make row of data based on the id
            # The values that need to be left unchanged are passed as null
            # If no match in homes, return an empty list
            home = homes_by_id.get(id_)
            if not home:
                return []
            return [
                home.get(h, None) if h not in skip_headers else None
                for h in headers
            ]

        updated_rows = [
            make_row(existing_home["id"])
            for (_, existing_home) in existing
        ]
        result = self.sheets.values().update(
            spreadsheetId=self.sheet_id,
            range="Houses!A2",
            valueInputOption="USER_ENTERED",
            body={
                "values": updated_rows
            }
        ).execute()
        return result["updatedRows"]

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
        return updated_rows

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
