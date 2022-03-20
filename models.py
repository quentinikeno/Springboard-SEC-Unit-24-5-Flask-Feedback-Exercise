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
    
    username = db.Column(db.String(20), primary_key=True)

    password = db.Column(db.Text, nullable=False)
    
    email = db.Column(db.String(50), nullable=False, unique=True)
    
    first_name = db.Column(db.String(30), nullable=False)
    
    last_name = db.Column(db.String(30), nullable=False)
    
    def __repr__(self):
        """Representation of User."""
        return f"<User username={self.username}>"
    
    @property
    def first_and_last_name(self):
        """Return a user's first and last name."""
        return f"{self.first_name} {self.last_name}"
    
    @classmethod
    def registerUser(cls, username, password, email, first_name, last_name):
        """Hash password and create user."""
        # hash password
        hashed = bcrypt.generate_password_hash(password)
        # turn bytestring into normal (unicode utf8) string
        hashed_utf8 = hashed.decode("utf8")
        return cls(username=username, password=hashed_utf8, email=email, first_name=first_name, last_name=last_name)
    
    @classmethod
    def authenticate(cls, username, password):
        """Validate that user exists & password is correct.

        Return user if valid; else return False.
        """
        user = User.query.filter_by(username=username).first()
        
        if user and bcrypt.check_password_hash(user.password, password):
            return user
        else:
            return False
        
class Feedback(db.Model):
    
    __tablename__ = "feedback"
    
    id = db.Column(db.Integer, primary_key=True, autoincrement = True)
    
    title = db.Column(db.String(100), nullable=False)
    
    content = db.Column(db.Text, nullable=False)
    
    username = db.Column(db.String(20), db.ForeignKey("users.username"))
    
    user = db.relationship("User", backref="feedback", cascade="all, delete-orphan")
    
    def __repr__(self):
        """Representation of Feedback."""
        return f"<Feedback id={self.id} title={self.title} content={self.content} username={self.username}>"