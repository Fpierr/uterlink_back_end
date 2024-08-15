from flask import Flask
from flask_cors import CORS
from flask_session import Session
from flask_wtf.csrf import CSRFProtect
import os
from dotenv import load_dotenv

load_dotenv()

def create_app():
    app = Flask(__name__)
    app.secret_key = os.getenv('SECRET_KEY')
    csrf = CSRFProtect(app)
    CORS(app, supports_credentials=True)

    app.config['SESSION_TYPE'] = 'filesystem'
    app.config['SESSION_PERMANENT'] = True
    Session(app)

    with app.app_context():
        # Import routes
        from api.api_main import app

    return app
