from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from . import db

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, password: str) -> None:
        """
        Hashes the given plaintext password and stores it.
        """
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        """
        Verifies a plaintext password against the stored hash.
        """
        return check_password_hash(self.password_hash, password)

    def to_dict(self) -> dict:
        """
        Returns a dictionary representation of the user (excluding sensitive data).
        """
        return {
            'id': self.id,
            'email': self.email,
            'created_at': self.created_at.isoformat()
        }
