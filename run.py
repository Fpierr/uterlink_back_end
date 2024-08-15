#!/usr/bin/python3
"""The main file to run app"""

import sys
import os

# Add the parent directory to the Python search path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))


from api import create_app

app = create_app()

if __name__ == '__main__':
    if os.getenv('RUN_APP_ENV') == 'production':
        from waitress import serve
        serve(app, host=os.getenv("RUN_HOST"), port=os.getenv("RUN_PORT"))
    else:
        app.run()