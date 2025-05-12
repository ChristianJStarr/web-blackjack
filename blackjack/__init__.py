from flask import Flask, jsonify, request
from flask_socketio import SocketIO
from flask_sqlalchemy import SQLAlchemy
import logging
from logging.handlers import RotatingFileHandler
import os
import sqlalchemy.exc

# Initialize extensions
db = SQLAlchemy()
socketio = SocketIO()

def create_app(config_name='default'):
    """Create and configure the Flask application."""
    from config import config
    
    # Create Flask app with proper template and static folders
    app = Flask(__name__, 
                template_folder='templates',
                static_folder='static')
    app.config.from_object(config[config_name])
    
    # Override with SQLite if running locally for first time
    if 'mysql' in app.config['SQLALCHEMY_DATABASE_URI'] and not os.environ.get('DATABASE_URL'):
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///blackjack.db'
    
    # Initialize extensions with app
    db.init_app(app)
    socketio.init_app(app, cors_allowed_origins="*")
    
    # Register blueprints
    from blackjack.web import web as web_blueprint
    app.register_blueprint(web_blueprint)
    
    from blackjack.api import api_bp
    app.register_blueprint(api_bp, url_prefix='/api/v1')
    
    from blackjack.auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint, url_prefix='/auth')
    
    # Set up error handlers
    @app.errorhandler(404)
    def not_found(error):
        if request.path.startswith('/api/'):
            return jsonify({'error': 'Not found'}), 404
        return "Page not found", 404
    
    @app.errorhandler(500)
    def internal_error(error):
        if request.path.startswith('/api/'):
            return jsonify({'error': 'Internal server error'}), 500
        return "Internal server error", 500
    
    # Configure logging
    if not app.debug and not app.testing:
        # Ensure log directory exists
        log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'logs')
        os.makedirs(log_dir, exist_ok=True)
        
        # Set up file handler
        file_handler = RotatingFileHandler(
            os.path.join(log_dir, 'blackjack.log'),
            maxBytes=10485760,  # 10MB
            backupCount=10
        )
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        ))
        file_handler.setLevel(logging.INFO)
        
        # Set up app logger
        app.logger.addHandler(file_handler)
        app.logger.setLevel(logging.INFO)
        app.logger.info('Blackjack startup')
    
    # Request logging
    @app.before_request
    def log_request_info():
        if not app.debug:
            app.logger.debug('Headers: %s', request.headers)
            app.logger.debug('Body: %s', request.get_data())
    
    @app.after_request
    def log_response_info(response):
        if not app.debug:
            app.logger.debug('Response: %s', response.status)
        return response
    
    # Create database tables
    try:
        with app.app_context():
            db.create_all()
    except sqlalchemy.exc.DatabaseError as e:
        app.logger.error(f"Database connection error: {e}")
        print(f"WARNING: Could not connect to database. Using SQLite instead.")
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///blackjack.db'
        with app.app_context():
            db.create_all()
        
    return app
