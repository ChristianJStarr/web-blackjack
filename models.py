from flask import current_app
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


class BlackjackPlayer(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False)
    username = db.Column(db.String(50), unique=True, nullable=False)
    name = db.Column(db.String(50), nullable=False)
    password = db.Column(db.String(50), nullable=False)
    balance = db.Column(db.Integer, nullable=False, default=0)
    game_id = db.Column(db.String(50), nullable=False)
    sid = db.Column(db.String(255), unique=True, nullable=True)

    def can_bet(self, amount):
        return self.balance >= amount

    def add_funds(self, amount):
        session = get_scoped_session()
        try:
            self.balance += amount
            session.commit()
        except Exception as e:
            session.rollback()
            print(f"Error adding funds: {e}")

    def remove_funds(self, amount):
        session = get_scoped_session()
        try:
            if self.can_bet(amount):
                self.balance -= amount
                session.commit()
            else:
                print(f"Player {self.id} cannot bet {amount}.")
        except Exception as e:
            session.rollback()
            print(f"Error removing funds: {e}")

    def __repr__(self):
        return f'<BlackjackPlayer {self.username}>'

    @property
    def state(self):
        return {
            'name': self.name,
            'id': self.id,
        }
