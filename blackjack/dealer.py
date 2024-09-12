from blackjack import utility as u


class BlackJackDealer:
    DOWN_CARD = 'B2'

    def __init__(self):
        self.up_card = None
        self.down_card = None
        self.turned = False
        self.checking = False
        self.cards = []
        self.history = []

    def clear(self):
        self.up_card = None
        self.down_card = None
        self.turned = False
        self.checking = False
        self.cards = []

    def initial_deal(self, up_card, down_card):
        self.up_card = up_card
        self.down_card = down_card
        self.cards = [self.up_card, self.down_card]

    @property
    def hand_value(self):
        return u.hand_value(self.cards)

    @property
    def is_blackjack(self):
        return self.hand_value == 21 and len(self.cards) == 2

    def should_check_for_blackjack(self):
        up_value = u.hand_value([self.up_card])
        if up_value == 11 or up_value == 10:
            return True

    @property
    def state(self):
        down_card = self.down_card if self.turned or self.down_card == None else self.DOWN_CARD
        if self.cards:
            cards = [self.up_card, down_card] + self.cards[2:]
        else:
            cards = self.cards
        return {
            'up_card': self.up_card,
            'down_card': down_card,
            'cards': cards,
            'checking': self.checking,
            'hand_value': u.hand_value(cards),
            'history': self.history[:28]
        }

    def save(self):
        return {
            'up_card': self.up_card,
            'down_card': self.down_card,
            'cards': self.cards,
            'checking': self.checking,
            'turned': self.turned,
            'history': self.history
        }
    def load(self, save):
        if save.get('dealer'):
            save = save.get('dealer')
        self.up_card = save['up_card']
        self.down_card = save['down_card']
        self.cards = save['cards']
        self.checking = save['checking']
        self.turned = save['turned']
        self.history = save['history']



