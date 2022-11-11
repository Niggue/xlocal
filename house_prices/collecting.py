import os, csv, time
import proxyr
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
options.page_load_strategy = 'normal'
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
# 'li' tag of every item
item_list_class = "sc-gPEVay dibcyk card-result-img"
# 'a' tag contained in 'li' tag, used to redirect to the post page
item_link_class = "sc-bdVaJa ebNrSm"
# 'ul' page numbers list
page_number_class = "sc-dVhcbM kVlaFh Pagination-w2fdu0-0 cxBThU paginator justify-content-center align-items-baseline pagination"
# 'a' page link number: this will allow to get last page of each searching
page_number_box_class = "page-item"
page_active_class = "page-item active disabled"

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
    'bogota','barrancabermeja','barranquilla','buenaventura',
    'cali','cartagena','medellin','mompos','riohacha','santa-marta',
    'turbo','tumaco'
]

facility = [
    'casa',
    'apartamento',
    'oficina'
]

via = 'venta'

#URL pattern https://www.metrocuadrado.com/[facility]/venta/[cities]/



### Functions Scope ###
#=======================================================================================================================================

def clattr(class_name):

    __response = class_name.replace(" ",".")
    return __response


def write_log(__log_file, __message):
    with open(__log_file, "a") as log:

    pass


def try_get(__url):
    
    print(f" >> Trying GET method for link {__url} ... ")
    # try GET connection with  different proxies. in case any works use the local IP and Port
    attempts = 0
    while (attempts <= 3):
        
        # setting options for each retry
        if (attempts != 3):
            proxy = proxyr.roll_proxy(proxyr._proxies, module="se")
            options.add_argument(f"--proxy-server={proxy}")
            __driver = webdriver.Chrome(options=options, service=service)
            __driver.implicitly_wait(5)
        else:
            __driver = webdriver.Chrome(options=local_proxy_options, service=service)
            __driver.implicitly_wait(5)
            print("Using local Proxy: ", end="")

        # getting the main list tag of the DoM where lies all the tag that we are gonna use along the whole script
        # all the 'li' tags constains the 'a' tag that will be stored in a csv formatted file, to scrap later in
        # other separated script.
        try:
            __driver.get(__url)
            if (__driver.find_element(By.CLASS_NAME, clattr(item_list_class)).is_displayed() &
                    __driver.find_element(By.CLASS_NAME, clattr(page_number_class)).is_displayed()):
                print("Got it!")
                break
            
        except:
            print("Site can't be reached, Retrying")

        attempts += 1
        __driver.close()

    return __driver



### Main Function ###
#========================================================================================================================================

if __name__=="__main__":
    
    # updating or creating 'gather.dat' file
    os.system("touch ./gather.dat")
    # setting the url link structure of every website that we're gonna scrap
    mecu_url = "%s/%s/%s/%s/" % (baseurl, facility[1], via, cities[9])
    finra_url = ""
    punpro_url = ""
    

    # Extracting links from Metro Cuadrado
    driver = try_get(mecu_url)
    current_page = 0
    # gathering data and writing into gather.dat
    while (True):
        
        # finding list of items
        li_tags = driver.find_elements(By.CLASS_NAME, clattr(item_list_class))
        # finding links of items, I mean "href" attributes
        a_tags = []
        for item in range(len(li_tags)):
            item_to_append = li_tags[item].find_element(By.CLASS_NAME, clattr(item_link_class))
            a_tags.append(item_to_append.get_attribute("href"))
    


        ### Saving 'a_tags' list into 'gather.dat' file
        current_page += 1
        print(f" L [page:{current_page}] a:href links collected >", len(a_tags))
        



        #  getting all the page item links
        page_index = driver.find_elements(By.CLASS_NAME, clattr(page_number_box_class))
        page_next = []

        # finding the 'current page' and seek for the 'next page element' to click on
        for i in range(len(page_index)):
            if (page_index[i].get_attribute("class") == page_active_class):
                page_next = page_index[i + 1]
                break

        # exiting the loop in case 'page next' would be the last page listed
        if (page_next.get_attribute("class") == "item-icon-next page-item disabled"):
            break

        # clicking on the 'next page element', to redirect scraping the next page
        next_page_element = page_next.find_element(By.TAG_NAME, "a")
        driver.execute_script("arguments[0].click();", next_page_element)
    
    driver.quit()








