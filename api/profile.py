#!/usr/bin/python3
"""Profile file contening code to uplodad all user and msg"""

from flask import Flask, jsonify
from flask import Blueprint
from .database import db

profile_bp = Blueprint('profile', __name__)

app = Flask(__name__)

# Définition des routes
@profile_bp.route('/all_profiles', methods=['GET'])
def get_all_profiles():
    """Recover profile data"""
    cur = db.cursor()
    query = """
    SELECT u.id, u.username, u.first_name, u.last_name, u.age, u.email, u.category,
           u.establishment, u.location, u.interests, u.preferences,
           GROUP_CONCAT(us.skills) as skills, MAX(up.photo_url) as photo_url
    FROM users u
    LEFT JOIN user_skills us ON u.id = us.user_id
    LEFT JOIN user_photos up ON u.id = up.user_id AND up.is_profile_photo = TRUE
    GROUP BY u.id, u.username, u.first_name, u.last_name, u.age, u.email, u.category,
             u.establishment, u.location, u.interests, u.preferences
    """
    cur.execute(query)
    rows = cur.fetchall()
    profiles = []

    for row in rows:
        profile = {
            'id': row[0],
            'username': row[1],
            'first_name': row[2],
            'last_name': row[3],
            'age': row[4],
            'email': row[5],
            'category': row[6],
            'establishment': row[7].split(',') if row[7] else None,
            'location': row[8] if row[8] else None,
            'interests': row[9].split(',') if row[9] else None,
            'preferences': row[10].split(',') if row[10] else None,
            'skills': row[11].split(',') if row[11] else [],
            'photoUrl': row[12] if row[11] else None
        }
        profiles.append(profile)

    cur.close()
    return jsonify(profiles)

@profile_bp.route('/all_messages', methods=['GET'])
def get_all_messages():
    """Récupère tous les messages depuis la base de données"""
    cur = db.cursor()
    query = """
    SELECT message_id, sender_id, receiver_id, message_content, timestamp
    FROM messages
    """
    cur.execute(query)
    rows = cur.fetchall()
    messages = []

    for row in rows:
        message = {
            'message_id': row[0],
            'sender_id': row[1],
            'receiver_id': row[2],
            'message_content': row[3],
            'timestamp': row[4].strftime('%Y-%m-%dT%H:%M:%S')
        }
        messages.append(message)

    cur.close()
    return jsonify(messages)

if __name__ == '__main__':
    app.run()

