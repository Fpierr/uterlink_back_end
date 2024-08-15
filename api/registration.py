#!/usr/bin/python3
"""register user"""

import os
import secrets
import mysql.connector
import bcrypt
import random
import smtplib
from email.message import EmailMessage
from flask import Flask, request, jsonify
from .database import db
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)

verification_store = {}

def hash_password(password):
    """Hash the password using a secure bcrypt"""
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    return hashed_password.decode('utf-8')

def generate_verification_code():
    """Generate a 6-digit verification code."""
    return ''.join([str(secrets.randbelow(10)) for _ in range(6)])

def send_verification_email(email, code):
    """Send verification email"""
    try:
        msg = EmailMessage()
        msg.set_content(f"""Your verification code is {code},
                        Please, don't share it with anybody.""")
        msg['Subject'] = 'Email Verification'
        msg['From'] = os.getenv('EMAIL_USER')
        msg['To'] = email

        with smtplib.SMTP(os.getenv('SMTP_SERVER'), int(os.getenv('SMTP_PORT'))) as server:
            server.starttls()
            server.login(os.getenv('EMAIL_USER'), os.getenv('EMAIL_PASSWORD'))
            server.send_message(msg)
        return True
    except Exception as e:
        print(f"Failed to send email: {e}")
        return False

@app.route('/register', methods=['POST'])
def register_user():
    """Handle user registration request"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Invalid JSON data provided'}), 400

        step = data.get('step')
        email = data.get('email')

        if step == 'send_code':
            username = data.get('username')
            first_name = data.get('firstName')
            last_name = data.get('lastName')
            age = data.get('age')
            password = data.get('password')
            category = data.get('category')
            selected_skills = data.get('selectedSkills')

            # Check if any required field is missing and Data validation logic
            if not all([username, first_name, last_name, email, password, category]):
                return jsonify({'error': 'Missing required fields'}), 400
            try:
                age = int(age)  # Convert age to integer
                if age <= 0:
                    raise ValueError("Age must be a positive integer")
            except ValueError:
                return jsonify({'error': 'Invalid age'}), 400

            # Check if user already exists
            with db.cursor() as cursor:
                cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
                existing_user = cursor.fetchone()

            if existing_user:
                return jsonify({'error': 'User already exists'}), 400

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
                    'email': email,
                    'password': password,
                    'category': category,
                    'selected_skills': selected_skills
                }
            }

            return jsonify({'message': 'Verification code sent to email'}), 200

        elif step == 'verify_code':
            code = data.get('code')

            if not email or not code:
                return jsonify({'error': 'Missing email or code'}), 400

            # Check if the code is correct
            if email in verification_store and verification_store[email]['code'] == code:
                user_data = verification_store[email]['user_data']
                hashed_password = hash_password(user_data['password'])
                
                # Proceed with the registration process (insert into database)
                with db.cursor() as cursor:
                    try:
                        cursor.execute("INSERT INTO users (username, first_name, "
                                       "last_name, age, email, password, category) "
                                       "VALUES (%s, %s, %s, %s, %s, %s, %s)",
                                       (user_data['username'], user_data['first_name'],
                                        user_data['last_name'], user_data['age'],
                                        user_data['email'], hashed_password,
                                        user_data['category']))
                        user_id = cursor.lastrowid
                        # Insert the selected skills into the user_skills table
                        for skill in user_data['selected_skills']:
                            cursor.execute("INSERT INTO user_skills "
                                           "(user_id, skills) VALUES (%s, %s)",
                                           (user_id, skill))
                        db.commit()
                        del verification_store[email]
                        result = {'message': 'User registered successfully'}
                        return jsonify(result), 200
                    except mysql.connector.Error as err:
                        print("Error inserting into database:", err)
                        db.rollback()
                        return jsonify({'error': 'Database error'}), 500
            else:
                return jsonify({'error': 'Invalid verification code'}), 400

        else:
            return jsonify({'error': 'Invalid step'}), 400

    except Exception as e:
        print(f"Exception during registration: {e}")
        return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    app.run()
