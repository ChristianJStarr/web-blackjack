import random
import string
from flask import request, session
from flask_restx import Resource, fields
from werkzeug.security import generate_password_hash, check_password_hash
from blackjack.api.v1 import ns_auth, api
from blackjack.models.user import User
from blackjack import db

# Define models for documentation
login_model = api.model('Login', {
    'username': fields.String(required=True, description='Username'),
    'password': fields.String(required=True, description='Password')
})

signup_model = api.model('Signup', {
    'username': fields.String(required=True, description='Username'),
    'name': fields.String(required=True, description='Display name'),
    'password': fields.String(required=True, description='Password'),
    'password_confirm': fields.String(required=True, description='Password confirmation')
})

guest_model = api.model('Guest', {
    'name': fields.String(required=True, description='Display name')
})

user_model = api.model('User', {
    'id': fields.Integer(description='User ID'),
    'username': fields.String(description='Username'),
    'name': fields.String(description='Display name'),
    'balance': fields.Integer(description='User balance')
})

auth_response = api.model('AuthResponse', {
    'success': fields.Boolean(description='Success flag'),
    'user': fields.Nested(user_model),
    'error': fields.String(description='Error message if any')
})

@ns_auth.route('/login')
class Login(Resource):
    @ns_auth.doc('login')
    @ns_auth.expect(login_model)
    @ns_auth.marshal_with(auth_response)
    def post(self):
        """Login with username and password"""
        data = request.json
        username = data.get('username')
        password = data.get('password')
        
        if not username or not password:
            return {'success': False, 'error': 'Username and password required'}, 400
            
        user = User.query.filter_by(username=username).first()
        if not user or not check_password_hash(user.password, password):
            return {'success': False, 'error': 'Invalid credentials'}, 401
            
        session['user_id'] = user.id
        return {'success': True, 'user': user.to_dict()}, 200

@ns_auth.route('/signup')
class Signup(Resource):
    @ns_auth.doc('signup')
    @ns_auth.expect(signup_model)
    @ns_auth.marshal_with(auth_response)
    def post(self):
        """Register a new user"""
        data = request.json
        username = data.get('username')
        name = data.get('name')
        password = data.get('password')
        password_confirm = data.get('password_confirm')
        
        if not username or not name or not password:
            return {'success': False, 'error': 'All fields are required'}, 400
            
        if password != password_confirm:
            return {'success': False, 'error': 'Passwords do not match'}, 400
            
        if User.query.filter_by(username=username).first():
            return {'success': False, 'error': 'Username already taken'}, 400
            
        hashed_password = generate_password_hash(password)
        new_user = User(username=username, name=name, password=hashed_password, balance=10000)
        db.session.add(new_user)
        db.session.commit()
        
        session['user_id'] = new_user.id
        return {'success': True, 'user': new_user.to_dict()}, 201

@ns_auth.route('/guest')
class Guest(Resource):
    @ns_auth.doc('guest')
    @ns_auth.expect(guest_model)
    @ns_auth.marshal_with(auth_response)
    def post(self):
        """Register as a guest user"""
        data = request.json
        name = data.get('name')
        
        if not name:
            return {'success': False, 'error': 'Display name is required'}, 400
            
        username = ''.join(random.choices(string.ascii_letters + string.digits, k=16))
        hashed_password = generate_password_hash(username)
        new_user = User(username=username, name=name, password=hashed_password, balance=10000)
        db.session.add(new_user)
        db.session.commit()
        
        session['user_id'] = new_user.id
        return {'success': True, 'user': new_user.to_dict()}, 201

@ns_auth.route('/logout')
class Logout(Resource):
    @ns_auth.doc('logout')
    def get(self):
        """Logout the current user"""
        session.clear()
        return {'success': True}, 200 