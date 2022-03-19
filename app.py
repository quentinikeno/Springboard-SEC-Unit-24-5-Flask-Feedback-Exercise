from flask import Flask, render_template, redirect, session, flash
from flask_debugtoolbar import DebugToolbarExtension
from models import connect_db, db, User
from sqlalchemy.exc import IntegrityError
from crypt import methods
from forms import UserRegistrationForm
from secret_keys import app_secret_key

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql:///flask_feedback"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ECHO"] = True
app.config["SECRET_KEY"] = app_secret_key
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False


connect_db(app)

toolbar = DebugToolbarExtension(app)

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
        new_user = User.register(username, password, email, first_name, last_name)
        db.session.add(new_user)
         
        try:
            db.session.commit()
        except IntegrityError:
            # If there's an error adding username to db, show error and render register
            form.username.errors.append('The username is already taken.  Please choose another.')
            return render_template('register.html', form=form)
        
        session['username'] = new_user.username
        
        flash(f'Thanks for joining {new_user.username}!  Your account has successfully been created!')
        return redirect('/secrets')
    
    return render_template('register.html', form=form)

@app.route('/secrets')
def show_secrets_page():
    """Show secret page if authorized."""
    if 'username' not in session:
        # If the user is not logged in/username not in session redirect to /register
        flash("Please register or login first!", "danger")
        return redirect('/register')

    return render_template('secrets.html')