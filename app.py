from flask import Flask, render_template, redirect, session, flash
from flask_debugtoolbar import DebugToolbarExtension
from models import connect_db, db, User
from sqlalchemy.exc import IntegrityError
from crypt import methods
from forms import UserLoginForm, UserRegistrationForm
from secret_keys import app_secret_key

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql:///flask_feedback"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ECHO"] = True
app.config["SECRET_KEY"] = app_secret_key
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False


connect_db(app)

toolbar = DebugToolbarExtension(app)

#Routes for users

@app.route('/')
def index():
    """Redirect to /register."""
    return redirect("/register")

@app.route("/register", methods=["GET", "POST"])
def register_user():
    """Show form to register users and add them to the database."""
    form = UserRegistrationForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        email = form.email.data
        first_name = form.first_name.data
        last_name = form.last_name.data
         
         # User register class method to hash password and create new user model instance
        new_user = User.registerUser(username, password, email, first_name, last_name)
        db.session.add(new_user)
         
        try:
            db.session.commit()
            session['username'] = new_user.username
            flash(f'Thanks for joining {new_user.username}!  Your account has successfully been created!', 'success')
            return redirect(f'/users/{new_user.username}')
        except IntegrityError:
            # If there's an error adding username to db, show error and render register
            form.username.errors.append('The username is already taken.  Please choose another.')
            return render_template('register.html', form=form)

    return render_template('register.html', form=form)

@app.route('/login', methods=["GET", "POST"])
def login_user():
    """Show form to login users and add their username to the session."""
    form = UserLoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data

        user = User.authenticate(username, password)
        if user:
            flash(f"Welcome Back, {user.username}! You've been successfully logged in.", "success")
            session['username'] = user.username
            return redirect(f'/users/{user.username}')
        else:
            form.username.errors = ['Invalid username/password.']
            
    return render_template('login.html', form=form)

@app.route('/users/<username>')
def show_secrets_page(username):
    """Show secret page if authorized."""
    if 'username' not in session:
        # If the user is not logged in/username not in session redirect to /register
        flash("Please register or login first!", "danger")
        return redirect('/register')

    user = User.query.get_or_404(username)
    
    return render_template('user_detail.html', user=user, feedback=user.feedback)

@app.route('/logout', methods=["POST"])
def logout_user():
    """Logout user."""
    session.pop('username')
    flash("You've been successfully logged out.", "info")
    return redirect('/')

#Routes for feedback

