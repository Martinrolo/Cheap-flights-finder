from selenium import webdriver
from selenium.webdriver.chrome.service import Service

htmlHead = """\
<html>
    <head>
        <link rel= "stylesheet" type= "text/css" href= "/static/styles/styles.css">
    </head>
    <body>
"""

html = htmlHead + "<h1>There are no past search to see.</h1><a href='/' class='link-button'>Link to the search page</a></body>"

# #Arrays that we will fill with the data and get the best price
indexBestDatesDepart = []
nameDatesBestPriceDepart = []
name_dates_elements = []

#Get Chrome webdriver
service = Service(executable_path=r'.\chromedriver.exe')
# service = Service(executable_path=r'/usr/lib/chromium-browser/chromedriver')
options = webdriver.ChromeOptions()
driver = None

def getDriver():
    global driver
    return driver

def set_driver(new_driver):
    global driver
    driver = new_driver