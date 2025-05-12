from blackjack.game.utility import calculate_hand_value
from blackjack.exceptions import InvalidActionError
import random

class BlackjackGame:
    """Core game logic independent of any web framework"""
    
    def __init__(self, game_id, config=None):
        self.game_id = game_id
        self.config = config or BlackjackConfig()
        self.deck = self._create_deck(self.config.deck_count)
        self.dealer_hand = []
        self.players = {}  # player_id -> player data
        self.seats = {}    # seat_id -> player_id
        self.state = "waiting"  # waiting, betting, playing, evaluating
        self.turn = None
        self.history = []
        
    def _create_deck(self, deck_count=1):
        """Create a shuffled deck of cards"""
        suits = ['hearts', 'diamonds', 'clubs', 'spades']
        ranks = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
        
        deck = []
        for _ in range(deck_count):
            for suit in suits:
                for rank in ranks:
                    deck.append({'suit': suit, 'rank': rank})
        
        random.shuffle(deck)
        return deck
    
    def add_player(self, player_id, seat_id):
        """Add a player to the game"""
        # Check if seat is available
        if seat_id in self.seats:
            return None, "Seat already taken"
        
        # Add player to game
        self.players[player_id] = {
            'id': player_id,
            'hand': [],
            'bet': 0,
            'status': 'waiting',
            'balance': 10000  # Default balance, should be loaded from database
        }
        
        # Assign seat
        self.seats[seat_id] = player_id
        
        return seat_id, None
        
    def remove_player(self, player_id):
        """Remove a player from the game"""
        # Find seat to remove
        seat_to_remove = None
        for seat, pid in self.seats.items():
            if pid == player_id:
                seat_to_remove = seat
                break
        
        # Remove player from seat
        if seat_to_remove:
            del self.seats[seat_to_remove]
        
        # Remove player data
        if player_id in self.players:
            del self.players[player_id]
            
        return True
        
    def place_bet(self, player_id, amount):
        """Process a player's bet"""
        if self.state != "betting":
            return False, "Betting is not allowed at this time"
            
        if player_id not in self.players:
            return False, "Player not in game"
            
        player = self.players[player_id]
        
        # Validate bet amount
        if amount <= 0:
            return False, "Bet must be greater than zero"
            
        if amount > player['balance']:
            return False, "Insufficient balance"
        
        # Place bet
        player['bet'] = amount
        player['balance'] -= amount
        player['status'] = 'betting'
        
        # Check if all players have bet
        all_bet = all(p['status'] == 'betting' for p in self.players.values())
        if all_bet and self.players:
            self._start_round()
        
        return True, None
        
    def player_action(self, player_id, action):
        """Process a player's action (hit, stand, etc.)"""
        if self.state != "playing":
            return False, "Game is not in play"
            
        if player_id not in self.players:
            return False, "Player not in game"
            
        if self.turn is None or self.seats.get(self.turn) != player_id:
            return False, "Not your turn"
            
        player = self.players[player_id]
        
        # Process action
        if action == "hit":
            return self._hit(player)
        elif action == "stand":
            return self._stand(player)
        else:
            return False, f"Invalid action: {action}"
    
    def _hit(self, player):
        """Hit action - draw a card"""
        if not self.deck:
            self.deck = self._create_deck(self.config.deck_count)
            
        card = self.deck.pop()
        player['hand'].append(card)
        
        # Check for bust
        value = calculate_hand_value(player['hand'])
        if value > 21:
            player['status'] = 'bust'
            self._next_turn()
            
        return True, None
        
    def _stand(self, player):
        """Stand action - end turn"""
        player['status'] = 'stand'
        self._next_turn()
        return True, None
        
    def _next_turn(self):
        """Move to the next player's turn or dealer's turn"""
        if self.turn is None:
            # Find first seat
            seats = sorted(self.seats.keys())
            self.turn = seats[0] if seats else None
            return
            
        seats = sorted(self.seats.keys())
        current_index = seats.index(self.turn)
        
        # Try to find next seat
        next_index = current_index + 1
        if next_index < len(seats):
            self.turn = seats[next_index]
        else:
            # Dealer's turn
            self._dealer_turn()
            
    def _dealer_turn(self):
        """Execute dealer's turn"""
        # Dealer draws until 17 or higher
        while calculate_hand_value(self.dealer_hand) < 17:
            if not self.deck:
                self.deck = self._create_deck(self.config.deck_count)
                
            self.dealer_hand.append(self.deck.pop())
            
        # Evaluate round
        self._evaluate_round()
        
    def _start_round(self):
        """Start a new round"""
        # Reset deck if needed
        if len(self.deck) < (len(self.players) * 4 + 2):
            self.deck = self._create_deck(self.config.deck_count)
            
        # Deal cards
        self.dealer_hand = [self.deck.pop(), self.deck.pop()]
        
        for player in self.players.values():
            player['hand'] = [self.deck.pop(), self.deck.pop()]
            player['status'] = 'playing'
            
        # Set game state
        self.state = "playing"
        self._next_turn()
        
    def _evaluate_round(self):
        """Evaluate the round results"""
        dealer_value = calculate_hand_value(self.dealer_hand)
        dealer_bust = dealer_value > 21
        
        # Process each player
        for player in self.players.values():
            if player['status'] == 'bust':
                # Player loses
                player['status'] = 'lose'
                continue
                
            player_value = calculate_hand_value(player['hand'])
            
            if dealer_bust:
                # Dealer bust, player wins
                player['status'] = 'win'
                player['balance'] += player['bet'] * 2
            elif player_value > dealer_value:
                # Player wins
                player['status'] = 'win'
                player['balance'] += player['bet'] * 2
            elif player_value == dealer_value:
                # Push
                player['status'] = 'push'
                player['balance'] += player['bet']
            else:
                # Player loses
                player['status'] = 'lose'
                
        # Add round to history
        self.history.append({
            'dealer': self.dealer_hand,
            'players': {pid: p['hand'] for pid, p in self.players.items()},
            'results': {pid: p['status'] for pid, p in self.players.items()}
        })
        
        # Reset for next round
        self.dealer_hand = []
        for player in self.players.values():
            player['hand'] = []
            player['bet'] = 0
            
        self.state = "betting"
        self.turn = None
        
    def to_dict(self):
        """Convert game state to dictionary for serialization"""
        return {
            'id': self.game_id,
            'state': self.state,
            'turn': self.turn,
            'dealer': self.dealer_hand,
            'players': self.players,
            'seats': self.seats,
            'history': self.history
        }
        
    @classmethod
    def from_dict(cls, data):
        """Create game from serialized state"""
        game = cls(data['id'])
        game.state = data['state']
        game.turn = data['turn']
        game.dealer_hand = data['dealer']
        game.players = data['players']
        game.seats = data['seats']
        game.history = data['history']
        return game


class BlackjackConfig:
    """Configuration for blackjack game"""
    def __init__(self):
        self.deck_count = 6
        self.min_bet = 100
        self.max_bet = 1000
        self.max_players = 6
        
    def load(self, config):
        """Load configuration from dictionary"""
        if not config:
            return
            
        self.deck_count = config.get('deck_count', self.deck_count)
        self.min_bet = config.get('min_bet', self.min_bet)
        self.max_bet = config.get('max_bet', self.max_bet)
        self.max_players = config.get('max_players', self.max_players) 