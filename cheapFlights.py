from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import time
import pandas as pd
import smtplib
from email.message import EmailMessage
from flask import Flask, request, render_template 
  
# Flask constructor
app = Flask(__name__)   

@app.route('/', methods =["GET", "POST"])
def home():
    if request.method == "POST":
        #**********************  Get form data and webdriver  **********************

        #Get the user's input
        leavingFrom = request.form["leavingFrom"]
        destination = request.form["destination"]
        # password = request.form["password"]
        # sender = request.form["emailSender"]
        # recipient = request.form["emailReceiver"]

        #Get Chrome webdriver
        service = Service(executable_path=r'.\chromedriver.exe')
        options = webdriver.ChromeOptions()
        driver = webdriver.Chrome(service=service, options=options)

        #Get departure and destination airports from user input
        going_to = destination

        #Go to Google Flights
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

        print(leavingFrom)
        leaving_from_element.click()
        time.sleep(0.1)
        leaving_from_element.clear()
        time.sleep(0.1)
        leaving_from_element.send_keys(leavingFrom)
        time.sleep(0.1)
        leaving_from_element.send_keys(Keys.DOWN, Keys.RETURN) 

        
        #**********************  DEPARTURE DATES/PRICE FINDER  **********************
        #The calendar opens alone so we wait a bit
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

        #arrays that we will fill with the data and get the best price
        bestPrice = 100000
        datesBestPriceDepart = []
        nameDatesBestPriceDepart = []
        indexBestDatesDepart = []
        firstDateBestPriceRetour = []

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

            except:
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

        #Initialize flights array
        #We will return it at the end with all the info
        flightsArray = []

        #********************** LOOP THROUGH ALL DEPARTURE DATES***********************

        #We loop through all the departing dates, to get the best returning dates for each.
        for i in range(len(datesBestPriceDepart)):
            #INITIALIZE DICTIONNARY FOR EACH DEPARTURE DATE POSSIBLE
            flightsDict = {}

            #Limit to 3 departing dates (in case there are more. You can change it!)
            if (i == 3): break

            #Open departure calendar
            departing_box_xpath = '(//input[@jsname="yrriRe"])[5]'
            depart_box_element = WebDriverWait(driver,5).until(
                EC.presence_of_element_located((By.XPATH, departing_box_xpath))
            )
            depart_box_element.click()
            time.sleep(0.2)

            #Try ALL the dates
            trip_date_xpath = '//div[@data-iso="' + datesBestPriceDepart[i] + '"]'
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
                    #We will ONLY check the returning flights in a 2 month span of the departing date.
                    if (j > indexBestDatesDepart[i] + 57 and prices_elements[j].text == ""):
                        break

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
            flightsDict['Departing date'] = nameDatesBestPriceDepart[i]
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
        trip_date_xpath = '//div[@data-iso="' + datesBestPriceDepart[0] + '"]'
        departing_date_element = WebDriverWait(driver,3).until(
            EC.presence_of_element_located((By.XPATH, trip_date_xpath))
        )
        departing_date_element.click()
        time.sleep(0.2)

        #Try the 1st date of the best return dates
        trip_date_xpath = '//div[@data-iso="' + firstDateBestPriceRetour[0] + '"]'
        departing_date_element = WebDriverWait(driver,3).until(
            EC.presence_of_element_located((By.XPATH, trip_date_xpath))
        )
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
        search_button_xpath = '//button[@jsname="vLv7Lb"]'
        search_element = WebDriverWait(driver,3).until(
            EC.presence_of_element_located((By.XPATH, search_button_xpath))
        )
        search_element.click()
        time.sleep(0.2)

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

            # email = EmailMessage()
            # email = MIMEMultipart('alternative')
            # email["From"] = sender
            # email["To"] = recipient
            # email["Subject"] = "Vols pas chers: {} --> {}".format(leavingFrom, destination)

            #Set the HTML display of the email
            html = """\
            <html>
                <head>
                    <style>
                        html {
                            width: 100%;
                            height: 100%;
                        }

                        body {
                            display: flex;
                            flex-direction: column;
                            align-items: center;
                            width: 100%;
                            height: 100%;
                            margin: 2%;
                            overflow-x: hidden;
                            overflow-y: scroll;
                            background-color: #F4D03F;
                            background-image: linear-gradient(132deg, #F4D03F 0%, #16A085 100%);
                            background-repeat: no-repeat;
                            background-attachment: fixed;
                            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, 'Open Sans', 'Helvetica Neue', sans-serif
                        }

                        table {
                            width: 800px;
                            border-collapse: collapse;
                            overflow: hidden;
                            box-shadow: 0 0 20px rgba(0,0,0,0.1);
                        }

                        th,
                        td {
                            padding: 15px;
                            background-color: rgba(255,255,255,0.2);
                            color: #000000;
                        }

                        th {
                            text-align: left;
                        }

                        thead {
                            th {
                                background-color: #27270821;
                            }
                        }

                        tbody {
                            tr {
                                &:hover {
                                background-color: rgba(255,255,255,0.3);
                                }
                            }
                            td {
                                position: relative;
                                &:hover {
                                    &:before {
                                        content: "";
                                        position: absolute;
                                        left: 0;
                                        right: 0;
                                        top: -9999px;
                                        bottom: -9999px;
                                        background-color: rgba(255,255,255,0.2);
                                        z-index: -1;
                                    }
                                }
                            }
                        }

                        a {
                            margin-bottom: 2%;
                        }
                    </style>
                </head>
                <body>
            """
            
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
                    html += '<br><a href="' + flightsArray[i]["Link"] + '">Link to the booking page</a>'
                    
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

            # htmlText = MIMEText(html, 'html')
            # email.attach(htmlText)

            # #Login to the input email and send the mail
            # smtp = smtplib.SMTP("smtp-mail.outlook.com", port=587)
            # smtp.starttls()
            # smtp.login(sender, password)
            # smtp.sendmail(sender, recipient, email.as_string())
            # smtp.quit()

            html += "</body>"

            #return page
            print(html)
            return html
    
    else:
        return render_template("index.html")
        
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, threaded=True)

