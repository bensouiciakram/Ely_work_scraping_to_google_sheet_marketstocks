from helpers.sheet import SheetManipulator
from helpers.params import SHEET_URL, SHEET_NAME
from web_site.value_investing import ValueInvesting
from web_site.alpha_spread import AlphaSpread
from web_site.gurus import Gurus
import json
import asyncio
import logging

logging.basicConfig(
    filename="scrap_details.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    filemode="w"
)

if __name__ == "__main__":
    try:
        print("+--------------------------------------------------------+")
        print("+--------------------- START ----------------------------+")
        print("+--------------------------------------------------------+")
        logging.info("Script started")
        
        # ---------------------------------------------------------- LOAD STOCK FROM FILE -------------------------------------
        # Load data from JSON file
        with open("stocks.json", "r", encoding="utf-8") as f:
            all_stocks = json.load(f)
        logging.info(f"Loaded {len(all_stocks)} stocks from stocks.json")
        remove_index = []
        
        # Sheet parameter
        credentials, service = SheetManipulator.get_credentials_and_service()
        spreadsheet_id = SheetManipulator.get_spreadsheet_id(SHEET_URL)
        
        # Build ticker -> row_index map from existing sheet data
        existing_data = SheetManipulator.get_all_stocks(spreadsheet_id, service)
        ticker_to_row = {row[0]: row[-1] for row in reversed(existing_data) if row[0]}
        logging.info(f"Built ticker map with {len(ticker_to_row)} existing tickers")
        
        # service.spreadsheets().values().clear(
        #     spreadsheetId=spreadsheet_id,
        #     range=f"'{SHEET_NAME}'!A2:Z"
        # ).execute()
        current_beginning_of_stock_index = 0
        # Append value_investing / gurus scraping
        for index, stock in enumerate(all_stocks):
            try:
                # Get key
                stock_symbol = stock[0]
                if stock_symbol in ["", None]:
                    remove_index.append(index)
                else:
                    print(f"{index + 1}\t: Scrap details {index + 1} / {stock_symbol} ...", end='\r', flush=True)
                    logging.info(f"Scraping {stock_symbol}...")
                    # Scrap info on other website
                    gurus_value = Gurus.scrape_dcf_pct(stock_symbol=stock_symbol)
                    value_investing_value = ValueInvesting.scrape_dcf_pct(stock_symbol=stock_symbol)
                    alpha_spread_value = AlphaSpread.scrape_dcf_pct(stock_symbol=stock_symbol)
                    logging.info(f"  Gurus: {gurus_value}, ValueInvesting: {value_investing_value}, AlphaSpread: {alpha_spread_value}")
                    # Add stock details before the data source
                    # Remove the link (second-to-last element)
                    
                    source = all_stocks[index].pop()
                    
                    # remove the link, then add an empty string, fixing dumpings link bugs (financial bug 18)
                    link = all_stocks[index].pop()
                    all_stocks[index].append("")
                    
                    # Add scraped values
                    all_stocks[index].extend(gurus_value)
                    all_stocks[index].extend(value_investing_value)
                    all_stocks[index].extend(alpha_spread_value)
                    # Append the source at the end
                    all_stocks[index].append(source)
                    
                # Insert per 100 row
                if (index + 1) % 100 == 0 or index == len(all_stocks) - 1:
                    # Remove empty stock_symbol
                    part_stock = [stock for i, stock in enumerate(all_stocks) if i not in remove_index and current_beginning_of_stock_index <= i <= index]
                    current_beginning_of_stock_index += 100
                    # Prepare rows for update - add row_index for each stock (skip ticker in col A)
                    rows_to_update = []
                    tickers_not_found = []
                    for stock in part_stock:
                        ticker = stock[0]
                        if ticker in ticker_to_row:
                            row_to_update = stock + [ticker_to_row[ticker]]
                            rows_to_update.append(row_to_update)
                        else:
                            tickers_not_found.append(ticker)
                    # Update existing rows in sheet
                    if rows_to_update:
                        SheetManipulator.update_line_items(spreadsheet_id=spreadsheet_id, modified_rows=rows_to_update, service=service)
                        logging.info(f"Updated {len(rows_to_update)} rows in sheet. Tickers not found: {tickers_not_found}")
                    else:
                        logging.info(f"No rows to update. Tickers not found: {tickers_not_found}")
            except Exception as e:
                print(f"{e}")
                logging.error(f"Error: {e}")
        print("+--------------------------------------------------------+")
        print("+------------------ Finished ----------------------------+")
        print("+--------------------------------------------------------+")
        logging.info("Script finished")
    except Exception as e:
        print(f"{e}")