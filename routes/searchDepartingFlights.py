from flask import Blueprint, request, render_template_string
from flightData import *



from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

departing_route = Blueprint('searchDepartingFlights', __name__, template_folder="templates")
@departing_route.route('/searchDepartingFlights', methods =["GET", "POST"])
def searchDepartingDates():
    if request.method == "POST":
        #**********************  Get form data and webdriver  **********************

        # Retrieve the JSON data from the request body
        json_data = request.get_json()

        #Get departure and destination airports from user input AND the dates
        leavingFrom = json_data['leavingFrom']
        going_to = json_data['goingTo']
        firstChosenDate = json_data['dates'][0]
        secondChosenDate = json_data['dates'][1]

        #Test
        print(firstChosenDate)
        print(secondChosenDate)
        print(firstChosenDate < secondChosenDate)

        #Go to Google Flights
        driver = webdriver.Chrome()
        set_driver(driver)
        
        driver.get("https://www.google.com/travel/flights")

        #**********************  Type the destination  **********************
        going_to_xpath = '(//input[@jsname="yrriRe"])[3]'
        going_to_element = WebDriverWait(driver,5).until(
            EC.presence_of_element_located((By.XPATH, going_to_xpath))
        )
        going_to_element.click()
        time.sleep(0.2)
        
        #Find the input element
        going_to_input_xpath = '(//input[@jsname="yrriRe"])[4]'
        going_to_input_element = WebDriverWait(driver,5).until(
            EC.presence_of_element_located((By.XPATH, going_to_input_xpath))
        )

        #Type the name of the destination
        going_to_input_element.clear()
        time.sleep(0.1) 
        going_to_input_element.send_keys(going_to)
        time.sleep(0.1) 
        going_to_input_element.send_keys(Keys.DOWN, Keys.RETURN)

        #**********************  Type the leaving from section  **********************
        leaving_from_xpath = '(//input[@jsname="yrriRe"])[1]'
        leaving_from_element = WebDriverWait(driver,5).until(
            EC.presence_of_element_located((By.XPATH, leaving_from_xpath))
        )
        time.sleep(0.1)

        leaving_from_element.click()
        time.sleep(0.1)

        leaving_from_xpath = '(//input[@jsname="yrriRe"])[4]'
        leaving_from_element = WebDriverWait(driver,5).until(
            EC.presence_of_element_located((By.XPATH, leaving_from_xpath))
        )
        time.sleep(0.1)

        leaving_from_element.click()
        time.sleep(0.1) 
        leaving_from_element.clear()
        time.sleep(0.1) 
        leaving_from_element.send_keys(leavingFrom)
        time.sleep(0.1) 
        leaving_from_element.send_keys(Keys.DOWN, Keys.RETURN)
        time.sleep(0.1) 

        #WAIT A BIT
        time.sleep(0.6)

        
        #**********************  DEPARTURE DATES/PRICE FINDER  **********************
        #The calendar opens 
        departure_calendar_xpath = '(//input[@jsname="yrriRe"])[5]'
        departure_calendar_element = WebDriverWait(driver,5).until(
            EC.presence_of_element_located((By.XPATH, departure_calendar_xpath))
        )

        departure_calendar_element.click()
        time.sleep(2)

        #Get the prices of ALL the dates
        prices_elements_xpath = '//div[@jsname="qCDwBb"]'
        prices_elements = WebDriverWait(driver,5).until(
            EC.presence_of_all_elements_located((By.XPATH, prices_elements_xpath))
        )
        time.sleep(0.1)

        #Get all the date elements
        dates_elements_xpath = '//div[@jsname="mG3Az"]'
        dates_elements = WebDriverWait(driver,5).until(
            EC.presence_of_all_elements_located((By.XPATH, dates_elements_xpath))
        )
        time.sleep(0.1)

        #Find NAMES of all the dates
        name_dates_xpath = '//div[@jsname="nEWxA"]'
        name_dates_elements = WebDriverWait(driver,5).until(
            EC.presence_of_all_elements_located((By.XPATH, name_dates_xpath))
        )
        time.sleep(0.1)

        #Arrays that we will fill with the data and get the best price
        bestPrice = 100000
        datesBestPriceDepart = []
        nameDatesBestPriceDepart = []
        indexBestDatesDepart = []

        #Loop all the dates, compare the prices of each date and get the cheapest dates
        for i in range (len(prices_elements)):
            try:
                if dates_elements[i].get_attribute('data-iso') > secondChosenDate:
                    break

                #Every 2 months, we change the calendar pages to get the next 2 months
                if (i > 57 and prices_elements[i].text == ""):

                    #Get the buttton to change the page
                    calendar_page_change_xpath = '(//div[@jsname="v6lL4e"])[1]'
                    calendar_page_change_element = WebDriverWait(driver,5).until(
                        EC.presence_of_element_located((By.XPATH, calendar_page_change_xpath))
                    )
                    
                    #Click twice and wait a bit for the prices to appear
                    calendar_page_change_element.click() 
                    time.sleep(0.8)
                    calendar_page_change_element.click() 
                    time.sleep(0.8)

                    #Get the new price elements
                    prices_elements = WebDriverWait(driver,5).until(
                        EC.presence_of_all_elements_located((By.XPATH, prices_elements_xpath))
                    )

                #Display the date and the prices (if they are not empty)
                if(prices_elements[i].text != "" and 
                   dates_elements[i].get_attribute('data-iso') >= firstChosenDate and
                   dates_elements[i].get_attribute('data-iso') <= secondChosenDate):
                    
                    #TEST
                    print(dates_elements[i].get_attribute('data-iso'))
                    print(prices_elements[i].text.strip("$"))

                    #Get the price of the current day
                    currentDayPrice = int(prices_elements[i].text.replace("$", "").replace("\u202f", ""))

                    #If the price is better than the best price so far, we keep it
                    if currentDayPrice < bestPrice:
                        #Set the price as the new best price, and save the date
                        bestPrice = currentDayPrice
                        datesBestPriceDepart.clear()
                        datesBestPriceDepart.append(dates_elements[i].get_attribute('data-iso'))

                        #Add the name of the date (in letters eg: April 24th 2024)
                        nameDatesBestPriceDepart.clear()
                        nameDatesBestPriceDepart.append(name_dates_elements[i].get_attribute('aria-label'))

                        #Save the index of the best date
                        indexBestDatesDepart.clear()
                        indexBestDatesDepart.append(i)

                    #If the price is equal to the cheapest, we still add it but NOT clear the past dates
                    elif currentDayPrice == bestPrice:
                        #Set the price as the new best price, and save the date
                        bestPrice = currentDayPrice
                        datesBestPriceDepart.append(dates_elements[i].get_attribute('data-iso'))
                        indexBestDatesDepart.append(i)

                        #Add the name of the date (in letters eg: April 24th 2024)
                        nameDatesBestPriceDepart.append(name_dates_elements[i].get_attribute('aria-label'))
                else:
                    continue

            except Exception as e:
                print(e)
                continue

        #TEST: Print the best price and the array of the best days for the leaving flight
        print(bestPrice)
        print(datesBestPriceDepart)

        #Click on "OK" to leave the calendar
        depart_date_done_xpath = '//div[@jsname="WCieBd"]'
        depart_date_done_element = WebDriverWait(driver,3).until(
            EC.presence_of_element_located((By.XPATH, depart_date_done_xpath))
        )
        depart_date_done_element.click()
        time.sleep(0.2)

        # ************** RETURN HTML PAGE FOR DEPARTURE DATE SELECTION **************
        #First, add the head (styles) and the loading div
        html = htmlHead 

        #If there are flights, we display them
        if(nameDatesBestPriceDepart):

            html += """
            <div id="loading">
                <div class="title">Finding the best dates for you..</div>
                <img src='/static/loading.gif' alt="Loading...">
            </div>"""

            #Add the title and the table head
            html += "<div id='content'><h1>Here is a list of the best departure dates</h1>"
            html += "<h3>Select up to 3 dates to get the return dates and flight info</h3>"
            html += "<table><thead><tr><th>Possible departure dates</th><th>Price</th></tr></thead><tbody>"

            #For each date, show the name of the date and the price in a row of the table
            for i in range(len(nameDatesBestPriceDepart)):
                html += "<tr id='" + str(datesBestPriceDepart[i]) + "'><td><p>" + str(nameDatesBestPriceDepart[i]) + "</p></td><td>" + str(bestPrice) + "$</td></tr>"

            #Close table
            html += "</tbody></table>"

            #Add the button to search return dates
            html += "<button type='submit' id='search' class='submit' onclick='loading();'>Search</button>"

            #Add a button back to the main menu and CLOSE THE CONTENT DIV       
            html += "<a href='/' class='link-button'>Link to the search page</a></body></div>"

            #Add script to allow user to choose date
            html += """
                <script src="../static/scripts/returnFlightsSearch.js"></script>
            """
        
        #Else, we display a message of error, close the browser and put a link back to the home page
        else:
            html += "<h1>No flights were found.</h1>"
            html += "<h2>Make sure that the departing and returning city names are valid</h2>"
            html += '<a href="/" class="link-button">Link to the search page</a>'
            driver.quit()

        #Close body and driver
        html += "</body></html>"

        return render_template_string(html)
    
    #Else, if the request is done
    else:
        return render_template_string(html)