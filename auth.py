from flask import Blueprint, render_template, redirect, request, url_for, flash, session, make_response
from flask_login import login_user, logout_user, login_required, current_user
from models import db, User

auth_bp = Blueprint('auth', __name__)

# User Registration
@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        phone_number = request.form['phone_number']

        # Check if user already exists
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash('Email already registered. Please log in.', 'danger')
            return redirect(url_for('auth.login'))

        # Create new user
        new_user = User(name=name, email=email, phone_number=phone_number)
        new_user.set_password(password)

        db.session.add(new_user)
        db.session.commit()
        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('register.html')

# User Login
@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        user = User.query.filter_by(email=email).first()
        if not user:
            flash('User not found!', 'danger')
            return render_template('register.html')
        if user and user.check_password(password):
            login_user(user)
            flash('Login successful!', 'success')
            return redirect(url_for('home'))

        flash('Invalid email or password.', 'danger')
        return redirect(url_for('auth.login'))

    # return "Hello worls"   
    return render_template('login.html')

# User Logout
@auth_bp.route('/logout', methods=['POST'])
@login_required
def logout():
    # resp = make_response(redirect(url_for('auth.login')))
    # resp.set_cookie('session', '', expires=0)  # Setting a cookie to expire immediately
    
    # # Also clear the session data
    # session.clear()
    logout_user()
    flash('You have been logged out.', 'success')
    return redirect(url_for('home'))


@auth_bp.route('/profile')
@login_required
def profile():
    return render_template('profile.html', user=current_user)
