from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from .config import Config
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Initialize the database
db = SQLAlchemy()


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialize the app with the database
    db.init_app(app)

    from .routes import main
    app.register_blueprint(main)

    # Create database tables
    with app.app_context():
        db.create_all()

    return app
