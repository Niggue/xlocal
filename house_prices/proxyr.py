import sys
import time
import random
from bs4 import BeautifulSoup as besoup
import requests


### Attributes Scope ###
#---------------------------------------------------------------------------------------------------------------------------------------- 

_FOUND_URL = 'https://www.showmyip.com'
_HEADERS = {'user-agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36'}
_proxies = ['45.167.125.97:9992', '190.26.201.194:8080', '45.167.125.61:9992', '186.96.108.30:8080']
_proxie = ['181.129.49.214:999', '190.60.39.196:999']


# seeking the connnection (original)
_response = requests.request('GET', url=_FOUND_URL, headers=_HEADERS)

# await for 1 second to avoid issues related to suddenly connection
time.sleep(1)

# obtaining the html page
_page = besoup(_response.text, 'html.parser')

# Obtaining the table where is the information about our IP address
_table = _page.find('table', class_='iptab').find_all('tr')

### The following is not human readable
# gathering every data about ip
ipdata = {}
ipdata['IPv4'] = _table[0].find_all('td')[1].find('b').string
ipdata['IPv6'] = _table[1].find_all('td')[1].find('div', id='ipv6').string  #this one is dinamically charged from page
ipdata['Country'] = _table[2].find_all('td')[1].string
ipdata['Region'] = _table[3].find_all('td')[1].string
ipdata['City'] = _table[4].find_all('td')[1].string
ipdata['Zip_'] = _table[5].find_all('td')[1].string
ipdata['Timezone'] = _table[6].find_all('td')[1].string
ipdata['ISP'] = _table[7].find_all('td')[1].string
ipdata['Organization'] = _table[8].find_all('td')[1].string 
ipdata['AS_number'] = _table[9].find_all('td')[1].string 
ipdata['user_agent'] = _table[0].find_all('td')[1].string 



### functions Scope ###
#----------------------------------------------------------------------------------------------------------------------------------------

def roll():
    
    # Rotate proxy for new requests apart of ourself original IP data
    proxy_of_use = {
        'http':_proxie[random.randint(0,1)],
        'https':_proxies[random.randint(0,3)]
    }

    return proxy_of_use



### Module's Isolated Execution ###
#-----------------------------------------------------------------------------------------------------------------------------------------

if __name__ == '__main__':
    
    print("\nData Extracted:\n")
    for item, value in ipdata.items():
        print(" > ", item, ' - ', value, end="\n")


