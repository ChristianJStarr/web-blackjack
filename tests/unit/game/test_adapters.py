import pytest
from unittest.mock import patch, MagicMock
from blackjack.game.adapters import GameDbAdapter
from blackjack.game.game import BlackjackGame
from blackjack.exceptions import GameNotFoundError


class TestGameDbAdapter:
    """Tests for the GameDbAdapter class."""

    @pytest.fixture
    def mock_db_session(self):
        """Create a mock DB session."""
        mock_session = MagicMock()
        return mock_session

    @patch('blackjack.game.adapters.db.session')
    @patch('blackjack.game.adapters.Game')
    def test_create_game(self, mock_game_model, mock_db_session):
        """Test creating a new game in the database."""
        # Setup
        mock_game_instance = MagicMock()
        mock_game_model.return_value = mock_game_instance
        mock_game_model.query.get.return_value = None  # No existing game with same ID
        
        # Test
        with patch('blackjack.game.adapters.generate_id', return_value='abcd'):
            blackjack_game = GameDbAdapter.create_game()
        
        # Assert
        assert isinstance(blackjack_game, BlackjackGame)
        assert blackjack_game.game_id == 'abcd'
        assert mock_game_model.called
        assert mock_db_session.add.called
        assert mock_db_session.commit.called

    @patch('blackjack.game.adapters.db.session')
    @patch('blackjack.game.adapters.Game')
    def test_save_game(self, mock_game_model, mock_db_session):
        """Test saving a game to the database."""
        # Setup
        game = BlackjackGame('abcd')
        mock_db_game = MagicMock()
        mock_game_model.query.get.return_value = mock_db_game
        
        # Test
        result = GameDbAdapter.save_game(game)
        
        # Assert
        assert result is True
        assert mock_db_game.state == game.to_dict()
        assert mock_db_session.commit.called

    @patch('blackjack.game.adapters.db.session')
    @patch('blackjack.game.adapters.Game')
    @patch('blackjack.game.adapters.current_app')
    def test_save_game_not_found(self, mock_current_app, mock_game_model, mock_db_session):
        """Test saving a game that doesn't exist in the database."""
        # Setup
        game = BlackjackGame('abcd')
        mock_game_model.query.get.return_value = None
        
        # Test
        result = GameDbAdapter.save_game(game)
        
        # Assert
        assert result is False
        assert mock_current_app.logger.error.called
        assert not mock_db_session.commit.called

    @patch('blackjack.game.adapters.db.session')
    @patch('blackjack.game.adapters.Game')
    def test_load_game(self, mock_game_model, mock_db_session):
        """Test loading a game from the database."""
        # Setup
        mock_db_game = MagicMock()
        mock_db_game.state = {
            'id': 'abcd',
            'state': 'waiting',
            'turn': None,
            'dealer': [],
            'players': {},
            'seats': {},
            'history': []
        }
        mock_game_model.query.get.return_value = mock_db_game
        
        # Test
        game = GameDbAdapter.load_game('abcd')
        
        # Assert
        assert isinstance(game, BlackjackGame)
        assert game.game_id == 'abcd'
        assert game.state == 'waiting'

    @patch('blackjack.game.adapters.db.session')
    @patch('blackjack.game.adapters.Game')
    def test_load_game_not_found_creates_new(self, mock_game_model, mock_db_session):
        """Test loading a game that doesn't exist creates a new one."""
        # Setup
        mock_game_model.query.get.return_value = None
        
        # Test
        game = GameDbAdapter.load_game('abcd')
        
        # Assert
        assert isinstance(game, BlackjackGame)
        assert game.game_id == 'abcd'
        assert mock_game_model.called
        assert mock_db_session.add.called
        assert mock_db_session.commit.called

    @patch('blackjack.game.adapters.db.session')
    @patch('blackjack.game.adapters.Game')
    def test_delete_game(self, mock_game_model, mock_db_session):
        """Test deleting a game from the database."""
        # Setup
        mock_db_game = MagicMock()
        mock_game_model.query.get.return_value = mock_db_game
        
        # Test
        result = GameDbAdapter.delete_game('abcd')
        
        # Assert
        assert result is True
        assert mock_db_session.delete.called
        assert mock_db_session.commit.called

    @patch('blackjack.game.adapters.db.session')
    @patch('blackjack.game.adapters.Game')
    def test_delete_game_not_found(self, mock_game_model, mock_db_session):
        """Test deleting a game that doesn't exist."""
        # Setup
        mock_game_model.query.get.return_value = None
        
        # Test
        result = GameDbAdapter.delete_game('abcd')
        
        # Assert
        assert result is False
        assert not mock_db_session.delete.called
        assert not mock_db_session.commit.called

    @patch('blackjack.game.adapters.Game')
    def test_get_active_games(self, mock_game_model):
        """Test getting a list of active games."""
        # Setup
        mock_game1 = MagicMock()
        mock_game1.id = 'game1'
        mock_game1.state = {'players': 3}
        mock_game1.updated_at = '2023-01-01'
        
        mock_game2 = MagicMock()
        mock_game2.id = 'game2'
        mock_game2.state = {'players': 1}
        mock_game2.updated_at = '2023-01-02'
        
        mock_query = MagicMock()
        mock_query.order_by.return_value.all.return_value = [mock_game1, mock_game2]
        mock_game_model.query = mock_query
        
        # Test
        games = GameDbAdapter.get_active_games()
        
        # Assert
        assert len(games) == 2
        assert games[0]['id'] == 'game1'
        assert games[1]['id'] == 'game2'
        assert mock_query.order_by.called 