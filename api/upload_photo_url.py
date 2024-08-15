#!/usr/bin/python3
"""Updload photo url"""

from flask import Flask, request, jsonify
from .database import db
import validators

app = Flask(__name__)

@app.route('/upload-url', methods=['POST'])
def upload_url():
    url = request.form.get('url')
    user_id = request.form.get('user_id')
    is_profile_photo = request.form.get('is_profile_photo', '0')
    is_cover_photo = request.form.get('is_cover_photo', '0')
    is_message_photo = request.form.get('is_message_photo', '0')
    is_shared_photo = request.form.get('is_shared_photo', '0')

    if not url or not user_id:
        return jsonify({"error": "Missing 'url' or 'user_id'"}), 400

    if not validators.url(url):
        return jsonify({"error": "Invalid URL format"}), 400

    try:
        cursor = db.cursor()
        cursor.execute("""
            INSERT INTO user_photos (user_id, photo_url, is_profile_photo, is_cover_photo, is_message_photo, is_shared_photo)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (user_id, url, is_profile_photo, is_cover_photo, is_message_photo, is_shared_photo))
        db.commit()
        cursor.close()
        return jsonify({"message": "URL saved to database successfully"}), 200
    except Exception as e:
        db.rollback()
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run()
