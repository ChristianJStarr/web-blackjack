from blackjack import utility as u
from blackjack.player import BlackjackPlayer


class BlackJackSeat:

    def __init__(self, seat_id, config):
        self.id = seat_id
        self.reset()

    def reset(self):
        self.player = None
        self.clear()

    def clear(self):
        self.bet = 0
        self.cards = []

    @property
    def hand_value(self):
        return u.hand_value(self.cards)

    @property
    def is_blackjack(self):
        return self.hand_value == 21 and len(self.cards) == 2

    @property
    def state(self):
        return {
            'id': self.id,
            'player': self.player.state if self.player is not None else None,
            'bet': self.bet,
            'cards': self.cards,
            'hand_value': self.hand_value
        }

    def save(self):
        return {
            'id': self.id,
            'player': self.player.id if self.player is not None else None,
            'bet': self.bet,
            'cards': self.cards
        }
    def load(self, save):
        self.bet = save.get('bet', 0)
        self.cards = save.get('cards', [])
        player_id = save.get('player', None)
        if player_id:
            self.player = BlackjackPlayer(player_id)
            self.player.update()



