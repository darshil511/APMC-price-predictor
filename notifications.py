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
print(firebase_key_path)

# Initialize Firebase Admin SDK
if not firebase_admin._apps:
    cred = credentials.Certificate(firebase_key_path)
    firebase_admin.initialize_app(cred)
    
# def send_fcm_notification(token, title, body):
#     """
#     Sends a push notification using Firebase Cloud Messaging (FCM).
#     :param token: FCM registration token of the target device
#     :param title: Notification title
#     :param body: Notification body/message
#     """
#     message = messaging.Message(
#         notification=messaging.Notification(
#             title=title,
#             body=body
#         ),
#         token=token
#     )

#     try:
#         response = messaging.send(message)
#         print(f"✅ Notification sent successfully: {response}")
#         return True
#     except Exception as e:
#         print(f"❌ Error sending notification: {e}")
#         return False

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
    
    
@login_required
def save_fcm_token():
    data = request.json
    token = data.get("token")

    if not token:
        return jsonify({"error": "No token provided"}), 400

    # Update user's FCM token in the database
    user = User.query.get(current_user.id)
    if user:
        user.fcm_token = token
        db.session.commit()
        return jsonify({"message": "FCM token saved successfully!"}), 200
    else:
        return jsonify({"error": "User not found"}), 404

# def check_and_notify_price_change(user_id, crop, new_price, old_price, user_token):
#     """
#     Checks if the price of a crop has changed and sends a notification if needed.
#     """
#     if new_price != old_price:  # Price change detected
#         title = f"Price Alert for {crop}!"
#         body = f"The price of {crop} has changed from ₹{old_price} to ₹{new_price}."
#         send_fcm_notification(user_token, title, body)