from flask import Flask
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    app.config.from_object('config.Config')
    db.init_app(app)
    
    from .models import init_db
    with app.app_context():
        init_db(app)  # Creates tables and admin on app start
    
    # Import routes here later, e.g., from .routes import api_bp; app.register_blueprint(api_bp)
    
    return app