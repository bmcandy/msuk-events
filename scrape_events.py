import requests
import json
import argparse
from datetime import datetime, timedelta

def scrape_events(output_file):
    url = "https://motorsportuk.sport80.com/api/public/events/locator/data"
    today = datetime.now()
    from_date = today.strftime("%Y-%m-%d")
    to_date = (today + timedelta(days=90)).strftime("%Y-%m-%d")
    events = []
    page = 0
    print(f"Scraping events from {from_date} to {to_date}...")
    while True:
        query_params = {
            "p": page,  # Pagination parameter
            "i": 100    # Number of results per page
        }
        payload = {
            "from_date": from_date,
            "to_date": to_date,
            "event_type": "1",  # Ensure values are strings for form data
            "region": None
        }
        form_data = {k: v for k, v in payload.items() if v is not None}
        response = requests.post(f"{url}?p={query_params['p']}&i={query_params['i']}&s=&l=&d=10&f=", data=form_data)
        if response.status_code != 200:
            print(f"Error: Received status code {response.status_code} from the server.")
            break
        response.raise_for_status()
        page_events = response.json()
        print(f"Page {page}: Retrieved {len(page_events['data'])} events.")
        if not page_events['data'] or len(page_events['data']) < 100:
            events.extend(page_events["data"])
            print(f"End of data reached at page {page}.")
            break
        events.extend(page_events["data"])
        page += 1

    with open(output_file, "w") as f:
        json.dump(events, f, indent=4)
    print(f"Events data saved to {output_file}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Scrape Motorsport UK events.")
    parser.add_argument("--output", required=True, help="Output JSON file")
    args = parser.parse_args()
    scrape_events(args.output)
