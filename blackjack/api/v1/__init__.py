from flask_restx import Api
from blackjack.api import api as api_blueprint

api = Api(
    api_blueprint,
    version='1.0',
    title='Blackjack API',
    description='A RESTful API for Blackjack game',
    doc='/doc'
)

# Define namespaces
ns_game = api.namespace('games', description='Game operations')
ns_player = api.namespace('players', description='Player operations')
ns_auth = api.namespace('auth', description='Authentication operations')

# Import resources
from . import games, players, auth, events 