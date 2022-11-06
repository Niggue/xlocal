import json
import requests
import proxyr
from datetime import datetime, time
from bs4 import BeautifulSoup as besoup
from pyspark import pandas

# *************************************************************************************************************
#
# The following scrist does web scraping of the sit 'metrocuadrado.com' with the aim of gather
# data related to prices of Offices, Apartments and  Housrelated to prices of Offices, Apartments
# and  Houses.
#
# *************************************************************************************************************


### Defining script variables
#=======================================================================================================================================

try:
    file = open('awsdb.json')
    aws_credential_file = json.load(file)
    #print(aws_credential_file)
    file.close()
except:
    print("Unable to open 'awsdb.json' file seeking for aws credentials")
    exit()

facility = ['/casa','/apartamento','/oficina']
baseurl = 'https://www.metrocuadrado.com/'
via = '/venta'

# on-listed UI of the site
item_list_class = "sc-gPEVay dibcyk"
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



### Functions Scope
#=======================================================================================================================================

def extract():
    
    url = baseurl + facility[0] + via

#   try:
    response = requests.request('GET', url, headers=proxyr.ipdata['user_agent'], proxies=proxyr.roll())
#   except requests.RequestException:
#       print("ERROR trying in 'Response' of site 'metrocuadrado.com'")
    
    
        
    

def trasform():
    pass





extract()
