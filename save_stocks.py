import requests
from helpers.params import HEADERS, YAHOO_SITES_NAME
from web_site.yahoo_finance import YahooFinance
import traceback
import json

# Persistent session to avoid lockouts
session = requests.Session()
session.headers.update(HEADERS)

if __name__ == "__main__":
    all_stocks = []
    try:
        print("+--------------------------------------------------------+")
        print("+--------------------- START ----------------------------+")
        print("+--------------------------------------------------------+")
        # ---------------------------------------------------------- SAVE STOCK FROM YAHOO -------------------------------------
        # Get all stocks from all 6 other
        for site in YAHOO_SITES_NAME:
            all_stocks.extend(YahooFinance.scrape_all_pages(session=session, on_screener=False, yahoo_site=site))
        # Write result in file
        with open("stocks.json", "w", encoding="utf-8") as f:
            json.dump(all_stocks, f, ensure_ascii=False, indent=None)
    except Exception as e:
        # Save scraped data
        with open("stocks.json", "w", encoding="utf-8") as f:
            json.dump(all_stocks, f, ensure_ascii=False, indent=None)
        traceback.print_exc()
        print("+--------------------------------------------------------+")
        print("+--------------------- ERROR ----------------------------+")
        print("+--------------------------------------------------------+")