import pytest
import os
from flight_deals_searcher.flight_search import FlightSearch
from dotenv import load_dotenv


load_dotenv()


#@pytest.mark.skip(reason="no way of currently testing this without .env file")
def test_flight_search():
    flight_searcher = FlightSearch(
        departure_code="PRG",
        kiwi_api_key=os.environ["KIWI_API_KEY"],
        kiwi_endpoint="http://tequila-api.kiwi.com",
        search_period_start=1,
        search_period_end=180,
    )

    threshold_price = 500
    search_results = flight_searcher.search_flights("ROM", threshold_price, 1, 2, 8)

    assert len(search_results) > 0, "should be more than 0"
    assert (
        search_results[0].departure_airport == "PRG"
    ), "should be PRG since that was input param"
    assert search_results[0].deep_link is not None, "deep_link should have value"
    assert search_results[0].deep_link != "", "deep_link should not be empty string"
    assert search_results[0].price < threshold_price, "should be less than input "
