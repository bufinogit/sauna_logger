import requests
import re
from zoneinfo import ZoneInfo
from bs4 import BeautifulSoup
from datetime import datetime
import gspread
from google.oauth2.service_account import Credentials

# === KONFIGURACE ===
URL = "https://www.bazenslovany.cz/"   # URL stránky s obsazeností
SHEET_ID = "1hDuxto3fA3aVnxe9I6RXigix-L-UnV0j14NKEEL-ntc"  # ID

# === GOOGLE SHEETS AUTH ===
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
creds = Credentials.from_service_account_file("credentials.json", scopes=SCOPES)
gc = gspread.authorize(creds)
sheet = gc.open_by_key(SHEET_ID).sheet1

# === SCRAPING ===
try:
    response = requests.get(URL, timeout=10)
    response.raise_for_status()
except requests.RequestException as e:
    print(f"Chyba při stahování stránky: {e}")
    occupancy = "ERROR"
else:
    soup = BeautifulSoup(response.text, "html.parser")
    # ...po načtení elementu
    line = soup.find(string=re.compile(r"/30\s+obsazeno"))

    if line:
        # regex: číslo před lomítkem
        match = re.search(r"(\d+)/30", line)
        if match:
            occupancy = int(match.group(1))
            print("Aktuální obsazenost:", occupancy)
        else:
            occupancy = "N/A"
    else:
        occupancy = "N/A"

# === LOGOVÁNÍ DO SHEET ===

try:
    timestamp = datetime.now(ZoneInfo("Europe/Prague")).isoformat()
    sheet.append_row([timestamp, occupancy])
    print(f"Zapsáno: {timestamp} | {occupancy}")
except Exception as e:
    print(f"Chyba při zápisu do Sheets: {e}")
