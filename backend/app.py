from flask import Flask, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager, jwt_required, get_jwt_identity
from datetime import timedelta
import os

jwt = JWTManager()

def create_app():
    app = Flask(__name__)
    CORS(app)
    
    # Configuration
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ai_tutor.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['JWT_SECRET_KEY'] = 'your-secret-key-change-in-production'
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=24)
    app.config['UPLOAD_FOLDER'] = 'uploads'
    app.config['MAX_CONTENT_LENGTH'] = 500 * 1024 * 1024  # 500MB max file size
    
    # Create upload folder if it doesn't exist
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    # Initialize extensions
    from models import db
    db.init_app(app)
    jwt.init_app(app)
    
    # JWT error handlers
    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        print(f"Invalid token error: {error}")
        return jsonify({'error': 'Invalid token', 'details': str(error)}), 422
    
    @jwt.unauthorized_loader
    def missing_token_callback(error):
        print(f"Missing token error: {error}")
        return jsonify({'error': 'Missing authorization token', 'details': str(error)}), 401
    
    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        print(f"Expired token - header: {jwt_header}, payload: {jwt_payload}")
        return jsonify({'error': 'Token has expired'}), 401
    
    # Import models to ensure they're registered
    with app.app_context():
        import models
        db.create_all()
        print("✓ Database initialized successfully")
    
    # Register blueprints
    from routes.auth import auth_bp
    from routes.modules import modules_bp
    from routes.lessons import lessons_bp
    from routes.telemetry import telemetry_bp
    
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(modules_bp, url_prefix='/api/modules')
    app.register_blueprint(lessons_bp, url_prefix='/api/lesson')
    app.register_blueprint(telemetry_bp, url_prefix='/api/telemetry')
    
    print("✓ All routes registered successfully")
    
    @app.route('/api/health')
    def health():
        return jsonify({'status': 'ok'})
    
    @app.route('/api/test-auth')
    @jwt_required()
    def test_auth():
        user_id = get_jwt_identity()
        return jsonify({'message': 'Auth works', 'user_id': user_id})
    
    # Add error handler for better debugging
    @app.errorhandler(Exception)
    def handle_error(e):
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500
    
    # Request logging middleware
    @app.before_request
    def log_request():
        from flask import request
        print(f"\n=== {request.method} {request.path} ===")
        if request.headers.get('Authorization'):
            auth_header = request.headers.get('Authorization')
            print(f"Auth header: {auth_header[:50]}...")
        else:
            print("No Authorization header")
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, port=5000)
