import re
import bs4
import time
import json
import requests

target_currency = ["Bitcoin", "Ethereum", "Dogecoin", "Binance USD", "Dai", "VeChain"]

URL = 'https://coinmarketcap.com/all/views/all/'

response = requests.request('GET', URL)                     # getting the entire page
print(f">> {'Response GET:':<20s}{str(response)+'.':>20s}")                        

page = bs4.BeautifulSoup(response.text, 'html.parser')      # parsing the html document
print(f">> {'Page name:':<20s}{str(page.name)+' Parsed.':>20s}")

a_tags = page.find_all("a")                                 # fetching all the 'a' tags
print(f">> {'Amount of `a` tag:':<20s}{str(len(a_tags))+'.':>20s}")


row_class = "cmc-table-row"                                 # class identifier of every row

# class attributte of every item to catch
name_class = "cmc-table__column-name--name cmc-link"
symbol_class = "cmc-table__column-name--symbol cmc-link"
rank_class = "cmc-table__cell cmc-table__cell--sticky cmc-table__cell--sortable cmc-table__cell--left cmc-table__cell--sort-by__rank"
price_class = "cmc-link"
market_class = "sc-1ow4cwt-1 ieFnWP"

# fetching all the crypto-currency description
for currency in range(len(target_currency)):

    # the following it's not human-readable :)
    try:
        currency_rank = page.find("a", attrs={"title": str(target_currency[currency])}).parent.parent.parent.find("div").string
        currency_symbol = page.find("a", attrs={"title": str(target_currency[currency])}, class_=symbol_class).string
        currency_name = page.find("a", attrs={"title": str(target_currency[currency])}, class_=name_class).string
        currency_market_cap = page.find_all("tr", class_=row_class)[int(currency_rank)-1].contents[3].find(class_=market_class).string
        currency_price = page.find_all("tr", class_=row_class)[int(currency_rank)-1].contents[4].find("span").string
        print()
        print(f"{currency_rank:>4s}{currency_symbol:>6s}{currency_name:>15s}{currency_market_cap:>20s}{currency_price:>15s}")
    except:

        print("\n\tToo low-rank to scrap {}".format(target_currency[currency]))



