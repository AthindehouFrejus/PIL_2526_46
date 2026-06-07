from flask import Blueprint, request, jsonify
from models.user import User
from models.profile import Profile
from extensions import db, mail
from flask_jwt_extended import create_access_token
import random
import string
from datetime import datetime, timedelta
from flask_mail import Message

auth_bp = Blueprint('auth', __name__)


# ==================== INSCRIPTION ====================
@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    if not all(k in data for k in ('email', 'phone', 'password', 'first_name', 'last_name')):
        return jsonify({'error': 'Champs obligatoires manquants'}), 400
    if User.query.filter((User.email == data['email']) | (User.phone == data['phone'])).first():
        return jsonify({'error': 'Email ou telephone deja utilise'}), 409
    user = User(email=data['email'], phone=data['phone'], first_name=data['first_name'], last_name=data['last_name'])
    user.set_password(data['password'])
    db.session.add(user)
    db.session.commit()
    profile = Profile(user_id=user.id, competences=data.get('competences', []), lacunes=data.get('lacunes', []))
    db.session.add(profile)
    db.session.commit()
    return jsonify({'message': 'Inscription reussie', 'user_id': user.id}), 201


# ==================== CONNEXION ====================
@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    identifier = data.get('identifier')
    password = data.get('password')
    user = User.query.filter((User.email == identifier) | (User.phone == identifier)).first()
    if not user or not user.check_password(password):
        return jsonify({'error': 'Identifiants incorrects'}), 401
    access_token = create_access_token(identity=str(user.id))
    return jsonify({'token': access_token, 'user_id': user.id}), 200


# ==================== MOT DE PASSE OUBLIE ====================
@auth_bp.route('/forgot-password', methods=['POST'])
def forgot_password():
    data = request.get_json()
    email = data.get('email')

    if not email:
        return jsonify({'error': 'Email requis'}), 400

    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({'message': 'Si cet email existe, un code a ete envoye'}), 200

    code = ''.join(random.choices(string.digits, k=6))
    user.reset_code = code
    user.reset_code_expires = datetime.utcnow() + timedelta(minutes=15)
    db.session.commit()

    # Envoyer l'email
    try:
        msg = Message(
            'Reinitialisation de mot de passe - Mentorat IFRI',
            sender=('Mentorat IFRI', 'gyuhorahugues@gmail.com'),
            recipients=[email]
        )
        msg.body = f"""Bonjour {user.first_name},

Vous avez demande la reinitialisation de votre mot de passe.

Votre code de reinitialisation : {code}

Ce code expire dans 15 minutes.

Si vous n'avez pas demande cette reinitialisation, ignorez cet email.
"""
        mail.send(msg)
        print(f"\n=== Email envoye a {email} ===\n")
    except Exception as e:
        print(f"\n=== Erreur email: {e} ===\n")

    return jsonify({'message': 'Si cet email existe, un code a ete envoye'}), 200


# ==================== VERIFIER LE CODE ====================
@auth_bp.route('/verify-code', methods=['POST'])
def verify_code():
    data = request.get_json()
    email = data.get('email')
    code = data.get('code')
    if not email or not code:
        return jsonify({'error': 'Email et code requis'}), 400
    user = User.query.filter_by(email=email).first()
    if not user or user.reset_code != code:
        return jsonify({'error': 'Code invalide'}), 400
    if datetime.utcnow() > user.reset_code_expires:
        return jsonify({'error': 'Code expire'}), 400
    return jsonify({'message': 'Code valide'}), 200


# ==================== REINITIALISER LE MOT DE PASSE ====================
@auth_bp.route('/reset-password', methods=['POST'])
def reset_password():
    data = request.get_json()
    email = data.get('email')
    code = data.get('code')
    new_password = data.get('new_password')
    if not email or not code or not new_password:
        return jsonify({'error': 'Email, code et nouveau mot de passe requis'}), 400
    user = User.query.filter_by(email=email).first()
    if not user or user.reset_code != code:
        return jsonify({'error': 'Code invalide'}), 400
    if datetime.utcnow() > user.reset_code_expires:
        return jsonify({'error': 'Code expire'}), 400
    user.set_password(new_password)
    user.reset_code = None
    user.reset_code_expires = None
    db.session.commit()
    return jsonify({'message': 'Mot de passe reinitialise avec succes'}), 200
