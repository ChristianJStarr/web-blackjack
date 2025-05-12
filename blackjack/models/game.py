import json
from blackjack import db

class Game(db.Model):
    """Game model for persisting game state"""
    __tablename__ = 'games'

    id = db.Column(db.String(4), primary_key=True, nullable=False)
    state_json = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, server_default=db.func.now(), onupdate=db.func.now())
    
    @property
    def state(self):
        """Deserialize game state from JSON"""
        try:
            return json.loads(self.state_json)
        except:
            return {}

    @state.setter
    def state(self, state):
        """Serialize game state to JSON"""
        if not state:
            state = {'id': self.id}
        self.state_json = json.dumps(state)

    def __repr__(self):
        return f'<Game {self.id}>'
        
    @classmethod
    def get_active_games(cls):
        """Get list of active games"""
        return cls.query.order_by(cls.updated_at.desc()).all() 