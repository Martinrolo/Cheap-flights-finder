from flask import Blueprint
routes = Blueprint('routes', __name__)

from .searchDepartingFlights import *
from .searchReturningFlights import *