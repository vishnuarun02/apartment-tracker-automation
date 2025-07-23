import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    # Google Maps API
    GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")

    # Shopify office address for distance calculation
    SHOPIFY_OFFICE_ADDRESS = "1100 112th Ave NE, Bellevue, WA 98004"

    # Google Sheets configuration
    GOOGLE_SHEETS_CREDENTIALS_FILE = "credentials.json"
    SPREADSHEET_ID = os.getenv("SPREADSHEET_ID")

    # Flask configuration
    PORT = int(os.getenv("PORT", 5000))
    DEBUG = os.getenv("DEBUG", "False").lower() == "true"
