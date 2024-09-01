import random
import time
import uuid
import utility as u



class BlackjackPlayer:
    def __init__(self, name, session_id, balance):
        self.name = name
        self.id = str(uuid.uuid4())
        self.sid = session_id
        self.balance = balance
        self.game_id = None

    def can_bet(self, amount):
        return self.balance >= amount

    def add_funds(self, amount):
        self.balance += amount

    def remove_funds(self, amount):
        self.balance -= amount

    @property
    def state(self):
        return {
            'name': self.name,
            'id': self.id,
            'balance': self.balance,
        }

class BlackJackSeat:

    def __init__(self, seat_id):
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
    def state(self):
        return {
            'id': self.id,
            'player': self.player.state if self.player is not None else None,
            'bet': self.bet,
            'cards': self.cards
        }

class BlackJackDeck:
    def __init__(self, deck_count=4):
        self.deck_count = deck_count
        self.cards = self.create_deck()
        self.shuffle()

    def check_deck(self):
        if self.deck_needs_shuffle():
            self.shuffle()

    def deck_needs_shuffle(self):
        return len(self.cards) < (self.deck_count * u.deck_size)

    def shuffle(self):
        random.shuffle(self.cards)

    def deal_card(self):
        return self.cards.pop()

    def card_count(self):
        return len(self.cards)

    def create_deck(self):
        return [f'{suit}{rank}' for suit in u.suits for rank in u.ranks] * self.deck_count

class BlackJackDealer:
    DOWN_CARD = 'B2'

    def __init__(self):
        self.up_card = None
        self.down_card = None
        self.turned = False
        self.cards = []

    def clear(self):
        self.up_card = None
        self.down_card = None
        self.turned = False
        self.cards = []

    def initial_deal(self, up_card, down_card):
        self.up_card = up_card
        self.down_card = down_card
        self.cards = [self.up_card, self.down_card]

    @property
    def hand_value(self):
        return u.hand_value(self.cards)

    @property
    def state(self):
        return {
            'up_card': self.up_card,
            'down_card': self.down_card if self.turned or self.down_card == None else self.DOWN_CARD,
            'cards': self.cards
        }

class BlackJackGame:
    BET_TIME = 5

    def __init__(self, game_id, message_fn, sleep_fn, seat_count=6):
        self.id = game_id
        self.seat_count = seat_count
        self.message_fn = message_fn
        self.sleep_fn = sleep_fn
        self.deck = BlackJackDeck()
        self.dealer = BlackJackDealer()
        self.seats = [BlackJackSeat(seat) for seat in range(1, seat_count+1)]
        self.actions = []
        self.loop_running = False
        self.turn = 0


    ##--------------------------
    ## Game Loop
    ##--------------------------
    def bump(self):
        print('bumping game')
        if not self.loop_running:
            self.game_loop()
    def game_loop(self):
        print('game loop started')
        self.loop_running = True
        while self.player_count():
            self.deck.check_deck()
            print('1')
            self.clear()
            print('2')

            self.wait_for_bets()
            print('3')

            self.initial_deal()
            print('4')

            self.wait_for_dealers_turn()
            print('5')

            self.sleep(2)
            print('6')

            self.dealers_turn()
            print('7')

            self.end_round()
            print('8')


        self.loop_running = False
        print('Game Loop Stopped')


    ##--------------------------
    ## Flow
    ##--------------------------
    def clear(self):
        self.turn = 0
        for seat in self.seats:
            seat.clear()
        self.dealer.clear()
        self.state_updated()
    def initial_deal(self):
        self.dealer.initial_deal(self.deck.deal_card(), self.deck.deal_card())
        self.state_updated()
        self.sleep(1)
        for seat in self.seats:
            if seat.player and seat.bet:
                seat.cards = [self.deck.deal_card(), self.deck.deal_card()]
                self.state_updated()
                self.sleep(1)
        self.next_turn()
        self.state_updated()
    def dealers_turn(self):
        self.dealer.turned = True
        self.state_updated()
        self.sleep(1)
        while self.dealer.hand_value < 17:
            self.dealer.cards.append(self.deck.deal_card())
            self.sleep(1)
            self.state_updated()
    def end_round(self):
        dealer_value = self.dealer.hand_value
        for seat in self.seats:
            if not seat.player:
                continue
            player_value = seat.hand_value
            if player_value > 21:
                result = 'bust'
            elif dealer_value > 21 or player_value > dealer_value:
                result = 'win'
                seat.player.balance += seat.bet * 2
            elif player_value == dealer_value:
                result = 'push'
                seat.player.balance += seat.bet
            else:
                result = 'lose'
            self.round_result(seat.player, result)
    def next_turn(self):
        self.turn = self.get_next_turn()
        self.actions = self.get_actions()


    ##--------------------------
    ## Flow - Methods
    ##--------------------------
    def add_player(self, player, role):
        print('adding player')
        seat_id = None
        error = ''
        for seat in self.seats:
            if not seat.player:
                seat.player = player
                seat.player.game_id = self.id
                seat_id = seat.id
                break
        if not seat_id:
            error = 'Seat not found'

        if seat_id:
            self.state_updated()

        return seat_id, error
    def remove_player(self, player):
        seat = self.find_seat_by_player(player)
        seat.player = None
        self.state_updated()
    def player_action(self, player, action):
        success = False
        error = ''

        seat = self.find_seat_by_player(player)
        if not seat:
            error = 'Unable to find seat'
            return success, error

        if seat.id != self.turn:
            error = 'Not players turn'
            return success, error

        if action not in self.actions:
            error = 'Invalid action'
            return success, error

        if action == 'hit':
            seat.cards.append(self.deck.deal_card())
            if seat.hand_value > 21:
                self.next_turn()
                self.player_bust(player)
            success = True

        elif action == 'stand':
            self.next_turn()
            success = True

        elif action == 'double':
            if not player.can_bet(seat.bet):
                error = 'Not enough money to double'
            else:
                player.remove_funds(seat.bet)
                seat.bet *= 2
                seat.cards.append(self.deck.deal_card())
                self.next_turn()
                if seat.hand_value > 21:
                    self.player_bust(player)
                success = True

        elif action == 'split':
            # Split logic here
            pass
        else:
            return 'Invalid action'

        if success:
            self.state_updated()

        return success, error
    def player_bet(self, player, amount):
        success = False
        error = ''
        amount = u.get_int(amount)
        seat = self.find_seat_by_player(player)
        if not amount:
            error = 'No bet given'
        elif seat:
            if player.can_bet(amount):
                seat.bet += amount
                player.remove_funds(amount)
                success = True
            else:
                error = 'Not enough money'
        else:
            error = 'Player not in game'

        if success:
            self.state_updated()

        return success, error


    ##--------------------------
    ## Methods
    ##--------------------------
    def player_count(self):
        print('count')
        return sum([1 if seat.player else 0 for seat in self.seats])
    def get_next_turn(self):
        turn = self.seat_count + 1
        for seat in self.seats:
            if seat.player and seat.bet and seat.id > self.turn:
                turn = seat.id
                break
        return turn
    def is_game_full(self):
        return all(seat.player is not None for seat in self.seats)
    def find_seat_by_player(self, player):
        for seat in self.seats:
            if seat.player and seat.player.id == player.id:
                return seat
    def get_actions(self):
        possible_actions = []
        actions = ['hit', 'stand', 'double']
        if self.turn != 0 and self.turn != self.seat_count + 1:
            possible_actions = actions
        return possible_actions


    ##--------------------------
    ## Waiting
    ##--------------------------
    def wait_for_bets(self):
        for x in range(1, self.BET_TIME + 1):
            if sum([1 if seat.bet else 0 for seat in self.seats]) == self.player_count():
                return
            print('bets waiting', self.id)
            self.sleep(1)
        while sum([1 if seat.bet else 0 for seat in self.seats]) == 0:
            print('bets waiting', self.id)
            self.sleep(1)
    def wait_for_dealers_turn(self):
        print('dealer turn', self.turn)
        print('dealer seat_count', self.seat_count)
        while self.turn != self.seat_count + 1:
            print('dealer waiting', self.id)
            self.sleep(1)


    ##--------------------------
    ## Messaging
    ##--------------------------
    def state_updated(self):
        print(f'Sending game_state with ID: {self.id}')
        print(f'State: {self.state}')
        self.message('game_state', self.state, self.id)
    def round_result(self, player, result):
        self.message('round_result', result, player.sid)
    def player_bust(self, player):
        self.message('player_bust', player.state, player.sid)


    def message(self, key, data, to):
        if self.message_fn:
            self.message_fn(key, data, to)


    def sleep(self, seconds):
        if self.sleep_fn:
            self.sleep_fn(seconds)

    @property
    def state(self):
        return {
            'seats': [seat.state for seat in self.seats],
            'dealer': self.dealer.state,
            'turn': self.turn,
            'actions': self.actions,
            'chips': [1,5,25,50,100,500]
        }

class BlackJackGameManager:
    def __init__(self):
        self.games = {}
        self.players = {}

    def create_game(self, game_id, message_fn, sleep_fn):
        game = BlackJackGame(game_id, message_fn, sleep_fn)
        self.games[game_id] = game
        return game

    def get_game(self, game_id):
        return self.games.get(game_id)

    def get_session(self, session_id):
        player = self.get_player(session_id)
        game = self.get_game(player.game_id)
        return player, game

    def remove_game(self, game_id):
        if game_id in self.games:
            del self.games[game_id]

    def register_player(self, session_id):
        player = BlackjackPlayer('player', session_id, 5000)
        self.players[session_id] = player
        return player

    def get_player(self, session_id):
        player = self.players.get(session_id)
        if not player:
            player = self.register_player(session_id)
        return player

