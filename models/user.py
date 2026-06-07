from extensions import db
from datetime import datetime

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True, nullable=False)
    phone = db.Column(db.String(20), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    first_name = db.Column(db.String(50))
    last_name = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    reset_code = db.Column(db.String(6), nullable=True)
    reset_code_expires = db.Column(db.DateTime, nullable=True)

    profile = db.relationship('Profile', uselist=False, back_populates='user')
    offers = db.relationship('MentorshipOffer', back_populates='user', lazy='dynamic')
    requests = db.relationship('MentorshipRequest', back_populates='user', lazy='dynamic')

    def set_password(self, password):
        from extensions import bcrypt
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')
    
    def check_password(self, password):
        from extensions import bcrypt
        return bcrypt.check_password_hash(self.password_hash, password)
