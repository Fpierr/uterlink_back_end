#!/usr/bin/python3

from flask import Flask, request, jsonify
from flask_cors import CORS
from .send_email import send_email
from .database import db, Config

app = Flask(__name__)
CORS(app)

@app.route('/contact', methods=['POST'])
def send():
    data = request.json
    name = data.get('name')
    email = data.get('email')
    message = data.get('message')
    send_copy = data.get('sendCopy', False)

    cursor = db.cursor(dictionary=True)
    cursor.execute(
        "INSERT INTO contacts (name, email, message, send_copy) VALUES (%s, %s, %s, %s)",
        (name, email, message, send_copy)
    )
    db.commit()
    cursor.close()

    # Send email to Developer
    developer_email = Config.DEVELOPER_EMAIL
    developer_message = f"Name: {name}\nEmail: {email}\nMessage: {message}"
    send_email(developer_email, developer_message)

    # Send a copy of the email to the user
    if send_copy:
        user_message = f"Thank you for contacting us.\n\nHere is a copy of your message:\n\n{developer_message}"
        send_email(email, user_message)

    return jsonify({'status': 'success'}), 200

if __name__ == '__main__':
    app.run()

