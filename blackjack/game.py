from blackjack.dealer import BlackJackDealer
from blackjack.deck import BlackJackDeck
from blackjack.seat import BlackJackSeat
from blackjack import utility as u
from models import get_scoped_session, Game, User


class BlackJackGame:

    def __init__(self, id, message_fn, sleep_fn, config):
        self.id = id
        self.config = config
        self.message_fn = message_fn
        self.sleep_fn = sleep_fn
        self.deck = BlackJackDeck(config)
        self.dealer = BlackJackDealer()
        self.seats = [BlackJackSeat(seat,config) for seat in range(1, self.config.SEAT_COUNT+1)]
        self.actions = ['repeat bet']
        self.bets = {}
        self.message_text = ''
        self.loop_running = False
        self.turn = 0
        self.message_time = 0


    ##--------------------------
    ## Game Loop
    ##--------------------------
    def bump(self):
        if not self.loop_running:
            self.game_loop()
    def game_loop(self):
        self.loop_running = True
        try:
            while self.player_count():
                self.clear()

                if self.deck.deck_needs_shuffle():
                    self.message_text = 'Shuffling Deck'
                    self.deck.shuffle_new_deck()
                    self.state_updated()
                    self.sleep()
                    self.message_text = ''
                    self.state_updated()

                self.wait_for_bets()

                self.sleep(1)

                if self.initial_deal():

                    self.wait_for_dealers_turn()

                    self.sleep(1)

                    self.dealers_turn()

                self.end_round()

                self.sleep(1)
        except Exception as err:
            raise err
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

        if self.dealer.should_check_for_blackjack():
            self.dealer.checking = True
            self.state_updated()
            self.sleep()
            self.dealer.checking = False
            self.state_updated()

        if self.dealer.is_blackjack:
            self.dealer.turned = True
            self.message_text = 'Dealer has a Blackjack!'
            self.state_updated()
            self.sleep()
            self.message_text = ''
            self.state_updated()
            return False


        for seat in self.seats:
            if seat.player and seat.is_blackjack:
                seat.player.add_funds(seat.bet * self.config.BLACKJACK_PAY)
                self.player_blackjack(seat.player)

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
            if not seat.player or not seat.cards or seat.is_blackjack:
                continue
            player = seat.player
            player_value = seat.hand_value
            if player_value > 21:
                result = 'bust'
            elif dealer_value > 21 or player_value > dealer_value:
                result = 'win'
                scoped_session = get_scoped_session()
                user = scoped_session.get(User, player.id)
                user.balance += abs(seat.bet * 2)
                scoped_session.commit()
            elif player_value == dealer_value:
                result = 'push'
                scoped_session = get_scoped_session()
                user = scoped_session.get(User, player.id)
                user.balance += abs(seat.bet)
                scoped_session.commit()
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
            self.state_updated()
        else:
            for seat in self.seats:
                if not seat.player:
                    seat.player = player
                    seat_id = seat.id
                    break

            if not seat_id:
                error = 'Seat not found'
            else:
                print('sending state')
                self.state_updated()

        return seat_id, error
    def remove_player(self, user_id):
        for seat in self.seats:
            if seat.player and seat.player.id == user_id:
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
            self.state_updated()
            if seat.hand_value > 21:
                self.player_bust(player)
                self.sleep()
                self.next_turn()
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
        if self.turn != 0:
            error = 'Not betting phase'
        elif not amount:
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
        turn = self.config.SEAT_COUNT + 1
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
        elif self.turn != 0 and self.turn != self.config.SEAT_COUNT + 1:
            possible_actions = actions

        return possible_actions


    ##--------------------------
    ## Waiting
    ##--------------------------
    def wait_for_bets(self):
        try:
            self.message_text = 'Place your bets'
            self.message_time = self.config.BET_TIME
            self.state_updated()
            for x in range(1, self.config.BET_TIME + 1):
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
        while self.turn != self.config.SEAT_COUNT + 1:
            self.sleep(1)


    ##--------------------------
    ## Messaging
    ##--------------------------
    def state_updated(self):
        session = get_scoped_session()
        game = session.get(Game, self.id)
        game.state = self.save()
        session.commit()
        self.message('game_state', self.state, self.id)
    def round_result(self, player, result):
        player.update()
        response = {
            'result': result,
            'balance': player.balance
        }
        self.message('round_result', response, player.sid)
    def player_bust(self, player):
        player.update()
        self.message('player_bust', 'You bust!', player.sid)
    def player_blackjack(self, player):
        player.update()
        response = {
            'message': 'You have a Blackjack!',
            'balance': player.balance
        }
        self.message('player_blackjack', response, player.sid)
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
                seconds = self.config.STANDARD_DELAY
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
            'chips': self.config.CHIPS,
            'message': self.message_text,
            'message_time': self.message_time,
            'shoe': self.deck.state
        }
    def save(self):
        return {
            'id': self.id,
            'turn': self.turn,
            'bets': self.bets,
            'actions': self.actions,
            'message': self.message_text,
            'message_time': self.message_time,
            'seats': [seat.save() for seat in self.seats],
            'dealer': self.dealer.save(),
            'deck': self.deck.save(),
            'config': self.config.save()
        }
    def load(self, save):
        if save.get('id'):
            self.id = save['id']
            self.turn = save.get('turn', 0)
            self.bets = save.get('bets', 0)
            self.actions = save.get('actions', [])
            self.message_text = save.get('message', '')
            self.message_time = save.get('message_time', 0)

            self.dealer.load(save.get('dealer', {}))
            self.deck.load(save.get('deck', {}))
            seats_save = save.get('seats', [])
            if seats_save:
                for index, seat in enumerate(self.seats):
                    for seat_save in seats_save:
                        if seat.id == seat_save.get('id'):
                            seat.load(seat_save)