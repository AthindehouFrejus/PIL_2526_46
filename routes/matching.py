from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.profile import Profile
from services.matching import calculer_score

matching_bp = Blueprint('matching', __name__)

@matching_bp.route('/suggestions', methods=['GET'])
@jwt_required()
def suggestions():
    user_id = int(get_jwt_identity())
    my_profile = Profile.query.filter_by(user_id=user_id).first_or_404()
    all_profiles = Profile.query.filter(Profile.user_id != user_id).all()

    result = []
    for other in all_profiles:
        s = calculer_score(my_profile, other)
        if s > 0:
            result.append({
                'user_id': other.user_id,
                'name': f"{other.user.first_name} {other.user.last_name}",
                'photo_url': other.photo_url,
                'competences_communes': list(set(my_profile.lacunes or []) & set(other.competences or [])),
                'score': s
            })
    result.sort(key=lambda x: x['score'], reverse=True)
    return jsonify(result[:20])
