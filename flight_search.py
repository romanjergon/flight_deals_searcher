import requests
import datetime
from flight_data import FlightData


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

    def get_iata_city_code(self, city: str):
        """
        Searches IATA code for given city, note this is city code, not code of any particual airport as there are cities with more then one airports.
        :param city:
        :return: IATA code for flight search
        """
        print(f"searching IATA city code for {city}")

        city_search_params = {"term": city, "location_types": "city"}
        iata_city_code_response = requests.get(
            f"{self.kiwi_endpoint}/locations/query",
            params=city_search_params,
            headers=self.kiwi_headers,
        )
        iata_city_code_response.raise_for_status()
        iata_city_code = iata_city_code_response.json()["locations"][0]["code"]
        print(f"Success IATA city code for {city} found {iata_city_code}")
        return iata_city_code

    def search_flights(
        self,
        destination: str,
        price_treshold: int,
        max_stopovers: int,
    ) -> FlightData:
        """
        Searches all flights by given parameters
        :param destination:
        :param price_treshold:
        :param max_stopovers:
        :return: none if no flight was found, list of flight_data if successful. List is ordered by price ascending as provided by Kiwi API
        """
        print(f"Searching flight to {destination}, for {max_stopovers} max_stopovers")

        flight_search_params: dict[str, object] = {
            "fly_from": self.departure_code,
            "fly_to": destination,
            "date_from": datetime.date.today()
            + datetime.timedelta(days=self.date_from_period),
            "date_to": datetime.date.today()
            + datetime.timedelta(days=self.date_to_period),
            "flight_type": "round",
            "max_stopovers": max_stopovers,
            "price_to": price_treshold,
        }

        flight_search_response = requests.get(
            f"{self.kiwi_endpoint}/search",
            params=flight_search_params,
            headers=self.kiwi_headers,
        )

        flight_search_response.raise_for_status()

        if len(flight_search_response.json()["data"]) > 0:
            cheapest_flight = flight_search_response.json()["data"][0]
            flight = FlightData(
                price=cheapest_flight["price"],
                origin_airport=cheapest_flight["flyFrom"],
                destination_airport=cheapest_flight["flyTo"],
                out_date=cheapest_flight["dTime"],
                return_date=cheapest_flight["aTime"],
            )
            return flight


def location_search_test():
    fs = FlightSearch()
    print(fs.get_iata_city_code("Rome"))


def flight_search_test():
    fs = FlightSearch()
    print(fs.search_flights("ROM", 3))


if __name__ == "__main__":
    flight_search_test()
