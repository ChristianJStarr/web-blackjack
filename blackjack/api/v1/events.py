from flask import session, current_app, request
from flask_socketio import join_room, leave_room, emit
from blackjack import socketio
from blackjack.game.adapters import GameDbAdapter
from blackjack.models.user import User
from blackjack import db

@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    game_id = session.get('game_id')
    user_id = session.get('user_id')
    
    if not game_id:
        return
        
    current_app.logger.info(f"User {user_id} connected to game {game_id}")
    
    # Join the game room
    join_room(game_id)
    
    # Update user's socket ID
    if user_id:
        user = User.query.get(user_id)
        if user:
            user.game_id = game_id
            user.sid = request.sid
            db.session.commit()
    
    # Get game state
    try:
        game = GameDbAdapter.load_game(game_id)
        emit('connected', {
            'success': True,
            'game_state': game.to_dict()
        })
    except Exception as e:
        current_app.logger.error(f"Error getting game state: {str(e)}")
        emit('connected', {
            'success': False,
            'error': 'Unable to load game'
        })

@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection"""
    game_id = session.get('game_id')
    user_id = session.get('user_id')
    
    current_app.logger.info(f"User {user_id} disconnected from game {game_id}")
    
    if game_id:
        leave_room(game_id)
    
    # Update user's socket ID
    if user_id:
        user = User.query.get(user_id)
        if user:
            user.sid = None
            db.session.commit()
            
    # Remove player from game
    if game_id and user_id:
        try:
            game = GameDbAdapter.load_game(game_id)
            game.remove_player(user_id)
            GameDbAdapter.save_game(game)
            
            # Broadcast updated game state
            emit('game_update', game.to_dict(), to=game_id)
        except Exception as e:
            current_app.logger.error(f"Error removing player from game: {str(e)}")

@socketio.on('join_game')
def handle_join_game(data):
    """Handle player joining a game"""
    game_id = session.get('game_id')
    user_id = session.get('user_id')
    seat_id = data.get('seat_id')
    
    if not game_id or not user_id or not seat_id:
        emit('join_game_response', {
            'success': False,
            'error': 'Missing required parameters'
        })
        return
        
    current_app.logger.info(f"User {user_id} attempting to join game {game_id} at seat {seat_id}")
    
    try:
        game = GameDbAdapter.load_game(game_id)
        seat_id, error = game.add_player(user_id, seat_id)
        
        if error:
            emit('join_game_response', {
                'success': False,
                'error': error
            })
            return
            
        # Save game state
        GameDbAdapter.save_game(game)
        
        # Broadcast updated game state
        emit('game_update', game.to_dict(), to=game_id)
        
        emit('join_game_response', {
            'success': True,
            'seat_id': seat_id
        })
    except Exception as e:
        current_app.logger.error(f"Error joining game: {str(e)}")
        emit('join_game_response', {
            'success': False,
            'error': 'An unexpected error occurred'
        })

@socketio.on('player_action')
def handle_player_action(data):
    """Handle player game actions (hit, stand, etc.)"""
    game_id = session.get('game_id')
    user_id = session.get('user_id')
    action = data.get('action')
    
    if not game_id or not user_id or not action:
        emit('player_action_response', {
            'success': False,
            'error': 'Missing required parameters'
        })
        return
        
    current_app.logger.info(f"User {user_id} performing action {action} in game {game_id}")
    
    try:
        game = GameDbAdapter.load_game(game_id)
        success, error = game.player_action(user_id, action)
        
        if not success:
            emit('player_action_response', {
                'success': False,
                'error': error,
                'action': action
            })
            return
            
        # Save game state
        GameDbAdapter.save_game(game)
        
        # Broadcast updated game state
        emit('game_update', game.to_dict(), to=game_id)
        
        emit('player_action_response', {
            'success': True,
            'action': action
        })
    except Exception as e:
        current_app.logger.error(f"Error processing player action: {str(e)}")
        emit('player_action_response', {
            'success': False,
            'error': 'An unexpected error occurred',
            'action': action
        })

@socketio.on('player_bet')
def handle_player_bet(data):
    """Handle player betting"""
    game_id = session.get('game_id')
    user_id = session.get('user_id')
    amount = data.get('amount')
    
    if not game_id or not user_id or not amount:
        emit('player_bet_response', {
            'success': False,
            'error': 'Missing required parameters'
        })
        return
        
    current_app.logger.info(f"User {user_id} placing bet of {amount} in game {game_id}")
    
    try:
        game = GameDbAdapter.load_game(game_id)
        success, error = game.place_bet(user_id, int(amount))
        
        if not success:
            emit('player_bet_response', {
                'success': False,
                'error': error,
                'amount': amount
            })
            return
            
        # Save game state
        GameDbAdapter.save_game(game)
        
        # Broadcast updated game state
        emit('game_update', game.to_dict(), to=game_id)
        
        emit('player_bet_response', {
            'success': True,
            'amount': amount
        })
    except Exception as e:
        current_app.logger.error(f"Error processing player bet: {str(e)}")
        emit('player_bet_response', {
            'success': False,
            'error': 'An unexpected error occurred',
            'amount': amount
        }) 