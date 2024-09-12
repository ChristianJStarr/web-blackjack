import json
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import scoped_session, sessionmaker

db = SQLAlchemy()


def create_scoped_session():
    """Initialize a scoped session."""
    engine = db.engine
    session_factory = sessionmaker(bind=engine)
    return scoped_session(session_factory)

# Placeholder for the scoped session
get_session = None

def initialize_scoped_session():
    """Initialize the scoped session when the app context is available."""
    global get_session
    if get_session is None:
        get_session = create_scoped_session()

def get_scoped_session():
    """Get the scoped session."""
    if get_session is None:
        raise RuntimeError("Scoped session not initialized.")
    return get_session()

class Game(db.Model):
    __tablename__ = 'games'

    id = db.Column(db.String(4), primary_key=True, nullable=False)
    state_json = db.Column(db.String(5000), nullable=False)

    @property
    def state(self):
        try:
            return json.loads(self.state_json)
        except:
            return {}

    @state.setter
    def state(self, state):
        if not state:
            state = {'id': self.id}
        self.state_json = json.dumps(state)

    def __repr__(self):
        return f'<Game {self.id}>'

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False)
    username = db.Column(db.String(50), unique=True, nullable=False)
    name = db.Column(db.String(50), nullable=False)
    password = db.Column(db.String(50), nullable=False)
    balance = db.Column(db.Integer, nullable=False, default=0)
    game_id = db.Column(db.String(50), nullable=False)
    sid = db.Column(db.String(255), unique=True, nullable=True)

    def __repr__(self):
        return f'<User {self.id}>'

