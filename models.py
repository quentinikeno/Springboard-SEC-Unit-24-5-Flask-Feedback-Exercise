from enum import unique
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt

db = SQLAlchemy()

bcrypt = Bcrypt()


def connect_db(app):
    """Connect to database."""

    db.app = app
    db.init_app(app)

class User(db.Model):
    
    __tablename__ = "users"
    
    username = db.Column(db.String(20), primary_key=True, autoincrement=True)

    password = db.Column(db.Text, nullable=False)
    
    email = db.Column(db.String(50), nullable=False, unique=True)
    
    first_name = db.Column(db.String(30), nullable=False)
    
    last_name = db.Column(db.String(30), nullable=False)
    
    def __repr__(self):
        """Representation of User."""
        return f"<User username={self.username}>"
    
    @classmethod
    def registerUser(cls, username, password, email, first_name, last_name):
        """Hash password and create user."""
        # hash password
        hashed = bcrypt.generate_password_hash(password)
        # turn bytestring into normal (unicode utf8) string
        hashed_utf8 = hashed.decode("utf8")
        return cls(username=username, password=hashed_utf8, email=email, first_name=first_name, last_name=last_name)