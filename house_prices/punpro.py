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
neighborhood_class = "location_info"
room_class = "bedrooms"
bath_class = "bathrooms"
parking_class = "tick"# repeated class
private_area_class = "dimensions"
built_area_class = "dimensions"
stratus_class = "tick"# repeated class
price_class = "price"#[0 or 1]
price_area = lambda price, area: round(price/area)
offertype = "Venta"
#property
old_class = "tick"# repeated class




def write_log(__message="\n", newl=True, __logfile="./punpro.log"):
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
    baseurl = "https://www.puntopropiedad.com"
    write_log("Starting Scraping : Punto Propiedad ... \n")
    write_log(str(post_links.loc[post_links['website'] == baseurl, 'website'].count()) + " Records from <PuntoPropiedad>")
    write_log(str(post_links.loc[post_links['website'] != baseurl, 'website'].count()) + " Records from other sources")
    write_log("Total-----------")
    write_log(str(post_links['website'].count()) + " Records")

    # filtering 'metrocuadrado.com' only
    punpro = post_links.loc[post_links['website'] == baseurl]

    # verifying duplicated data
    if (len(punpro['code'].drop_duplicates()) - len(punpro['code']) == 0):
        write_log("No codes Duplicated")
    else:
        lendif = len(punpro['code']) - len(punpro['code'].drop_duplicates())
        write_log(f"{lendif} codes Duplicated")
        punpro = punpro.drop_duplicates('code')
        write_log(f"{len(punpro)} codes Stuck")
    
    # getting 'href' links
    links = list(punpro['href'].values)    # this is the final list to scrap every link previously obtained from collect.py
    
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
    os.system("rm ./punpro.log ./punpro.dat")
    os.system("touch ./punpro.log ./punpro.dat")
    
    __stop=0
    # starting road through links
    for link in range(len(links)):
        # testing post available
        try:
            # going for every link
            driver.get(links[link])

            # getting the neigborhood
            neighborhood = driver.find_element(By.TAG_NAME, "h1")
            neighborhood = neighborhood.text
            neighborhood = neighborhood.split(",")[0]
            neighborhood = neighborhood.lstrip("Casa en venta ")
        except:
            write_log(f"Post deprecated ... {links[link]}")
            continue
        
        # getting main cards
        #try:
        __ticks = driver.find_elements(By.CLASS_NAME, clattr(old_class))

        # this allowed me to see where the data were when i scraped the page
        i = 0
        for t in __ticks:
            check = t.text.split(":")[0]
            match (check):
                case "Estrato": stratus = t
                case "Año de construcción": old = t
                case "Parqueadero": parking_lot = 1
                case "Área útil": built_area = t
            #print(i,"->", t.text)
            i += 1
        
        try:
            rooms = driver.find_elements(By.CLASS_NAME, clattr(room_class))
            rooms = rooms[1].text
            rooms = rooms.split(" ")[0]
        except:
            rooms = str(0)
        
        try:
            baths = driver.find_elements(By.CLASS_NAME, clattr(bath_class))
            baths = baths[1].text
            baths = baths.split(" ")[0]
        except:
            baths = str(0)
        
        price = driver.find_elements(By.CLASS_NAME, clattr(price_class))
        price = price[1].find_element(By.TAG_NAME, "h2")
        price = price.text
        price = price.replace(".", "")
        price = price.replace("COP$", "")
        price = price.strip()
        try:
            check = int(price)
        except:
            write_log(f"Error at extracting process: POSTCODE:[{punpro['code'].values[link]}], link:{links[link]}")
            continue

        try:
            built_area = built_area.text
            built_area = built_area.split(":")[1]
            built_area = built_area.lstrip()
            built_area = built_area.split(",")[0]
            built_area = built_area.split(".")[0]
            private_area = built_area
            check = int(built_area)
        except:
            try:
                built_area = driver.find_elements(By.CLASS_NAME, clattr(built_area_class))
                built_area = built_area[1].text
                built_area = built_area.rstrip("m2")
                built_area = built_area.split(",")[0]
                built_area = built_area.split(".")[0]
                private_area = built_area
            except:
                write_log(f"Error at extracting process: POSTCODE:[{punpro['code'].values[link]}], link:{links[link]}")
                continue
        
        try:
            old = old.text
            old = old.split(":")[1]
            old = old.lstrip().replace(".", "")
            old = int(old)
            old_diff = 2022 - old
            old = str(old_diff)
        except:
            old = "nan"
        
        try:
            parking_lot = int(parking_lot)
            parking_lot = str(parking_lot)
        except:
            parking_lot = str(0)

        try:
            stratus = stratus.text
            stratus = stratus.split(":")[1]
            stratus = stratus.strip()
            stratus = int(stratus)
            stratus = str(stratus)
        except:
            stratus = "nan"

        #except:
        #    write_log("Something bad has happened at extracting process")
        #    operation_status = False
        
        # confirming the struture of information
        #print(repr(neighborhood), repr(rooms), repr(baths), repr(price), repr(old), repr(built_area), repr(private_area), repr(stratus), repr(parking_lot))
        
        # printing the gathering status
        write_log(f"POSTCODE:[{punpro['code'].values[link]}], link:{links[link]}")
        
        # appending scraped-data into data dictionary
        write_log("Appending data ... ", newl=False)
        data['code'].append(punpro['code'].values[link])
        data['neighborhood'].append(neighborhood)
        data['city'].append(punpro['city'].values[link].capitalize())
        data['offer type'].append(offertype.capitalize())
        data['property'].append(punpro['facility'].values[link].capitalize())
        data['rooms'].append(rooms)
        data['baths'].append(baths)
        data['parking lots'].append(parking_lot)
        data['built area'].append(built_area)
        data['private area'].append(private_area)
        data['stratus'].append(stratus)
        data['price'].append(price)
        data['price/area'].append(price_area(float(price), float(built_area)))
        data['old'].append(old)
        write_log("Data Successfully appended [OK]")
        #print(data)

        #__stop += 1    # used to stop the for loop due to test purposes
        if (__stop == 30):
            break

    # saving data to .dat file
    write_log("Saving data collect to punpro.dat ... ", newl=False)
    try:
        df = pandas.DataFrame(data=data)
        df.to_csv("./punpro.dat", sep=",", na_rep="", header=False) 
    except:
        write("Error: Data Not Saved [FAILURE]")
    else:
        write_log("Data Saved to punpro.dat [OK], exiting script ...")


    driver.quit()


