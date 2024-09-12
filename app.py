from flask import Flask, render_template, request, redirect, jsonify, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash
from flask_socketio import emit
from sqlalchemy.exc import SQLAlchemyError
from blackjack.game_manager import BlackJackGameManager
from models import db, initialize_scoped_session, get_scoped_session, User
import blackjack.utility as u

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
app.secret_key = 'secret!'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://dev:NOe2C3R3O8ED@159.89.176.186/blackjack'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)
with app.app_context():
    initialize_scoped_session()

from flask_socketio import SocketIO

socketio = SocketIO(app, cors_allowed_origins="*")
game_manager = BlackJackGameManager(app, socketio)




##-----------------------------------------------------
## Pages
##-----------------------------------------------------
@app.route('/')
def index():
    scoped_session = get_scoped_session()
    user_id = session.get('user_id')
    user = scoped_session.get(User, user_id)
    leaderboard = scoped_session.query(User).order_by(User.balance).all()
    return render_template('index.html',
        games=list(game_manager.games.items()),
        player=user,
        leaderboard=leaderboard
    )
@app.route('/game/<game_id>')
def game(game_id):
    if not u.valid_game_id(game_id):
        return redirect(url_for('index'))

    game = game_manager.get_game(game_id)
    if not game:
        return redirect(url_for('index'))

    scoped_session = get_scoped_session()
    user_id = session.get('user_id')
    user = scoped_session.get(User, user_id)
    session['game_id'] = game.id
    leaderboard = scoped_session.query(User).order_by(User.balance).all()

    return render_template('game.html',
       game=game,
       player_required=True,
       player=user,
       leaderboard=leaderboard
    )
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

        player = User.query.filter_by(username=username).first()
        if player:
            if check_password_hash(player.password, password):
                session['user_id'] = player.id
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

        if User.query.filter_by(username=username).first():
            response['errors'].append('User already exists')
            return jsonify(response), 400

        hashed_password = generate_password_hash(password)
        new_player = User(username=username, name=name, password=hashed_password, balance=5000)
        db.session.add(new_player)
        db.session.commit()

        session['user_id'] = new_player.id
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
    game_id = session.get('game_id')
    user_id = session.get('user_id')
    game_manager.connect_game(game_id, user_id, request.sid)
@socketio.on('disconnect')
def handle_disconnect():
    game_id = session.get('game_id')
    user_id = session.get('user_id')
    game_manager.leave_game(game_id, user_id)
@socketio.on('join_game')
def handle_join_game(role):
    game_id = session.get('game_id')
    user_id = session.get('user_id')
    seat_id, error = game_manager.join_game(game_id, user_id)

    emit('join_game', {
        'success': not not seat_id,
        'seat_id': seat_id,
        'error': error,
        'role': role
    })
@socketio.on('player_action')
def handle_player_action(action):
    game_id = session.get('game_id')
    user_id = session.get('user_id')
    success, error = game_manager.player_action(game_id, user_id, action)

    emit('player_action', {
        'success': success,
        'error': error,
        'action': action
    })
@socketio.on('player_bet')
def handle_player_bet(amount):
    game_id = session.get('game_id')
    user_id = session.get('user_id')
    success, error = game_manager.player_bet(game_id, user_id, amount)

    emit('player_bet', {
        'success': success,
        'error': error,
        'amount': amount
    })





if __name__ == '__main__':
    socketio.run(app, debug=True, host='0.0.0.0', allow_unsafe_werkzeug=True)

