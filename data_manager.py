from typing import TypedDict
import logging
import requests


class DataManager:
    """This class is responsible for talking to the Google Sheet via https://sheety.co/ service."""

    class Destination(TypedDict):
        city: str
        iataCode: str
        thresholdPrice: int
        lowestPriceDetected: int
        maxStopovers: int
        minNights: int
        maxNights: int
        id: int

    sheety_endpoint: str
    sheety_headers: dict[str, str] = {}
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
        thresholdPrice: int
        lowestPriceDetected: int
        maxStopovers: int
        minNights: int
        maxNights: int
        id: int
        """
        logging.info("Reading destinations list from Google sheets")

        response = requests.get(self.sheety_endpoint, headers=self.sheety_headers)
        response.raise_for_status()
        self.destinations = response.json()["prices"]

        logging.info("Destinations list read")
        logging.info(self.destinations)
        return self.destinations

    def update_destination(self, destination_details: Destination):
        """
        Updates destination sheet in google sheet. Updates every column for given record identified by 'id'
        :param destination_details:
        :return:
        """
        logging.info(f"updating destination_details with {destination_details}")

        row_endpoint = f"{self.sheety_endpoint}/{destination_details['id']}"
        update_params = {
            "price": {
                "city": destination_details["city"],
                "iataCode": destination_details["iataCode"],
                "thresholdPrice": destination_details["thresholdPrice"],
                "lowestPriceDetected": destination_details["lowestPriceDetected"],
                "maxStopovers": destination_details["maxStopovers"],
                "minNights": destination_details["minNights"],
                "maxNights": destination_details["maxNights"],
            }
        }
        response = requests.put(
            row_endpoint, json=update_params, headers=self.sheety_headers
        )
        response.raise_for_status()
