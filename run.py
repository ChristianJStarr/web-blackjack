import os
from blackjack import create_app, socketio

app = create_app(os.getenv('FLASK_ENV', 'default'))

if __name__ == '__main__':
    socketio.run(app, debug=app.config['DEBUG'], host='0.0.0.0', allow_unsafe_werkzeug=True) 