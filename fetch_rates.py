import os
import requests
from datetime import datetime, timezone, timedelta
import gspread
from google.oauth2.service_account import Credentials
import json

# ── Config ────────────────────────────────────────────────────────────────────
EXCHANGERATE_API_KEY = os.environ["EXCHANGERATE_API_KEY"]
GOOGLE_CREDENTIALS_JSON = os.environ["GOOGLE_CREDENTIALS_JSON"]
SPREADSHEET_ID = os.environ["SPREADSHEET_ID"]

BASE_CURRENCY = "NZD"
TARGET_CURRENCIES = ["USD", "AUD", "KRW"]

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
]

# ── Fetch rates ───────────────────────────────────────────────────────────────
def fetch_rates() -> dict:
    url = f"https://v6.exchangerate-api.com/v6/{EXCHANGERATE_API_KEY}/latest/{BASE_CURRENCY}"
    response = requests.get(url, timeout=10)
    response.raise_for_status()
    data = response.json()

    if data["result"] != "success":
        raise RuntimeError(f"API error: {data.get('error-type', 'unknown')}")

    rates = data["conversion_rates"]
    return {currency: rates[currency] for currency in TARGET_CURRENCIES}


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
        sheet.append_row(["Timestamp (NZST)", "NZD→USD", "NZD→AUD", "NZD→KRW"])

    return sheet


def append_rates(sheet, rates: dict):
    nzst = timezone(timedelta(hours=12))  # NZST (UTC+12), change to 13 in summer
    timestamp = datetime.now(nzst).strftime("%Y-%m-%d %H:%M:%S")
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
    print(f"Fetching NZD exchange rates at {datetime.now(timezone.utc).isoformat()} UTC...")
    rates = fetch_rates()
    print(f"  NZD → USD: {rates['USD']}")
    print(f"  NZD → AUD: {rates['AUD']}")
    print(f"  NZD → KRW: {rates['KRW']}")

    sheet = get_sheet()
    append_rates(sheet, rates)


if __name__ == "__main__":
    main()
