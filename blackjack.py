import random
from flask import current_app
from flask_socketio import join_room, leave_room
import utility as u
from models import BlackjackPlayer, get_scoped_session

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
    def is_blackjack(self):
        return self.hand_value == 21 and len(self.cards) == 2
    @property
    def player(self):
        session = get_scoped_session()
        player = None
        try:
            if self.player_id:
                player = session.query(BlackjackPlayer).get(self.player_id)
        except Exception as e:
            session.rollback()
            print(f"Error getting player: {e}")
        finally:
            return player
    @player.setter
    def player(self, player):
        if player:
            self.player_id = player.id
        else:
            self.player_id = None




    @property
    def state(self):
        return {
            'id': self.id,
            'player': self.player.state if self.player is not None else None,
            'bet': self.bet,
            'cards': self.cards,
            'hand_value': self.hand_value
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

    @property
    def state(self):
        return {
            'cards': ['X' for x in self.cards],
            'card_count': self.card_count(),
            'deck_needs_shuffle': self.deck_needs_shuffle(),
        }



class BlackJackDealer:
    DOWN_CARD = 'B2'

    def __init__(self):
        self.up_card = None
        self.down_card = None
        self.turned = False
        self.cards = []
        self.history = []

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
    def is_blackjack(self):
        return self.hand_value == 21 and len(self.cards) == 2
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
            'hand_value': u.hand_value(cards),
            'history': self.history
        }

class BlackJackGame:
    BET_TIME = 5
    STANDARD_DELAY = 1
    BLACKJACK_PAY = 2.5

    def __init__(self, game_id, app, message_fn, sleep_fn, seat_count=6):
        self.id = game_id
        self.seat_count = seat_count
        self.message_fn = message_fn
        self.sleep_fn = sleep_fn
        self.app = app
        self.deck = BlackJackDeck()
        self.dealer = BlackJackDealer()
        self.seats = [BlackJackSeat(seat) for seat in range(1, seat_count+1)]
        self.actions = ['repeat bet']
        self.chips = [1,5,25,50,100,500]
        self.bets = {}
        self.message_text = ''
        self.loop_running = False
        self.turn = 0
        self.message_time = 0
        self.db_session = None


    ##--------------------------
    ## Game Loop
    ##--------------------------
    def bump(self):
        with self.app.app_context():
            if not self.loop_running:
                self.game_loop()
    def game_loop(self):
        self.loop_running = True
        self.db_session = get_scoped_session()
        try:
            while self.player_count():
                self.deck.check_deck()
                self.clear()

                self.wait_for_bets()

                self.sleep(1)

                if self.initial_deal():

                    self.wait_for_dealers_turn()

                    self.sleep(1)

                    self.dealers_turn()

                self.end_round()
                self.sleep(1)
        except Exception as err:
            print(f'Error occurred in game loop. Error: {err}')
        finally:
            self.loop_running = False


    ##--------------------------
    ## Flow
    ##--------------------------
    def clear(self):
        self.turn = 0
        self.message_text = ''
        for seat in self.seats:
            seat.clear()
        self.dealer.clear()
        self.state_updated()
    def initial_deal(self):
        self.dealer.initial_deal(self.deck.deal_card(), self.deck.deal_card())
        self.state_updated()

        for seat in self.seats:
            if seat.player and seat.bet:
                seat.cards = [self.deck.deal_card(), self.deck.deal_card()]
                self.state_updated()
                self.sleep()

        if self.dealer.is_blackjack:
            self.dealer_message('Dealer has a Blackjack!')
            return False

        for seat in self.seats:
            if seat.player and seat.is_blackjack:
                self.player_message(seat.player, 'You have a Blackjack!')
                seat.player.add_funds(seat.bet * self.BLACKJACK_PAY)

        self.next_turn()
        self.state_updated()

        self.bets = {seat.player.id: seat.bet for seat in self.seats if seat.player is not None}

        return True

    def dealers_turn(self):
        self.dealer.turned = True
        self.state_updated()
        self.sleep(1)
        while self.dealer.hand_value < 17:
            self.dealer.cards.append(self.deck.deal_card())
            if self.dealer.hand_value > 21:
                self.dealer_message('Dealer bust')
            self.state_updated()
            self.sleep(1)
    def end_round(self):
        dealer_value = self.dealer.hand_value
        if self.dealer.is_blackjack:
            self.dealer.history.append('BJ')
        elif dealer_value > 21:
            self.dealer.history.append('B')
        else:
            self.dealer.history.append(dealer_value)

        for seat in self.seats:
            if not seat.player or not seat.cards:
                continue
            player = seat.player

            player = self.db_session.query(BlackjackPlayer).get(player.id)
            player_value = seat.hand_value
            if player_value > 21:
                result = 'bust'
            elif dealer_value > 21 or player_value > dealer_value:
                result = 'win'
                player.add_funds(seat.bet * 2)
            elif player_value == dealer_value:
                result = 'push'
                player.add_funds(seat.bet)
            else:
                result = 'lose'
            self.round_result(player, result)
    def next_turn(self):
        self.turn = self.get_next_turn()
        self.actions = self.get_actions()


    ##--------------------------
    ## Flow - Methods
    ##--------------------------
    def add_player(self, player):
        seat_id = 0
        error = None
        seat = self.find_seat_by_player(player)

        if seat:
            seat_id = seat.id
        else:
            for seat in self.seats:
                if not seat.player:
                    seat.player = player
                    seat_id = seat.id
                    break
            if not seat_id:
                error = 'Seat not found'
            else:
                self.state_updated()

        return seat_id, error
    def remove_player(self, player):
        seat = self.find_seat_by_player(player)
        if seat:
            seat.player = None
            self.state_updated()
    def player_action(self, player, action):
        success = False
        error = ''

        seat = self.find_seat_by_player(player)
        if not seat:
            error = 'Unable to find seat'
            return success, error

        if seat.id != self.turn and action != 'repeat bet':
            error = 'Not players turn'
            return success, error
        if action not in self.get_actions():
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

        elif action == 'repeat bet':
            prev_bet = self.bets.get(player.id)
            if prev_bet:
                self.player_bet(player, prev_bet)

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
        return sum([1 if seat.player else 0 for seat in self.seats])
    def get_next_turn(self):
        turn = self.seat_count + 1
        for seat in self.seats:
            if seat.player and seat.bet and seat.id > self.turn and seat.hand_value < 21:
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
        if self.turn == 0:
            possible_actions = ['repeat bet']
        elif self.turn != 0 and self.turn != self.seat_count + 1:
            possible_actions = actions

        return possible_actions


    ##--------------------------
    ## Waiting
    ##--------------------------
    def wait_for_bets(self):
        try:
            self.message_text = 'Place your bets'
            self.message_time = self.BET_TIME
            self.state_updated()
            for x in range(1, self.BET_TIME + 1):
                if sum([1 if seat.bet else 0 for seat in self.seats]) == self.player_count():
                    return
                self.sleep(1)
            while sum([1 if seat.bet else 0 for seat in self.seats]) == 0:
                self.sleep()
        finally:
            self.message_text = 'Bets closed'
            self.message_time = 0
            self.state_updated()
            self.sleep()
            self.message_text = ''

    def wait_for_dealers_turn(self):
        while self.turn != self.seat_count + 1:
            self.sleep(1)


    ##--------------------------
    ## Messaging
    ##--------------------------
    def state_updated(self):
        self.message('game_state', self.state, self.id)
    def round_result(self, player, result):
        player = self.db_session.query(BlackjackPlayer).get(player.id)
        response = {
            'result': result,
            'balance': player.balance
        }
        self.message('round_result', response, player.sid)
    def player_bust(self, player):
        self.message('player_bust', 'You bust!', player.sid)
    def dealer_message(self, message):
        self.message_text = message
    def player_message(self, player, message):
        self.message('message', message, player.sid)
    def message(self, key, data, to):
        if self.message_fn:
            self.message_fn(key, data, to)
    def sleep(self, seconds=0):
        if self.sleep_fn:
            if not seconds:
                seconds = self.STANDARD_DELAY
            self.sleep_fn(seconds)

    ##--------------------------
    ## State
    ##--------------------------
    @property
    def state(self):
        return {
            'id': self.id,
            'seats': [seat.state for seat in self.seats],
            'dealer': self.dealer.state,
            'turn': self.turn,
            'actions': self.get_actions(),
            'chips': self.chips,
            'message': self.message_text,
            'message_time': self.message_time,
            'shoe': self.deck.state
        }

class BlackJackGameManager:
    def __init__(self, app, socketio):
        self.app = app
        self.socketio = socketio
        self.games = {}

    def bump_game(self, game):
        with self.app.app_context():
            self.socketio.start_background_task(game.bump)

    def join_game(self, game, player):
        join_room(game.id)
        seat_id, error = game.add_player(player)
        if not seat_id:
            self.message('error', {'message': error}, player.sid)
        else:
            self.bump_game(game)
            response = {
                'success': True,
                'seat_id': seat_id,
                'player': player.state,
                'game_state': game.state,
                'balance': player.balance,
            }
            self.message('player_assigned', response, player.sid)

    def leave_game(self, game, player):
        leave_room(game.id)
        game.remove_player(player)

    def player_action(self, game, player, action):
        success, error = game.player_action(player, action)

        if not success:
            self.message('error', {'message': error}, player.sid)
        else:
            self.message('player_action', {'success': True}, player.sid)

    def player_bet(self, game, player, bet):
        success, error = game.player_bet(player, bet)

        if not success:
            self.message('error', {'message': error}, player.sid)
        else:
            response = {
                'success': True,
                'balance': player.balance
            }
            self.message('player_bet', response, player.sid)

    def get_or_create_game(self, game_id):
        game = self.get_game(game_id)
        if not game:
            game = BlackJackGame(game_id, self.app, self.message, self.sleep)
            self.games[game_id] = game
        return game

    def get_game(self, game_id):
        return self.games.get(game_id)

    def sleep(self, seconds):
        self.socketio.sleep(seconds)

    def message(self, key, data, to=None):
        if to:
            self.socketio.emit(key, data, to=to)
        else:
            self.socketio.emit(key, data)
