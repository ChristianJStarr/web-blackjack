import socketio
import random
import string
import threading

class BlackJackBot:

    def __init__(self, game_ip, game_id):
        self.seat_id = 0
        self.player_id = 0
        self.bet = 0
        self.balance = 5000
        self.role = 'player'
        self.game_id = game_id
        self.game_ip = game_ip


    ##--------------------------------------
    ## Runtime
    ##--------------------------------------
    def start(self):
        self.thread = threading.Thread(target=self.bot_thread)
        self.thread.start()

    def bot_thread(self):
        self.socket = socketio.Client()

        self.socket.on('connect', self.on_connect)
        self.socket.on('disconnect', self.on_disconnect)
        self.socket.on('update_game_state', self.on_update_game_state)
        self.socket.on('betting_phase', self.on_betting_phase)
        self.socket.on('round_result', self.on_round_result)
        self.socket.on('player_assigned', self.on_player_assigned)
        self.socket.on('spectator_assigned', self.on_spectator_assigned)
        self.socket.on('player_bust', self.on_player_bust)
        self.socket.on('player_bet', self.on_player_bet)

        self.socket.connect(self.game_ip)
        self.socket.wait()


    ##--------------------------------------
    ## Methods
    ##--------------------------------------
    def update_state(self, state):
        self.state = state
        self.betting_phase = state['betting_phase']
        if self.can_place_bet():
            self.place_bet()

        if self.is_turn():
            self.take_turn()

    def join_game(self):
        self.socket.emit('join_game', {
            'game_id': self.game_id,
            'role': self.role,
        })

    def can_place_bet(self):
        return self.betting_phase and self.state.get('seats')[self.seat_id-1].get('bet') == 0

    def get_bet(self):
        min_amount = self.balance
        if min_amount >= 100:
            return random.randint(1, self.balance / 100) * 100
        return 250

    def place_bet(self):
        if not self.bet:
            self.bet = self.get_bet()
            self.socket.emit('player_bet', {
                'game_id': self.game_id,
                'player_id': self.player_id,
                'amount': self.bet
            })

    def is_turn(self):
        is_player_turn = self.seat_id == self.state.get('turn')
        return is_player_turn

    def take_turn(self):
        random_action = random.choice(['hit', 'stand'])
        self.socket.emit('player_action', {
            'game_id': self.game_id,
            'player_id': self.player_id,
            'action': random_action
        })


    ##--------------------------------------
    ## Events
    ##--------------------------------------
    def on_update_game_state(self, data):
        self.update_state(data)

    def on_player_assigned(self, data):
        self.player_id = data['player_id']
        self.seat_id = data['seat_id']
        self.balance = data['balance']

    def on_spectator_assigned(self, data):
        pass

    def on_connect(self):
        if not self.player_id:
            self.join_game()

    def on_disconnect(self):
        if self.socket:
            self.socket.disconnect()

    def on_player_bet(self, data):
        self.balance = data['balance']
        self.bet = data['amount']

    def on_round_result(self, data):
        self.balance = data['balance']

    def on_betting_phase(self, data):
        self.betting_phase = data['betting_phase']
        self.bet = 0
        if self.can_place_bet():
            self.place_bet()
        if self.balance <= 200:
            self.socket.disconnect()
    def on_player_bust(self, data):
        pass

    def state_change(self, game_state):
        self.state = game_state

        if self.is_turn():
            self.take_turn()

        if self.can_bet():
            self.place_bet()

        self.bet = self.state.get('seats')[self.seat_id-1].get('bet')

class BlackJackBotManager:

    def __init__(self, game_ip):
        self.game_ip = game_ip
        self.bots = []


    def start(self):

        for bot in self.bots:
            bot.start()

        for bot in self.bots:
            bot.thread.join()

    def create_bots(self, count):
        game_ids = [''.join(random.choices(string.ascii_letters + string.digits, k=4)) for x in range(int((count / 4) + 1))]
        for x in range(1, count):
            game_id = random.choice(game_ids)
            bot = BlackJackBot(self.game_ip, game_id)
            self.bots.append(bot)



if __name__ == '__main__':
    NUM_BOTS = 200
    SERVER_URL = 'http://localhost:5000'

    bot_manager = BlackJackBotManager(SERVER_URL)
    bot_manager.create_bots(NUM_BOTS)
    bot_manager.start()





