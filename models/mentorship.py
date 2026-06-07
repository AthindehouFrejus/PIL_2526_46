from extensions import db
from datetime import datetime

class MentorshipOffer(db.Model):
    __tablename__ = 'mentorship_offers'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    matiere = db.Column(db.String(100))
    description = db.Column(db.Text)
    format = db.Column(db.String(20))  # presentiel, en ligne, les_deux
    disponibilites = db.Column(db.JSON)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user = db.relationship('User', back_populates='offers')

class MentorshipRequest(db.Model):
    __tablename__ = 'mentorship_requests'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    matiere = db.Column(db.String(100))
    description = db.Column(db.Text)
    format = db.Column(db.String(20))
    disponibilites = db.Column(db.JSON)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user = db.relationship('User', back_populates='requests')
