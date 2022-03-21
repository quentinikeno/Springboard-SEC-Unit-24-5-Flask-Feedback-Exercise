from unittest import TestCase

from app import app
from flask import session
from models import db, User, Feedback

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
        """Add a test user and feedback."""
        
        User.query.delete()
        
        test_user_1 = User.registerUser(username="testUser1", password="password", email="test@email.com", first_name="John", last_name="Smith")
        db.session.add(test_user_1)
        db.session.commit()
        
        self.test_user_1 = test_user_1
        
        feedback = Feedback(title='Test Feedback', content='This is only a test.', username=test_user_1.username)
        db.session.add(feedback)
        db.session.commit()
        
        self.feedback = feedback
        
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
            self.assertIn('<form method="post">', html)
            
    def test_add_user(self):
        """Testing the adding of new user to db. POST request to /register."""
        with app.test_client() as client:
            data = {"username": "testUser2", "password": "123456", "email": "notarealemail@test.com", "first_name": "Jane", "last_name": "Doe"}
            resp = client.post("/register", data=data, follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn(f'<h1 class="card-title display-1">testUser2</h1>', html)
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
            
    def test_login_form(self):
        """Testing the /login route to show the login form."""
        with app.test_client() as client:
            resp = client.get("/login")
            html = resp.get_data(as_text=True)
            
            self.assertEqual(resp.status_code, 200)
            self.assertIn('<h1 class="display-1">Log In</h1>', html)
            self.assertIn('<form method="post">', html)
            
    def test_log_in_user(self):
        """Testing logging in a user."""
        with app.test_client() as client:
            data = {"username": "testUser1", "password": "password"}
            resp = client.post("/login", data=data, follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn(f'<h1 class="card-title display-1">{self.test_user_1.username}</h1>', html)
            self.assertEqual(f'{session.get("username")}', f'{self.test_user_1.username}')
            
    def test_log_in_invalid_username(self):
        """Testing logging in a user with an invalid username."""
        with app.test_client() as client:
            data = {"username": "BobaFett", "password": "password"}
            resp = client.post("/login", data=data, follow_redirects=True)
            html = resp.get_data(as_text=True)
            
            self.assertEqual(resp.status_code, 200)
            self.assertIn('<h1 class="display-1">Log In</h1>', html)
            self.assertIn('Invalid username/password.', html)
            self.assertIsNone(session.get("username"))
            
    def test_log_in_invalid_password(self):
        """Testing logging in a user with an invalid password."""
        with app.test_client() as client:
            data = {"username": "testUser1", "password": "IncorrectPassword123"}
            resp = client.post("/login", data=data, follow_redirects=True)
            html = resp.get_data(as_text=True)
            
            self.assertEqual(resp.status_code, 200)
            self.assertIn('<h1 class="display-1">Log In</h1>', html)
            self.assertIn('Invalid username/password.', html)
            self.assertIsNone(session.get("username"))
            
    def test_log_out(self):
        """Testing logging out a user."""
        with app.test_client() as client:
            data = {"username": "testUser1", "password": "password"}
            client.post("/login", data=data, follow_redirects=True)
            resp = client.post("/logout", follow_redirects=True)
            html = resp.get_data(as_text=True)
            
            self.assertEqual(resp.status_code, 200)
            self.assertIn('<h1 class="display-1">Sign Up</h1>', html)
            self.assertIsNone(session.get("username"))
            
    def test_deleting_user(self):
        """Testing deleting a user."""
        with app.test_client() as client:
            data = {"username": "testUser1", "password": "password"}
            client.post("/login", data=data, follow_redirects=True)
            resp = client.post(f"/users/testUser1/delete", follow_redirects=True)
            html = resp.get_data(as_text=True)
            
            self.assertEqual(resp.status_code, 200)
            self.assertIn('Your account has successfully been deleted.', html)
            self.assertIsNone(session.get("username"))
            
    def test_deleting_user_not_logged_in(self):
        """Testing deleting a user when not logged in.  The user shouldn't be deleted."""
        with app.test_client() as client:
            resp = client.post(f"/users/{self.test_user_1.username}/delete", follow_redirects=True)
            html = resp.get_data(as_text=True)
            
            self.assertEqual(resp.status_code, 401)
            self.assertIn("<h1>You aren't authorized to do that.</h1>", html)
            
class FeedbackViewsTestCase(TestCase):
    """Test views for Feedback"""
    
    def setUp(self):
        """Add a test user and feedback."""
        
        User.query.delete()
        
        test_user_1 = User.registerUser(username="testUser1", password="password", email="test@email.com", first_name="John", last_name="Smith")
        db.session.add(test_user_1)
        db.session.commit()
        
        self.test_user_1 = test_user_1
        
        feedback = Feedback(title='Test Feedback', content='This is only a test.', username=test_user_1.username)
        db.session.add(feedback)
        db.session.commit()
        
        self.feedback = feedback
        self.feedback_id = feedback.id
        
    def tearDown(self):
        """Clean up any fouled transaction."""

        db.session.rollback()
        
    def test_show_feedback_form(self):
        """Testing showing the new feedback form."""
        with app.test_client() as client:
            data = {"username": "testUser1", "password": "password"}
            client.post("/login", data=data, follow_redirects=True)
            resp = client.get("/users/testUser1/feedback/add")
            html = resp.get_data(as_text=True)
            
            self.assertEqual(resp.status_code, 200)
            self.assertIn('<h1 class="display-1">Add New Feedback for testUser1</h1>', html)
            
    def test_adding_feedback(self):
        """Testing adding new feedback to database."""
        with app.test_client() as client:
            data = {"username": "testUser1", "password": "password"}
            client.post("/login", data=data, follow_redirects=True)
            feedback = {"title": "Adding new Feeback", "content": "This is to test adding new feedback."}
            resp = client.post("/users/testUser1/feedback/add", data=feedback, follow_redirects=True)
            html = resp.get_data(as_text=True)
            
            self.assertEqual(resp.status_code, 200)
            self.assertIn('Successfully created new feedback!', html)
            self.assertIn('<h5 class="card-subtitle">Adding new Feeback</h5>', html)
            
    def test_adding_feedback_not_logged_in(self):
        """Testing adding new feedback when not logged in.  Should result in a 401."""
        with app.test_client() as client:
            feedback = {"title": "Adding new Feeback", "content": "This is to test adding new feedback."}
            resp = client.post("/users/testUser1/feedback/add", data=feedback, follow_redirects=True)
            html = resp.get_data(as_text=True)
            
            self.assertEqual(resp.status_code, 401)
            self.assertIn('Please log in before adding new feedback.', html)
            
    def test_show_update_feedback_form(self):
        """Testing showing the new feedback form."""
        with app.test_client() as client:
            data = {"username": "testUser1", "password": "password"}
            client.post("/login", data=data, follow_redirects=True)
            resp = client.get(f"feedback/{self.feedback_id}/update")
            html = resp.get_data(as_text=True)
            
            self.assertEqual(resp.status_code, 200)
            self.assertIn('<h1 class="display-1">Update Feedback</h1>', html)
            
    def test_updating_feedback(self):
        """Testing updating new feedback to database."""
        with app.test_client() as client:
            data = {"username": "testUser1", "password": "password"}
            client.post("/login", data=data, follow_redirects=True)
            feedback = {"title": "Updating Feedback", "content": "This is to test updating feedback."}
            resp = client.post(f"feedback/{self.feedback_id}/update", data=feedback, follow_redirects=True)
            html = resp.get_data(as_text=True)
            
            self.assertEqual(resp.status_code, 200)
            self.assertIn(f'Successfully updated {feedback.get("title")}!', html)
            self.assertIn('<h5 class="card-subtitle">Updating Feedback</h5>', html)
            
    def test_deleting_feedback(self):
        """Testing deleting feedback."""
        with app.test_client() as client:
            data = {"username": "testUser1", "password": "password"}
            client.post("/login", data=data, follow_redirects=True)
            resp = client.post(f"feedback/{self.feedback_id}/delete", follow_redirects=True)
            html = resp.get_data(as_text=True)
            
            self.assertEqual(resp.status_code, 200)
            self.assertIn('Successfully deleted feedback!', html)
            self.assertNotIn('<h5 class="card-subtitle">Test Feedback</h5>', html)