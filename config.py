import os
from dotenv import load_dotenv
load_dotenv()

class Config:
    # SECRET_KEY = os.getenv('DATABASE_SECRET_KEY')
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', f"postgresql://{os.getenv('DB_USERNAME')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
