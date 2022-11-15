from pyspark import pandas
from pyspark.sql import SparkSession
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

from bs4 import BeautifulSoup

# silencing the damn Future Warnings >:c
import warnings
warnings.filterwarnings('ignore', module='pyspark')


    ### Creating PySpark Session ###
#========================================================================================================================

spark = SparkSession.builder.getOrCreate()


    ### Catching all the Post data from Metro Cuadrado ###
#========================================================================================================================

post_links = pandas.read_csv(path='./collect.dat')

if (post_links.empty):
    raise Exception("CsvFileEmpty: The csv file has no information.")
else:
    # verifying data integrity and value counting
    baseurl = "https://www.metrocuadrado.com"
    print(post_links.loc[post_links['website'] == baseurl, 'website'].count(), " Records from <MetroCuadrado>")
    print(post_links.loc[post_links['website'] != baseurl, 'website'].count(), " Records from other sources")
    print("Total-----------")
    print(post_links['website'].count(), " Records")

    # obtaining the href links
    mecu = post_links.loc[post_links['website']==baseurl, 'href']
    mecu = list(mecu.values)

