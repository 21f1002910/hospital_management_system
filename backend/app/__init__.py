from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_cors import CORS

db = SQLAlchemy()
jwt = JWTManager()

def create_app():
    app = Flask(__name__)
    CORS(app, resources={r"/api/*": {"origins": "http://localhost:5173"}})
    app.config.from_object('config.Config')
    db.init_app(app)
    jwt.init_app(app)
    
    from .models import init_db
    with app.app_context():
        init_db(app)  # Creates tables and admin on app start
    
    # Import routes here later, e.g., from .routes import api_bp; app.register_blueprint(api_bp)
    from .routes import api_bp
    app.register_blueprint(api_bp, url_prefix='/api')


    return app