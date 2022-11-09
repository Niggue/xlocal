import os
import json
import proxyr
from datetime import datetime, time
from pyspark import pandas
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

# *************************************************************************************************************
#
# The following script does web scraping of the site 'metrocuadrado.com' with the aim of gather
# data related to prices of Offices, Apartments and  Houses.
#
# *************************************************************************************************************

### Creating the WebDriver ###
#=======================================================================================================================================

options = webdriver.ChromeOptions()
options.page_load_strategy = 'eager'
options.add_argument('--incognito')
options.add_argument('--disable-gpu')
options.add_argument('--window-position=960,0')
options.add_argument('--blink-settings=imagesEnabled=false')
#options.add_argument('--headless')

local_proxy_options = webdriver.ChromeOptions()
local_proxy_options.add_argument('--incognito')
local_proxy_options.add_argument('--disable-gpu')
local_proxy_options.add_argument('--window-position=960,0')
local_proxy_options.add_argument('--blink-settings=imagesEnabled=false')


service = Service(executable_path=ChromeDriverManager().install())

#driver = webdriver.Chrome(options=options, service=service)
#driver.implicitly_wait(5)



### Defining script variables
#=======================================================================================================================================

baseurl = 'https://www.metrocuadrado.com'

### on-listed UI of the site
# 'ul' tag where the items are listed
item_listbox_class = "Ul-sctud2-0 jyGHXP realestate-results-list browse-results-list"
# 'li' tag of every item
item_list_class = "sc-gPEVay dibcyk"
# 'a' tag contained in 'li' tag, used to redirect to the post page
item_link_class = "sc-bdVaJa ebNrSm"

# on-a tag href redirected
# post headers
postname_class = "H1-xsrgru-0 jdfXCo mb-2 card-title" #h1
postneighbor_class = "P-sc-31hrrf-0 hGwghD card-subtitle" #p
id_class =  "Col-sc-14ninbu-0 lfGZKA mb-3 pb-1 col-12 col-lg-3" #div[0] >| p:'card-text'

# post body
city_class = "A-sc-70cat-0 dlmcsa d-none d-sm-inline-block breadcrumb-item" #a
room_class = "H2-kplljn-0 igCxTv vcenter-text card-text" #h2
bath_class = "H2-kplljn-0 igCxTv vcenter-text card-text" #h2
tier_class = "H2-kplljn-0 igCxTv card-text" #h2
price_class = "Col-sc-14ninbu-0 lfGZKA mb-3 pb-1 col-12 col-lg-3" #div[2] >| p:'card-text'
age_class = "Col-sc-14ninbu-0 lfGZKA mb-3 pb-1 col-12 col-lg-3" #div[3] >| p:'card-text'
area_class =  "Col-sc-14ninbu-0 lfGZKA mb-3 pb-1 col-12 col-lg-3" #div[5] >| p:'card-text'
management_class = "Col-sc-14ninbu-0 lfGZKA mb-3 pb-1 col-12 col-lg-3" #div[6] >| p:'card-text'
parkinglot_class =  "Col-sc-14ninbu-0 lfGZKA mb-3 pb-1 col-12 col-lg-3" #div[7] >| p:'card-text'


# iterable lists
cities = [
    'bogota',
    'barrancabermeja',
    'barranquilla',
    'buenaventura',
    'cali',
    'cartagena',
    'medellin',
    'mompos',
    'riohacha',
    'santa-marta',
    'turbo',
    'tumaco'
]

facility = [
    'casa',
    'apartamento',
    'oficina'
]

via = 'venta'

#URL pattern https://www.metrocuadrado.com/[facility]/venta/[cities]/



### Functions Scope
#=======================================================================================================================================

def select_class(class_name):

    __response = class_name.replace(" ",".")
    return __response



if __name__=="__main__":
    
    os.system("touch ./gathered_links.dat")
    
    url = "%s/%s/%s/%s/" % (baseurl, facility[0], via, cities[0])
    
    # try GET connection with 3 different proxies. in cases any works us the local IP and Port
    attempts = 0
    while (attempts <= 3):
        
        if (attempts != 3):
            proxy = proxyr.roll_proxy(proxyr._proxies, module="se")
            options.add_argument(f"--proxy-server={proxy}")
            driver = webdriver.Chrome(options=options, service=service)
            driver.implicitly_wait(5)
        else:
            driver = webdriver.Chrome(options=local_proxy_options, service=service)
            driver.implicitly_wait(5)
            print("Using local Proxy: ", end="")

        # getting the main list tag of the DoM where lies all the tag that we are gonna use along the whole script
        # all the 'li' tags constains the 'a' tag that will be stored in a csv formatted file, to scrap later in
        # other separated script.
        try:
            driver.get(url)
            if (driver.find_element(By.CLASS_NAME, select_class(item_listbox_class)).is_displayed()):
                print("Got")
                break
            
        except:
            print("Site can't be reached, Retrying")

        attempts += 1
        driver.close()







