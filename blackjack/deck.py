import random
from blackjack import utility as u

class BlackJackDeck:
    def __init__(self, config):
        self.deck_count = config.DECK_COUNT
        self.deck_cut = config.DECK_CUT
        self.cards = self.create_deck()
        self.shuffle()

    def shuffle_new_deck(self):
        if self.deck_needs_shuffle():
            self.cards = self.create_deck()
            self.shuffle()

    def deck_needs_shuffle(self):
        return len(self.cards) <= self.deck_cut

    def shuffle(self):
        random.shuffle(self.cards)

    def deal_card(self):
        return self.cards.pop()

    def card_count(self):
        return len(self.cards)

    def create_deck(self):
        return [f'{suit}{rank}' for suit in u.suits for rank in u.ranks] * self.deck_count

    @property
    def state(self):
        return {
            'cards': ['X' for x in self.cards],
            'card_count': self.card_count(),
            'deck_cut': self.deck_cut,
            'deck_needs_shuffle': self.deck_needs_shuffle(),
        }

    def save(self):
        return {
            'cards': self.cards
        }
    def load(self, save):
        if save.get('deck'):
            save = save.get('deck')
        self.cards = save.get('cards')
