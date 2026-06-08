from dotenv import load_dotenv
import os
load_dotenv()

print("===== DATABASE_URL:", os.getenv('DATABASE_URL', 'PAS TROUVE')) 

from flask import send_from_directory
from flask import Flask
from config import Config
from extensions import db, migrate, bcrypt, jwt, socketio, cors, mail
import os

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Charger les variables d'environnement depuis .env
    from dotenv import load_dotenv
    load_dotenv()

    # Initialiser les extensions
    db.init_app(app)
    migrate.init_app(app, db)
    bcrypt.init_app(app)
    jwt.init_app(app)
    cors.init_app(app)
    socketio.init_app(app)
    mail.init_app(app)

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
    @app.route('/login')
    def login_page():
        return send_from_directory('static', 'login.html')
    @app.route('/chat')
    def chat_test():
        return send_from_directory('static', 'chat.html')

    def home():
        return {'message': 'API Mentorat en ligne !'}

    return app

if __name__ == '__main__':
    app = create_app()
    import os
    port = int(os.environ.get('PORT', 5000))
    socketio.run(app, debug=False, host='0.0.0.0', port=port)
