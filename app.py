from flask import Flask, render_template, redirect, session, flash
from flask_debugtoolbar import DebugToolbarExtension
from models import Feedback, connect_db, db, User
from sqlalchemy.exc import IntegrityError
from forms import UserLoginForm, UserRegistrationForm, FeedbackForm
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

@app.route('/users/<username>/delete', methods=["POST"])
def delete_user(username):
    """Delete user only if authorized."""
    if 'username' not in session:
        flash("Please log in before deleting your user profile.", "danger")
        return render_template('401.html'), 401

    user = User.query.get_or_404(username)
    session.pop('username')
    
    db.session.delete(user)
    db.session.commit()
    
    flash('Your account has successfully been deleted.', 'success')
    
    return redirect('/')

@app.route('/logout', methods=["POST"])
def logout_user():
    """Logout user."""
    session.pop('username')
    flash("You've been successfully logged out.", "info")
    return redirect('/')

#Routes for feedback

@app.route('/users/<username>/feedback/add', methods=["GET", "POST"])
def show_new_feedback_form(username):
    """Show feedback form and add to feedback to database."""
    if 'username' not in session or username != session['username']:
        flash("Please log in before adding new feedback.", "danger")
        return render_template('401.html'), 401
    
    form = FeedbackForm()
    if form.validate_on_submit():
        title = form.title.data
        content = form.content.data
        
        new_feedback = Feedback(title=title, content=content, username=username)
        db.session.add(new_feedback)
        db.session.commit()
        
        flash('Successfully created new feedback!', 'success')
        return redirect(f'/users/{username}')
    
    return render_template('add_feedback_form.html', form=form)

@app.route('/feedback/<int:feedback_id>/update', methods=["GET", "POST"])
def show_update_feedback_form(feedback_id):
    """Show feedback update form and update feedback in database."""
    feedback = Feedback.query.get_or_404(feedback_id)
    
    if 'username' not in session or feedback.username != session['username']:
        flash("Please log in before editing feedback.", "danger")
        return render_template('401.html'), 401
    
    form = FeedbackForm(obj=feedback)
    if form.validate_on_submit():
        feedback.title = form.title.data
        feedback.content = form.content.data
        
        db.session.add(feedback)
        db.session.commit()
        
        flash(f'Successfully updated {feedback.title}!', 'success')
        return redirect(f'/users/{feedback.username}')
    
    return render_template('update_feedback_form.html', form=form)

@app.route('/feedback/<int:feedback_id>/delete', methods=["POST"])
def delete_feedback(feedback_id):
    """Delete Feedback from database."""
    feedback = Feedback.query.get_or_404(feedback_id)
    
    if 'username' not in session or feedback.username != session['username']:
        flash("Please log in before deleting feedback.", "danger")
        return render_template('401.html'), 401
    
    db.session.delete(feedback)
    db.session.commit()
    
    flash('Successfully deleted feedback!', 'success')
    return redirect(f'/users/{session["username"]}')

#404 error handler
@app.errorhandler(404)
def not_found(e):
  return render_template("404.html")

#401 error handler
@app.errorhandler(401)
def not_found(e):
  return render_template("401.html")