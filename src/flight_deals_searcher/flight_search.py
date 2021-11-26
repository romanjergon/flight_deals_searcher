import datetime
import logging
from typing import Any
import requests

from flight_deals_searcher.flight_data import FlightData


class FlightSearch:
    """This class is responsible for talking to the KIWI Flight Search API."""

    kiwi_endpoint: str
    kiwi_headers: dict[str, str]
    departure_code: str
    date_from_period: int
    date_to_period: int

    def __init__(
        self,
        departure_code: str,
        search_period_start: int,
        search_period_end: int,
        kiwi_endpoint: str,
        kiwi_api_key: str,
    ):
        self.departure_code = departure_code
        self.date_from_period = search_period_start
        self.date_to_period = search_period_end
        self.kiwi_endpoint = kiwi_endpoint
        self.kiwi_headers = {"apikey": kiwi_api_key}

    def get_iata_city_code(self, city: str) -> str:
        """
        Searches IATA code for given city, note this is city code, not code of any particual airport as there are cities with more then one airports.
        :param city: general name of city, e.g. Rome
        :return: IATA code for flight search
        """
        logging.info(f"searching IATA city code for {city}")

        city_search_params = {"term": city, "location_types": "city"}
        iata_city_code_response = requests.get(
            f"{self.kiwi_endpoint}/locations/query",
            params=city_search_params,
            headers=self.kiwi_headers,
        )
        iata_city_code_response.raise_for_status()
        iata_city_code: str = iata_city_code_response.json()["locations"][0]["code"]
        logging.info(f"Success IATA city code for {city} found {iata_city_code}")
        return iata_city_code

    def search_flights(
        self,
        destination: str,
        price_threshold: int,
        max_stopovers: int,
        min_nights: int,
        max_nights: int,
    ) -> list[FlightData]:
        """
        Searches all flights by given parameters
        :param destination: IATA code of destination city/airport
        :param price_threshold: Maximum price of flight in EUR
        :param max_stopovers:
        :param min_nights: Minimum number of nights in destination
        :param max_nights: Max number of nights in destination
        :return: none if no flight was found, list of flight_data if successful. List is ordered by price ascending as provided by Kiwi API
        """
        logging.info(
            f"Searching flight to {destination}, for {max_stopovers} \
            max_stopovers and {min_nights} to {max_nights} nights."
        )

        flight_search_params: dict[str, Any] = {
            "fly_from": self.departure_code,
            "fly_to": destination,
            "date_from": datetime.date.today()
            + datetime.timedelta(days=self.date_from_period),
            "date_to": datetime.date.today()
            + datetime.timedelta(days=self.date_to_period),
            "flight_type": "round",
            "max_stopovers": max_stopovers,
            "price_to": price_threshold,
            "nights_in_dst_from": min_nights,
            "nights_in_dst_to": max_nights,
            "curr": "EUR",
            "one_for_city": 1,
        }

        flight_search_response = requests.get(
            f"{self.kiwi_endpoint}/search",
            params=flight_search_params,
            headers=self.kiwi_headers,
        )

        flight_search_response.raise_for_status()

        flights_data = flight_search_response.json()["data"]
        logging.info(f"Found {len(flights_data)} flights")
        logging.debug(flights_data)

        result_flights: list[FlightData] = []

        for flight_source in flights_data:
            out_date = datetime.datetime.fromtimestamp(
                flight_source["route"][0]["dTime"]
            ).isoformat()
            return_date = ""

            # find first return route flight
            for route in flight_source["route"]:
                if route["return"] == 1:
                    return_date = datetime.datetime.fromtimestamp(
                        route["dTime"]
                    ).isoformat()
                    break

            flight = FlightData(
                price=flight_source["price"],
                departure_airport=flight_source["flyFrom"],
                destination_airport=flight_source["flyTo"],
                out_date=out_date,
                return_date=return_date,
                deep_link=flight_source["deep_link"],
            )
            result_flights.append(flight)

        return result_flights
