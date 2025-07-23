from flask import Flask, request, jsonify
import logging
from google_maps_handler import GoogleMapsHandler
from sheets_handler import SheetsHandler
from config import Config

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Initialize handlers
maps_handler = GoogleMapsHandler()
sheets_handler = SheetsHandler()


@app.route("/", methods=["GET"])
def health_check():
    """Simple health check endpoint"""
    return jsonify({"status": "healthy", "message": "Apartment tracker API is running"})


@app.route("/process-address", methods=["POST"])
def process_address():
    """Main endpoint to process apartment address"""
    try:
        # Get data from n8n webhook
        data = request.get_json()

        if not data or "address" not in data:
            return jsonify({"error": "Missing address in request"}), 400

        address = data["address"].strip()

        if not address:
            return jsonify({"error": "Address cannot be empty"}), 400

        logger.info(f"Processing address: {address}")

        # Get property data from Google Maps
        property_data = maps_handler.process_address(address)

        # Update Google Sheets
        success = sheets_handler.update_property_data(
            address=address,
            property_name=property_data["property_name"],
            car_commute=property_data["car_commute"],
            bike_commute=property_data["bike_commute"],
            transit_commute=property_data["transit_commute"],
            maps_link=property_data["maps_link"],
        )

        if success:
            response = {
                "status": "success",
                "message": f"Successfully processed {address}",
                "data": property_data,
            }
            logger.info(f"Successfully processed: {address}")
            return jsonify(response)
        else:
            return jsonify(
                {"status": "error", "message": "Failed to update Google Sheets"}
            ), 500

    except Exception as e:
        logger.error(f"Error processing address: {str(e)}")
        return jsonify(
            {"status": "error", "message": f"Internal server error: {str(e)}"}
        ), 500


@app.route("/batch-process", methods=["POST"])
def batch_process():
    """Process multiple addresses or all pending addresses"""
    try:
        data = request.get_json()

        if data and "addresses" in data:
            # Process specific addresses
            addresses = data["addresses"]
        else:
            # Process all pending addresses
            pending = sheets_handler.get_pending_addresses()
            addresses = [item["address"] for item in pending]

        if not addresses:
            return jsonify({"status": "success", "message": "No addresses to process"})

        results = []

        for address in addresses:
            try:
                logger.info(f"Batch processing: {address}")
                property_data = maps_handler.process_address(address)

                success = sheets_handler.update_property_data(
                    address=address,
                    property_name=property_data["property_name"],
                    car_commute=property_data["car_commute"],
                    bike_commute=property_data["bike_commute"],
                    transit_commute=property_data["transit_commute"],
                    maps_link=property_data["maps_link"],
                )

                results.append(
                    {
                        "address": address,
                        "status": "success" if success else "failed",
                        "data": property_data if success else None,
                    }
                )

            except Exception as e:
                logger.error(f"Error processing {address}: {str(e)}")
                results.append({"address": address, "status": "error", "error": str(e)})

        return jsonify(
            {"status": "completed", "processed": len(results), "results": results}
        )

    except Exception as e:
        logger.error(f"Error in batch processing: {str(e)}")
        return jsonify(
            {"status": "error", "message": f"Batch processing failed: {str(e)}"}
        ), 500


@app.route("/test-sheets", methods=["GET"])
def test_sheets():
    """Test endpoint to check Google Sheets connection"""
    try:
        # Test reading from sheet
        all_data = sheets_handler.worksheet.get_all_records()

        return jsonify(
            {
                "status": "success",
                "message": "Successfully connected to Google Sheets",
                "row_count": len(all_data),
                "columns": list(all_data[0].keys()) if all_data else [],
            }
        )

    except Exception as e:
        return jsonify(
            {
                "status": "error",
                "message": f"Failed to connect to Google Sheets: {str(e)}",
            }
        ), 500


@app.route("/test-maps", methods=["POST"])
def test_maps():
    """Test endpoint for Google Maps functionality"""
    try:
        data = request.get_json()
        address = data.get("address", "1600 Amphitheatre Parkway, Mountain View, CA")

        result = maps_handler.process_address(address)

        return jsonify({"status": "success", "test_address": address, "result": result})

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=Config.PORT, debug=Config.DEBUG)
