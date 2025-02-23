from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from config import Config

db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app)
    jwt.init_app(app)
    
    # Very permissive CORS - for debugging only
    CORS(app, resources={
        r"/*": {
            "origins": "*",
            "methods": ["*"],
            "allow_headers": ["*"]
        }
    })
    
    @app.route('/test', methods=['GET'])
    def test():
        return {'message': 'test'}
    
    @app.route('/health')
    def health_check():
        return {'status': 'healthy'}
    
    return app