import random
import string
from flask import request, session, jsonify, redirect, url_for, current_app
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.exc import SQLAlchemyError
from blackjack import db
from blackjack.auth import auth
from blackjack.models.user import User
from blackjack.exceptions import AuthenticationError

@auth.route('/', methods=['POST', 'GET'])
def authenticate():
    """Handle authentication requests"""
    response = {
        'success': False,
        'errors': []
    }
    try:
        if request.method == "GET":
            type = request.args.get('type')
            if type == 'logout':
                session.clear()
                return redirect(url_for('web.index'))
        else:
            type = request.form.get('type')
            name = request.form.get('name')
            username = request.form.get('username')
            password = request.form.get('password')
            password_2 = request.form.get('password_2')

            if type == 'login':
                if not username or not password:
                    response['errors'].append('Username and Password must be provided')
                    return jsonify(response), 400
                    
                user = User.query.filter_by(username=username).first()
                if user:
                    if check_password_hash(user.password, password):
                        session['user_id'] = user.id
                        response['user_id'] = user.id
                        response['success'] = True
                        return jsonify(response), 200
                    else:
                        response['errors'].append('Incorrect password')
                else:
                    response['errors'].append('User does not exist')
                    
            elif type == 'signup':
                if not name or not username or not password or not password_2:
                    response['errors'].append('Display Name, Username, and Password must be provided')
                    return jsonify(response), 400
                    
                if User.query.filter_by(username=username).first():
                    response['errors'].append('User already exists')
                    return jsonify(response), 400

                hashed_password = generate_password_hash(password)
                new_user = User(username=username, name=name, password=hashed_password, balance=10000)
                db.session.add(new_user)
                db.session.commit()

                session['user_id'] = new_user.id
                response['user_id'] = new_user.id
                response['success'] = True
                return jsonify(response), 201
                
            elif type == 'guest':
                if not name:
                    response['errors'].append('Display Name must be provided')
                    return jsonify(response), 400
                    
                username = ''.join(random.choices(string.ascii_letters + string.digits, k=16))
                hashed_password = generate_password_hash(username)
                new_user = User(username=username, name=name, password=hashed_password, balance=10000)
                db.session.add(new_user)
                db.session.commit()

                session['user_id'] = new_user.id
                response['user_id'] = new_user.id
                response['success'] = True
                return jsonify(response), 201

    except SQLAlchemyError as e:
        current_app.logger.error(f"Database error in auth: {str(e)}")
        response['errors'].append(f'Database error: {str(e)}')
    except Exception as e:
        current_app.logger.error(f"Unexpected error in auth: {str(e)}")
        response['errors'].append(f'An unexpected error occurred: {str(e)}')
    finally:
        if request.method == 'POST':
            return jsonify(response), 500 if response['errors'] else 200
            
@auth.route('/user')
def current_user():
    """Get current authenticated user"""
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({
            'authenticated': False,
            'user': None
        })
    
    user = User.query.get(user_id)
    if not user:
        session.clear()
        return jsonify({
            'authenticated': False,
            'user': None
        })
        
    return jsonify({
        'authenticated': True,
        'user': user.to_dict()
    }) 