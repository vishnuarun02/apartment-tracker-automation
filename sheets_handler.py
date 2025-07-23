import gspread
from google.oauth2.service_account import Credentials
from config import Config
import logging
import json
import os


class SheetsHandler:
    def __init__(self):
        scope = [
            "https://spreadsheets.google.com/feeds",
            "https://www.googleapis.com/auth/drive",
        ]

        # Check if running on Railway (production) or locally
        if os.getenv("GOOGLE_CREDENTIALS"):
            # Production: use environment variable
            creds_dict = json.loads(os.getenv("GOOGLE_CREDENTIALS"))
            creds = Credentials.from_service_account_info(creds_dict, scopes=scope)
        else:
            # Local: use credentials file
            creds = Credentials.from_service_account_file(
                Config.GOOGLE_SHEETS_CREDENTIALS_FILE, scopes=scope
            )

        self.client = gspread.authorize(creds)
        self.spreadsheet = self.client.open_by_key(Config.SPREADSHEET_ID)
        self.worksheet = self.spreadsheet.sheet1

    def find_row_by_address(self, address):
        """Find the row number that contains the given address"""
        try:
            # Get all values in the address column (Column D)
            address_column = self.worksheet.col_values(4)

            for i, cell_address in enumerate(address_column):
                if cell_address.strip().lower() == address.strip().lower():
                    return i + 1  # gspread uses 1-based indexing

            return None

        except Exception as e:
            logging.error(f"Error finding row: {str(e)}")
            return None

    def update_property_data(
        self,
        address,
        property_name,
        car_commute,
        bike_commute,
        transit_commute,
        maps_link,
    ):
        """Update the property data for a given address"""
        try:
            row = self.find_row_by_address(address)

            if not row:
                logging.error(f"Address not found in sheet: {address}")
                return False

            # Extract city from address for column E
            city = address.split(",")[-2].strip() if "," in address else "Unknown"

            # Update the cells based on your actual column structure
            # A=Property Name, E=City, L=Commute Time, O=Google Map Link
            updates = [
                {
                    "range": f"A{row}",  # Property Name column
                    "values": [[property_name]],
                },
                {
                    "range": f"E{row}",  # City column
                    "values": [[city]],
                },
                {
                    "range": f"L{row}",  # Commute Time to Shopify column
                    "values": [
                        [
                            f" Car: {car_commute} | Bike: {bike_commute} | Transit: {transit_commute}"
                        ]
                    ],
                },
                {
                    "range": f"O{row}",  # Google Map Link column
                    "values": [[maps_link]],
                },
            ]

            # Batch update for efficiency
            self.worksheet.batch_update(updates)

            logging.info(f"Successfully updated row {row} for address: {address}")
            return True

        except Exception as e:
            logging.error(f"Error updating sheet: {str(e)}")
            return False

    def get_pending_addresses(self):
        """Get addresses that need processing (property name is empty)"""
        try:
            # Get all data
            all_data = self.worksheet.get_all_records()

            pending = []
            for i, row in enumerate(all_data):
                # If property name is empty but address exists
                if (
                    not row.get("Property Name", "").strip()
                    and row.get("Address", "").strip()
                ):
                    pending.append(
                        {
                            "row": i + 2,  # +2 because of header and 0-based index
                            "address": row["Address"],
                        }
                    )

            return pending

        except Exception as e:
            logging.error(f"Error getting pending addresses: {str(e)}")
            return []
