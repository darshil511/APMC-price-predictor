from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from models import db, bcrypt, User, UserCrops
from app import app
import firebase_admin
from firebase_admin import credentials, messaging
import os, pandas as pd
from pathlib import Path
from dotenv import load_dotenv
load_dotenv()

base_dir = Path(os.getenv("BASE_DIRECTORY"))

firebase_key_path = base_dir / os.getenv("FCM_PRIVATE_KEY_PATH")

# Initialize Firebase Admin SDK
if not firebase_admin._apps:
    cred = credentials.Certificate(firebase_key_path)
    firebase_admin.initialize_app(cred)
    
data_dir = base_dir / "data"


def load_price_data(category):
    category_paths = {
        "Commodities": os.path.join(data_dir, "commodities", "commodities_price_data.csv"),
        "Fruits": os.path.join(data_dir, "fruits", "fruits_price_data.csv"),
        "Vegetables": os.path.join(data_dir, "vegetables", "vegetables_price_data.csv"),
    }
    
    file_path = category_paths.get(category)
    if file_path and os.path.exists(file_path):
        return pd.read_csv(file_path, encoding='utf-8', parse_dates=['Date'], date_format='%d/%m/%Y')
    return None


def detect_price_changes():
    users = User.query.all()
    for user in users:
        for user_crop in user.crops:
            category = user_crop.category
            crop_name = user_crop.crop_name
            df = load_price_data(category)
            if df is None:
                continue

            # Convert Date to datetime format
            df["Date"] = pd.to_datetime(df["Date"], dayfirst=True)
            df = df[df["Item Name"] == crop_name].sort_values("Date", ascending=False)
            print(df.head())

            if len(df) < 2:
                continue  # Not enough data to compare

            latest_entry = df.iloc[0]
            previous_entry = df.iloc[1]

            latest_price = latest_entry["Average Price"]
            previous_price = previous_entry["Average Price"]

            if previous_price > 0:  # Avoid division by zero
                price_change_percent = ((latest_price - previous_price) / previous_price) * 100
                print(abs(price_change_percent))
                print()
                
                if abs(price_change_percent) > 10:
                    send_notification(user, crop_name, previous_price, latest_price, price_change_percent)
                    
                    
def send_notification(user, crop_name, previous_price, latest_price, price_change_percent):
    if user.fcm_token:
        message = messaging.Message(
            notification=messaging.Notification(
                title=f"Price Alert: {crop_name}",
                body=f"{crop_name} price changed by {price_change_percent:.2f}%. New price: {latest_price}. Old price: {previous_price}"
            ),
            token=user.fcm_token
        )
        response = messaging.send(message)
        print(f"Notification sent to {user.email}: {response}")
        

def run_price_change_detection():
    with app.app_context():
        detect_price_changes()

if __name__ == "__main__":
    run_price_change_detection()