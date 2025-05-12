from flask import Blueprint

api_bp = Blueprint('api', __name__)

# Import routes
from blackjack.api.v1 import api  # Import the API instance, not all modules 