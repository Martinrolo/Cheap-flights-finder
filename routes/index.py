from flask import Blueprint, render_template

index_route = Blueprint('/', __name__, template_folder="templates")
@index_route.route('/', methods =["GET", "POST"])
def index():
    return render_template("index.html")