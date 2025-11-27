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

    from .routes import register_routes
    register_routes(app)
     
    with app.app_context():
        from .models import init_db
        init_db(app) 

    return app