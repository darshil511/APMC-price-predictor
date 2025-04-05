from flask import Blueprint, request, jsonify, current_app
import firebase_admin
from firebase_admin import credentials, messaging
import os
from pathlib import Path
from models import db, User
from flask_login import current_user, login_required

notifications_bp = Blueprint('notifications', __name__)
base_dir = Path(os.getenv("BASE_DIRECTORY"))

firebase_key_path = base_dir / os.getenv("FCM_PRIVATE_KEY_PATH")

# Initialize Firebase Admin SDK
if not firebase_admin._apps:
    cred = credentials.Certificate(firebase_key_path)
    firebase_admin.initialize_app(cred)


@notifications_bp.route('/store_fcm_token', methods=['POST'])
@login_required
def store_fcm_token():
    data = request.json
    fcm_token = data.get("fcm_token")

    if not fcm_token:
        return jsonify({"error": "FCM token is missing"}), 400

    # Store token in the database for the current logged-in user
    user = User.query.get(current_user.id)
    if user:
        user.fcm_token = fcm_token
        db.session.commit()
        return jsonify({"message": "FCM token stored successfully!"}), 200
    else:
        return jsonify({"error": "User not found"}), 404


@notifications_bp.route('/remove_fcm_token', methods=['POST'])
@login_required
def remove_fcm_token():
    data = request.get_json()
    token_to_remove = data.get("token")

    if token_to_remove:
        token_entry = User.query.filter_by(id=current_user.id, fcm_token=token_to_remove).first()
        if token_entry:
            token_entry.fcm_token = None
            db.session.commit()
            return jsonify({'message': 'Token deleted'}), 200
        else:
            return jsonify({'message': 'Token not found'}), 404

    return jsonify({'message': 'Invalid token'}), 400


@notifications_bp.route("/check_fcm_token", methods=["GET"])
@login_required
def check_fcm_token():
    user = current_user
    if not user.fcm_token:
        return jsonify({"error": "Token not set"}), 404
    return jsonify({ "token": user.fcm_token })
