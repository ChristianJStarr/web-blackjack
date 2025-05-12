class BlackjackError(Exception):
    """Base exception for Blackjack application"""
    status_code = 500
    
    def __init__(self, message, status_code=None, payload=None):
        super().__init__(message)
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload
        
    def to_dict(self):
        rv = dict(self.payload or ())
        rv['message'] = self.message
        rv['status'] = self.status_code
        return rv

class GameNotFoundError(BlackjackError):
    """Raised when game cannot be found"""
    status_code = 404

class InvalidActionError(BlackjackError):
    """Raised when player attempts invalid action"""
    status_code = 400
    
class AuthenticationError(BlackjackError):
    """Raised when authentication fails"""
    status_code = 401
    
class ForbiddenError(BlackjackError):
    """Raised when access is forbidden"""
    status_code = 403
    
class ValidationError(BlackjackError):
    """Raised when data validation fails"""
    status_code = 422 