import mysql.connector
import bs4
from datetime import datetime
import json
import requests


# this file execute the scraping task to get some data about the following array of crypto-currencies

# Sine the webpage 'coinmarketcap.com' contains the most of the currencies as static html doc we can take use
# of BeautifulSoup4 instead of selenium

# Once we get the most relevant data related to currencies, this file execute some queries on mysql-connector
# to populate a database with the data in real time, and later this is orchestrated by crontab to execute it
# every 5 minutes, including the time.


target_currency = ["Bitcoin", "Ethereum", "Dogecoin", "Tether", "BNB"]      # currencies that we are gonna chase.

URL = 'https://coinmarketcap.com/all/views/all/'

# MYSQL connection
connection = mysql.connector.connect(user='root', password='kali', database='xlocal')

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

datetime_stamp_mysql = "{0:%Y}-{0:%m}-{0:%d} {0:%H}:{0:%M}:{0:%S}".format(datetime.now())       # current timestamp


# fetching all the crypto-currency description
for currency in range(len(target_currency)):

    # the following it's not human-readable :)
    try:
        currency_rank = page.find("a", attrs={"title": str(target_currency[currency])}).parent.parent.parent.find("div").string
        currency_symbol = page.find("a", attrs={"title": str(target_currency[currency])}, class_=symbol_class).string
        currency_name = page.find("a", attrs={"title": str(target_currency[currency])}, class_=name_class).string
        currency_market_cap = page.find_all("tr", class_=row_class)[int(currency_rank)-1].contents[3].find(class_=market_class).string
        currency_price = page.find_all("tr", class_=row_class)[int(currency_rank)-1].contents[4].find("span").string
        print(f"{currency_rank:>4s}{currency_symbol:>6s}{currency_name:>15s}{currency_market_cap:>20s}{currency_price:>12s}{datetime_stamp_mysql:>22s}")
    except:
        print("\n\tToo low-rank to scrap {}".format(target_currency[currency]))



