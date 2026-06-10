from dotenv import load_dotenv
import os
load_dotenv()

from flask import Flask, send_from_directory
from config import Config
from extensions import db, migrate, bcrypt, jwt, socketio, cors, mail

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialiser les extensions
    db.init_app(app)
    migrate.init_app(app, db)
    bcrypt.init_app(app)
    jwt.init_app(app)
    cors.init_app(app)
    socketio.init_app(app)
    mail.init_app(app)

    # Importer les modèles pour Flask-Migrate
    from models.user import User
    from models.profile import Profile
    from models.mentorship import MentorshipOffer, MentorshipRequest
    from models.message import Conversation, Message, ConversationParticipants

    # Importer et enregistrer les blueprints
    from routes.auth import auth_bp
    from routes.profile import profile_bp
    from routes.mentorship import mentorship_bp
    from routes.matching import matching_bp
    from routes.messaging import messaging_bp

    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(profile_bp, url_prefix='/api/profile')
    app.register_blueprint(mentorship_bp, url_prefix='/api/mentorship')
    app.register_blueprint(matching_bp, url_prefix='/api/matching')
    app.register_blueprint(messaging_bp, url_prefix='/api/messages')

    # Route d'accueil
    @app.route('/')
    def home():
        return {'message': 'API Mentorat IFRI en ligne !'}

    # Routes pour les pages HTML
    @app.route('/login')
    def login_page():
        return send_from_directory('static', 'login.html')

    @app.route('/register')
    def register_page():
        return send_from_directory('static', 'register.html')

    @app.route('/chat')
    def chat_test():
        return send_from_directory('static', 'chat.html')

    @app.route('/static/<path:filename>')
    def static_files(filename):
        return send_from_directory('static', filename)
    
    @app.route('/profile')
    def profile_page():
        return send_from_directory('static', 'profile.html')
    @app.route('/dashboard')
    def dashboard_page():
        return send_from_directory('static', 'dashboard.html')
    
        return app

if __name__ == '__main__':
    app = create_app()
    port = int(os.environ.get('PORT', 5000))
    socketio.run(app, debug=False, host='0.0.0.0', port=port)
