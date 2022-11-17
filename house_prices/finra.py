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

# All the info could be found inside 'p' tags
offertype = "venta"
price_area = lambda price, area: round(price/area)


def write_log(__message="\n", newl=True, __logfile="./finra.log"):
    # printing conditional
    if (newl):
        print(__message)
        # writing logfile
        with open(__logfile, "a") as file:
            file.write(__message + "\n")
    else:
        print(__message, end="")
        # writing logfile
        with open(__logfile, "a") as file:
            file.write(__message)




    ### Catching all the Post data from Metro Cuadrado ###
#========================================================================================================================

post_links = pandas.read_csv('./collect.dat')

if (post_links.empty):
    raise Exception("CsvFileEmpty: The csv file has no information.")
else:
    # verifying data integrity and value counting
    baseurl = "https://fincaraiz.com.co"
    write_log("Starting Scraping : Fincaraiz ... \n")
    write_log(str(post_links.loc[post_links['website'] == baseurl, 'website'].count()) + " Records from <Fincaraiz>")
    write_log(str(post_links.loc[post_links['website'] != baseurl, 'website'].count()) + " Records from other sources")
    write_log("Total-----------")
    write_log(str(post_links['website'].count()) + " Records")

    # filtering 'metrocuadrado.com' only
    finra = post_links.loc[post_links['website'] == baseurl]

    # verifying duplicated data
    if (len(finra['code'].drop_duplicates()) - len(finra['code']) == 0):
        write_log("No codes Duplicated")
    else:
        lendif = len(finra['code']) - len(finra['code'].drop_duplicates())
        write_log(f"{lendif} codes Duplicated")
        finra = finra.drop_duplicates('code')
        write_log(f"{len(finra)} codes Stuck")
    
    # getting 'href' links
    links = list(finra['href'].values)    # this is the final list to scrap every link previously obtained from collect.py

    
    # dictionary that will be populated with data from every iteration in the main scope
    data = {
        'code':[],
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
    os.system("rm ./finra.log ./finra.dat")
    os.system("touch ./finra.log ./finra.dat")
    
    __stop=0

    # starting road through links
    for link in range(len(links)):
        # seeking for every link
        driver.get(links[link])
        operation_status = True
        
        # getting main cards
        try:
            __ptags = driver.find_elements(By.TAG_NAME, "p")
        
            # this allowed me to see where the data were when I scraped the page
            i = 0
            for p in __ptags:
                match (p.text):
                    case "Precio (COP)": price_pos = i+1
                    case "Casa en venta": neighborhood_pos = i+1
                    case "Habitaciones": rooms_pos = i+1
                    case "Baños": baths_pos = i+1
                    case "Área construída": built_area_pos = i+1
                    case "Área privada": private_area_pos = i+1
                    case "Estrato": stratus_pos = i+1
                    case "Parqueaderos": parking_lot_pos = i+1
                    case "Antigüedad": old_pos = i+1
                #print(i,"->", p.text)
                i += 1

            neighborhood = __ptags[neighborhood_pos].text
            neighborhood = neighborhood.split(" - ")[0]
            
            rooms = __ptags[rooms_pos].text

            baths = __ptags[baths_pos].text

            price = __ptags[price_pos].text
            price = price.replace("$", "")
            price = price.replace(".", "")
            price = price.lstrip()
    
            try:
                old = __ptags[old_pos].text
                old = old.lstrip("más de ")
                old = old.rstrip(" años")
                old = old.replace(' a ', "~")
                check = int(old[0])
            except:
                old = "nan"
            
            built_area = __ptags[built_area_pos].text
            built_area = built_area.split(" ")[0]

            private_area = __ptags[private_area_pos].text
            private_area = private_area.split(" ")[0]
            if (int(private_area) == 0):
                private_area = built_area
            
            try:
                parking_lot = __ptags[parking_lot_pos].text
                parking_lot = int(parking_lot)
                parking_lot = str(parking_lot)
            except:
                parking_lot = str(0)

            try:
                stratus = __ptags[stratus_pos].text
            except:
                stratus = "nan"

        except:
            write_log("Something bad has happened at extracting process")
            operation_status = False
        
        # confirming the struture of information
        #print(repr(neighborhood), repr(rooms), repr(baths), repr(price), repr(old), repr(built_area), repr(private_area), repr(parking_lot), repr(stratus))
        
        # printing the gathering status
        write_log(f"POSTCODE:[{finra['code'].values[link]}] operation [{'SUCCESS' if ({operation_status}) else 'FAILURE'}] , link:{links[link]}")
        
        # appending scraped-data into data dictionary
        write_log("Appending data ... ", newl=False)
        data['code'].append(finra['code'].values[link])
        data['neighborhood'].append(neighborhood. capitalize())
        data['city'].append(finra['city'].values[link].capitalize())
        data['offer type'].append(offertype.capitalize())
        data['property'].append(finra['facility'].values[link].capitalize())
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

        #__stop += 1    # used to stop the for loop due to test purposes
        if (__stop == 30):
            break

    # saving data to .dat file
    write_log("Saving data collect to finra.dat ... ", newl=False)
    try:
        df = pandas.DataFrame(data=data)
        df.to_csv("./finra.dat", sep=",", na_rep="", header=False) 
    except:
        write("Error: Data Not Saved [FAILURE]")
    else:
        write_log("Data Saved to finra.dat [OK], exiting script ...")


    driver.quit()


