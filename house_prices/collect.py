import os, time
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
options.add_argument('--window-position=960,0')
options.add_argument('--window-size=960,1080')
#options.add_argument('--blink-settings=imagesEnabled=false')
#options.add_argument('--headless')

local_proxy_options = webdriver.ChromeOptions()
local_proxy_options.add_argument('--incognito')
local_proxy_options.add_argument('--window-position=960,0')
local_proxy_options.add_argument('--window-size=960,1080')
local_proxy_options.add_argument('--blink-settings=imagesEnabled=false')
#local_proxy_options.add_argument('--headless')



### Defining script variables
#=======================================================================================================================================

# iterable lists
baseurl = [
    'https://www.metrocuadrado.com',
    'https://fincaraiz.com.co',
    'https://www.puntopropiedad.com'
]

cities = [
    'mompos','barrancabermeja','barranquilla','buenaventura',
    'cali','cartagena','medellin','bogota','riohacha','santa-marta',
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
mecu_list_class = "sc-gPEVay dibcyk card-result-img"
# 'a' tag contained in 'li' tag, used to redirect to the post page
mecu_link_class = "sc-bdVaJa ebNrSm"
# 'ul' page numbers list
page_number_class = "sc-dVhcbM kVlaFh Pagination-w2fdu0-0 cxBThU paginator justify-content-center align-items-baseline pagination"
# 'a' page link number: this will allow to get last page of each searching
page_number_box_class = "page-item"
page_active_class = "page-item active disabled"


### Finca raiz tag_classes
# 'div' tags that contains 'a' tags
finra_link_class = "MuiGrid-root MuiGrid-item MuiGrid-grid-xs-12 MuiGrid-grid-sm-6 MuiGrid-grid-lg-4 MuiGrid-grid-xl-4"
# 'button' tags to click on
finra_page_number_class = "MuiButtonBase-root MuiPaginationItem-root MuiPaginationItem-page MuiPaginationItem-outlined MuiPaginationItem-rounded"


### PuntoPropiedad tag_classes
# 'li' tags
punpro_list_box_class = "ad featured"
# 'a' tag contined inside of 'li' tags 
punpro_link_class = "detail-redirection"
# 'ul' tag that contain all the page index
punpro_page_index_class = "pagination"
punpro_page_current_class = "current"
punpro_page_next_class = "next"




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
            #proxy = proxyr.roll_proxy(proxyr._proxies, module="se")
            #options.add_argument(f"--proxy-server={proxy}")
            __driver = webdriver.Chrome(options=options, service=Service(executable_path=ChromeDriverManager().install()))
            __driver.minimize_window()
            __driver.implicitly_wait(2)
        else:
            __driver = webdriver.Chrome(options=local_proxy_options, service=Service(executable_path=ChromeDriverManager().install()))
            __driver.minimize_window()
            __driver.implicitly_wait(2)
            write_log("Using local Proxy: ")

        # getting the main list tag of the DOM where lies all the tag that we are gonna use along the whole script
        # all the 'li' tags constains the 'a' tag that will be stored in a csv formatted file, to scrap later in
        # other separated script.
        try:
            __driver.get(__url)
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
                
                time.sleep(1)
                # finding list of items
                li_tags = driver.find_elements(By.CLASS_NAME, clattr(mecu_list_class))
                # finding links of items, I mean "href" attributes
                for li in li_tags:
                    item_to_append = li.find_element(By.CLASS_NAME, clattr(mecu_link_class))
                    a_tags.append(item_to_append.get_attribute("href"))

                # writing log for more info about process
                current_page += 1
                info = f" L[{baseurl[0].split('/')[-1]} : page : {current_page} : {city_item}] a:href links got > {len(a_tags)}"
                write_log(info)

                #  getting all the page item links
                try:
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
                except:
                    break

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

    for facility_item in facility:
        for city_item in cities:
            # declaring the variables that we'll use, and the 'data' dictionary that will be returned
            total_pages = 0
            a_tags = []

            # setting the url structure
            finra_url = "%s/%ss/%s/%s?pagina=1" % (baseurl[1], facility_item, via, city_item)

            # getting the total of pages, since the website index pages with the url 
            # trying the connection
            driver = try_get(finra_url)      

            # checks wheather one page only
            try:
                page_index = driver.find_elements(By.CLASS_NAME, clattr(finra_page_number_class))
                last_page = int(page_index[-2].text)
            except:
                page_index = False
            
            # runtime depend of page_index
            if (page_index != False):

                for pg in range(1, (last_page + 1)):

                    time.sleep(1)
                    # setting the url structure
                    finra_url = "%s/%ss/%s/%s?pagina=%d" % (baseurl[1], facility_item, via, city_item, pg)
                    # passing toward next page
                    driver.get(finra_url)
                    
                    # getting all the 'div' container of 'a' tags to extract href links
                    div_tags = driver.find_elements(By.CLASS_NAME, clattr(finra_link_class))
                    
                    # extracting links
                    for div in div_tags:
                        try:
                            item_to_append = div.find_element(By.TAG_NAME, "a").get_attribute("href")
                        except:
                            item_to_append = False   # some 'div' tags has sponsor, so we need skip them

                        if (item_to_append != False):
                            a_tags.append(item_to_append)
                    
                    info = f" L[{baseurl[1].split('/')[-1]} : page : {pg} : {city_item}] a:href links got > {len(a_tags)}"
                    write_log(info)
            
            else:

                write_log("no page index: must be just one page")
                # setting the url structure
                finra_url = "%s/%ss/%s/%s?pagina=%d" % (baseurl[1], facility_item, via, city_item, int(1))
                # passing toward next page
                driver.get(finra_url)
                
                # getting all the 'div' container of 'a' tags to extract href links
                div_tags = driver.find_elements(By.CLASS_NAME, clattr(finra_link_class))
                
                # extracting links
                for div in div_tags:
                    try:
                        item_to_append = div.find_element(By.TAG_NAME, "a").get_attribute("href")
                    except:
                        continue    # some 'div' tags has sponsor, so we need skip them
                    else:
                        a_tags.append(item_to_append)
                
                info = f" L[{baseurl[1].split('/')[-1]}:page:Unica] a:href links got > {len(a_tags)}"
                write_log(info)

            # closing the browser session
            driver.quit()

            # Appending info to data variable to save in 'gather.dat'
            write_log(f"Appending links for {baseurl[1]} ... ")
            
            for a in a_tags:
                __data['href'].append(a)
                __data['facility'].append(facility_item)
                __data['city'].append(city_item)
                __data['website'].append(baseurl[1]) 
                __data['code'].append(a.split("/")[-1])




def collect_puntopropiedad(__data):

    if (__data == None):
        raise AttributeError("You haven't passed '__data' argument")
    
    for facility_item in facility:
        for city_item in cities:
            # setting the url structure
            punpro_url = "%s/%s/%ss/%s" % (baseurl[2], via, facility_item, city_item)
            
            # trying the connection
            driver = try_get(punpro_url)

            # declaring the variables that we'll use, and the 'data' dictionary that will be returned
            a_tags = []

            
            # gathering data and writing into gather.dat
            while (True):

                time.sleep(1)
                # finding li elements in DOM
                li_tags = driver.find_elements(By.CLASS_NAME, clattr(punpro_list_box_class))
                # finding a tags in li elements
                for li in li_tags:
                    item_to_append = li.find_element(By.CLASS_NAME, clattr(punpro_link_class))
                    a_tags.append(item_to_append.get_attribute("href"))

                # getting the page index
                page_current = ""
                page_next = ""
                page_text = ""
                try:
                    page_box = driver.find_element(By.CLASS_NAME, clattr(punpro_page_index_class))
                    page_index = page_box.find_elements(By.TAG_NAME, "li")
                    for page in page_index:
                        if (page.get_attribute("class") == punpro_page_next_class):
                            page_next = page.find_element(By.TAG_NAME, "span")
                        if (page.get_attribute("class") == punpro_page_current_class):
                            page_current = page.find_element(By.TAG_NAME, "span")
                            page_text = page_current.text
                except:
                    page_text = "1"
                    write_log("Warning: Just has found only one page ... ")

                # writing log for more info about process
                info = f" L[{baseurl[2].split('/')[-1]} : page : {page_text} : {city_item}] a:href links got > {len(a_tags)}"
                write_log(info)
                
                # click in the next page 
                try:
                    driver.execute_script("arguments[0].click();", page_next)
                except:
                    break
                

            # closing the browser session
            driver.quit()

            # Appending info to data variable to save in 'gather.dat'
            write_log(f"Appending links for {baseurl[2]} ... ")
            
            for a in a_tags:
                __data['href'].append(a)
                __data['facility'].append(facility_item)
                __data['city'].append(city_item)
                __data['website'].append(baseurl[2]) 
                __data['code'].append(a.split("/")[-1])




### Main Function ###
#========================================================================================================================================

if __name__=="__main__":
    
    # updating or creating 'gather.dat' file
    os.system("touch collect.dat")
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
    task2.start()

    task3 = Thread(target=collect_puntopropiedad, args=([data]))
    task3.start()

    task1.join(timeout=float(21800))
    task2.join(timeout=float(21800))
    task3.join(timeout=float(21800))
    
    
    # Saving to CSV file
    try:
        df = pandas.DataFrame(
            data=data,
            index=range(1, len(data['href']) + 1),
            columns=['facility','city','code','website','href']
        )
        df.to_csv("./collect.dat", sep=",", header=True)
    except:
        write_log("[ERROR] Saving links into csv file.")
    else:
        write_log("[OK] All the things went good.")







