#!/usr/bin/python3
""" Login API"""

import bcrypt
from flask import Flask, make_response, redirect
from flask import request, jsonify, session, url_for
from flask_session import Session
import jwt
from flask_cors import CORS
import datetime
from datetime import datetime, timedelta, timezone
import logging
import mysql.connector
from .login import login_user
from .upload_photo_url import upload_url
from .registration import register_user
from .profile import get_all_profiles, get_all_messages
from .profile import profile_bp
from .user_profile import get_user_profile
from .update_profile import update_profile
from .contact_us import send
from .database import db, Config

app = Flask(__name__)

# Configuration of secret key for the sessions Flask
app.secret_key = Config.SECRET_KEY

app.config['SESSION_PERMANENT'] = True
app.config['SESSION_TYPE'] = 'filesystem'
Session(app)
logging.basicConfig(level=logging.DEBUG)
CORS(app, supports_credentials=True)

app.register_blueprint(profile_bp)

def hash_password(password):
    """Hash the password using bcrypt"""
    hashed_password = bcrypt.hashpw(
            password.encode('utf-8'), bcrypt.gensalt())
    return hashed_password.decode('utf-8')

def verify_password(plain_password, hashed_password):
    """Verify if the plain password matches the hashed password"""
    return bcrypt.checkpw(plain_password.encode(
        'utf-8'), hashed_password.encode('utf-8'))

def decode_token(token):
    """Decode JWT token and extract user_id"""
    try:
        # Decode token using secret key
        decoded_token = jwt.decode(token, app.secret_key,
                                   algorithms=['HS256'])

        # Extract user_id from token payload
        user_id = decoded_token.get('user_id')
        return user_id
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

def generate_token(user_id):
    """Generate JWT token for the user"""
    payload = {
        'user_id': user_id,
        'exp': datetime.now(timezone.utc) + timedelta(hours=1)
    }
    token = jwt.encode(payload, app.secret_key, algorithm='HS256')
    return token


@app.route('/register', methods=['POST'])
def register():
    """Call function to register user"""
    return register_user()

@app.route('/login', methods=['POST'])
def login():
    """Call function to connect user"""
    return login_user()

@app.route('/upload-url', methods=['POST'])
def upload():
    return upload_url()

@app.route('/contact', methods=['POST'])
def contact_us():
    return send()

@app.route('/update_profile', methods=['POST'])
def edit_profile():
    return update_profile()

@app.route('/all_profiles', methods=['GET'])
def all_profile():
    return get_all_profiles()

@app.route('/all_messages', methods=['GET'])
def all_messages():
    return get_all_messages()

@app.route('/profile/<int:user_id>', methods=['GET'])
def user_profile(user_id):
    try:
        auth_header = request.headers.get('Authorization')
        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header.split()[1]
            user_id_decode = decode_token(token)

            if user_id and user_id == user_id_decode:
                user_profile = get_user_profile(user_id)
                if user_profile:
                    return make_response(jsonify(user_profile), 200)
                else:
                    return make_response(jsonify({'error':
                        'Failed to fetch user profile'}), 500)
            else:
                return make_response(jsonify({'error':
                    'Invalid authorization header'}), 401)
    except Exception as e:
        return make_response(jsonify({'error': str(e)}), 401)

@app.route('/search', methods=['GET'])
def search_profiles():
    try:
        keyword = request.args.get('q')
        cursor = db.cursor(dictionary=True)
        # SQL request to search profile
        query = """
            SELECT users.id, username, first_name, last_name, age,
            email, category, establishment, location, interests,
            preferences, skills, photo_url
            FROM users
            LEFT JOIN user_skills ON users.id = user_skills.user_id
            LEFT JOIN user_photos ON users.id = user_photos.user_id
            WHERE username LIKE %s
                OR first_name LIKE %s
                OR last_name LIKE %s
                OR skills LIKE %s
                OR interests LIKE %s
                OR category LIKE %s
                OR preferences LIKE %s
                OR establishment LIKE %s
                OR location LIKE %s
                OR age LIKE %s
        """
        cursor.execute(query, (f'%{keyword}%', f'%{keyword}%', f'%{keyword}%',
                               f'%{keyword}%', f'%{keyword}%', f'%{keyword}%',
                               f'%{keyword}%', f'%{keyword}%', f'%{keyword}%',
                               f'%{keyword}%'))
        profiles = cursor.fetchall()
        cursor.close()
        return jsonify(profiles), 200
    except mysql.connector.Error as err:
        logging.error('Database error: %s', err)
        return jsonify({'error': 'Failed to search profiles'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/messages', methods=['POST'])
def send_message():
    data = request.get_json()
    try:
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        cursor = db.cursor()
        cursor.execute(
            "INSERT INTO messages (sender_id, receiver_id, "
            "message_content, timestamp) "
            "VALUES (%s, %s, %s, %s)",
            (data['sender_id'], data['receiver_id'],
             data['message_content'], timestamp)
        )
        db.commit()
        cursor.close()
        return jsonify({'message': 'Message sent'}), 201
    except mysql.connector.Error as err:
        logging.error('Database error: %s', err)
        return jsonify({'error': 'Failed to send message'}), 500


@app.route('/messages', methods=['GET'])
def get_messages():
    user_id = request.args.get('userId')
    peer_id = request.args.get('peerId')
    cursor = db.cursor()
    cursor.execute("SELECT * FROM messages "
                   "WHERE (sender_id = %s AND receiver_id = %s) "
                   "OR (sender_id = %s AND receiver_id = %s)",
                   (user_id, peer_id, peer_id, user_id))
    messages = cursor.fetchall()
    cursor.close()
    response_messages = [{'message_id': message[0],
                          'sender_id': message[1],
                          'receiver_id': message[2],
                          'message_content': message[3],
                          'timestamp': message[4]} for message in messages]
    return jsonify(response_messages), 200


@app.route('/logout', methods=['GET', 'POST'])
def logout_user():
    if request.method == 'GET':
        session.pop('user_id', None)
        return redirect(url_for('login'))
    elif request.method == 'POST':
        session.pop('user_id', None)
        return jsonify({'message': 'User logged out successfully'}), 200
    else:
        return "Method not allowed", 405


if __name__ == '__main__':
    app.run()
