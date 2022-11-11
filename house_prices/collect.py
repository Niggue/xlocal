import os
import proxyr
import pandas
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
options.add_argument('--headless')

local_proxy_options = webdriver.ChromeOptions()
local_proxy_options.add_argument('--incognito')
local_proxy_options.add_argument('--disable-gpu')
local_proxy_options.add_argument('--window-position=960,0')
local_proxy_options.add_argument('--blink-settings=imagesEnabled=false')
local_proxy_options.add_argument('--headless')


service = Service(executable_path=ChromeDriverManager().install())



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

def clattr(class_name):

    __response = class_name.replace(" ",".")
    return __response


def write_log(__message, __log_file="collect.log"):

    with open(__log_file, "a") as log:
        log.write(f"{__message}\n")
        print(__message)


def try_get(__url):
    
    stdout = f" >>> Trying GET method for link {__url} ... "
    write_log(stdout)
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
            stdout = "Using local Proxy: "
            write_log(stdout)

        # getting the main list tag of the DoM where lies all the tag that we are gonna use along the whole script
        # all the 'li' tags constains the 'a' tag that will be stored in a csv formatted file, to scrap later in
        # other separated script.
        try:
            __driver.get(__url)
            if (__driver.find_element(By.CLASS_NAME, clattr(item_list_class)).is_displayed() &
                    __driver.find_element(By.CLASS_NAME, clattr(page_number_class)).is_displayed()):
                stdout = "Got it!"
                write_log(stdout)
                break
        except:
            write_log("Site can't be reached, Retrying")

        attempts += 1
        __driver.close()

    return __driver



### Main Function ###
#========================================================================================================================================

if __name__=="__main__":
    
    # updating or creating 'gather.dat' file
    os.system("touch gather.dat")
    os.system("rm collect.log; touch collect.log")
    # setting the url link structure of every website that we're gonna scrap
    finra_url = ""
    punpro_url = ""
    
    
        ##### Extracting links from Metro Cuadrado #####

    for facility_item in facility:
        for city_item in cities:
            # setting the url link structure of every website that we're gonna scrap
            mecu_url = "%s/%s/%s/%s/" % (baseurl[0], facility_item, via, city_item)

            driver = try_get(mecu_url)

            current_page = 0
            a_tags = []
            data = {}
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
                info = f" L [page:{current_page}] a:href links collected > {len(a_tags)}"
                write_log(info)

                #  getting all the page item links
                page_index = driver.find_elements(By.CLASS_NAME, clattr(page_number_box_class))
                page_next = []

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

            driver.quit()

            # Appending info to data variable to save in 'gather.dat'
            write_log("Appending links ... ")
            
            for a in a_tags:
                data['href'].append(a)
                data['facility'].append(facility_item)
                data['city'].append(city_item)
                data['website'].append(baseurl[0]) 
                data['Code'].append(a.split("/")[-1])

            try:
                df = pandas.DataFrame(data=data, columns=['facility','city','Code','website','href'])
                df.to_csv("./gather.dat", sep=",", header=True)
            except:
                write_log("[ERROR] Saving csv file of links.")
            else:
                write_log("[OK] All the things went good.")







