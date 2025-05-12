from blackjack import db

class User(db.Model):
    """User model for authentication and player information"""
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False)
    username = db.Column(db.String(50), unique=True, nullable=False)
    name = db.Column(db.String(50), nullable=False)
    password = db.Column(db.String(255), nullable=False)
    balance = db.Column(db.Integer, nullable=False, default=10000)
    game_id = db.Column(db.String(50), nullable=True)
    sid = db.Column(db.String(255), unique=True, nullable=True)
    
    def __repr__(self):
        return f'<User {self.id}>'
        
    def to_dict(self):
        """Convert user to dictionary for serialization"""
        return {
            'id': self.id,
            'username': self.username,
            'name': self.name,
            'balance': self.balance,
            'game_id': self.game_id
        } 