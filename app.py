from flask import Flask, render_template, request, redirect, jsonify, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash
from flask_socketio import SocketIO, emit
from sqlalchemy.exc import SQLAlchemyError
from blackjack import BlackJackGameManager
from models import db, BlackjackPlayer, initialize_scoped_session, get_scoped_session

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
app.secret_key = 'secret!'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://dev:NOe2C3R3O8ED@159.89.176.186/blackjack'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)
with app.app_context():
    initialize_scoped_session()

from blackjack import BlackJackGameManager
from flask_socketio import SocketIO

socketio = SocketIO(app, cors_allowed_origins="*")
game_manager = BlackJackGameManager(app, socketio)


def get_leaderboard():
    leaderboard = []
    try:
        leaderboard = BlackjackPlayer.query.order_by(BlackjackPlayer.balance.desc()).all()
    except:
        pass
    finally:
        return leaderboard


##-----------------------------------------------------
## Pages
##-----------------------------------------------------
@app.route('/')
def index():
    player_id = session.get('player_id')
    player = BlackjackPlayer.query.get(player_id)
    return render_template('index.html',
        games=list(game_manager.games.items()),
        player=player,
        leaderboard=get_leaderboard()
    )
@app.route('/game/<game_id>')
def game(game_id):
    game = game_manager.get_or_create_game(game_id)
    player_id = session.get('player_id')
    player = BlackjackPlayer.query.get(player_id)
    if game:
        session['game_id'] = game.id

    return render_template('game.html',
                           game=game,
                           player_required=True,
                           player=player,
        leaderboard=get_leaderboard())
@app.route('/privacy')
def privacy():
    return render_template('privacy.html')
@app.route('/terms')
def terms():
    return render_template('terms.html')


##-----------------------------------------------------
## Authentication
##-----------------------------------------------------
@app.route('/login', methods=['POST'])
def login():
    response = {
        'success': False,
        'errors': []
    }
    try:
        username = request.form.get('username')
        password = request.form.get('password')

        if not username or not password:
            response['errors'].append('Username and Password must be provided')
            return jsonify(response), 400

        player = BlackjackPlayer.query.filter_by(username=username).first()
        if player:
            if check_password_hash(player.password, password):
                session['player_id'] = player.id
                response['success'] = True
                return jsonify(response), 200
            else:
                response['errors'].append('Incorrect password')
        else:
            response['errors'].append('User does not exist')

    except SQLAlchemyError as e:
        response['errors'].append(f'Database error: {str(e)}')
    except Exception as e:
        response['errors'].append(f'An unexpected error occurred: {str(e)}')
    finally:
        return jsonify(response), 500 if response['errors'] else 200
@app.route('/signup', methods=['POST'])
def signup():
    response = {
        'success': False,
        'errors': []
    }
    try:
        username = request.form.get('username')
        name = request.form.get('name')
        password = request.form.get('password')

        if not username or not password or not name:
            response['errors'].append('Name, Username, and Password must be provided')
            return jsonify(response), 400

        if BlackjackPlayer.query.filter_by(username=username).first():
            response['errors'].append('User already exists')
            return jsonify(response), 400

        hashed_password = generate_password_hash(password)
        new_player = BlackjackPlayer(username=username, name=name, password=hashed_password, balance=5000)
        db.session.add(new_player)
        db.session.commit()

        session['player_id'] = new_player.id
        response['success'] = True
        return jsonify(response), 201

    except SQLAlchemyError as e:
        response['errors'].append(f'Database error: {str(e)}')
    except Exception as e:
        response['errors'].append(f'An unexpected error occurred: {str(e)}')
    finally:
        return jsonify(response), 500 if response['errors'] else 200
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))


##-----------------------------------------------------
## Sockets
##-----------------------------------------------------
@socketio.on('connect')
def handle_connect():
    player_id = session.get('player_id')
    game_id = session.get('game_id')
    if player_id:
        player = BlackjackPlayer.query.get(player_id)
        if player:
            player.sid = request.sid
            if game_id:
                player.game_id = game_id
            db.session.commit()
@socketio.on('disconnect')
def handle_disconnect():
    player = None
    game = None

    player_id = session.get('player_id')
    game_id = session.get('game_id')

    if player_id:
        player = BlackjackPlayer.query.get(player_id)

    if game_id:
        game = game_manager.get_game(game_id)

    if player:
        player.sid = None
        player.game_id = None
        db.session.commit()
        if game:
            game_manager.leave_game(game, player)
@socketio.on('join_game')
def handle_join_game(data):

    # Get the Game
    game_id = session.get('game_id')
    game = game_manager.get_or_create_game(game_id)
    if not game:
        emit('error', {'message': 'Unable to create game'})
        return

    # Get the Player
    player_id = session.get('player_id')
    player = BlackjackPlayer.query.get(player_id)
    if not player:
        emit('error', {'message': 'Player not found'})
        return

    # Join the Game
    game_manager.join_game(game, player)
@socketio.on('player_action')
def handle_player_action(action):

    # Get the Action
    if not action:
        emit('error', {'message': 'Invalid action'})
        return

    # Get the Game
    game_id = session.get('game_id')
    game = game_manager.get_game(game_id)
    if not game:
        emit('error', {'message': 'Game not found'})
        return

    # Get the Player
    player_id = session.get('player_id')
    player = BlackjackPlayer.query.get(player_id)
    if not player:
        emit('error', {'message': 'Player not found'})
        return

    game_manager.player_action(game, player, action)
@socketio.on('player_bet')
def handle_player_bet(data):
    # Get the Game
    game_id = session.get('game_id')
    game = game_manager.get_game(game_id)
    if not game:
        emit('error', {'message': 'Game not found'})
        return

    # Get the Player
    player_id = session.get('player_id')
    db_session = get_scoped_session()
    player = db_session.query(BlackjackPlayer).get(player_id)
    if not player:
        emit('error', {'message': 'Player not found'})
        return

    # Get the Amount
    amount = data.get('amount')
    if not amount:
        emit('error', {'message': 'Invalid amount'})
        return

    game_manager.player_bet(game, player, amount)


if __name__ == '__main__':
    socketio.run(app, debug=True, host='0.0.0.0', allow_unsafe_werkzeug=True)

