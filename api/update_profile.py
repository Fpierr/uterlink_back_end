#!/usr/bin/python3
"""update user profile"""

import os
import mysql.connector
from email.message import EmailMessage
from flask import Flask, request, jsonify
from dotenv import load_dotenv
from .registration import generate_verification_code, send_verification_email
from .database import db

# Load environment variables
load_dotenv()

app = Flask(__name__)

verification_store = {}

@app.route('/update_profile', methods=['POST'])
def update_profile():
    """Handle profile update request"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Invalid JSON data provided'}), 400
        
        step = data.get('step')
        email = data.get('email')

        if not step or not email:
            return jsonify({'error': 'Missing step or email in request'}), 400

        if step == 'send_code':
            username = data.get('username')
            first_name = data.get('firstName')
            last_name = data.get('lastName')
            age = data.get('age')
            category = data.get('category')
            location = data.get('location')
            interests = data.get('interests')
            preferences = data.get('preferences')
            establishment = data.get('establishment')
            selected_skills = data.get('selectedSkills')

            # Check if any required field is missing and Data validation logic
            if not all([username, first_name, last_name, category, location, establishment, interests, preferences]) or not selected_skills:
                return jsonify({'error': 'Missing required fields'}), 400
            try:
                age = int(age)  # Convert age to integer
                if age <= 0:
                    raise ValueError("Age must be a positive integer")
            except ValueError:
                return jsonify({'error': 'Invalid age'}), 400

            # Generate verification code
            verification_code = generate_verification_code()

            # Send verification email
            if not send_verification_email(email, verification_code):
                return jsonify({'error': 'Failed to send verification email'}), 500

            # Store the verification code temporarily (in memory or a temporary database)
            verification_store[email] = {
                'code': verification_code,
                'user_data': {
                    'username': username,
                    'first_name': first_name,
                    'last_name': last_name,
                    'age': age,
                    'category': category,
                    'location': location,
                    'interests': interests,
                    'preferences': preferences,
                    'establishment': establishment,
                    'selected_skills': selected_skills
                }
            }

            return jsonify({'message': 'Verification code sent to email'}), 200

        elif step == 'verify_code':
            code = data.get('code')

            if not code:
                return jsonify({'error': 'Missing code in request'}), 400

            # Check if the code is correct
            if email in verification_store and verification_store[email]['code'] == code:
                user_data = verification_store[email]['user_data']
                
                # Proceed with the profile update process (update in database)
                with db.cursor() as cursor:
                    try:
                        cursor.execute("""
                            UPDATE users SET
                                username = %s,
                                first_name = %s,
                                last_name = %s,
                                age = %s,
                                category = %s,
                                location = %s,
                                interests = %s,
                                preferences = %s,
                                establishment = %s
                            WHERE email = %s
                        """, (
                            user_data['username'],
                            user_data['first_name'],
                            user_data['last_name'],
                            user_data['age'],
                            user_data['category'],
                            user_data['location'],
                            user_data['interests'],
                            user_data['preferences'],
                            user_data['establishment'],
                            email
                        ))

                        cursor.execute("SELECT id FROM users WHERE email = %s", (email,))
                        user_id = cursor.fetchone()[0]

                        cursor.execute("DELETE FROM user_skills WHERE user_id = %s", (user_id,))
                        # Insert the selected skills into the user_skills table
                        for skill in user_data['selected_skills']:
                            cursor.execute("INSERT INTO user_skills (user_id, skills) VALUES (%s, %s)", (user_id, skill))
                        
                        db.commit()
                        del verification_store[email]
                        return jsonify({'message': 'Profile updated successfully'}), 200
                    except mysql.connector.Error as err:
                        print("Error updating database:", err)
                        db.rollback()
                        return jsonify({'error': 'Database error'}), 500
            else:
                return jsonify({'error': 'Invalid verification code'}), 400

        else:
            return jsonify({'error': 'Invalid step'}), 400

    except Exception as e:
        print(f"Exception during profile update: {e}")
        return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    app.run()
