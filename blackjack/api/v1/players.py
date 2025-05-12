from flask import request, session
from flask_restx import Resource, fields
from blackjack.api.v1 import ns_player, api
from blackjack.models.user import User
from blackjack import db

# Define models for documentation
player_model = api.model('Player', {
    'id': fields.Integer(required=True, description='Player identifier'),
    'name': fields.String(required=True, description='Player display name'),
    'username': fields.String(required=True, description='Player username'),
    'balance': fields.Integer(description='Player balance'),
    'game_id': fields.String(description='Current game ID')
})

@ns_player.route('/')
class PlayerList(Resource):
    @ns_player.doc('list_players')
    @ns_player.marshal_list_with(player_model)
    def get(self):
        """List top players by balance"""
        players = User.query.order_by(User.balance.desc()).limit(10).all()
        return [p.to_dict() for p in players]

@ns_player.route('/<int:player_id>')
@ns_player.param('player_id', 'The player identifier')
class Player(Resource):
    @ns_player.doc('get_player')
    @ns_player.marshal_with(player_model)
    def get(self, player_id):
        """Get a specific player"""
        player = User.query.get_or_404(player_id)
        return player.to_dict()
        
@ns_player.route('/me')
class CurrentPlayer(Resource):
    @ns_player.doc('get_current_player')
    @ns_player.marshal_with(player_model)
    def get(self):
        """Get the current authenticated player"""
        user_id = session.get('user_id')
        if not user_id:
            api.abort(401, "Not authenticated")
            
        player = User.query.get(user_id)
        if not player:
            api.abort(404, "Player not found")
            
        return player.to_dict() 