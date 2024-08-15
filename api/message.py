from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from .database import db
import os

app = Flask(__name__)
CORS(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:Fap&2121*7656@localhost/palavem_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sender = db.Column(db.String(255))
    receiver = db.Column(db.String(255))
    text = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, default=db.func.current_timestamp())

@app.route('/messages', methods=['POST'])
def send_message():
    data = request.get_json()
    new_message = Message(sender=data['sender'], receiver=data['receiver'], text=data['text'])
    db.session.add(new_message)
    db.session.commit()
    return jsonify({'message': 'Message sent'}), 201

@app.route('/messages/<receiver>', methods=['GET'])
def get_messages(receiver):
    messages = Message.query.filter_by(receiver=receiver).all()
    return jsonify([{
        'id': message.id,
        'sender': message.sender,
        'receiver': message.receiver,
        'text': message.text,
        'timestamp': message.timestamp
    } for message in messages])

if __name__ == '__main__':
    db.create_all()
    app.run()

