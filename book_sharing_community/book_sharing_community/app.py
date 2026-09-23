import os
from datetime import datetime
from flask import Flask
from flask_login import LoginManager, current_user
from config import Config
from models import db, User, BorrowRequest
from routes.auth import auth_bp
from routes.books import books_bp
from routes.requests import requests_bp
from routes.main import main_bp

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize extensions
    db.init_app(app)

    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.login_message_category = 'info'

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Register blueprints
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(books_bp)
    app.register_blueprint(requests_bp)

    # Context processor to make badge counts & global variables available in all templates
    @app.context_processor
    def inject_global_vars():
        pending_incoming_count = 0
        if current_user.is_authenticated:
            pending_incoming_count = BorrowRequest.query.filter_by(
                owner_id=current_user.id,
                status='Pending'
            ).count()
        return {
            'now': datetime.utcnow(),
            'pending_incoming_count': pending_incoming_count
        }

    # Ensure tables exist
    with app.app_context():
        db.create_all()

    return app

app = create_app()

if __name__ == '__main__':
    print("=" * 60)
    print("[BOOKSHARE] Book Sharing Community Application Starting...")
    print("   Open your browser at: http://127.0.0.1:5000")
    print("=" * 60)
    app.run(debug=True, host='127.0.0.1', port=5000)
