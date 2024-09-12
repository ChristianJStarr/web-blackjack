from flask_socketio import join_room, leave_room
import blackjack.utility as u
from blackjack.config import BlackJackConfig
from blackjack.game import BlackJackGame
from blackjack.player import BlackjackPlayer
from models import Game, get_scoped_session, User


class BlackJackGameManager:
    def __init__(self, app, socketio):
        self.app = app
        self.socketio = socketio
        self.games = {}


    def bump_game(self, game):
        with self.app.app_context():
            self.socketio.start_background_task(game.bump)


    def get_game(self, id):

        if not id or not u.valid_game_id(id):
            return None

        if id in self.games:
            return self.games[id]

        session = get_scoped_session()
        game = session.get(Game, id)

        config = BlackJackConfig()

        if game:
            config.load(game.state.get('config'))

        blackjack_game = BlackJackGame(id,
           message_fn=self.message,
           sleep_fn=self.sleep,
           config=config)

        if game:
            blackjack_game.load(game.state)
        else:
            game = Game(id=id, state=blackjack_game.save())
            session.add(game)
            session.commit()

        self.games[id] = blackjack_game

        return blackjack_game
    def get_player(self, id):
        player = BlackjackPlayer(id)
        player.update()
        return player


    def connect_game(self, game_id, user_id, session_id):
        success = None
        error = None

        try:
            if not game_id:
                error = 'Game ID must be provided'
                return

            if not user_id:
                error = 'User ID must be provided'
                return

            game = self.get_game(game_id)
            if not game:
                error = 'Unable to find or create game'
                return

            session = get_scoped_session()
            try:
                user = session.get(User, user_id)
                user.sid = session_id
                user.game_id = game.id
                session.commit()
                success = True
            except Exception as e:
                session.rollback()

        except:
            error = 'Unable to connect to game'
        finally:
            return success, error
    def join_game(self, game_id, user_id):
        success = None
        error = None

        try:
            if not game_id:
                error = 'Game ID must be provided'
                return

            if not user_id:
                error = 'User ID must be provided'
                return

            game = self.get_game(game_id)
            if not game:
                error = 'Unable to find or create game'
                return

            player = self.get_player(user_id)
            if not player:
                error = 'Unable to find or create player'
                return

            join_room(game.id)

            success, error = game.add_player(player)

            if success:
                self.bump_game(game)
            else:
                leave_room(game.id)

        except:
            error = 'Unable to join game'
        finally:
            return success, error
    def leave_game(self, game_id, user_id):
        success = None
        error = None

        try:
            if not game_id:
                error = 'Game ID must be provided'
                return

            if not user_id:
                error = 'User ID must be provided'
                return

            game = self.get_game(game_id)
            if not game:
                error = 'Unable to find or create game'
                return

            leave_room(game.id)
            game.remove_player(user_id)

            session = get_scoped_session()
            try:
                user = session.get(User, user_id)
                user.sid = None
                user.game_id = None
                session.commit()
                success = True
            except Exception as e:
                session.rollback()
        except:
            error = 'Unable to leave game'
        finally:
            return success, error


    def player_action(self, game_id, user_id, action):
        success = None
        error = None

        try:
            if not action:
                error = 'Action must be provided'
                return

            if not game_id:
                error = 'Game ID must be provided'
                return

            if not user_id:
                error = 'User ID must be provided'
                return

            game = self.get_game(game_id)
            if not game:
                error = 'Unable to find or create game'
                return

            player = self.get_player(user_id)
            if not player:
                error = 'Unable to find or create player'
                return

            success, error = game.player_action(player, action)

        except:
            error = 'Unable to perform action'
        finally:
            return success, error
    def player_bet(self, game_id, user_id, bet):
        success = None
        error = None

        try:
            if not bet:
                error = 'Bet must be provided'
                return

            if not game_id:
                error = 'Game ID must be provided'
                return

            if not user_id:
                error = 'User ID must be provided'
                return

            game = self.get_game(game_id)
            if not game:
                error = 'Unable to find or create game'
                return

            player = self.get_player(user_id)
            if not player:
                error = 'Unable to find or create player'
                return

            success, error = game.player_bet(player, bet)


        except:
            error = 'Unable to place bet'
        finally:
            return success, error


    def sleep(self, seconds):
        self.socketio.sleep(seconds)
    def message(self, key, data, to=None):
        if to:
            self.socketio.emit(key, data, to=to)
        else:
            self.socketio.emit(key, data)