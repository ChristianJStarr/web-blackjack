from flask import render_template, redirect, url_for, session, jsonify, request
from blackjack.web import web
from blackjack.models.user import User
from blackjack import db
from blackjack.game.adapters import GameDbAdapter
import blackjack.game.utility as u

@web.route('/')
def index():
    """Homepage with list of available games"""
    user_id = session.get('user_id')
    user = User.query.get(user_id) if user_id else None
    leaderboard = User.query.order_by(User.balance.desc()).limit(10).all()
    
    # Get active games from adapter
    games = GameDbAdapter.get_active_games()
    
    return render_template('index.html',
        games=games,
        player=user,
        leaderboard=leaderboard
    )
    
@web.route('/game/<game_id>')
def game(game_id):
    """Game room page"""
    if not u.valid_game_id(game_id):
        return redirect(url_for('web.index'))

    # Get game from adapter
    game = GameDbAdapter.load_game(game_id)
    if not game:
        return redirect(url_for('web.index'))

    user_id = session.get('user_id')
    user = User.query.get(user_id) if user_id else None
    session['game_id'] = game_id
    
    leaderboard = User.query.order_by(User.balance.desc()).limit(10).all()

    return render_template('game.html',
       game=game,
       player_required=True,
       player=user,
       leaderboard=leaderboard
    )
    
@web.route('/api/modal/<modal_name>')
def modal(modal_name):
    """Handle modal template rendering"""
    response = {
        'success': False,
    }
    modals = ['login', 'signup', 'guest', 'create']
    try:
        if modal_name not in modals:
            response['error'] = 'Modal does not exist'
            return jsonify(response), 404
            
        template_name = f'modals/{modal_name}.html'
        template_html = render_template(template_name, modal=modal_name)
        
        if template_html:
            response['success'] = True
            response['content'] = template_html
            
    except Exception as e:
        response['error'] = f'Unable to load modal: {str(e)}'
        
    return jsonify(response)
    
@web.route('/privacy')
def privacy():
    """Privacy policy page"""
    return render_template('privacy.html')
    
@web.route('/terms')
def terms():
    """Terms of service page"""
    return render_template('terms.html') 