from bs4 import BeautifulSoup
from parsel import Selector 
import time
from helpers.params import YAHOO_SCREENER_BASE_URL, YAHOO_SITES_BASE_URL, YAHOO_FINANCE_INDEX_URL
from helpers.sheet import SheetManipulator


class YahooFinance:
    _index_cache = {}

    @staticmethod
    def get_index_and_link(session, stock_symbol, retries=1, delay=5):
        url = YAHOO_FINANCE_INDEX_URL.format(stock_symbol)
        for _ in range(retries):
            try:
                response = session.get(url, timeout=100)
                if response.status_code == 200:
                    sel = Selector(text=response.text)
                    index = sel.xpath('string(//span[contains(@class,"exchange")])').get()
                    return index.strip(), url
                time.sleep(delay)
            except Exception as _:
                time.sleep(delay)
        return "", url
    
    @staticmethod
    def get_index_cached(session, stock_symbol):
        """Get index from cache or fetch if not cached."""
        if stock_symbol not in YahooFinance._index_cache:
            index, _ = YahooFinance.get_index_and_link(session, stock_symbol)
            YahooFinance._index_cache[stock_symbol] = index
        return YahooFinance._index_cache[stock_symbol]
    
    @staticmethod
    def scrape_page_undervalued_growth_stocks(session, url, retries=3, delay=5):
        """Scrape the page, handling errors and crashes."""
        for _ in range(retries):
            try:
                response = session.get(url, timeout=100)
                if response.status_code == 200:
                    sel = Selector(text=response.text)
                    stocks_on_page = []
                    for tr in sel.xpath('//table//tbody//tr'):
                        td_elements = tr.xpath('.//td')
                        if len(td_elements) < 2:
                            continue
                        # Get text from each td like bs4 does
                        td_texts = [td.xpath('string()').get("").strip() for td in td_elements]
                        # Symbol
                        stock = td_texts[1] if len(td_texts) >= 2 else ""
                        stock = stock.split()[1] if len(stock.split()) >= 2 else stock
                        # Name
                        name = td_texts[2] if len(td_texts) >= 3 else ""
                        # Price intraday
                        price_intraday = td_texts[4] if len(td_texts) >= 5 else ""
                        # Change
                        change = td_texts[5] if len(td_texts) >= 6 else ""
                        # Change percent
                        change_percent = td_texts[6] if len(td_texts) >= 7 else ""
                        # P/E ratio
                        p_e_ratio = td_texts[10] if len(td_texts) >= 11 else ""
                        p_e_ratio = "=" + p_e_ratio if "+" in p_e_ratio else p_e_ratio
                        # Exchange (cached)
                        index = YahooFinance.get_index_cached(session=session, stock_symbol=stock)
                        # Link
                        link = f"https://finance.yahoo.com/quote/{stock}/"
                        # Append all column value
                        stocks_on_page.append([stock, name, index, price_intraday, change, SheetManipulator.clean_non_ascii(change_percent), link, "screener"])
                    return stocks_on_page
                time.sleep(delay)
            except Exception as _:
                time.sleep(delay)
        return []
    
    
    @staticmethod
    def scrape_page_common(session, url, yahoo_site, retries=3, delay=5):
        """Scrape the page, handling errors and crashes."""
        for _ in range(retries):
            try:
                response = session.get(url, timeout=100)
                if response.status_code == 200:
                    sel = Selector(text=response.text)
                    stocks_on_page = []
                    for tr in sel.xpath('//table//tbody//tr'):
                        td_elements = tr.xpath('.//td')
                        if len(td_elements) < 1:
                            continue
                        # Get text from each td like bs4 does
                        td_texts = [td.xpath('string()').get("").strip() for td in td_elements]
                        # Symbol
                        stock = td_texts[0] if len(td_texts) >= 1 else ""
                        # Name
                        name = td_texts[1] if len(td_texts) >= 2 else ""
                        # Price
                        price = td_texts[3] if len(td_texts) >= 4 else ""
                        price = price.split()[0] if price.split() else price
                        # Change
                        change = td_texts[4] if len(td_texts) >= 5 else ""
                        # Change percent
                        change_percent = td_texts[5] if len(td_texts) >= 6 else ""
                        # P/E ratio
                        p_e_ratio = td_texts[9] if len(td_texts) >= 10 else ""
                        p_e_ratio = "=" + p_e_ratio if "+" in p_e_ratio else p_e_ratio
                        # Exchange (cached)
                        index = YahooFinance.get_index_cached(session=session, stock_symbol=stock)
                        # Link
                        link = f"https://finance.yahoo.com/quote/{stock}/"
                        # Append all column value
                        stocks_on_page.append([stock, name, index, price, change, SheetManipulator.clean_non_ascii(change_percent), link, yahoo_site])
                    return stocks_on_page
                time.sleep(delay)
            except Exception as _:
                time.sleep(delay)
        return []


    @staticmethod
    def scrape_all_pages(session, on_screener: bool, yahoo_site="",start_page=0, number_per_page=50, page_number=20):
        """Scrape multiple pages by paging the results"""
        start = start_page
        all_stocks = []
        for _ in range(start_page, page_number):
            
            stocks_on_page = []
            if on_screener is True:
                url = YAHOO_SCREENER_BASE_URL.format(start, number_per_page)
                print(f"\t: Scrap screener : {url} ...", end='\r', flush=True)
                stocks_on_page = YahooFinance.scrape_page_undervalued_growth_stocks(session=session, url=url)
            else:
                url = YAHOO_SITES_BASE_URL.format(yahoo_site, start, number_per_page)
                print(f"\t: Scrap {yahoo_site} : {url} ...", end='\r', flush=True)
                stocks_on_page = YahooFinance.scrape_page_common(session=session, url=url, yahoo_site=yahoo_site)
            
            # There is no left stock on the sheet as our parameter is too big
            if not stocks_on_page:
                break
            
            # If not paginate break
            if len(all_stocks) >= 1 and len(stocks_on_page) >= 1 and YahooFinance.is_already_in(all_stocks=all_stocks, new_stocks_on_page=stocks_on_page) is True:
                break
            all_stocks.extend(stocks_on_page)
            start += number_per_page
        print(f"-> {len(all_stocks)} stock(s) has found on {yahoo_site if yahoo_site != '' else 'screener'}.")
        return all_stocks
    
    @staticmethod
    def is_already_in(all_stocks, new_stocks_on_page):
        for new_stock in new_stocks_on_page:
            stock_name = new_stock[0]
            for stock in all_stocks:
                if stock_name == stock[0]:
                    return True
        return False
