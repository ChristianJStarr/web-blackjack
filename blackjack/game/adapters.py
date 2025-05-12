from blackjack import db
from blackjack.models.game import Game
from blackjack.game.utility import generate_id
from blackjack.exceptions import GameNotFoundError
from blackjack.game.game import BlackjackGame
from flask import current_app

class GameDbAdapter:
    """Adapter for game state persistence in database"""
    
    @staticmethod
    def create_game():
        """Create a new game in the database"""
        game_id = generate_id()
        # Ensure ID is unique
        while Game.query.get(game_id):
            game_id = generate_id()
            
        blackjack_game = BlackjackGame(game_id)
        game = Game(id=game_id, state=blackjack_game.to_dict())
        
        db.session.add(game)
        db.session.commit()
        
        return blackjack_game
    
    @staticmethod
    def save_game(game):
        """Save game state to database"""
        game_data = game.to_dict()
        db_game = Game.query.get(game.game_id)
        
        if db_game:
            db_game.state = game_data
            db.session.commit()
            return True
        else:
            current_app.logger.error(f"Game {game.game_id} not found in database for saving")
            return False
    
    @staticmethod
    def load_game(game_id):
        """Load game state from database"""
        db_game = Game.query.get(game_id)
        
        if not db_game:
            current_app.logger.warning(f"Game {game_id} not found in database")
            # Create new game if it doesn't exist
            blackjack_game = BlackjackGame(game_id)
            game = Game(id=game_id, state=blackjack_game.to_dict())
            db.session.add(game)
            db.session.commit()
            return blackjack_game
            
        try:
            return BlackjackGame.from_dict(db_game.state)
        except Exception as e:
            current_app.logger.error(f"Error deserializing game {game_id}: {str(e)}")
            raise GameNotFoundError(f"Unable to load game {game_id}")
    
    @staticmethod
    def delete_game(game_id):
        """Delete game from database"""
        db_game = Game.query.get(game_id)
        
        if db_game:
            db.session.delete(db_game)
            db.session.commit()
            return True
        return False
    
    @staticmethod
    def get_active_games():
        """Get list of active games"""
        games = Game.query.order_by(Game.updated_at.desc()).all()
        return [{
            'id': game.id,
            'state': game.state,
            'updated_at': game.updated_at
        } for game in games] 