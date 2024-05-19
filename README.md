# Cheap flights finder

# What is Cheap flights finder?
This python program scrapes data from the Google Flights website. It returns the dates where the flights are at the cheapest price for a given source and destination airport

# How to install dependencies
First, this program has many dependencies. You need to install them before being able to use the program:
- Selenium
- Flask

You can install them with the following commands:
- `pip install flask`
- `pip install selenium`

The script uses Chromedriver to scrape the data. The driver is already included in the repository, but make sure that it is compatible with your version of chrome.
Else, replace it by installing the right version in [this link](https://googlechromelabs.github.io/chrome-for-testing/). 

Choose the version for your Chrome version and for your operating system. Then, replace the chromedriver named "chromedriver.exe" with the chromedriver you downloaded. **They must have the same name!**

# How to use it
Once everything is installed, you can run the python script "cheapFlights.py". This starts a local server, so you can head to the following url:
- `http://localhost:5000`

This opens up a nice (ugly) form. You simply input your home airport and the destination you want to fly to. Then wait for the magic to happen!

After about a minute, the results appear on the page. Tables with every departing date along with their respective possible returning dates show up. As well as the details of the departing/returning flight(s), and a link directly to the Google Flights page (you might have to adjust the dates according to the days you want to fly of all the possible dates the program found).

Enjoy, and hope you find some good deals with that!
