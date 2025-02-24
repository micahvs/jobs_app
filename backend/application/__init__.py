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
    migrate.init_app(app, db)
    jwt.init_app(app)
    
    # Configure CORS
    CORS(app, resources={r"/*": {"origins": "*"}})
    
    # Register blueprints
    from application.routes.auth import bp as auth_bp
    from application.routes.jobs import bp as jobs_bp
    from application.routes.swipes import bp as swipes_bp
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(jobs_bp)
    app.register_blueprint(swipes_bp)
    
    @app.route('/health')
    def health_check():
        return {'status': 'healthy'}
    
    return app