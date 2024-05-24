# TODO: add error management if flights are not found AND if destination/city doesnt exist

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
# import smtplib
# from email.mime.multipart import MIMEMultipart
# from email.mime.text import MIMEText
# from email.message import EmailMessage
from flask import Flask, jsonify, render_template_string, request, render_template, url_for 

htmlHead = html = """\
<html>
    <head>
        <link rel= "stylesheet" type= "text/css" href= "/static/styles/styles.css">
    </head>
    <body>
"""

# #Arrays that we will fill with the data and get the best price
indexBestDatesDepart = []
nameDatesBestPriceDepart = []
name_dates_elements = []

#Get Chrome webdriver
service = Service(executable_path=r'.\chromedriver.exe')
# service = Service(executable_path=r'/usr/lib/chromium-browser/chromedriver')
options = webdriver.ChromeOptions()
driver = None

# Flask constructor
app = Flask(__name__)   

@app.route('/result', methods =["GET", "POST"])
def searchDepartingDates():
    if request.method == "POST":
        #**********************  Get form data and webdriver  **********************
        #Get the user's input
        leavingFrom = request.form["leavingFrom"]
        destination = request.form["destination"]

        #Get departure and destination airports from user input
        going_to = destination

        #Go to Google Flights
        global driver
        driver = webdriver.Chrome()
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
        global name_dates_elements
        name_dates_elements = WebDriverWait(driver,5).until(
            EC.presence_of_all_elements_located((By.XPATH, name_dates_xpath))
        )
        time.sleep(0.1)

        #Arrays that we will fill with the data and get the best price
        bestPrice = 100000
        datesBestPriceDepart = []
        global nameDatesBestPriceDepart
        nameDatesBestPriceDepart = []
        global indexBestDatesDepart 
        indexBestDatesDepart = []

        #Loop all the dates, compare the prices of each date and get the cheapest dates
        for i in range (len(prices_elements)):
            try:
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
                if(prices_elements[i].text != ""):
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
            html += "<button type='submit' id='search' class='submit' onclick='loading();'>Search</button></div>"

            #Add script to allow user to choose date
            html += """
                <script>
                    let nbSelected = 0;
                    let datesToSearch = [];
                    let datesNames = []

                    document.querySelectorAll('tr').forEach(function(tr) {
                        tr.addEventListener('click', function() {
                            if(tr.classList.contains('selected')) {
                                //Remove the class, decrement nbSelected and remove the date from the array
                                tr.classList.remove('selected')
                                nbSelected--;
                                let indexToRemove = datesToSearch.indexOf(tr.id);
                                datesToSearch.splice(indexToRemove, 1)
                                datesNames.splice(indexToRemove, 1)
                            }

                            else if(nbSelected < 3) {
                                //Add the class, increment nbSelected and add the date to the array
                                tr.classList.add('selected');
                                nbSelected++;
                                datesToSearch.push(tr.id)




                                datesNames.push(tr.children[0].children[0].innerText)
                                console.log("NAME PUSHED: " + datesNames[0])
                            }

                            //TEST
                            console.log("DATES: ")
                            datesToSearch.forEach(function(date) {
                                console.log(date)
                            })
                        })
                    })

                    //FUNCTION LOADING
                    function loading(){
                        //Only hide them if there is a search to make
                        if (nbSelected > 0) {
                            document.getElementById('loading').style.display = 'flex';
                            document.getElementById('content').style.display = 'none';
                        }
                    }

                    //EVENT LISTENER to send the request
                    document.getElementById('search').addEventListener('click', function() {
                        //If at least 1 element is selected
                        if (nbSelected > 0) {
                            var xhr = new XMLHttpRequest();
                            // we defined the xhr

                            xhr.onreadystatechange = function () {
                                if (this.readyState != 4) return;

                                if (this.status == 200) {
                                    var responseHTML = this.responseText;
                                    console.log(responseHTML)
                                    document.open();
                                    document.write(responseHTML);
                                    document.close();
                                }

                                // end of state change: it can be after some time (async)
                            };

                            xhr.open('POST', '/returnDates', true);
                            xhr.setRequestHeader('Content-Type', 'application/json');

                            const data = {dates: datesToSearch, names: datesNames}

                            xhr.send(JSON.stringify(data));
                        }
                    })
                </script>
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


@app.route('/returnDates', methods =["GET", "POST"])
def searchReturningDates():
    print("in good route!")
    if request.method == "POST":
        #Get driver and go to Google Flights
        global driver

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
        time.sleep(1.5)

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
        print(urlBooking)
        flightsArray.append({'Link': urlBooking})

        #RETURN THE ARRAY OF ALL DEPARTURE DATES WITH THE POSSIBLE RETURN DATES
        print(flightsArray)
        driver.quit()


        #**********************  EMAIL SENDING  **********************

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
                    html += '<br><a href="' + flightsArray[i]["Link"] + '" class="link-button">Link to the booking page</a>'
                    
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


        #TODO: Redirect person to /

        return render_template("index.html")
    
@app.route('/', methods =["GET", "POST"])
def index():
    return render_template("index.html")
        
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, threaded=True)

