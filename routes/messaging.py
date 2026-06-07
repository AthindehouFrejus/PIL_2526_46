from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.message import Conversation, ConversationParticipants, Message
from models.user import User
from extensions import db, socketio
from flask_socketio import emit, join_room, leave_room

messaging_bp = Blueprint('messaging', __name__)

# ==================== HTTP : Conversations ====================

# Récupérer toutes les conversations de l'utilisateur connecté
@messaging_bp.route('/conversations', methods=['GET'])
@jwt_required()
def get_conversations():
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({'error': 'Utilisateur non trouvé'}), 404

    convs = user.conversations
    result = []
    for c in convs:
        # Trouver l'autre participant
        other = None
        for p in c.participants:
            if p.id != user_id:
                other = p
                break
        
        # Dernier message
        last_msg = Message.query.filter_by(conversation_id=c.id)\
            .order_by(Message.timestamp.desc()).first()
        
        result.append({
            'id': c.id,
            'other_user': {
                'id': other.id,
                'name': f"{other.first_name} {other.last_name}"
            },
            'last_message': {
                'content': last_msg.content,
                'timestamp': last_msg.timestamp.isoformat()
            } if last_msg else None
        })
    
    return jsonify(result)


# Récupérer les messages d'une conversation
@messaging_bp.route('/conversations/<int:conv_id>/messages', methods=['GET'])
@jwt_required()
def get_messages(conv_id):
    user_id = int(get_jwt_identity())
    conv = Conversation.query.get_or_404(conv_id)
    
    # Vérifier que l'utilisateur fait partie de la conversation
    if user_id not in [p.id for p in conv.participants]:
        return jsonify({'error': 'Accès non autorisé'}), 403

    messages = Message.query.filter_by(conversation_id=conv_id)\
        .order_by(Message.timestamp.asc()).all()

    return jsonify([{
        'id': m.id,
        'sender_id': m.sender_id,
        'content': m.content,
        'timestamp': m.timestamp.isoformat()
    } for m in messages])


# Créer une conversation avec un autre utilisateur
@messaging_bp.route('/conversations', methods=['POST'])
@jwt_required()
def create_conversation():
    user_id = int(get_jwt_identity())
    data = request.get_json()
    other_id = data.get('user_id')

    if not other_id:
        return jsonify({'error': 'user_id requis'}), 400

    # Vérifier que l'autre utilisateur existe
    other = User.query.get(other_id)
    if not other:
        return jsonify({'error': 'Utilisateur non trouvé'}), 404

    # Vérifier si une conversation existe déjà entre les deux
    user = User.query.get(user_id)
    for c in user.conversations:
        if other_id in [p.id for p in c.participants]:
            return jsonify({'message': 'Conversation existante', 'conversation_id': c.id}), 200

    # Créer une nouvelle conversation
    conv = Conversation()
    conv.participants.append(user)
    conv.participants.append(other)
    db.session.add(conv)
    db.session.commit()

    return jsonify({'message': 'Conversation créée', 'conversation_id': conv.id}), 201


# ==================== SOCKETIO : Temps réel ====================

# Quand un utilisateur se connecte au WebSocket
@socketio.on('connect')
def handle_connect():
    print('Un utilisateur est connecté')


# Quand un utilisateur rejoint une conversation
@socketio.on('join')
def handle_join(data):
    conversation_id = data.get('conversation_id')
    if conversation_id:
        join_room(str(conversation_id))
        print(f'Utilisateur a rejoint la conversation {conversation_id}')


# Quand un utilisateur quitte une conversation
@socketio.on('leave')
def handle_leave(data):
    conversation_id = data.get('conversation_id')
    if conversation_id:
        leave_room(str(conversation_id))


# Quand un utilisateur envoie un message
@socketio.on('send_message')
def handle_send_message(data):
    user_id = data.get('user_id')
    conversation_id = data.get('conversation_id')
    content = data.get('content')

    if not all([user_id, conversation_id, content]):
        return

    # Sauvegarder dans la base de données
    message = Message(
        conversation_id=conversation_id,
        sender_id=user_id,
        content=content
    )
    db.session.add(message)
    db.session.commit()

    # Envoyer le message à tous dans la conversation
    emit('new_message', {
        'id': message.id,
        'sender_id': user_id,
        'content': content,
        'timestamp': message.timestamp.isoformat()
    }, room=str(conversation_id))
