import os
import logging

import flight_deals_searcher.data_manager
import flight_deals_searcher.flight_search
import flight_deals_searcher.mail_notifier
from flight_deals_searcher.flight_data import FlightData

from dotenv import load_dotenv

load_dotenv()


def update_lowest_price(
    dest: flight_deals_searcher.data_manager.DataManager.Destination,
    flights: list[FlightData],
    data_man: flight_deals_searcher.data_manager.DataManager,
) -> None:
    changed_price = False
    for flight in flights:
        # Type dirty hack but this is what we get from sheety
        if dest["lowestPriceDetected"] == "":  # type: ignore[comparison-overlap]
            dest["lowestPriceDetected"] = flight.price
            changed_price = True
        elif dest["lowestPriceDetected"] > flight.price:
            dest["lowestPriceDetected"] = flight.price
            changed_price = True
    # update data in google sheet
    if changed_price:
        data_man.update_destination(dest)


def main() -> None:
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s %(levelname)s:%(message)s"
    )
    # region constants
    DEPARTURE_CODE = "PRG"
    SEARCH_PERIOD_START = 1
    SEARCH_PERIOD_END = 180
    SHEETY_ENDPOINT = (
        "https://api.sheety.co/4be43daa7f211de4f250b73f8449ee74/flightDeals/prices"
    )
    KIWI_ENDPOINT = "http://tequila-api.kiwi.com"
    SMTP_HOST = "smtp.gmail.com"
    SMTP_PORT = 587
    # endregion

    # region load env vars
    sheety_token = os.environ["SHEETY_TOKEN"]
    kiwi_apiKey = os.environ["KIWI_API_KEY"]
    notification_mailbox = os.environ["NOTIFICATION_MAILBOX"]
    mail_password = os.environ["MAIL_PASSWORD"]
    personal_mailbox = os.environ["PERSONAL_MAILBOX"]
    # endregion

    # get destinations from sheety
    dm = flight_deals_searcher.data_manager.DataManager(SHEETY_ENDPOINT, sheety_token)
    dm.read_destinations()

    flight_searcher = flight_deals_searcher.flight_search.FlightSearch(
        departure_code=DEPARTURE_CODE,
        kiwi_api_key=kiwi_apiKey,
        kiwi_endpoint=KIWI_ENDPOINT,
        search_period_start=SEARCH_PERIOD_START,
        search_period_end=SEARCH_PERIOD_END,
    )
    mailer_notifier = flight_deals_searcher.mail_notifier.MailNotifier(
        smtp_host=SMTP_HOST,
        smtp_port=SMTP_PORT,
        notification_mailbox=notification_mailbox,
        personal_mailbox=personal_mailbox,
        mail_password=mail_password,
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
            destination["thresholdPrice"],
            destination["maxStopovers"],
            destination["minNights"],
            destination["maxNights"],
        )
        # If any flight is found, send details in mail notification
        if len(flights) > 0:
            mail_subject = f"Air ticket price {destination['city']} alert"
            mail_body = (
                f"Cheap tickets from {DEPARTURE_CODE} to {destination['city']}\n "
            )
            for flight in flights:
                mail_body += f"Flight from {flight.departure_airport} to {flight.destination_airport} \
                just for {flight.price} Euro, departure on {flight.out_date}, \
                return on {flight.return_date}, book at {flight.deep_link}\n "
            mailer_notifier.send_notif_mail(mail_subject, mail_body)

            # update detected lowest price
            update_lowest_price(destination, flights, dm)


if __name__ == "__main__":
    main()
