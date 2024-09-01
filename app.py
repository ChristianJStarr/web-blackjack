from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit, join_room, leave_room
from blackjack import BlackJackGameManager

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, cors_allowed_origins="*")
game_manager = BlackJackGameManager()


def sleep(seconds):
    socketio.sleep(seconds)

def message(key, data, to=None):
    try:
        if not isinstance(key, str):
            print(f'Invalid key type: {type(key)}')
            return
        print(f'key: {key}, data: {data}, to: {to}')
        if to:
            socketio.emit(key, data, to=to)
        else:
            socketio.emit(key, data)
    except:
        print('err')

@app.route('/')
def home():
    games = game_manager.games
    return render_template('index.html', games=list(games.items()))

@app.route('/game/<game_id>')
def game(game_id):
    game = game_manager.get_game(game_id)
    if not game:
        game = game_manager.create_game(game_id, message, sleep)
        socketio.start_background_task(game.game_loop)

    return render_template('game.html', game_id=game_id)

@socketio.on('disconnect')
def disconnect():
    player, game = game_manager.get_session(request.sid)
    if game:
        game.remove_player(player)
        leave_room(game.id)

@socketio.on('join_game')
def handle_join_game(data):
    print('handle_join_game')
    player, game = game_manager.get_session(request.sid)

    if not game and data.get('game_id'):
        game = game_manager.get_game(data.get('game_id'))
        if game:
            player.game_id = game.id

    role = data.get('role')

    if not game:
        emit('error', {'message': 'Game not found'})
        return

    if not player:
        emit('error', {'message': 'Player not found'})
        return

    if not role:
        emit('error', {'message': 'Invalid role'})
        return

    socketio.start_background_task(game.bump)
    join_room(game.id)

    seat_id, error = game.add_player(player, role)

    if not seat_id:
        emit('error', {'message': error})
    else:
        print('assigning player')
        emit('player_assigned', {
            'player_id': player.id,
            'seat_id': seat_id,
            'balance': player.balance
        })

@socketio.on('player_action')
def handle_player_action(data):
    player, game = game_manager.get_session(request.sid)
    action = data.get('action')

    if not game:
        emit('error', {'message': 'Game not found'})
        return

    if not player:
        emit('error', {'message': 'Player not found'})
        return

    if not action:
        emit('error', {'message': 'Invalid action'})
        return

    success, error = game.player_action(player, action)

    if not success:
        emit('error', {'message': error})
    else:
        emit('player_action', {'success': True})

@socketio.on('player_bet')
def handle_player_bet(data):
    player, game = game_manager.get_session(request.sid)
    amount = data.get('amount')

    if not game:
        emit('error', {'message': 'Game not found'})
        return

    if not player:
        emit('error', {'message': 'Player not found'})
        return

    if not amount:
        emit('error', {'message': 'Amount required'})
        return
    print('player bet', amount)
    success, error = game.player_bet(player, amount)
    print('player bet', amount)
    if not success:
        print('player error', amount)
        emit('error', {'message': error})
    else:
        print('player success', amount)
        emit('player_bet', {'success': True})



if __name__ == '__main__':
    socketio.run(app, host="0.0.0.0", debug=True, allow_unsafe_werkzeug=True)

