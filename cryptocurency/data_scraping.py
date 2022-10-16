import mysql.connector
import bs4
from datetime import datetime
import sys
import requests
print()

# For some responsive purpose, to add a '-v' --verbose option CLI command it's not a waste.
xargs = False
if (len(sys.argv) > 2):
    print("Error : Too many arguments")
    exit()
elif (len(sys.argv) == 2):
    xargs = True if (sys.argv[1] == '-v') else print("\nUsage:\n\tonly either '-v' or nothing args\n")

# this file execute the scraping task to get some data about the following array of crypto-currencies

# Since the webpage 'coinmarketcap.com' contains the mostly currencies as static html doc we can take use
# of BeautifulSoup4 instead of selenium

# Once we get the more relevant data related to currencies, this file execute some queries on mysql-connector
# to populate a database with the data in real time, and later this is orchestrated by crontab to execute it
# every 5 minutes, including the time.


target_currency = ["Bitcoin", "Ethereum", "Dogecoin", "Tether", "BNB"]      # currencies that we are gonna chase.

URL = 'https://coinmarketcap.com/all/views/all/'

# MYSQL connection
connection = mysql.connector.connect(user='root', password='kali', database='xlocal')
cursor = connection.cursor()


response = requests.request('GET', URL)                     # getting the entire page
print(f">> {'Response GET:':<20s}{str(response)+'.':>20s}")

page = bs4.BeautifulSoup(response.text, 'html.parser')      # parsing the html document
print(f">> {'Page name:':<20s}{str(page.name)+' Parsed.':>20s}")

a_tags = page.find_all("a")                                 # fetching all the 'a' tags
print(f">> {'Amount of `a` tag:':<20s}{str(len(a_tags))+'.':>20s}")


# class attributte of every item to catch
row_class = "cmc-table-row"                                 # class identifier of every row
name_class = "cmc-table__column-name--name cmc-link"
symbol_class = "cmc-table__column-name--symbol cmc-link"
rank_class = "cmc-table__cell cmc-table__cell--sticky cmc-table__cell--sortable cmc-table__cell--left cmc-table__cell--sort-by__rank"
price_class = "cmc-link"
market_class = "sc-1ow4cwt-1 ieFnWP"

datetime_stamp_mysql = "{0:%Y}-{0:%m}-{0:%d} {0:%H}:{0:%M}:{0:%S}".format(datetime.now())       # current timestamp

# fetching all the crypto-currency description
def get_data():
    
    sql_data = []

    for currency in range(len(target_currency)):

        try:
            # the following it's not human-readable :)
            currency_rank = page.find("a", attrs={"title": str(target_currency[currency])}).parent.parent.parent.find("div").string
            currency_symbol = page.find("a", attrs={"title": str(target_currency[currency])}, class_=symbol_class).string
            currency_name = page.find("a", attrs={"title": str(target_currency[currency])}, class_=name_class).string
            currency_market_cap = page.find_all("tr", class_=row_class)[int(currency_rank)-1].contents[3].find(class_=market_class).string
            currency_price = page.find_all("tr", class_=row_class)[int(currency_rank)-1].contents[4].find("span").string
            if (xargs):
                print(f"{currency_rank:>4s}{currency_symbol:>6s}{currency_name:>15s}{currency_market_cap:>20s}{currency_price:>12s}{datetime_stamp_mysql:>22s}")
                
            sql_data.append(tuple([currency_rank, currency_symbol, currency_name, currency_market_cap, currency_price, datetime_stamp_mysql]))

        except:    
            print("\n\tToo low-rank to scrap {}".format(target_currency[currency]))
    
    return sql_data

# generating the query to ingest data into MYSQL
def get_insert_query(sql_values, table, database):
    
    query = ""
    query += f"USE {database};\n" if database != None else ""
    query = f"INSERT INTO {table} (currency_rank, symbol, name, market_value, prices, date_of_ingest) VALUES\n"
    
    for row in range(len(sql_values)):
        rank = int(sql_values[row][0])
        symbol = repr(sql_values[row][1])
        name = repr(sql_values[row][2])
        market_cap = repr(sql_values[row][3])
        price = float(sql_values[row][4].replace('$','').replace(',',''))
        date_time = repr(sql_values[row][5])

        query += f"({rank},{symbol},{name},{market_cap},{price},{date_time})"
        query += ",\n" if row != (len(sql_values)-1) else "\n"

    return query



mysql_values = get_data()
sql_query = get_insert_query(mysql_values, 'cryptocurrencies', 'xlocal')
print(sql_query)

cursor.execute(sql_query)
connection.commit()

connection.close()






