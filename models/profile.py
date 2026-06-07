from extensions import db

class Profile(db.Model):
    __tablename__ = 'profiles'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), unique=True)
    photo_url = db.Column(db.String(255), nullable=True)
    filiere = db.Column(db.String(100))
    niveau = db.Column(db.String(50))
    competences = db.Column(db.JSON, default=[])
    lacunes = db.Column(db.JSON, default=[])
    disponibilites = db.Column(db.JSON, default=[])
    bio = db.Column(db.Text)

    user = db.relationship('User', back_populates='profile')
