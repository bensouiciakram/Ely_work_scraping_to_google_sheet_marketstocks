from bs4 import BeautifulSoup
import time
from helpers.sheet import SheetManipulator
from helpers.params import GURUS_BASE_URL
import time
from playwright.sync_api import sync_playwright
from helpers.params import HEADERS

from parsel import Selector 
from playwright_stealth import Stealth

class Gurus:
    @staticmethod
    def scrape_dcf_pct(stock_symbol, retries=2, delay=5):
        """Scrape the page, handling errors and crashes."""
        url = GURUS_BASE_URL.format(stock_symbol)
        for i in range(retries):
            try:
                # with sync_playwright() as p:
                with Stealth().use_sync(sync_playwright()) as p : 
                    browser = p.chromium.launch(headless=True)
                    context = browser.new_context(user_agent=HEADERS["User-Agent"])
                    context.set_default_navigation_timeout(60000)
                    page = context.new_page()
                    page.goto(url)
                    page.wait_for_timeout(5000)
                    page.wait_for_selector('//div[contains(@class,"dcf-table-row")]')
                    selector = Selector(text=page.content())

                    stock_details = []

                    # Extract Stock Price
                    stock_price = selector.xpath('string(//div[@class="summary capture-area"]/span)').re_first(r'\d+\.\d+')

                    # Extract Fair Value
                    fair_value = selector.xpath(
                        'string(//div[contains(text(),"Fair Value")]/ancestor::div[1]/following-sibling::div)'
                        ).get('').strip()
                    
                    # Extract Margin of Safety
                    margin_of_safety = selector.xpath(
                        '//div[contains(text(),"Margin of Safety")]/ancestor::div[1]/following-sibling::div//i/following-sibling::text()'
                        ).get('').strip()
                    
                    # Clean up and store the extracted details
                    stock_details.extend([SheetManipulator.clean_non_ascii(fair_value), SheetManipulator.clean_non_ascii(margin_of_safety)])

                    # Return the collected stock details
                    browser.close()
                    return stock_details
                time.sleep(delay)
            except Exception as e:
                print(e)
                time.sleep(delay)

        # If all retries fail, return empty values
        return ["", ""]