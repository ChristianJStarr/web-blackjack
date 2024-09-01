
suits = ['S', 'H', 'D', 'C']
ranks = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']

deck_size = len(ranks)


def hand_value(cards):
    value = 0
    num_aces = 0
    for card in cards:
        card_value = card[1:]
        if card_value in ['J', 'Q', 'K', 'T']:
            value += 10
        elif card_value == 'A':
            num_aces += 1
            value += 11
        else:
            value += int(card_value)

    while value > 21 and num_aces:
        value -= 10
        num_aces -= 1

    return value

def get_int(amount):
    try:
        return int(amount)
    except:
        return 0
