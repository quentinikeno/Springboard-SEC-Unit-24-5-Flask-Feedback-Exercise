from unittest import TestCase

from app import app
from flask import session
from models import db, User

# Use test database and don't clutter tests with SQL
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///flask_feedback_test_db'
app.config['SQLALCHEMY_ECHO'] = False
app.config['TESTING'] = True
app.config['DEBUG_TB_HOSTS'] = ['dont-show-debug-toolbar']
app.config['WTF_CSRF_ENABLED'] = False

db.drop_all()
db.create_all()

class UserViewsTestCase(TestCase):
    """Test views for Users"""
    
    def setUp(self):
        """Add a test user."""
        
        User.query.delete()
        
        test_user_1 = User(username="testUser1", password="password", email="test@email.com", first_name="John", last_name="Smith")
        db.session.add(test_user_1)
        db.session.commit()
        
        self.test_user_1 = test_user_1
        
    def tearDown(self):
        """Clean up any fouled transaction."""

        db.session.rollback()
        
    def test_route_route(self):
        """Testing the route route redirects to register page."""
        with app.test_client() as client:
            resp = client.get("/", follow_redirects=True)
            html = resp.get_data(as_text=True)
            
            self.assertEqual(resp.status_code, 200)
            self.assertIn('<h1 class="display-1">Sign Up</h1>', html)
            
    def test_register_form(self):
        """Testing the /register route to show the sign up form."""
        with app.test_client() as client:
            resp = client.get("/register")
            html = resp.get_data(as_text=True)
            
            self.assertEqual(resp.status_code, 200)
            self.assertIn('<h1 class="display-1">Sign Up</h1>', html)
            
    def test_add_user(self):
        """Testing the adding of new user to db. POST request to /register."""
        with app.test_client() as client:
            data = {"username": "testUser2", "password": "123456", "email": "notarealemail@test.com", "first_name": "Jane", "last_name": "Doe"}
            resp = client.post("/register", data=data, follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('<h1 class="display-1">You made it!</h1>', html)
            self.assertEqual(f'{User.query.get("testUser2")}', "<User username=testUser2>")
            self.assertEqual(f'{session["username"]}', 'testUser2')
            
    def test_add_user_with_duplicate_username(self):
        """Testing the adding of new user with a user_name that is already take.  Should show error and redirect back to /register. POST request to /register."""
        with app.test_client() as client:
            data = {"username": "testUser1", "password": "123456", "email": "notarealemail@test.com", "first_name": "Jane", "last_name": "Doe"}
            resp = client.post("/register", data=data, follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('<h1 class="display-1">Sign Up</h1>', html)
            self.assertIn('The username is already taken.  Please choose another.', html)
            self.assertIsNone(session.get("username"))