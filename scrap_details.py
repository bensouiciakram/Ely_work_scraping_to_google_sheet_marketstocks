from helpers.sheet import SheetManipulator
from helpers.params import SHEET_URL, SHEET_NAME
from web_site.value_investing import ValueInvesting
from web_site.alpha_spread import AlphaSpread
from web_site.gurus import Gurus
import json
import asyncio

if __name__ == "__main__":
    try:
        print("+--------------------------------------------------------+")
        print("+--------------------- START ----------------------------+")
        print("+--------------------------------------------------------+")
        # ---------------------------------------------------------- LOAD STOCK FROM FILE -------------------------------------
        # Load data from JSON file
        with open("stocks.json", "r", encoding="utf-8") as f:
            all_stocks = json.load(f)
        remove_index = []
        # Sheet parameter
        credentials, service = SheetManipulator.get_credentials_and_service()
        spreadsheet_id = SheetManipulator.get_spreadsheet_id(SHEET_URL)
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
                    # Scrap info on other website
                    gurus_value = Gurus.scrape_dcf_pct(stock_symbol=stock_symbol)
                    value_investing_value = ValueInvesting.scrape_dcf_pct(stock_symbol=stock_symbol)
                    alpha_spread_value = AlphaSpread.scrape_dcf_pct(stock_symbol=stock_symbol)
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
                    # Add on sheet
                    SheetManipulator.append_stock(spreadsheet_id=spreadsheet_id, new_rows=part_stock, service=service)
            except Exception as e:
                print(f"{e}")
        print("+--------------------------------------------------------+")
        print("+------------------ Finished ----------------------------+")
        print("+--------------------------------------------------------+")
    except Exception as e:
        print(f"{e}")