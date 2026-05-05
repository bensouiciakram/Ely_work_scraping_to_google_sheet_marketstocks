# PERSONAL GOOGLE SHEET URL
# SHEET_URL = "https://docs.google.com/spreadsheets/d/1QBcRAVQKwmZgd9HRl5kNoNr_Na-3dKT7NXIVzu_6-ls/edit?gid=0#gid=0"

# CLIENT GOOGLE SHEET URL
SHEET_URL = "https://docs.google.com/spreadsheets/d/1nWLVF4DKaGE-IUOkRjyLG3Tr6af1oa7ZeM9WoYMoHKU/edit?gid=249601463#gid=249601463"
# SHEET_URL = "https://docs.google.com/spreadsheets/d/1A8SfGTTAmEnwo_lpgyknNa0bDjmohvf1ko0eIXu2bgM/edit?gid=0#gid=0"
SHEET_NAME = "Stock Price & DCF Websites"
# WEB SITE URL FOR SCRAPING
YAHOO_SCREENER_BASE_URL = "https://finance.yahoo.com/research-hub/screener/undervalued_growth_stocks/?start={}&count={}"
YAHOO_SITES_NAME = [ "most-active", "trending", "gainers", "losers", "52-week-gainers", "52-week-losers"]
YAHOO_SITES_BASE_URL = "https://finance.yahoo.com/markets/stocks/{}/?start={}&count={}"
YAHOO_FINANCE_INDEX_URL = "https://finance.yahoo.com/quote/{}/"
ALPHA_SPREAD_BASE_URL = "https://www.alphaspread.com/security/{}/{}/dcf-valuation/base-case"
GURUS_BASE_URL = "https://www.gurufocus.com/stock/{}/dcf"
VALUE_INVESTING_BASE_URL = "https://valueinvesting.io/{}/valuation/dcf-growth-exit-5y"
# SRAPING PARAMS
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36"
}
