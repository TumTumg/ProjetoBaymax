import requests
from geopy.geocoders import Nominatim

class DataAnalysis:
    def __init__(self):
        self.geolocator = Nominatim(user_agent="campus_navigation")

    def get_location_from_coordinates(self, latitude, longitude):
        location = self.geolocator.reverse((latitude, longitude))
        return location.address

    def get_directions(self, origin, destination):
        url = f"https://router.project-osrm.org/route/v1/driving/{origin[1]},{origin[0]};{destination[1]},{destination[0]}?overview=false"
        response = requests.get(url)
        directions = response.json()["routes"][0]["legs"][0]["steps"]
        return [step["maneuver"]["instruction"] for step in directions]
