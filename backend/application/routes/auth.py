from flask import Blueprint, request, jsonify, make_response
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    jwt_required,
    get_jwt_identity
)
from application.models.user import User
from application import db
from datetime import datetime
from email_validator import validate_email, EmailNotValidError

bp = Blueprint('auth', __name__, url_prefix='/api/auth')

@bp.route('/login', methods=['POST', 'OPTIONS'])
def login():
    if request.method == 'OPTIONS':
        response = make_response()
        response.headers.add('Access-Control-Allow-Origin', 'http://localhost:3000')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
        response.headers.add('Access-Control-Allow-Methods', 'POST')
        return response

    data = request.get_json()
    
    if not data or 'email' not in data or 'password' not in data:
        return jsonify({'error': 'Missing email or password'}), 400
    
    user = User.query.filter_by(email=data['email']).first()
    
    if not user or not user.check_password(data['password']):
        return jsonify({'error': 'Invalid email or password'}), 401
    
    # Update last login
    user.last_login = datetime.utcnow()
    db.session.commit()
    
    access_token = create_access_token(identity=user.id)
    refresh_token = create_refresh_token(identity=user.id)
    
    response = jsonify({
        'user': user.to_dict(),
        'access_token': access_token,
        'refresh_token': refresh_token
    })
    
    response.headers.add('Access-Control-Allow-Origin', 'http://localhost:3000')
    return response

@bp.route('/register', methods=['POST', 'OPTIONS'])
def register():
    if request.method == 'OPTIONS':
        response = make_response()
        response.headers.add('Access-Control-Allow-Origin', 'http://localhost:3000')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
        response.headers.add('Access-Control-Allow-Methods', 'POST')
        return response

    data = request.get_json()
    
    # Validate required fields
    required_fields = ['email', 'password', 'user_type']
    if not all(field in data for field in required_fields):
        return jsonify({'error': 'Missing required fields'}), 400
    
    try:
        # Validate email
        valid = validate_email(data['email'])
        email = valid.email
        
        # Validate user type
        if data['user_type'] not in ['candidate', 'employer']:
            return jsonify({'error': 'Invalid user type'}), 400
        
        # Check if user exists
        if User.query.filter_by(email=email).first():
            return jsonify({'error': 'Email already registered'}), 400
        
        # Create user
        user = User(
            email=email,
            user_type=data['user_type']
        )
        user.set_password(data['password'])
        
        db.session.add(user)
        db.session.commit()
        
        access_token = create_access_token(identity=user.id)
        refresh_token = create_refresh_token(identity=user.id)
        
        response = jsonify({
            'user': user.to_dict(),
            'access_token': access_token,
            'refresh_token': refresh_token
        })
        
        response.headers.add('Access-Control-Allow-Origin', 'http://localhost:3000')
        return response, 201
        
    except EmailNotValidError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500