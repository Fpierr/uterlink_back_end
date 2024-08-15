#!/usr/bin/python3
""" Login API"""

from flask import Flask, logging, request, jsonify, session, make_response
from flask_session import Session
from flask_cors import CORS
import bcrypt
import jwt
from datetime import datetime, timezone, timedelta
from validate_email import validate_email
from flask_wtf.csrf import CSRFProtect
from .database import db, Config

app = Flask(__name__)
app.secret_key = Config.SECRET_KEY
csrf = CSRFProtect(app)
CORS(app, supports_credentials=True)

app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_PERMANENT'] = True
Session(app)

def verify_password(plain_password, hashed_password):
    """Verify if the plain password matches the hashed password"""
    return bcrypt.checkpw(plain_password.encode('utf-8'),
                          hashed_password.encode('utf-8'))

def generate_token(user_id):
    """Generate JWT token for the user"""
    payload = {
        'user_id': user_id,
        'exp': datetime.now(timezone.utc) + timedelta(hours=1)
    }
    return jwt.encode(payload, app.secret_key, algorithm='HS256')

def get_user_profile(user_id):
    """Get user profile from the database"""
    with db.cursor() as cursor:
        cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
        user = cursor.fetchone()
        if user:
            return {
                'user_id': user[0],
                'username': user[1],
                'first_name': user[2],
                'last_name': user[3],
                'age': user[4],
                'email': user[5],
                'is_student': user[7]
            }
        else:
            return None

@app.route('/login', methods=['POST'])
@csrf.exempt
def login_user():
    try:
        data = request.get_json()
        if not data or not isinstance(data, dict) or 'email' not in data or 'password' not in data:
            return jsonify({'error': 'Invalid JSON data provided'}), 400

        email = data.get('email')
        password = data.get('password')

        if not validate_email(email):
            return jsonify({'error': 'Invalid email format'}), 400

        # Fetch the user from the database based on the provided email
        with db.cursor() as cursor:
            cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
            user = cursor.fetchone()

        if not user:
            return jsonify({'error': 'User not found'}), 404

        # Verify if the provided password matches the hashed password stored
        if verify_password(password, user[6]):
            # Generate JWT token for the user
            token = generate_token(user[0])
            # Get user profile
            user_profile = get_user_profile(user[0])
            if user_profile:
                session.permanent = True
                user_id = user[0]
                session['user_id'] = user_id
                session.modified = True
                response_data = {'message': 'Login successful',
                                 'token': token,
                                 'user_profile': user_profile,
                                 'user_id': session['user_id']
                                }
                return make_response(jsonify(response_data), 200)
            else:
                return make_response(jsonify({'error': 'Failed to fetch user profile'}), 500)
        else:
            return jsonify({'error': 'Invalid credentials'}), 401

    except Exception as e:
        logging.error(f"An error occurred: {e}")
        return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    app.run()
