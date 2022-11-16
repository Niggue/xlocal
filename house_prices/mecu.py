import os
import pandas
from collect import clattr
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

# silencing the damn Future Warnings >:c
import warnings
warnings.filterwarnings('ignore', module='pyspark')




    ### Creating WebDriver ###
#========================================================================================================================

options = webdriver.ChromeOptions()
options.add_argument('--incognito')
options.add_argument('--window-position=960,0')
options.add_argument('--window-size=960,1080')
options.add_argument('--blink-settings=imagesEnabled=false')
options.page_load_strategy = 'eager'

service = Service(executable_path=ChromeDriverManager().install())

driver = webdriver.Chrome(options=options, service=service)
driver.implicitly_wait(1)
driver.minimize_window()




    ### tag classes to find in site ###
#========================================================================================================================

#city
neighborhood_class = 'H1-xsrgru-0 jdfXCo mb-2 card-title'
room_class = 'H2-kplljn-0 igCxTv vcenter-text card-text'
bath_class = 'H2-kplljn-0 igCxTv vcenter-text card-text'
parking_class = "card-text"#[6]
private_area_class = "card-text"#[5]
built_area_class = "card-text"#[4]
stratus_class = "H2-kplljn-0 igCxTv card-text"
price_class = "card-text"#[2]
price_area = lambda price, area: round(price/area)
offertype = "Venta"
#property
old_class = "card-text"#[3]




def write_log(__message="\n", __logfile="./mecu.log"):
    print(__message)
    with open(__logfile, "a") as file:
        file.write(__message)




    ### Catching all the Post data from Metro Cuadrado ###
#========================================================================================================================

post_links = pandas.read_csv('./collect.dat')

if (post_links.empty):
    raise Exception("CsvFileEmpty: The csv file has no information.")
else:
    # verifying data integrity and value counting
    baseurl = "https://www.metrocuadrado.com"
    write_log("Starting Scraping : Metro Cuadrado ... \n")
    write_log(str(post_links.loc[post_links['website'] == baseurl, 'website'].count()) + " Records from <MetroCuadrado>")
    write_log(str(post_links.loc[post_links['website'] != baseurl, 'website'].count()) + " Records from other sources")
    write_log("Total-----------")
    write_log(str(post_links['website'].count()) + " Records")

    # filtering 'metrocuadrado.com' only
    mecu = post_links.loc[post_links['website'] == baseurl]

    # verifying duplicated data
    if (len(mecu['code'].drop_duplicates()) - len(mecu['code']) == 0):
        write_log("No codes Duplicated")
    else:
        lendif = len(mecu['code']) - len(mecu['code'].drop_duplicates())
        mecu = mecu.drop_duplicates('code')
        write_log(f"{lendif} codes Duplicated")
    
    # getting 'href' links
    links = list(mecu['href'].values)    # this is the final list to scrap every link previously obtained from collect.py

    
    # dictionary that will be populated with data from every iteration in the main scope
    data = {
        'neighborhood':[],
        'city':[],
        'offer type':[],
        'property':[],
        'rooms':[],
        'baths':[],
        'parking lots':[],
        'private area':[],
        'built area':[],
        'stratus':[],
        'price':[],
        'price/area':[],
        'old':[]
    }




    ### Main execution ###
#=========================================================================================================================

if __name__ == '__main__':
    
    # opening the log file where we'll write all the process information
    os.system("rm ./mecu.log ./mecu.dat")
    os.system("touch ./mecu.log ./mecu.dat")

    # starting road through links
    for link in range(len(links)):
        # going for every link
        driver.get(links[link])
        operation_status = True

        # getting the neigborhood
        neighborhood = driver.find_element(By.CLASS_NAME, clattr(neighborhood_class))
        neighborhood = neighborhood.text
        neighborhood = neighborhood.split(",")[-1]
        neighborhood = neighborhood.lstrip()
        
        # getting main cards
        try:
            __cards = driver.find_elements(By.CLASS_NAME, clattr(room_class))
            __cards2 = driver.find_elements(By.CLASS_NAME, clattr(parking_class))
        
        # this allowd me to see where the data were when i scraped the page
        #i = 0
        #for c in __cards2:
        #    print(i,"->", c.text)
        #    i += 1
        
            rooms = __cards[1].text
            rooms = rooms.splitlines()[0]
            rooms = rooms.split(" ")[0]

            baths = __cards[2].text
            baths = baths.splitlines()[0]
            baths = baths.split(" ")[0]

            price = __cards2[13].text
            price = price.replace("$", "")
            price = price.replace(".", "")

            old = __cards2[14].text
            old = old.lstrip("Entre ").rstrip(" años")
            old = old.replace(" y ", "~")
            
            built_area = __cards2[15].text
            built_area = built_area.split(" ")[0]

            private_area = __cards2[16].text
            private_area = private_area.split(" ")[0]
            
            parking_lot = __cards2[17].text

            stratus = __cards2[4].text
            stratus = stratus.splitlines()[0]
        except:
            write_log("Something bad has happened at extracting process")
            operation_status = False
        
        # confirming the struture of information
        print(repr(neighborhood), repr(rooms), repr(baths), repr(price), repr(old), repr(built_area), repr(private_area), repr(parking_lot))
        
        # printing the gathering status
        write_log(f"POSTCODE:[{mecu['code'].values[link]}] operation [{'SUCCESS' if ({operation_status}) else 'FAILURE'}] , link:{links[link]}")
        
        # appending scraped-data into data dictionary
        write_log("Appending data ...")
        data['neighborhood'].append(neighborhood)
        data['city'].append(mecu['city'].values[link].capitalize())
        data['offer type'].append(offertype.capitalize())
        data['property'].append(mecu['facility'].values[link].capitalize())
        data['rooms'].append(rooms)
        data['baths'].append(baths)
        data['parking lots'].append(parking_lot)
        data['built area'].append(built_area)
        data['private area'].append(private_area)
        data['stratus'].append(stratus)
        data['price'].append(price)
        data['price/area'].append(price_area(float(price), float(private_area)))
        data['old'].append(old)
        write_log("Data Successfully appended [OK]")
        #print(data)

    # saving data to .dat file
    write_log("Saving data collect to mecu.dat ...")
    try:
        df = pandas.DataFrame(data=data)
        df.to_csv("./mecu.dat", sep=",", na_rep="", header=False) 
    except:
        write("Error: Data Not Saved [FAILURE]")
    else:
        write_log("Data Saved to mecu.dat [OK], exiting script ...")


    driver.quit()


