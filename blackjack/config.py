from blackjack.sidebets import SideBetPairs, SideBetTwentyFour


class BlackJackConfig:
    def __init__(self):
        self.BET_TIME = 10
        self.STANDARD_DELAY = 1
        self.SEAT_COUNT = 6
        self.BLACKJACK_PAY = 2.5
        self.DECK_COUNT = 4
        self.DECK_CUT = 112
        self.SIDE_BET_L = SideBetPairs
        self.SIDE_BET_R = SideBetTwentyFour
        self.CHIPS = [1,5,25,50,100,500]

    @property
    def state(self):
        return {
            'bet_time': self.BET_TIME,
            'standard_delay': self.STANDARD_DELAY,
            'seat_count': self.SEAT_COUNT,
            'blackjack_pay': self.BLACKJACK_PAY,
            'deck_count': self.DECK_COUNT,
            'deck_cut': self.DECK_CUT,
            'side_bet_l': self.SIDE_BET_L,
            'side_bet_r': self.SIDE_BET_R,
            'chips': self.CHIPS
        }

    def load(self, state):
        self.BET_TIME = state.get('bet_time', self.BET_TIME)
        self.STANDARD_DELAY = state.get('standard_delay', self.STANDARD_DELAY)
        self.SEAT_COUNT = state.get('seat_count', self.SEAT_COUNT)
        self.BLACKJACK_PAY = state.get('blackjack_pay', self.BLACKJACK_PAY)
        self.DECK_COUNT = state.get('deck_count', self.DECK_COUNT)
        self.DECK_CUT = state.get('deck_cut', self.DECK_CUT)
        self.CHIPS = state.get('chips', self.CHIPS)
        self.SIDE_BET_L = state.get('side_bet_l', self.SIDE_BET_L)
        self.SIDE_BET_R = state.get('side_bet_r', self.SIDE_BET_R)

        if self.SIDE_BET_L == 'SideBetTwentyFour':
            self.SIDE_BET_L = SideBetTwentyFour
        elif self.SIDE_BET_L == 'SideBetPairs':
            self.SIDE_BET_L = SideBetPairs

        if self.SIDE_BET_R == 'SideBetTwentyFour':
            self.SIDE_BET_R = SideBetTwentyFour
        elif self.SIDE_BET_R == 'SideBetPairs':
            self.SIDE_BET_R = SideBetPairs


    def save(self):
        return {
            'bet_time': self.BET_TIME,
            'standard_delay': self.STANDARD_DELAY,
            'seat_count': self.SEAT_COUNT,
            'blackjack_pay': self.BLACKJACK_PAY,
            'deck_count': self.DECK_COUNT,
            'deck_cut': self.DECK_CUT,
            'side_bet_l': self.SIDE_BET_L.__name__,
            'side_bet_r': self.SIDE_BET_R.__name__,
            'chips': self.CHIPS
        }