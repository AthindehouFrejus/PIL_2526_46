from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.mentorship import MentorshipOffer, MentorshipRequest
from extensions import db

mentorship_bp = Blueprint('mentorship', __name__)

# ==================== OFFRES ====================

# Créer une offre de mentorat
@mentorship_bp.route('/offers', methods=['POST'])
@jwt_required()
def create_offer():
    user_id = int(get_jwt_identity())
    data = request.get_json()

    if not data.get('matiere'):
        return jsonify({'error': 'La matière est obligatoire'}), 400

    offer = MentorshipOffer(
        user_id=user_id,
        matiere=data['matiere'],
        description=data.get('description', ''),
        format=data.get('format', 'les_deux'),
        disponibilites=data.get('disponibilites', [])
    )
    db.session.add(offer)
    db.session.commit()

    return jsonify({'message': 'Offre créée', 'id': offer.id}), 201


# Lister toutes les offres (avec filtre optionnel par matière)
@mentorship_bp.route('/offers', methods=['GET'])
def get_offers():
    matiere = request.args.get('matiere')
    query = MentorshipOffer.query
    if matiere:
        query = query.filter(MentorshipOffer.matiere.ilike(f'%{matiere}%'))
    offers = query.order_by(MentorshipOffer.created_at.desc()).all()

    result = []
    for o in offers:
        result.append({
            'id': o.id,
            'user_id': o.user_id,
            'user_name': f"{o.user.first_name} {o.user.last_name}",
            'matiere': o.matiere,
            'description': o.description,
            'format': o.format,
            'disponibilites': o.disponibilites,
            'created_at': o.created_at.isoformat()
        })
    return jsonify(result)


# Voir une offre spécifique
@mentorship_bp.route('/offers/<int:id>', methods=['GET'])
def get_offer(id):
    offer = MentorshipOffer.query.get_or_404(id)
    return jsonify({
        'id': offer.id,
        'user_id': offer.user_id,
        'user_name': f"{offer.user.first_name} {offer.user.last_name}",
        'matiere': offer.matiere,
        'description': offer.description,
        'format': offer.format,
        'disponibilites': offer.disponibilites,
        'created_at': offer.created_at.isoformat()
    })


# Supprimer son offre
@mentorship_bp.route('/offers/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_offer(id):
    user_id = int(get_jwt_identity())
    offer = MentorshipOffer.query.get_or_404(id)
    if offer.user_id != user_id:
        return jsonify({'error': 'Non autorisé'}), 403
    db.session.delete(offer)
    db.session.commit()
    return jsonify({'message': 'Offre supprimée'})


# ==================== DEMANDES ====================

# Créer une demande de mentorat
@mentorship_bp.route('/requests', methods=['POST'])
@jwt_required()
def create_request():
    user_id = int(get_jwt_identity())
    data = request.get_json()

    if not data.get('matiere'):
        return jsonify({'error': 'La matière est obligatoire'}), 400

    req = MentorshipRequest(
        user_id=user_id,
        matiere=data['matiere'],
        description=data.get('description', ''),
        format=data.get('format', 'les_deux'),
        disponibilites=data.get('disponibilites', [])
    )
    db.session.add(req)
    db.session.commit()

    return jsonify({'message': 'Demande créée', 'id': req.id}), 201


# Lister toutes les demandes (avec filtre optionnel par matière)
@mentorship_bp.route('/requests', methods=['GET'])
def get_requests():
    matiere = request.args.get('matiere')
    query = MentorshipRequest.query
    if matiere:
        query = query.filter(MentorshipRequest.matiere.ilike(f'%{matiere}%'))
    requests = query.order_by(MentorshipRequest.created_at.desc()).all()

    result = []
    for r in requests:
        result.append({
            'id': r.id,
            'user_id': r.user_id,
            'user_name': f"{r.user.first_name} {r.user.last_name}",
            'matiere': r.matiere,
            'description': r.description,
            'format': r.format,
            'disponibilites': r.disponibilites,
            'created_at': r.created_at.isoformat()
        })
    return jsonify(result)


# Voir une demande spécifique
@mentorship_bp.route('/requests/<int:id>', methods=['GET'])
def get_request(id):
    req = MentorshipRequest.query.get_or_404(id)
    return jsonify({
        'id': req.id,
        'user_id': req.user_id,
        'user_name': f"{req.user.first_name} {req.user.last_name}",
        'matiere': req.matiere,
        'description': req.description,
        'format': req.format,
        'disponibilites': req.disponibilites,
        'created_at': req.created_at.isoformat()
    })


# Supprimer sa demande
@mentorship_bp.route('/requests/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_request(id):
    user_id = int(get_jwt_identity())
    req = MentorshipRequest.query.get_or_404(id)
    if req.user_id != user_id:
        return jsonify({'error': 'Non autorisé'}), 403
    db.session.delete(req)
    db.session.commit()
    return jsonify({'message': 'Demande supprimée'})

# ==================== REPONDRE A UNE OFFRE OU DEMANDE ====================

@mentorship_bp.route('/respond/<string:type>/<int:id>', methods=['POST'])
@jwt_required()
def respond(type, id):
    user_id = int(get_jwt_identity())

    # Trouver l'offre ou la demande
    if type == 'offer':
        item = MentorshipOffer.query.get_or_404(id)
    elif type == 'request':
        item = MentorshipRequest.query.get_or_404(id)
    else:
        return jsonify({'error': 'Type invalide (offer ou request)'}), 400

    other_id = item.user_id

    # On ne peut pas répondre à soi-même
    if user_id == other_id:
        return jsonify({'error': 'Vous ne pouvez pas repondre a vous-meme'}), 400

    # Vérifier si une conversation existe déjà entre les deux
    from models.user import User
    from models.message import Conversation

    user = User.query.get(user_id)
    for c in user.conversations:
        if other_id in [p.id for p in c.participants]:
            return jsonify({
                'message': 'Conversation deja existante',
                'conversation_id': c.id
            }), 200

    # Créer une nouvelle conversation
    other = User.query.get(other_id)
    conv = Conversation()
    conv.participants.append(user)
    conv.participants.append(other)
    db.session.add(conv)
    db.session.commit()

    return jsonify({
        'message': 'Conversation creee',
        'conversation_id': conv.id,
        'other_user': {
            'id': other.id,
            'name': f"{other.first_name} {other.last_name}"
        }
    }), 201
