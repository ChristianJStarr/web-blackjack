import unittest
import uuid
import blackjack as bj
import utility as u


class TestBlackjack(unittest.TestCase):

    def setUp(self):
        self.message_fn_called = []

        def message_fn(key, data, to):
            self.message_fn_called.append((key, data, to))

        self.game_manager = bj.BlackJackGameManager()
        self.game_id = str(uuid.uuid4())
        self.game = self.game_manager.create_game(self.game_id, message_fn)
        self.session_id = str(uuid.uuid4())
        self.player = self.game_manager.register_player(self.session_id)
        self.game.add_player(self.player, 'player')

    def test_create_game(self):
        game = self.game_manager.get_game(self.game_id)
        self.assertIsNotNone(game, "Game should be created and retrieved")

    def test_add_player(self):
        player, game = self.game_manager.get_session(self.session_id)
        self.assertIsNotNone(player, "Player should be registered")
        self.assertEqual(player.name, 'player', "Player name should be 'player'")
        self.assertEqual(game, self.game, "Player's game should be the created game")

    def test_initial_deal(self):
        self.game.initial_deal()
        dealer_state = self.game.dealer.state
        self.assertEqual(len(self.game.dealer.cards), 2, "Dealer should have 2 cards initially")
        self.assertTrue(all(card is not None for card in [dealer_state['up_card'], dealer_state['down_card']]),
                        "Dealer should have both up and down cards")

    def test_player_bet(self):
        success, error = self.game.player_bet(self.player, 100)
        self.assertTrue(success, "Player should be able to place a bet")
        self.assertEqual(self.player.balance, 4900, "Player's balance should decrease by the bet amount")

    def test_player_action_hit(self):
        self.game.player_bet(self.player, 100)
        self.game.initial_deal()
        initial_hand_value = self.game.seats[0].hand_value
        self.game.player_action(self.player, 'hit')
        new_hand_value = self.game.seats[0].hand_value
        self.assertGreater(new_hand_value, initial_hand_value, "Player's hand value should increase after hitting")

    def test_player_action_stand(self):
        self.game.player_bet(self.player, 100)
        self.game.initial_deal()
        self.game.player_action(self.player, 'stand')
        self.assertEqual(self.game.turn, 0, "Turn should move to the next player after standing")

    def test_dealers_turn(self):
        self.game.player_bet(self.player, 100)
        self.game.initial_deal()
        self.game.wait_for_dealers_turn()
        self.assertEqual(self.game.dealer.hand_value, u.hand_value(self.game.dealer.cards),
                         "Dealer's hand value should be updated after their turn")

    def test_end_round(self):
        self.game.player_bet(self.player, 100)
        self.game.initial_deal()
        self.game.dealer.cards = ['H2', 'H3', 'H4']  # Set a predetermined hand for dealer
        self.game.end_round()
        result = [call for call in self.message_fn_called if call[0] == 'round_result']
        self.assertTrue(result, "Round result message should be sent")
        self.assertEqual(result[0][1], 'lose', "Round result should reflect a loss")


if __name__ == '__main__':
    unittest.main()
