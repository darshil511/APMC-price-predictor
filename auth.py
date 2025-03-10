from flask import Blueprint, render_template, redirect, request, url_for, flash, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from models import db, User

auth_bp = Blueprint('auth', __name__)

# User Registration
@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        data = request.get_json()
        name = data.get('name')
        email = data.get('email')
        password = data.get('password')
        phone_number = data.get('phone_number')
        #name = request.form['name']
        #email = request.form['email']
        #password = request.form['password']
        #phone_number = request.form['phone_number']

        # Check if user already exists
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            return jsonify({'status': 'error', 'message': 'Email already registered. Please log in.'}), 400

        # Create new user
        new_user = User(name=name, email=email, phone_number=phone_number)
        new_user.set_password(password)

        db.session.add(new_user)
        db.session.commit()
        
        return jsonify({'status': 'success', 'message': 'Registration successful! Please log in.'}), 201

    return render_template('register.html')

# User Login
@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')
        #email = request.form['email']
        #password = request.form['password']

        user = User.query.filter_by(email=email).first()
        if not user:
            return jsonify({'status': 'error', 'message': 'User not found!'}), 400
        if user and user.check_password(password):
            login_user(user)
            return jsonify({'status': 'success', 'message': 'Login successful!'}), 200

        return jsonify({'status': 'error', 'message': 'Invalid email or password.'}), 400
 
    return render_template('login.html')

# User Logout
@auth_bp.route('/logout', methods=['POST'])
@login_required
def logout():
    logout_user()
    return jsonify({'status': 'success', 'message': 'You have been logged out.'}), 200


@auth_bp.route('/profile')
@login_required
def profile():
    return render_template('profile.html', user=current_user)

#updating user name
@auth_bp.route('/update-name', methods=['POST'])
@login_required
def update_name():
    data = request.get_json()
    new_name = data.get("name")
    
    if not new_name or new_name.strip() == "":
        return jsonify({"success": False, "message": "Name cannot be empty."}), 400

    current_user.name = new_name.strip()
    db.session.commit()

    return jsonify({"success": True, "message": "Name updated successfully!"})
