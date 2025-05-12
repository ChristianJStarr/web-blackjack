import random
import string
import re

def generate_id(length=4):
    """Generate a random alphanumeric ID"""
    chars = string.ascii_letters + string.digits
    return ''.join(random.choice(chars) for _ in range(length))

def valid_game_id(game_id):
    """Validate game ID format"""
    if not game_id:
        return False
    # Check that game_id is alphanumeric and has correct length
    return bool(re.match(r'^[a-zA-Z0-9]{4}$', game_id))

def calculate_hand_value(hand):
    """Calculate the value of a blackjack hand"""
    value = 0
    aces = 0
    
    for card in hand:
        if card['rank'] in ['J', 'Q', 'K']:
            value += 10
        elif card['rank'] == 'A':
            aces += 1
            value += 11
        else:
            value += int(card['rank'])
    
    # Adjust for aces
    while value > 21 and aces > 0:
        value -= 10
        aces -= 1
        
    return value 