from flask import Blueprint, request, jsonify, send_from_directory
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.user import User
from models.profile import Profile
from extensions import db
import os
import uuid

profile_bp = Blueprint('profile', __name__)

UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# ==================== VOIR SON PROFIL ====================
@profile_bp.route('', methods=['GET'])
@jwt_required()
def get_profile():
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)
    profile = Profile.query.filter_by(user_id=user_id).first()
    if not profile:
        return jsonify({'error': 'Profil non trouve'}), 404
    return jsonify({
        'first_name': user.first_name,
        'last_name': user.last_name,
        'email': user.email,
        'phone': user.phone,
        'photo_url': profile.photo_url,
        'filiere': profile.filiere,
        'niveau': profile.niveau,
        'competences': profile.competences,
        'lacunes': profile.lacunes,
        'disponibilites': profile.disponibilites,
        'bio': profile.bio
    })


# ==================== MODIFIER SON PROFIL ====================
@profile_bp.route('', methods=['PUT'])
@jwt_required()
def update_profile():
    user_id = int(get_jwt_identity())
    profile = Profile.query.filter_by(user_id=user_id).first()
    if not profile:
        return jsonify({'error': 'Profil inexistant'}), 404

    data = request.get_json()
    for field in ['photo_url', 'filiere', 'niveau', 'competences', 'lacunes', 'disponibilites', 'bio']:
        if field in data:
            setattr(profile, field, data[field])
    db.session.commit()
    return jsonify({'message': 'Profil mis a jour'})


# ==================== UPLOAD PHOTO ====================
@profile_bp.route('/photo', methods=['POST'])
@jwt_required()
def upload_photo():
    user_id = int(get_jwt_identity())
    profile = Profile.query.filter_by(user_id=user_id).first()
    if not profile:
        return jsonify({'error': 'Profil inexistant'}), 404

    if 'photo' not in request.files:
        return jsonify({'error': 'Aucun fichier'}), 400

    file = request.files['photo']
    if file.filename == '':
        return jsonify({'error': 'Fichier vide'}), 400

    if not allowed_file(file.filename):
        return jsonify({'error': 'Format non autorise (png, jpg, jpeg, gif)'}), 400

    # Supprimer l'ancienne photo si elle existe
    if profile.photo_url:
        old_path = os.path.join(UPLOAD_FOLDER, os.path.basename(profile.photo_url))
        if os.path.exists(old_path):
            os.remove(old_path)

    # Générer un nom unique
    ext = file.filename.rsplit('.', 1)[1].lower()
    filename = f"{uuid.uuid4().hex}.{ext}"
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    file.save(filepath)

    # Mettre à jour le profil
    profile.photo_url = f"/static/uploads/{filename}"
    db.session.commit()

    return jsonify({'message': 'Photo telechargee', 'photo_url': profile.photo_url}), 200


# ==================== VOIR LE PROFIL DE QUELQU'UN ====================
@profile_bp.route('/<int:user_id>', methods=['GET'])
@jwt_required()
def get_user_profile(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'Utilisateur non trouve'}), 404
    profile = Profile.query.filter_by(user_id=user_id).first()
    return jsonify({
        'first_name': user.first_name,
        'last_name': user.last_name,
        'photo_url': profile.photo_url if profile else None,
        'filiere': profile.filiere if profile else None,
        'niveau': profile.niveau if profile else None,
        'competences': profile.competences if profile else [],
        'lacunes': profile.lacunes if profile else [],
        'bio': profile.bio if profile else ''
    })
