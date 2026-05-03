from bs4 import BeautifulSoup
import time
from helpers.sheet import SheetManipulator
from helpers.params import GURUS_BASE_URL
import time
from playwright.sync_api import sync_playwright
from helpers.params import HEADERS

class Gurus:
    @staticmethod
    def scrape_dcf_pct(stock_symbol, retries=2, delay=5):
        """Scrape the page, handling errors and crashes."""
        url = GURUS_BASE_URL.format(stock_symbol)
        for i in range(retries):
            try:
                with sync_playwright() as p:
                    browser = p.chromium.launch(headless=True)
                    context = browser.new_context(user_agent=HEADERS["User-Agent"])
                    page = context.new_page()
                    page.goto(url)
                    page.wait_for_timeout(5000)
                    content = page.content()

                    # Parse the content with BeautifulSoup
                    soup = BeautifulSoup(content, "html.parser")
                    stock_details = []

                    # Extract Stock Price
                    stock_price = soup.select(".el-col.inline.p-l-xs .stock-dcf-table .text-right.fs-regular.el-col.el-col-8")
                    stock_price = stock_price[0].get_text(strip=True) if len(stock_price) >= 1 else ""
                    
                    # Extract Fair Value
                    fair_value = soup.select(".el-col.inline.p-l-xs .stock-dcf-table .fs-x-large.fw-bolder.text-right.el-col.el-col-12")
                    fair_value = fair_value[0].get_text(strip=True) if len(fair_value) >= 1 else ""
                    
                    # Extract Margin of Safety
                    margin_of_safety = soup.select(".el-col.inline.p-l-xs .stock-dcf-table .dcf-result")
                    margin_of_safety = margin_of_safety[0].get_text(strip=True) if len(margin_of_safety) >= 1 else ""
                    
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