import os
import requests
from datetime import datetime
from zoneinfo import ZoneInfo
import gspread
from google.oauth2.service_account import Credentials
import json

# ── Config ────────────────────────────────────────────────────────────────────
EXCHANGERATE_API_KEY = os.environ["EXCHANGERATE_API_KEY"]
GOOGLE_CREDENTIALS_JSON = os.environ["GOOGLE_CREDENTIALS_JSON"]
SPREADSHEET_ID = os.environ["SPREADSHEET_ID"]

BASE_CURRENCY = "NZD"
TARGET_CURRENCIES = ["USD", "AUD", "KRW"]
NZ_TZ = ZoneInfo("Pacific/Auckland")  # auto-handles NZST/NZDT, no manual offset needed

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
]

# ── Fetch rates ───────────────────────────────────────────────────────────────
def fetch_rates() -> dict:
    url = "https://api.frankfurter.app/latest?from=NZD&to=USD,AUD"
    response = requests.get(url, timeout=10)
    response.raise_for_status()
    data = response.json()
    rates = data["rates"]

    # Frankfurter doesn't have KRW, so fetch it separately
    krw_url = "https://open.er-api.com/v6/latest/NZD"
    krw_response = requests.get(krw_url, timeout=10)
    krw_response.raise_for_status()
    krw_data = krw_response.json()
    rates["KRW"] = krw_data["rates"]["KRW"]

    return rates


# ── Write to Google Sheets ────────────────────────────────────────────────────
def get_sheet():
    creds_dict = json.loads(GOOGLE_CREDENTIALS_JSON)
    creds = Credentials.from_service_account_info(creds_dict, scopes=SCOPES)
    client = gspread.authorize(creds)
    spreadsheet = client.open_by_key(SPREADSHEET_ID)

    # Use first sheet, or create one called "Rates" if none exist
    try:
        sheet = spreadsheet.worksheet("Rates")
    except gspread.exceptions.WorksheetNotFound:
        sheet = spreadsheet.add_worksheet(title="Rates", rows=10000, cols=10)
        # Write header row
        sheet.append_row(["Timestamp (NZ Time)", "NZD→USD", "NZD→AUD", "NZD→KRW"])

    return sheet


def append_rates(sheet, rates: dict):
    timestamp = datetime.now(NZ_TZ).strftime("%Y-%m-%d %H:%M:%S %Z")
    row = [
        timestamp,
        rates["USD"],
        rates["AUD"],
        rates["KRW"],
    ]
    sheet.append_row(row)
    print(f"✅ Appended row: {row}")


# ── Main ──────────────────────────────────────────────────────────────────────
def main():
    print(f"Fetching NZD exchange rates at {datetime.now(NZ_TZ).strftime('%Y-%m-%d %H:%M:%S %Z')}...")
    rates = fetch_rates()
    print(f"  NZD → USD: {rates['USD']}")
    print(f"  NZD → AUD: {rates['AUD']}")
    print(f"  NZD → KRW: {rates['KRW']}")

    sheet = get_sheet()
    append_rates(sheet, rates)


if __name__ == "__main__":
    main()
