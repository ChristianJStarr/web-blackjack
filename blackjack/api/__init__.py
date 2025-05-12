from flask import Blueprint

api = Blueprint('api', __name__)

# Import routes
from blackjack.api.v1 import * 