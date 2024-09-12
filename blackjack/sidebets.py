



class BlackJackSideBet():
    def __init__(self):
        self.name = ''


class SideBetPairs(BlackJackSideBet):
    def __init__(self):
        super().__init__()
        self.name = 'Pairs'


class SideBetTwentyFour(BlackJackSideBet):
    def __init__(self):
        super().__init__()
        self.name = '21 + 3'