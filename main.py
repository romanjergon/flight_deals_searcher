import os
import dotenv

import data_manager
import flight_search


def main():
    DEPARTURE_CODE = "PRG"
    SEARCH_PERIOD_START = 1
    SEARCH_PERIOD_END = 180
    # load env vars
    dotenv.load_dotenv()
    sheety_token = os.environ["SHEETY_TOKEN"]
    sheety_endpoint = os.environ["SHEETY_ENDPOINT"]
    # get destinations from sheety
    dm = data_manager.DataManager(sheety_endpoint, sheety_token)
    dm.read_destinations()

    kiwi_apiKey = os.environ["KIWI_API_KEY"]
    kiwi_endpoint = os.environ["KIWI_ENDPOINT"]
    flight_searcher = flight_search.FlightSearch(
        departure_code=DEPARTURE_CODE,
        kiwi_api_key=kiwi_apiKey,
        kiwi_endpoint=kiwi_endpoint,
        search_period_start=SEARCH_PERIOD_START,
        search_period_end=SEARCH_PERIOD_END,
    )
    # for destinations without codes search for codes
    for destination in dm.destinations:
        if destination["iataCode"] == "":
            destination["iataCode"] = flight_searcher.get_iata_city_code(
                city=destination["city"]
            )
            # save destination codes back to sheet
            dm.update_destination(destination)

    # for each destination search flights
    for destination in dm.destinations:
        flights = flight_searcher.search_flights(
            destination["iataCode"],
            destination["tresholdPrice"],
            destination["maxStopovers"],
        )
        print(flights)


#     if len(flights) > 0:
# if the flight is cheaper than data set threshold then send notification


if __name__ == "__main__":
    main()
