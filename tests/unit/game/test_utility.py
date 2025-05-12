import pytest
from blackjack.game.utility import generate_id, valid_game_id, calculate_hand_value


class TestUtilityFunctions:
    """Tests for the utility functions in the game module."""

    def test_generate_id(self):
        """Test that generate_id returns an ID of the correct length."""
        id1 = generate_id()
        id2 = generate_id()
        
        # IDs should be 4 characters by default
        assert len(id1) == 4
        assert len(id2) == 4
        
        # IDs should be different each time
        assert id1 != id2
        
        # Custom length
        id3 = generate_id(length=8)
        assert len(id3) == 8

    def test_valid_game_id(self):
        """Test the game ID validation function."""
        # Valid game IDs
        assert valid_game_id("abcd") is True
        assert valid_game_id("1234") is True
        assert valid_game_id("a1b2") is True
        
        # Invalid game IDs
        assert valid_game_id("") is False
        assert valid_game_id(None) is False
        assert valid_game_id("abc") is False  # Too short
        assert valid_game_id("abcde") is False  # Too long
        assert valid_game_id("ab-d") is False  # Invalid character

    def test_calculate_hand_value(self):
        """Test the hand value calculation function."""
        # Empty hand
        assert calculate_hand_value([]) == 0
        
        # Simple hands
        assert calculate_hand_value([{'rank': '2', 'suit': 'hearts'}]) == 2
        assert calculate_hand_value([{'rank': '10', 'suit': 'hearts'}]) == 10
        assert calculate_hand_value([{'rank': 'J', 'suit': 'hearts'}]) == 10
        assert calculate_hand_value([{'rank': 'Q', 'suit': 'hearts'}]) == 10
        assert calculate_hand_value([{'rank': 'K', 'suit': 'hearts'}]) == 10
        assert calculate_hand_value([{'rank': 'A', 'suit': 'hearts'}]) == 11
        
        # Multiple cards
        assert calculate_hand_value([
            {'rank': '2', 'suit': 'hearts'},
            {'rank': '3', 'suit': 'clubs'}
        ]) == 5
        
        # Face cards
        assert calculate_hand_value([
            {'rank': 'J', 'suit': 'hearts'},
            {'rank': 'Q', 'suit': 'clubs'}
        ]) == 20
        
        # Aces high
        assert calculate_hand_value([
            {'rank': 'A', 'suit': 'hearts'},
            {'rank': '5', 'suit': 'clubs'}
        ]) == 16
        
        # Aces adjusting to low for multiple aces
        assert calculate_hand_value([
            {'rank': 'A', 'suit': 'hearts'},
            {'rank': 'A', 'suit': 'clubs'}
        ]) == 12  # 11 + 1
        
        # Aces adjusting to low to avoid busting
        assert calculate_hand_value([
            {'rank': 'A', 'suit': 'hearts'},
            {'rank': '10', 'suit': 'clubs'},
            {'rank': '5', 'suit': 'diamonds'}
        ]) == 16  # Ace becomes 1 instead of 11 to avoid busting 