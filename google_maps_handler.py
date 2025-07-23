import googlemaps
from config import Config
import logging


class GoogleMapsHandler:
    def __init__(self):
        self.gmaps = googlemaps.Client(key=Config.GOOGLE_MAPS_API_KEY)
        self.office_address = Config.SHOPIFY_OFFICE_ADDRESS

    def get_property_name(self, address):
        """Get property name from address using Google Places API"""
        try:
            # Geocode the address to get more details
            geocode_result = self.gmaps.geocode(address)

            if not geocode_result:
                return "Property name not found"

            # Extract property name from place details
            place_id = geocode_result[0]["place_id"]
            place_details = self.gmaps.place(place_id=place_id)

            # Try to get the property name
            if "result" in place_details:
                name = place_details["result"].get("name", "N/A")
                return name if name != "N/A" else address.split(",")[0]

            return address.split(",")[0]  # Fallback to first part of address

        except Exception as e:
            logging.error(f"Error getting property name: {str(e)}")
            return "Error retrieving name"

    def get_commute_times(self, address):
        """Get commute times by car, bike, and public transport from address to Shopify office"""
        try:
            # Get directions for driving
            car_directions = self.gmaps.directions(
                origin=address,
                destination=self.office_address,
                mode="driving",
                departure_time="now",
                traffic_model="best_guess",
            )

            # Get directions for bicycling
            bike_directions = self.gmaps.directions(
                origin=address, destination=self.office_address, mode="bicycling"
            )

            # Get directions for public transport
            transit_directions = self.gmaps.directions(
                origin=address,
                destination=self.office_address,
                mode="transit",
                departure_time="now",
            )

            # Extract duration
            car_time = "N/A"
            bike_time = "N/A"
            transit_time = "N/A"

            if car_directions:
                car_duration = car_directions[0]["legs"][0].get("duration_in_traffic")
                car_time = (
                    car_duration["text"]
                    if car_duration
                    else car_directions[0]["legs"][0]["duration"]["text"]
                )

            if bike_directions:
                bike_time = bike_directions[0]["legs"][0]["duration"]["text"]

            if transit_directions:
                transit_time = transit_directions[0]["legs"][0]["duration"]["text"]

            return {
                "car_time": car_time,
                "bike_time": bike_time,
                "transit_time": transit_time,
            }

        except Exception as e:
            logging.error(f"Error getting commute times: {str(e)}")
            return {"car_time": "Error", "bike_time": "Error", "transit_time": "Error"}

    def get_google_maps_link(self, address):
        """Generate a Google Maps link for the address"""
        try:
            # URL encode the address for Google Maps
            import urllib.parse

            encoded_address = urllib.parse.quote(address)
            maps_link = f"https://www.google.com/maps/place/{encoded_address}"
            return maps_link
        except Exception as e:
            logging.error(f"Error generating maps link: {str(e)}")
            return "Error generating link"

    def process_address(self, address):
        """Main function to process an address and return all data"""
        property_name = self.get_property_name(address)
        commute_times = self.get_commute_times(address)
        maps_link = self.get_google_maps_link(address)

        return {
            "property_name": property_name,
            "car_commute": commute_times["car_time"],
            "bike_commute": commute_times["bike_time"],
            "transit_commute": commute_times["transit_time"],
            "maps_link": maps_link,
        }
