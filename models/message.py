from extensions import db
from datetime import datetime

class Conversation(db.Model):
    __tablename__ = 'conversations'
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    participants = db.relationship('User', secondary='conversation_participants', backref='conversations')

class ConversationParticipants(db.Model):
    __tablename__ = 'conversation_participants'
    conversation_id = db.Column(db.Integer, db.ForeignKey('conversations.id'), primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)

class Message(db.Model):
    __tablename__ = 'messages'
    id = db.Column(db.Integer, primary_key=True)
    conversation_id = db.Column(db.Integer, db.ForeignKey('conversations.id'))
    sender_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    content = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    sender = db.relationship('User', backref='messages')
