#!/usr/bin/python3
"""Code cotening logic to get user profile"""

import mysql.connector
import logging
from .database import db

def get_user_profile(user_id):
    try:
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
        user_data = cursor.fetchone()

        if user_data:
            user_profile = {
                'user_id': user_data['id'],
                'username': user_data['username'],
                'first_name': user_data['first_name'],
                'last_name': user_data['last_name'],
                'age': user_data['age'],
                'email': user_data['email'],
                'category': user_data['category'],
                'interests': user_data['interests'],
                'preferences': user_data['preferences'],
                'establishment': user_data['establishment'],
                'location': user_data['location'],
                'skills': [],
                'profile_photo_url': None,
                'cover_photo_url': None,
                'message_photo_urls': [],
                'shared_photo_urls': []
            }

            # Récupérer les compétences de l'utilisateur
            cursor.execute("SELECT skills FROM user_skills WHERE user_id = %s", (user_id,))
            skills_data = cursor.fetchall()
            user_profile['skills'] = [skill['skills'] for skill in skills_data]

            # Récupérer les photos de l'utilisateur
            cursor.execute("""
                SELECT photo_url, is_profile_photo, is_cover_photo, is_message_photo, is_shared_photo
                FROM user_photos
                WHERE user_id = %s
            """, (user_id,))
            photos_data = cursor.fetchall()

            for photo in photos_data:
                if photo['is_profile_photo']:
                    user_profile['profile_photo_url'] = photo['photo_url']
                elif photo['is_cover_photo']:
                    user_profile['cover_photo_url'] = photo['photo_url']
                elif photo['is_message_photo']:
                    user_profile['message_photo_urls'].append(photo['photo_url'])
                elif photo['is_shared_photo']:
                    user_profile['shared_photo_urls'].append(photo['photo_url'])

            return user_profile
        else:
            return None
    except mysql.connector.Error as err:
        logging.error('Database error: %s', err)
        return None