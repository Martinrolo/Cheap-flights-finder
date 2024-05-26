from flask import Blueprint, request, render_template_string
from flightData import *

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time


returning_route = Blueprint('searchReturningFlights', __name__, template_folder="templates")

@returning_route.route('/searchReturningFlights', methods =["GET", "POST"])
def searchReturningDates():
    #Get the global driver
    driver = getDriver()

    if request.method == "POST":
        #Get driver and go to Google Flights

        #Initialize flights array
        #We will return it at the end with all the info
        flightsArray = []
        firstDateBestPriceRetour = []

        # Retrieve the JSON data from the request body
        json_data = request.get_json()
        chosenDepartDates = json_data['dates']
        namesDepartDates = json_data['names']

        # Print the received data to the console
        print(chosenDepartDates)

        #********************** LOOP THROUGH ALL DEPARTURE DATES***********************

        #We loop through all the departing dates, to get the best returning dates for each.
        for i in range(len(chosenDepartDates)):
            #INITIALIZE DICTIONNARY FOR EACH DEPARTURE DATE POSSIBLE
            flightsDict = {}

            #Open departure calendar
            departing_box_xpath = '(//input[@jsname="yrriRe"])[5]'
            depart_box_element = WebDriverWait(driver,5).until(
                EC.presence_of_element_located((By.XPATH, departing_box_xpath))
            )
            depart_box_element.click()
            time.sleep(0.2)

            #Try ALL the dates
            trip_date_xpath = '//div[@data-iso="' + chosenDepartDates[i] + '"]'
            departing_date_element = WebDriverWait(driver,3).until(
                EC.presence_of_element_located((By.XPATH, trip_date_xpath))
            )
            departing_date_element.click() #Click on the departure date
            time.sleep(0.2)
            
            #Click on "OK" to leave the calendar
            depart_date_done_xpath = '//div[@jsname="WCieBd"]'
            depart_date_done_element = WebDriverWait(driver,3).until(
                EC.presence_of_element_located((By.XPATH, depart_date_done_xpath))
            )
            depart_date_done_element.click()
            time.sleep(0.2)


            #**********************  RETURN DATES/PRICE FINDER  **********************

            #Open calendar (RETURN)
            return_box_xpath = '(//input[@jsname="yrriRe"])[6]'
            return_box_element = WebDriverWait(driver,5).until(
                EC.presence_of_element_located((By.XPATH, return_box_xpath))
            )
            return_box_element.click() 
            time.sleep(1.5)

            #Get the prices of ALL the dates
            prices_elements_xpath = '//div[@jsname="qCDwBb"]'
            prices_elements = WebDriverWait(driver,5).until(
                EC.presence_of_all_elements_located((By.XPATH, prices_elements_xpath))
            )
            time.sleep(0.1)

            #Get all the dates
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

            # ******* FIND BEST RETURN PRICES/DATES *******
            bestPrice = 10000
            datesBestPriceRetour = []
            nameDatesBestPriceRetour = []

            #Loop through all the returning prices
            for j in range (len(prices_elements)):
                try:
                    #If there is a price to the date
                    if(prices_elements[j].text != ""):
                        #TEST display date and price
                        print(dates_elements[j].get_attribute('data-iso'))
                        print(prices_elements[j].text.strip("$"))

                        currentDayPrice = int(prices_elements[j].text.replace("$", "").replace("\u202f", ""))
                        
                        #If the price is better than the best price so far, we keep it
                        if currentDayPrice < bestPrice:
                            #Save the price and the date
                            bestPrice = currentDayPrice
                            datesBestPriceRetour.clear()
                            datesBestPriceRetour.append(dates_elements[j].get_attribute('data-iso'))

                            #Get names of the dates
                            nameDatesBestPriceRetour.clear()
                            print(name_dates_elements[j])
                            nameDatesBestPriceRetour.append(name_dates_elements[j].get_attribute('aria-label'))

                        #If the price is as goodd
                        elif currentDayPrice == bestPrice:
                            #We add it to the array
                            bestPrice = currentDayPrice
                            datesBestPriceRetour.append(dates_elements[j].get_attribute('data-iso'))

                            #Get names of the dates
                            nameDatesBestPriceRetour.append(name_dates_elements[j].get_attribute('aria-label'))

                    else:
                        continue
                except:
                    continue

            #Save the 1st return date for the 1st departure date for our search later
            if(i == 0): firstDateBestPriceRetour.append(datesBestPriceRetour[0])

            #Click OK to leave calendar
            depart_date_done_xpath = '//div[@jsname="WCieBd"]'
            depart_date_done_element = WebDriverWait(driver,3).until(
                EC.presence_of_element_located((By.XPATH, depart_date_done_xpath))
            )
            depart_date_done_element.click()
            time.sleep(0.2)

            #ADD FLIGHT DEPARTURE DATE + RETURN DATES + PRICE
            flightsDict['Departing date'] = namesDepartDates[i]
            flightsDict['Returning date'] = nameDatesBestPriceRetour
            flightsDict['Price'] = bestPrice 

            #Add dictionnary to the array
            flightsArray.append(flightsDict)


        # **************** CLICK ON 1ST DATE OF EACH TO GET FLIGHT INFO ****************
        # We will assume that the best dates with the best prices all have the same type of flights.
        #This is to avoid displaying the details of too many flights, which would also take too much
        #time.

        #Open the calendar (returning box)
        return_box_xpath = '(//input[@jsname="yrriRe"])[6]'
        return_box_element = WebDriverWait(driver,5).until(
            EC.presence_of_element_located((By.XPATH, return_box_xpath))
        )
        return_box_element.click() 
        time.sleep(1)

        #REINITIALIZE, then click on the 2 dates (we select the 1st departing and 1st returning date as default)
        reinitialize_xpath = '(//span[@jsname="V67aGc"])[31]'
        reinitialize_element = WebDriverWait(driver,3).until(
            EC.presence_of_element_located((By.XPATH, reinitialize_xpath))
        )
        reinitialize_element.click() #Click on the departure date
        time.sleep(0.2)

        #Try the 1st date of the best departure dates
        trip_date_xpath = '//div[@data-iso="' + chosenDepartDates[0] + '"]'
        departing_date_element = WebDriverWait(driver,3).until(
            EC.presence_of_element_located((By.XPATH, trip_date_xpath))
        )
        departing_date_element.click()
        time.sleep(0.2)

        #Try the 1st date of the best return dates
        trip_date_xpath = '//div[@data-iso="' + firstDateBestPriceRetour[0] + '"]'


        departing_date_element = WebDriverWait(driver,3).until(
            EC.visibility_of_element_located((By.XPATH, trip_date_xpath))
        )

        departing_date_element = WebDriverWait(driver,3).until(
            EC.presence_of_element_located((By.XPATH, trip_date_xpath))
        )

        try:
            departing_date_element.click() #Click on the departure date
            time.sleep(0.2)
        except:
            #Get the buttton to change the page
            calendar_page_change_xpath = '(//div[@jsname="v6lL4e"])[1]'
            calendar_page_change_element = WebDriverWait(driver,5).until(
                EC.presence_of_element_located((By.XPATH, calendar_page_change_xpath))
            )
            
            #Click twice and wait a bit for the prices to appear
            calendar_page_change_element.click() 
            time.sleep(0.8)

            #Try again to click
            departing_date_element.click() #Click on the departure date
            time.sleep(0.2)
        
        #Click OK to leave calendar
        depart_date_done_xpath = '//div[@jsname="WCieBd"]'
        depart_date_done_element = WebDriverWait(driver,3).until(
            EC.presence_of_element_located((By.XPATH, depart_date_done_xpath))
        )
        depart_date_done_element.click()
        time.sleep(0.2)

        
        #**********************  Click Search  **********************
        try:
            search_button_xpath = '//button[@jsname="vLv7Lb"]'
            search_element = WebDriverWait(driver,3).until(
                EC.presence_of_element_located((By.XPATH, search_button_xpath))
            )
            search_element.click()
            time.sleep(0.2)
        except:
            print("No need to search")

        #******************* SAVE THE FLIGHT DATA ******************
        #Now that we have searched flights for a specific departing and returning date,
        #the flight details will be displayed on the page. We will get the info of those.

        #Click on price sorting to get the cheapest flight
        sort_button_xpath = '//div[@jsname="ajmXBc"]'
        sort_button_element = WebDriverWait(driver,3).until(
            EC.presence_of_element_located((By.XPATH, sort_button_xpath))
        )
        sort_button_element.click()
        time.sleep(0.2)

        #Sort by price
        sort_price_xpath = '(//span[@jsname="K4r5Ff"])[11]'
        sort_price_element = WebDriverWait(driver,3).until(
            EC.presence_of_element_located((By.XPATH, sort_price_xpath))
        )
        sort_price_element.click()
        time.sleep(1)

        #Get 1st flight (DEPARTING)
        best_departure_flight_xpath = '(//li[@class="pIav2d"])[1]'
        best_departure_flight_element = WebDriverWait(driver,3).until(
            EC.presence_of_element_located((By.XPATH, best_departure_flight_xpath))
        )
        
        #Add the departing flight info to the array
        flightsArray.append({'Details of leaving flight': best_departure_flight_element.text.split("\n")})

        #CLICK on the 1st flight to get departing flight and go to the next page to get the returning flight
        best_departure_flight_element.click()
        time.sleep(1)

        #Get 1st flight (RETURNING)
        best_returning_flight_xpath = '(//li[@class="pIav2d"])[1]'
        best_returning_flight_element = WebDriverWait(driver,3).until(
            EC.presence_of_element_located((By.XPATH, best_returning_flight_xpath))
        )

        #Add the returning flight info to the array
        flightsArray.append({'Details of returning flight': best_returning_flight_element.text.split("\n")})

        #Click on the flight to go to the booking page
        best_returning_flight_element.click()
        time.sleep(1)

        #Add the url of the booking page to the array
        urlBooking = driver.current_url
        flightsArray.append({'Link': urlBooking})

        #RETURN THE ARRAY OF ALL DEPARTURE DATES WITH THE POSSIBLE RETURN DATES
        print(flightsArray)
        driver.quit()


        #**********************  DISPLAY THE INFO  **********************

        #Only send an email if we have actual flight info      
        if flightsArray:     
            #Set the HTML display of the email
            html = htmlHead
            html += "<h1>Done! Here are all the possible travel dates</h1>"
            html += "<h3>(for the departing dates you chose earlier)</h3>"
            
            #For each departure/returns pairs
            for i in range(len(flightsArray)):
                #Last element of the array are the flight details
                if (i == len(flightsArray) - 3):

                    #Close table and display title of details table DEPARTING FLIGHT
                    html += "<h1>Details of the flights</h1><h3>Departing flight</h3>"

                    #Create table + header titles
                    html += "<table><thead><tr><th>Departure time</th><th>Arrival time</th><th>Airline</th><th>Flight time</th><th>Route</th><th>Layovers</th></tr></thead><tbody><tr>"

                    #Add all the infos above
                    for j in range(len(flightsArray[i]['Details of leaving flight'])):
                        if(j == 0 or j == 2 or j == 3 or j == 4 or j == 5 or j == 6):
                            html += "<td><p>" + flightsArray[i]['Details of leaving flight'][j] + "</p></td>"

                    #Close table
                    html += "</tr></tbody></table>"

                elif (i == len(flightsArray) - 2):
                    #Close table and display title of details table DEPARTING FLIGHT
                    html += "<h3>Returning flight</h3>"

                    #Create table + header titles
                    html += "<table><thead><tr><th>Departure time</th><th>Arrival time</th><th>Airline</th><th>Flight time</th><th>Route</th><th>Layovers</th></tr></thead><tbody><tr>"

                    #Add all the infos above
                    for j in range(len(flightsArray[i]['Details of returning flight'])):
                        if(j == 0 or j == 2 or j == 3 or j == 4 or j == 5 or j == 6):
                            html += "<td><p>" + flightsArray[i]['Details of returning flight'][j] + "</p></td>"

                    #Close table
                    html += "</tr></tbody></table>"

                elif (i == len(flightsArray) - 1):
                    #Display the link to the booking page and a link back to the search page
                    html += '<br><a href="' + flightsArray[i]["Link"] + '" class="link-button" target="_blank">Link to the booking page</a>'
                    html += '<a href="/" class="link-button">Link to the search page</a>'
                    
                else:
                    #Add table headers
                    html += "<table><thead><tr><th>Departing date</th><th>Returning dates</th><th>Price</th></tr></thead>"

                    #Display departure date
                    html += "<tbody><tr><td><p>"+ flightsArray[i]['Departing date'] + "</p></td><td>"

                    #Display each return date
                    for returnDate in flightsArray[i]['Returning date']:
                        html += "<p>" + returnDate + "</p>"

                    #Display price
                    html += "</td><td><p>" + str(flightsArray[i]['Price']) + "$</p></td></tr></tbody></table><br>"

        html += "</body></html>"

        return render_template_string(html)
        
        # #Else if there are no flights
        # else:
        #   print...
    
    else:
        return render_template_string(html)