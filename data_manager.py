import requests
from typing import TypedDict
from pprint import pprint


class DataManager:
    """This class is responsible for talking to the Google Sheet via https://sheety.co/ service."""

    sheety_endpoint: str
    sheety_headers: dict[str, str] = {}

    class Destination(TypedDict):
        city: str
        iataCode: str
        tresholdPrice: int
        maxStopovers: int
        id: int

    destinations: list[Destination]

    def __init__(self, endpoint: str, token: str):
        self.sheety_endpoint = endpoint
        self.sheety_headers = {"Authorization": f"Bearer {token}"}

    def read_destinations(self) -> list[Destination]:
        """
        Reads destinations from google sheets and saves it as an attribute destinations
        :return: list of destination, each destination is dict:
        city: str
        iataCode: str
        tresholdPrice: int
        maxStopovers: int
        id: int
        """
        print("Reading destinations list from Google sheets")

        response = requests.get(self.sheety_endpoint, headers=self.sheety_headers)
        response.raise_for_status()
        self.destinations = response.json()["prices"]

        print("Destinations list read")
        pprint(self.destinations)
        return self.destinations

    def update_destination(self, destination_details: Destination):
        """
        Updates destination sheet in google sheet. Updates every column for given record identified by 'id'
        :param destination_details:
        :return:
        """
        print(f"updating destination_details with {destination_details}")

        row_endpoint = f"{self.sheety_endpoint}/{destination_details['id']}"
        update_params = {
            "price": {
                "city": destination_details["city"],
                "iataCode": destination_details["iataCode"],
                "tresholdPrice": destination_details["tresholdPrice"],
                "maxStopovers": destination_details["maxStopovers"],
            }
        }
        response = requests.put(
            row_endpoint, json=update_params, headers=self.sheety_headers
        )
        response.raise_for_status()
