class FlightData:
    # This class is responsible for structuring the flight data.
    def __init__(
        self,
        price: int,
        departure_airport: str,
        destination_airport: str,
        out_date: str,
        return_date: str,
        deep_link: str,
    ):
        self.price = price
        self.departure_airport = departure_airport
        self.destination_airport = destination_airport
        self.out_date = out_date
        self.return_date = return_date
        self.deep_link = deep_link
