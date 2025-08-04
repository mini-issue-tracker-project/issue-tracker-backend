from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from .config import Config
from flask_cors import CORS
from flask_migrate import Migrate
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager
# Initialize the database
db = SQLAlchemy()
migrate = Migrate()
bcrypt = Bcrypt()
jwt = JWTManager()

from . import models

def create_app():
    
    app = Flask(__name__)
    app.config.from_object(Config)
    # Optionally configure JWT token options here
    # Enable CORS with configurable origins
    CORS(app, origins=app.config['ALLOWED_ORIGINS'], supports_credentials=True)

    # Initialize the app with the database
    db.init_app(app)
    migrate.init_app(app, db)
    bcrypt.init_app(app)
    jwt.init_app(app)
    from .routes import main
    app.register_blueprint(main)

    return app
