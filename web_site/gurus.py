from bs4 import BeautifulSoup
import time
import random
import re
from helpers.sheet import SheetManipulator
from helpers.params import GURUS_BASE_URL
from playwright.sync_api import sync_playwright
from helpers.params import HEADERS

from parsel import Selector 
from playwright_stealth import Stealth
from playwright.sync_api import TimeoutError,Page
import logging

from DrissionPage import ChromiumPage, ChromiumOptions
from RecaptchaSolver import RecaptchaSolver 

class Gurus:

    @staticmethod
    def _init_driver(proxy=None, headless=True):
        """Initialize DrissionPage browser with anti-detection configuration"""
        options = ChromiumOptions()
        options.set_argument('--no-sandbox')
        options.set_argument('--disable-blink-features=AutomationControlled')
        options.set_argument('--disable-dev-shm-usage')
        options.set_argument('--disable-gpu')
        options.set_argument('--remote-debugging-port=56221')
        options.set_argument('--user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36')
        #if headless:
            #options.set_argument('--headless=new')
        driver = ChromiumPage(addr_or_opts=options)
        return driver

    @staticmethod
    def _solve_captchas(driver):
        """Handle CAPTCHA challenges"""
        try:
            if driver.ele('#captcha-form', timeout=5) or \
               driver.ele('iframe[src*="recaptcha"]', timeout=5):
                logging.info("CAPTCHA detected, solving...")
                solver = RecaptchaSolver(driver)
                solver.solveCaptcha()
                time.sleep(random.uniform(3, 6))
                return True
        except Exception as e:
            logging.error(f"CAPTCHA solving failed: {str(e)}")
        return False

    @staticmethod
    def _human_delay():
        """Randomized human-like interaction delays"""
        time.sleep(random.uniform(3, 7))

    @staticmethod
    def _extract_from_google_results(driver, stock_symbol):
        """Extract Fair Value from Google search results using XPath"""
        guru_links = driver.eles('xpath://div[@id="center_col"]//a[contains(@href,"gurufocus")]')
        
        fair_value = ""
        for link in guru_links:
            link_text = link.text
            if "Intrinsic Value: DCF (FCF Based)" in link_text and stock_symbol.upper() in link_text.upper():
                match = re.search(r'-?\d+\.\d+', link_text)
                if match:
                    fair_value = match.group(0)
                    logging.info(f"Fair Value extracted: {fair_value} from: {link_text.strip()}")
                    break
        
        if not fair_value:
            logging.warning("Fair Value not found in Google results")
        
        return [fair_value, ""]

    @staticmethod
    def _get_google_search_url(ticker, counter):
        """Generate Google search URL with domain rotation"""
        domains = [
            "https://www.google.com/search?q={}+Intrinsic+Value:+DCF+(FCF+Based)+site:gurufocus.com",
            "https://www.google.ca/search?q={}+Intrinsic+Value:+DCF+(FCF+Based)+site:gurufocus.com",
            "https://www.google.co.uk/search?q={}+Intrinsic+Value:+DCF+(FCF+Based)+site:gurufocus.com",
            "https://www.google.com.au/search?q={}+Intrinsic+Value:+DCF+(FCF+Based)+site:gurufocus.com"
        ]
        return domains[counter % len(domains)].format(ticker)

    @staticmethod
    def smart_reload(page):
        for _ in range(5): 
            try :
                page.wait_for_selector('//div[contains(@class,"dcf-table-row")]',timeout=5000)
            except TimeoutError: 
                logging.info('Page didn\'t load properly')
                page.reload()
                continue 
            return 

    # @staticmethod
# def scrape_dcf_pct(stock_symbol, retries=2, delay=5):
#     """Scrape the page, handling errors and crashes."""
#     url = GURUS_BASE_URL.format(stock_symbol)
#     for i in range(retries):
#         try:
#             # with sync_playwright() as p:
#             with Stealth().use_sync(sync_playwright()) as p : 
#                 browser = p.chromium.launch(headless=True)
#                 context = browser.new_context(user_agent=HEADERS["User-Agent"])
#                 context.set_default_navigation_timeout(60000)
#                 page = context.new_page()
#                 page.goto(url)
#                 page.wait_for_timeout(5000)
#                 Gurus.smart_reload(page)
#                 selector = Selector(text=page.content())

#                 stock_details = []

#                 # Extract Stock Price
#                 stock_price = selector.xpath('string(//div[@class="summary capture-area"]/span)').re_first(r'\d+\.\d+')

#                 # Extract Fair Value
#                 fair_value = selector.xpath(
#                     'string(//div[contains(text(),"Fair Value")]/ancestor::div[1]/following-sibling::div)'
#                     ).get('').strip()
                
#                 # Extract Margin of Safety
#                 margin_of_safety = selector.xpath(
#                     '//div[contains(text(),"Margin of Safety")]/ancestor::div[1]/following-sibling::div//i/following-sibling::text()'
#                     ).get('').strip()
                
#                 # Clean up and store the extracted details
#                 stock_details.extend([SheetManipulator.clean_non_ascii(fair_value), SheetManipulator.clean_non_ascii(margin_of_safety)])

#                 # Return the collected stock details
#                 browser.close()
#                 return stock_details
#             time.sleep(delay)
#         except Exception as e:
#             print(e)
#             time.sleep(delay)

#     # If all retries fail, return empty values
#     return ["", ""]

    @staticmethod
    def scrape_via_google(stock_symbol, retries=2, delay=5):
        """
        Extract GuruFocus DCF data from Google search results only.
        No navigation to GuruFocus - extracts from Google snippet text.
        Returns: ["fair_value", "margin_of_safety"] or ["", ""]
        """
        for attempt in range(retries):
            driver = None
            try:
                driver = Gurus._init_driver(headless=True)
                
                search_url = Gurus._get_google_search_url(stock_symbol, attempt)
                logging.info(f"Google search attempt {attempt + 1}: {search_url}")
                
                driver.get(search_url)
                Gurus._human_delay()
                
                stock_details = Gurus._extract_from_google_results(driver, stock_symbol)
                driver.quit()
                
                if stock_details[0] or stock_details[1]:
                    logging.info(f"Successfully scraped {stock_symbol}: {stock_details}")
                    return stock_details
                
                if attempt < retries - 1:
                    time.sleep(delay)
                    continue
                    
            except Exception as e:
                logging.error(f"Error in scrape_via_google for {stock_symbol} (attempt {attempt + 1}): {str(e)}")
                if driver:
                    try:
                        driver.quit()
                    except:
                        pass
                if attempt < retries - 1:
                    time.sleep(delay)
                    continue
        
        return ["", ""]