from bs4 import BeautifulSoup
import time
from helpers.params import HEADERS, ALPHA_SPREAD_BASE_URL
import requests
import random
from helpers.sheet import SheetManipulator


# New update, 19/6/2025 , add Exchange map to pass security type
EXCHANGE_MAP = {
    "NasdaqGS": "nasdaq",
    "NasdaqCM": "nasdaq",
    "Nasdaq": "nasdaq",
    "NYSE": "nyse",
    "NYSEArca": "nysearca",
    "OTC": "otc",
}

class AlphaSpread:
    @staticmethod
    def get_security_type(stock_symbol):
        url = f"https://finance.yahoo.com/quote/{stock_symbol}"
        for _ in range(3):
            try:
                response = requests.get(url, headers=HEADERS, timeout=10)
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, "html.parser")
                    exchange_element = soup.find("span", class_="exchange")
                    if exchange_element:
                        exchange = exchange_element.get_text(strip=True).split()[0]  # Get "NYSE", "OTC", etc.
                        
                        # Map the value to exchange map, if not return stock
                        slug = EXCHANGE_MAP.get(exchange, "stock")
                        return slug
                elif response.status_code == 403:
                    print(f"🚫 Yahoo blocked request for {stock_symbol}. Retrying...")
                    time.sleep(random.uniform(3, 7))
            except Exception as e:
                print(f"⚠️ Error fetching security type for {stock_symbol}: {e}")
            time.sleep(random.uniform(5, 10))
        return "stock"

    @staticmethod
    def scrape_dcf_pct(stock_symbol, retries=1, delay=5):
        """Scrape the page, handling errors and crashes."""
        security_type = AlphaSpread.get_security_type(stock_symbol=stock_symbol)
        url = ALPHA_SPREAD_BASE_URL.format(security_type, stock_symbol)
        print(url)
        for i in range(retries):
            try:
                response = requests.get(url, headers=HEADERS, timeout=10)
                print(response.status_code)
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, "html.parser")
                    stock_details = []
                    
                    # Price
                    price = soup.select(".ui.top.attached.small.black.label .color-grey-100")
                    price = price[0].get_text(strip=True) if len(price) >= 1 else ""
                    # DCF
                    dcf = soup.select(".dcf-value-color.no-margin.valuation-scenario-value.header.restriction-sensitive-data")
                    dcf = dcf[0].get_text(strip=True) if len(dcf) >= 1 else ""
                    # Undervaluation
                    undervaluation = soup.select(".opacity-90.space-no-wrap")
                    undervaluation = undervaluation[0].get_text(strip=True) if len(undervaluation) >= 1 else ""
                    undervaluation = undervaluation.split()[1] if undervaluation != "" else ""
                    
                    stock_details.extend([SheetManipulator.clean_non_ascii(dcf), SheetManipulator.clean_non_ascii(undervaluation)])
                    print(stock_details)
                    return stock_details
                time.sleep(delay)
            except Exception as e:
                print(e)
                time.sleep(delay)
        return ["", ""]