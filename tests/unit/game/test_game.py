import pytest
from blackjack.game.game import BlackjackGame, BlackjackConfig


class TestBlackjackGame:
    """Tests for the BlackjackGame class."""

    @pytest.fixture
    def game(self):
        """Create a fresh game instance for each test."""
        return BlackjackGame("test")

    def test_init(self, game):
        """Test the initialization of a game."""
        assert game.game_id == "test"
        assert game.state == "waiting"
        assert game.turn is None
        assert len(game.deck) > 0
        assert isinstance(game.players, dict)
        assert isinstance(game.seats, dict)
        assert isinstance(game.history, list)
        assert len(game.dealer_hand) == 0

    def test_create_deck(self, game):
        """Test the deck creation."""
        # Default game has 6 decks
        assert len(game.deck) == 6 * 52  # 6 decks * 52 cards
        
        # Test with a custom deck count
        config = BlackjackConfig()
        config.deck_count = 2
        custom_game = BlackjackGame("test", config)
        assert len(custom_game.deck) == 2 * 52  # 2 decks * 52 cards

    def test_add_player(self, game):
        """Test adding a player to the game."""
        seat_id, error = game.add_player("player1", 1)
        
        assert seat_id == 1
        assert error is None
        assert "player1" in game.players
        assert game.seats[1] == "player1"
        
        # Default player balance should be set
        assert game.players["player1"]["balance"] == 10000
        assert game.players["player1"]["bet"] == 0
        assert game.players["player1"]["status"] == "waiting"
        
        # Test adding a player to an occupied seat
        seat_id, error = game.add_player("player2", 1)
        assert seat_id is None
        assert error == "Seat already taken"

    def test_remove_player(self, game):
        """Test removing a player from the game."""
        # Add a player first
        game.add_player("player1", 1)
        
        # Remove the player
        result = game.remove_player("player1")
        
        assert result is True
        assert "player1" not in game.players
        assert 1 not in game.seats
        
        # Test removing a player that doesn't exist
        result = game.remove_player("nonexistent")
        assert result is True  # Should return True regardless

    def test_place_bet(self, game):
        """Test placing a bet."""
        # Add a player
        game.add_player("player1", 1)
        
        # Set game state to betting
        game.state = "betting"
        
        # Place a valid bet
        success, error = game.place_bet("player1", 500)
        
        assert success is True
        assert error is None
        assert game.players["player1"]["bet"] == 500
        assert game.players["player1"]["balance"] == 9500  # 10000 - 500
        assert game.players["player1"]["status"] == "playing"
        
        # Test invalid bet amounts
        success, error = game.place_bet("player1", 0)
        assert success is False
        assert "must be greater than zero" in error
        
        success, error = game.place_bet("player1", 100000)
        assert success is False
        assert "Insufficient balance" in error
        
        # Test placing a bet when game isn't in betting state
        game.state = "playing"
        success, error = game.place_bet("player1", 500)
        assert success is False
        assert "not allowed at this time" in error
        
        # Test placing a bet for nonexistent player
        game.state = "betting"
        success, error = game.place_bet("nonexistent", 500)
        assert success is False
        assert "Player not in game" in error

    def test_serialization(self, game):
        """Test serialization and deserialization of game state."""
        # Add a player and some state
        game.add_player("player1", 1)
        game.dealer_hand = [{"rank": "A", "suit": "hearts"}, {"rank": "K", "suit": "clubs"}]
        game.state = "playing"
        game.turn = 1
        
        # Serialize
        data = game.to_dict()
        
        # Verify serialized data
        assert data["id"] == "test"
        assert data["state"] == "playing"
        assert data["turn"] == 1
        assert len(data["dealer"]) == 2
        assert "player1" in data["players"]
        assert data["seats"][1] == "player1"
        
        # Deserialize
        new_game = BlackjackGame.from_dict(data)
        
        # Verify deserialized game
        assert new_game.game_id == "test"
        assert new_game.state == "playing"
        assert new_game.turn == 1
        assert len(new_game.dealer_hand) == 2
        assert "player1" in new_game.players
        assert new_game.seats[1] == "player1"

    def test_player_action_hit(self, game):
        """Test the hit action."""
        # Set up the game
        game.add_player("player1", 1)
        game.state = "playing"
        game.turn = 1
        game.players["player1"]["hand"] = [
            {"rank": "5", "suit": "hearts"},
            {"rank": "6", "suit": "clubs"}
        ]
        
        # Test hit
        success, error = game.player_action("player1", "hit")
        
        assert success is True
        assert error is None
        assert len(game.players["player1"]["hand"]) == 3  # Should have 3 cards now
        
        # Test hit resulting in bust (need to set up a new scenario)
        game.players["player1"]["hand"] = [
            {"rank": "10", "suit": "hearts"},
            {"rank": "10", "suit": "clubs"}
        ]
        
        # Mock the deck to ensure the next card will cause a bust
        game.deck = [{"rank": "5", "suit": "diamonds"}] + game.deck
        
        success, error = game.player_action("player1", "hit")
        
        assert success is True
        assert error is None
        assert game.players["player1"]["status"] == "lose"

    def test_player_action_stand(self, game):
        """Test the stand action."""
        # Set up the game
        game.add_player("player1", 1)
        game.state = "playing"
        game.turn = 1
        game.players["player1"]["hand"] = [
            {"rank": "10", "suit": "hearts"},
            {"rank": "9", "suit": "clubs"}
        ]
        
        # Test stand
        success, error = game.player_action("player1", "stand")
        
        assert success is True
        assert error is None
        assert game.players["player1"]["status"] == "win"
        
        # The turn should have moved to the next player or dealer
        assert game.turn != 1 