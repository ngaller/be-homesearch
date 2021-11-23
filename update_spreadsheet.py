import csv
import os
import os.path
import sys
from typing import Iterable, Dict, List

import dotenv
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

# refer to https://developers.google.com/workspace/guides/create-credentials to create the credentials.json file

dotenv.load_dotenv()

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

# The ID and range of a sample spreadsheet.
SPREADSHEET_ID = os.environ["SPREADSHEET_ID"]
SPREADSHEET_GID = os.environ["SPREADSHEET_GID"]


def build_service():
    """Shows basic usage of the Sheets API.
    Prints values from a sample spreadsheet.
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
    sheet = service.spreadsheets()
    return sheet


def read_codes(sheet) -> Dict[str, int]:
    """Get the codes that are already on the spreadsheet"""
    result = sheet.values().get(spreadsheetId=SPREADSHEET_ID,
                                range="Houses!A2:A").execute()
    values = result.get('values', [])
    return {r[0]: i for i, r in enumerate(values)}


def read_headers(sheet) -> List[str]:
    result = sheet.values().get(spreadsheetId=SPREADSHEET_ID,
                                range="Houses!A1:ZZ1").execute()
    values = result.get('values', [])
    return values[0]


def read_home_csv(csv_path) -> Iterable[Dict]:
    """
    Read home.csv file generated from analysis.
    """
    with open(csv_path, "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            row["Link.Url"] = row.pop("Link")
            row["Image.Url"] = row.pop("Image")
            yield row


def add_homes(sheet, headers, homes):
    for home in homes:
        # fix formulas
        home["Image"] = '=IMAGE(INDIRECT("RC[-1]", false), 4, 100, 120)'
        home["Link"] = '=HYPERLINK(INDIRECT("RC[-1]", false))'
    new_rows = [
        [home.get(key, "") for key in headers]
        for home in homes]
    result = sheet.values().append(
        spreadsheetId=SPREADSHEET_ID,
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
    sheet.batchUpdate(
        spreadsheetId=SPREADSHEET_ID,
        body={
            "requests": [
                {
                    "updateDimensionProperties": {
                        "range": {
                            "sheetId": SPREADSHEET_GID,
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


def hide_rows(sheet, row_indices):
    requests = []
    for i in row_indices:
        requests.append({
            "updateDimensionProperties": {
                "range": {
                    "sheetId": SPREADSHEET_GID,
                    "dimension": "ROWS",
                    "startIndex": i + 1,
                    "endIndex": i + 2,
                },
                "properties": {
                    "hiddenByUser": True
                },
                "fields": "hiddenByUser"
            }
        })
        sheet.batchUpdate(
            spreadsheetId=SPREADSHEET_ID,
            body={
                "requests": requests
            }).execute()


def main(home_csv):
    sheet = build_service()
    existing_codes = read_codes(sheet)
    headers = read_headers(sheet)
    homes = {r["Code #"]: r for r in read_home_csv(home_csv)}
    homes_to_add = [h for c, h in homes.items() if c not in existing_codes]
    if homes_to_add:
        print("Adding", len(homes_to_add), "new homes", ", ".join(h["Code #"] for h in homes_to_add))
        add_homes(sheet, headers, homes_to_add)
    rows_to_remove = [(i, c) for c, i in existing_codes.items() if c not in homes]
    if rows_to_remove:
        print("Removing", len(rows_to_remove), "homes", ", ".join(r[1] for r in rows_to_remove))
        hide_rows(sheet, [r[0] for r in rows_to_remove])


if __name__ == '__main__':
    main(sys.argv[1] if len(sys.argv) == 2 else "homes_scored.csv")
