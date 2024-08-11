from flask import Flask

#Import routes from other files
from routes.searchDepartingFlights import departing_route
from routes.searchReturningFlights import returning_route
from routes.index import index_route

# Flask constructor & get the different routes
app = Flask(__name__)   
app.register_blueprint(departing_route)
app.register_blueprint(returning_route)
app.register_blueprint(index_route)

#Start the app        
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5001, threaded=True)


#cloudflared tunnel --config C:\Users\marti\Desktop\Projets_persos\Test_Website\config.yml run 37621abe-519b-460b-8071-370715656ca0

