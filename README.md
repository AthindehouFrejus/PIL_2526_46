# Mentorat IFRI

Application web de mise en relation entre mentors et mentorés pour l'IFRI.

## Fonctionnalités
- Inscription et connexion (email/téléphone)
- Profil utilisateur avec photo
- Offres et demandes de mentorat
- Algorithme de matching (compétences, filière, niveau, disponibilités)
- Messagerie instantanée en temps réel
- Réinitialisation de mot de passe par email

## Technologies
- Backend : Python / Flask
- Base de données : PostgreSQL
- Temps réel : SocketIO
- Authentification : JWT

## Installation

1. Cloner le projet
2. Créer un environnement virtuel : `python3 -m venv venv`
3. Activer : `source venv/bin/activate`
4. Installer les dépendances : `pip install -r requirements.txt`
5. Configurer le fichier `.env` (voir `.env.example`)
6. Créer la base PostgreSQL : `createdb mentorat_db`
7. Appliquer les migrations : `flask db upgrade`
8. Lancer : `python app.py`

## Équipe
ATHINDEHOU Oluwa-Tobi Amos Fréjus
KPADONOU Horeb Immaculée La joie
AMEHO Fifamè Grâce
AZONHOUMON Adrien
DAMADO Gloria
OKE Sourou Julie Hilary
HANTO Jordy Mayel
