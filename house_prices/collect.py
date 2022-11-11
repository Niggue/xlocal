import os, time
import proxyr
import pandas
from threading import Thread
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
options.add_argument('--headless')

local_proxy_options = webdriver.ChromeOptions()
local_proxy_options.add_argument('--incognito')
local_proxy_options.add_argument('--disable-gpu')
local_proxy_options.add_argument('--window-position=960,0')
local_proxy_options.add_argument('--blink-settings=imagesEnabled=false')
local_proxy_options.add_argument('--headless')






### Defining script variables
#=======================================================================================================================================

# iterable lists
baseurl = [
    'https://www.metrocuadrado.com',
    'https://fincaraiz.com.co',
    'https://www.puntopropiedad.com'
]

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


### Metro Cuadrado tag classes
# 'li' tag of every item
item_list_class = "sc-gPEVay dibcyk card-result-img"
# 'a' tag contained in 'li' tag, used to redirect to the post page
item_link_class = "sc-bdVaJa ebNrSm"
# 'ul' page numbers list
page_number_class = "sc-dVhcbM kVlaFh Pagination-w2fdu0-0 cxBThU paginator justify-content-center align-items-baseline pagination"
# 'a' page link number: this will allow to get last page of each searching
page_number_box_class = "page-item"
page_active_class = "page-item active disabled"



### Functions Scope ###
#=======================================================================================================================================

def clattr(__class_name): # this function adapt the class attributes strings for use of the 'find_element()' which does not support spaces

    __response = __class_name.replace(" ",".")
    return __response



def write_log(__message, __log_file="collect.log"): # this write and print info about the runtime status

    with open(__log_file, "a") as log:
        log.write(f"{__message}\n")
        print(__message)



def try_get(__url): # this function try 3 times with different proxies, if none of them works, use the local IP
    
    write_log(f" >>> Trying GET method for link {__url} ... ")
    # try GET connection with  different proxies. in case any works use the local IP and Port
    attempts = 0
    while (attempts <= 3):
        
        # setting options for each retry
        if (attempts != 3):
            proxy = proxyr.roll_proxy(proxyr._proxies, module="se")
            options.add_argument(f"--proxy-server={proxy}")
            __driver = webdriver.Chrome(options=options, service=Service(executable_path=ChromeDriverManager().install()))
            __driver.implicitly_wait(5)
        else:
            __driver = webdriver.Chrome(options=local_proxy_options, service=Service(executable_path=ChromeDriverManager().install()))
            __driver.implicitly_wait(5)
            write_log("Using local Proxy: ")

        # getting the main list tag of the DoM where lies all the tag that we are gonna use along the whole script
        # all the 'li' tags constains the 'a' tag that will be stored in a csv formatted file, to scrap later in
        # other separated script.
        try:
            __driver.get(__url)
            if (__driver.find_element(By.CLASS_NAME, clattr(item_list_class)).is_displayed() &
                    __driver.find_element(By.CLASS_NAME, clattr(page_number_class)).is_displayed()):
                write_log("Got it!")
                break
        except:
            write_log("Site can't be reached, Retrying")

        attempts += 1
        __driver.close()

    return __driver



def collect_metrocuadrado(__data):    # this gather links for scraping from 'metrocuadrado.com'
    
    if (__data == None):
        raise AttributeError("you haven't passed '__data' argument")

    for facility_item in facility:
        for city_item in cities:
            # setting the url link structure of every website that we're gonna scrap
            mecu_url = "%s/%s/%s/%s/" % (baseurl[0], facility_item, via, city_item)
            
            # trying connection
            driver = try_get(mecu_url)

            # declaring the variables that we'll use, and the 'data' dictionary that will be returned
            current_page = 0
            a_tags = []

            # gathering data and writing into gather.dat
            while (True):

                # finding list of items
                li_tags = driver.find_elements(By.CLASS_NAME, clattr(item_list_class))
                # finding links of items, I mean "href" attributes
                for item in range(len(li_tags)):
                    item_to_append = li_tags[item].find_element(By.CLASS_NAME, clattr(item_link_class))
                    a_tags.append(item_to_append.get_attribute("href"))

                # writing log for more info about process
                current_page += 1
                info = f" L[{baseurl[0].split('/')[-1]}:page:{current_page}] a:href links got > {len(a_tags)}"
                write_log(info)

                #  getting all the page item links
                page_index = driver.find_elements(By.CLASS_NAME, clattr(page_number_box_class))
                

                # finding the 'current page' and seek for the 'next page element' to click on
                for i in range(len(page_index)):
                    if (page_index[i].get_attribute("class") == page_active_class):
                        page_next = page_index[i + 1]
                        break

                # exiting the loop in case 'page next' were the last page listed
                if (page_next.get_attribute("class") == "item-icon-next page-item disabled"):
                    break

                # clicking on the 'next page element', to redirect scraping the next page
                next_page_element = page_next.find_element(By.TAG_NAME, "a")
                driver.execute_script("arguments[0].click();", next_page_element)
            
            # closing the browser session
            driver.quit()

            # Appending info to data variable to save in 'gather.dat'
            write_log(f"Appending links for {baseurl[0]} ... ")
            
            for a in a_tags:
                __data['href'].append(a)
                __data['facility'].append(facility_item)
                __data['city'].append(city_item)
                __data['website'].append(baseurl[0]) 
                __data['code'].append(a.split("/")[-1])
    


def collect_fincaraiz(__data):
    
    if (__data == None):
        raise AttributeError("You haven't passed '__data' argument")
    # setting the url structure
    finra_url = "%s/%ss/%s/%s" % (baseurl[1], facility[0], via, cities[9])
    
    # trying the connection
    driver = try_get(finra_url)

    # declaring the variables that we'll use, and the 'data' dictionary that will be returned
    current_page = 0
    a_tags = []

    
    # gathering data and writing into gather.dat
    while (False):




    # closing the browser session
    driver.quit()

    # Appending info to data variable to save in 'gather.dat'
    write_log(f"Appending links for {baseurl[0]} ... ")
    
    for a in a_tags:
        __data['href'].append(a)
        __data['facility'].append(facility_item)
        __data['city'].append(city_item)
        __data['website'].append(baseurl[0]) 
        __data['code'].append(a.split("/")[-1])



def collect_puntopropiedad(__data):

    
    if (__data == None):
        raise AttributeError("You haven't passed '__data' argument")
    # setting the url structure
    finra_url = "%s/%ss/%s/%s" % (baseurl[1], facility[0], via, cities[9])
    
    # trying the connection
    driver = try_get(finra_url)

    # declaring the variables that we'll use, and the 'data' dictionary that will be returned
    current_page = 0
    a_tags = []

    
    # gathering data and writing into gather.dat
    while (False):




    # closing the browser session
    driver.quit()

    # Appending info to data variable to save in 'gather.dat'
    write_log(f"Appending links for {baseurl[0]} ... ")
    
    for a in a_tags:
        __data['href'].append(a)
        __data['facility'].append(facility_item)
        __data['city'].append(city_item)
        __data['website'].append(baseurl[0]) 
        __data['code'].append(a.split("/")[-1])




### Main Function ###
#========================================================================================================================================

if __name__=="__main__":
    
    # updating or creating 'gather.dat' file
    os.system("touch gather.dat")
    os.system("rm collect.log; touch collect.log")
    # setting the url link structure of every website that we're gonna scrap
    punpro_url = ""
    
    # dictionary where all sources are gonna merge
    data = {
        'href':[],
        'facility':[],
        'city':[],
        'website':[],
        'code':[]
    }

    task1 = Thread(target=collect_metrocuadrado, args=([data]))
    task1.start()
    
    task2 = Thread(target=collect_fincaraiz, args=([data]))
    task2.run()

    task1.join()
    task2.join()
    
    

    try:
        df = pandas.DataFrame(
            data=data,
            index=range(1, len(data['href']) + 1),
            columns=['facility','city','code','website','href']
        )
        df.to_csv("./gather.dat", sep=",", header=True)
    except:
        write_log("[ERROR] Saving links into csv file.")
    else:
        write_log("[OK] All the things went good.")







