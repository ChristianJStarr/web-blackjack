from flask import request
from flask_restx import Resource, fields
from blackjack.api.v1 import ns_game, api
from blackjack.game.adapters import GameDbAdapter

# Define models for documentation
game_model = api.model('Game', {
    'id': fields.String(required=True, description='Game identifier'),
    'state': fields.String(description='Current game state'),
    'players': fields.Integer(description='Number of players'),
    'updated_at': fields.DateTime(description='Last update time')
})

@ns_game.route('/')
class GameList(Resource):
    @ns_game.doc('list_games')
    @ns_game.marshal_list_with(game_model)
    def get(self):
        """List all games"""
        return GameDbAdapter.get_active_games()
        
    @ns_game.doc('create_game')
    @ns_game.marshal_with(game_model, code=201)
    def post(self):
        """Create a new game"""
        game = GameDbAdapter.create_game()
        return {'id': game.game_id, 'state': game.state}, 201

@ns_game.route('/<game_id>')
@ns_game.param('game_id', 'The game identifier')
class Game(Resource):
    @ns_game.doc('get_game')
    @ns_game.marshal_with(game_model)
    def get(self, game_id):
        """Get a specific game"""
        game = GameDbAdapter.load_game(game_id)
        return {'id': game.game_id, 'state': game.state}
        
    @ns_game.doc('delete_game')
    def delete(self, game_id):
        """Delete a game"""
        success = GameDbAdapter.delete_game(game_id)
        return {'success': success}, 200 if success else 404 