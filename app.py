from flask import Flask, render_template, request, jsonify, make_response, send_from_directory
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
import csv
import joblib
import hashlib
import base64
from statsmodels.tsa.arima.model import ARIMA
from io import BytesIO
from matplotlib import font_manager as fm
from pathlib import Path
from config import Config
from models import db, User, UserCrops
from auth import auth_bp
from crops import crops_bp
from notifications import notifications_bp
from flask_login import LoginManager, current_user, login_required
from flask_migrate import Migrate
from dotenv import load_dotenv
load_dotenv()

app = Flask(__name__)
app.config.from_object(Config)

# Initialize Database
db.init_app(app)

migrate = Migrate(app, db)

# Initialize Login Manager
login_manager = LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))  # Load user from DB


@app.context_processor
def inject_user():
    return dict(current_user=current_user)

# Register Blueprint
app.register_blueprint(auth_bp, url_prefix='/auth')
app.register_blueprint(crops_bp, url_prefix='/crops')
app.register_blueprint(notifications_bp, url_prefix='/notifications')
# print(app.url_map)

app.secret_key = os.environ.get('FLASK_SECRET_KEY', os.urandom(24))

base_dir = Path(os.getenv("BASE_DIRECTORY"))
font_path = base_dir / "NotoSerifGujarati-Black.ttf"
guj_fonts = fm.FontProperties(fname=font_path)
global_file_path = base_dir / "data/commodities/commodities_price_data-all_years.csv"
global_model_dir = base_dir / "ml_models/commodities_saved_models"
global_filename = base_dir / "ml_models/commodities_saved_models/commodities_parameters.csv"

def safe_filename(product_name):
    return hashlib.md5(product_name.encode('utf-8')).hexdigest()

def get_product_parameters(filename, product_name):
    result = []
    
    # Open the CSV file
    with open(filename, mode='r', newline='', encoding='utf-8') as file:
        reader = csv.DictReader(file)  # Using DictReader to work with column headers
        for row in reader:
            if product_name in row['Item Name']:  # Check if product_name matches
                result.append({
                    'Date': row['Date'],
                    'Item Name': row['Item Name'],
                    'p': row['p'],
                    'd': row['d'],
                    'q': row['q']
                })
    
    return result

@app.route('/get-products', methods=['POST'])
def get_products():
    data = request.get_json()
    category = data.get("category")

    # Normalize category name (capitalize first letter, lowercase rest)
    category = category.capitalize()

    # Dynamically construct file path and model directory
    file_path = base_dir / f"data/{category}/{category}_price_data.csv"
    global_file_path = file_path
    model_dir = base_dir / f"ml_models/{category}_saved_models"
    global_model_dir = model_dir

    try:
        # Check if the file exists
        if not file_path.exists():
            return jsonify({"error": f"Data file for {category} not found"}), 404

        # Read CSV file
        df = pd.read_csv(file_path)

        # Extract unique product names
        if "Item Name" in df.columns:
            products = df["Item Name"].dropna().unique().tolist()
        else:
            return jsonify({"error": "Invalid CSV format"}), 500

        return jsonify({"products": products, "model_dir": str(model_dir)})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.context_processor
def inject_firebase_config():
    return {
        'FIREBASE_CONFIG': {
            'apiKey': os.getenv("FIREBASE_CONFIG_apiKey"),
            'authDomain': os.getenv("FIREBASE_CONFIG_authDomain"),
            'projectId': os.getenv("FIREBASE_CONFIG_projectId"),
            'storageBucket': os.getenv("FIREBASE_CONFIG_storageBucket"),
            'messagingSenderId': os.getenv("FIREBASE_CONFIG_messagingSenderId"),
            'appId': os.getenv("FIREBASE_CONFIG_appId"),
            'measurementId': os.getenv("FIREBASE_CONFIG_measurementId")
        },
        'FIREBASE_PUBLIC_KEY': os.getenv("FIREBASE_PUBLIC_KEY"),
        'is_logged_in': current_user.is_authenticated
    }

@app.route("/base")
def base():
    return render_template('base.html')

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/about")
def about():
    return render_template("about.html")

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        data = request.get_json()
        name = data.get('name')
        email = data.get('email')
        message = data.get('message')
        
        if not (name and email and message):
            return jsonify({"success": False, "message": "Please enter the required fields"}), 400
        
        return jsonify({"success": True, "message": f"Thank you {name} for contacting us 😇"})

    return render_template('contact.html')

@app.route("/predict", methods=["POST"])
def predict():
    # Get form data
    category = request.form.get("category")
    product = request.form.get("product")
    
    file_path = base_dir / f"data/{category}/{category}_price_data.csv"
    model_dir = base_dir / f"ml_models/{category}_saved_models"

    # Load data
    data = pd.read_csv(file_path, parse_dates=["Date"], index_col="Date", dayfirst=True)
    product_data = data[data["Item Name"] == product]

    if product_data.empty:
        error_message = "Oops.... Given Product does not exist :(   Redirecting to homepage...."
        return render_template("error.html", message=error_message, page='home')

    # Prepare file paths
    hashed_name = safe_filename(product)
    model_path = os.path.join(model_dir, f"arima_model_{hashed_name}.pkl")

    # Check if the model exists
    if not os.path.exists(model_path):
        error_message = "Model for the given product not found :(    Redirecting to homepage...."
        return render_template("error.html", message=error_message, page='home')

    # Load the model
    loaded_model = joblib.load(model_path)
    
    # price_data = product_data["Average Price"]
    # product_parameters = get_product_parameters(global_filename, product)
    # p, d, q = None, None, None
    
    # if not product_parameters:
    #     error_message = "Product parameters are missing or empty. Redirecting to homepage..."
    #     return render_template("error.html", message=error_message, page='home')
    
    # for item in product_parameters:
    #     try:
    #         p = int(item['p'])  # Convert to int
    #         d = int(item['d'])  # Convert to int
    #         q = int(item['q'])  # Convert to int
    #         if p is None or d is None or q is None:
    #             raise ValueError("Missing one or more parameters ('p', 'd', 'q') in the product data.")
    #         # Use the p, d, q values here
    #     except KeyError as e:
    #         print(f"Missing key in product data: {e}")
    #         error_message = "Model for the given product not found :(    Redirecting to homepage...."
    #         return render_template("error.html", message=error_message, page='home')
    #     except ValueError as e:
    #         print(f"Invalid value encountered: {e}")
    #         error_message = "Model for the given product not found :(    Redirecting to homepage...."
    #         return render_template("error.html", message=error_message, page='home')
        
    # if p is None or d is None or q is None:
    #     error_message = "Model parameters (p, d, q) not found for the product. Redirecting to homepage..."
    #     return render_template("error.html", message=error_message, page='home')
        
    # fit_successful = False

    # while not fit_successful and q >= 0:
    #     try:
    #         print(f"\nFitting ARIMA model with order ({p}, {d}, {q})...")
    #         model = ARIMA(price_data, order=(p, d, q))
    #         loaded_model = model.fit()
    #         fit_successful = True  
    #         print("ARIMA model fitted successfully!")
                
    #     except np.linalg.LinAlgError as err:
    #         print(f"Error encountered: {err}")
    #         if q > 0: 
    #             q -= 1
    #             print(f"Reducing q to {q} and trying again...")
    #         else:
    #             error_message = "Unable to fit model after reducing q multiple times. Exiting loop."
    #             return render_template("error.html", message=error_message, page='home')

    # In-sample predictions
    price_data = product_data["Average Price"]
    pred = loaded_model.get_prediction(start=0, end=len(price_data) - 1)
    pred_mean = pred.predicted_mean

    # Forecast
    forecast_steps = 10
    forecast = loaded_model.get_forecast(steps=forecast_steps)
    forecast_mean = forecast.predicted_mean
    forecast_ci = forecast.conf_int()
    
    # Ensure indices are proper DateTime format
    price_data.index = pd.to_datetime(price_data.index)
    forecast_mean.index = pd.to_datetime(forecast_mean.index)
    
    # print(price_data.index.dtype)  # Should be datetime64[ns]
    # print(forecast_mean.index.dtype)  # Should be datetime64[ns]
    # Ensure price_data.index is a DatetimeIndex
    last_date = pd.to_datetime(price_data.index[-1])  # Get the last date in your data
    forecast_horizon = len(forecast_mean)  # Number of future predictions
    
    # Generate future dates, excluding Sundays
    future_dates = []
    current_date = last_date + pd.Timedelta(days=1)

    while len(future_dates) < forecast_horizon:
        if current_date.weekday() != 6:  # 6 corresponds to Sunday
            future_dates.append(current_date)
        current_date += pd.Timedelta(days=1) 
    
    # Send JSON Data
    
    response = {
        "dates": [date.strftime("%d-%m-%Y") for date in price_data.index],
        "observed": [float(val) for val in price_data.values],  # Convert to float
        "predicted": [float(val) for val in pred_mean.values],  # Convert to float
        "forecast_dates": [date.strftime("%d-%m-%Y") for date in future_dates],
        "forecast": [float(val) for val in forecast_mean.values],  # Convert to float
    }
    return render_template("result.html", response=response, product=product)
    # return jsonify(response, product)

    # # Plot the results
    # fig, ax = plt.subplots(figsize=(10, 5))
    # ax.plot(price_data.index, price_data, label="Observed", color="blue")
    # ax.plot(pred_mean.index, pred_mean, label="In-sample Prediction", color="orange")
    # ax.plot(forecast_mean.index, forecast_mean, label="Forecast", color="green")
    # ax.fill_between(forecast_ci.index, forecast_ci.iloc[:, 0], forecast_ci.iloc[:, 1], color="green", alpha=0.2)
    
    #  # # Adjust the y-axis range based on observed and forecasted prices
    # plt.ylim(price_data.min() * 0.95, price_data.max() * 1.05)
    # ax.set_title(f"Price Prediction for {product}", fontproperties=guj_fonts)
    # ax.set_xlabel("Date")
    # plt.xticks(rotation=90)
    # ax.set_ylabel("Average Price")
    # ax.legend()
    # plt.tight_layout()

    # # Save plot as a base64 string
    # img = BytesIO()
    # plt.savefig(img, format="png")
    # img.seek(0)
    # plot_url = base64.b64encode(img.getvalue()).decode("utf8")

    # return render_template("result.html", plot_url=plot_url, product=product)
    

@app.route("/dashboard")
@login_required
def dashboard():
    return render_template('dashboard.html')

@app.route('/firebase-messaging-sw.js')
def service_worker():
    return send_from_directory('static/js', 'firebase-messaging-sw.js', mimetype='application/javascript')


@app.route("/dashboard-data")
@login_required
def dashboard_data():
    user_id = current_user.id

    if not user_id:
        return jsonify({"error": "User not authenticated"}), 401

    # Fetch registered crops along with their categories
    crops_data = UserCrops.query.filter_by(user_id=user_id).all()

    if not crops_data:
        return jsonify({"error": "No registered crops found!"}), 404

    response_data = {}

    for entry in crops_data:
        category = entry.category
        crop_name = entry.crop_name

        file_path = base_dir / f"data/{category}/{category}_price_data.csv"
        model_dir = base_dir / f"ml_models/{category}_saved_models"

        # Load dataset
        if not os.path.exists(file_path):
            continue  # Skip if dataset file does not exist

        data = pd.read_csv(file_path, parse_dates=["Date"], index_col="Date", dayfirst=True)

        # Filter for the specific crop
        product_data = data[data["Item Name"] == crop_name]

        if product_data.empty:
            continue  # Skip if no data for this crop

        # Model path
        hashed_name = safe_filename(crop_name)
        model_path = os.path.join(model_dir, f"arima_model_{hashed_name}.pkl")

        if not os.path.exists(model_path):
            continue  # Skip if no trained model

        # Load ARIMA model
        loaded_model = joblib.load(model_path)

        # Observed and Predicted Data
        price_data = product_data["Average Price"]
        pred = loaded_model.get_prediction(start=0, end=len(price_data) - 1)
        pred_mean = pred.predicted_mean

        # Forecast Future Prices
        forecast_steps = 10
        forecast = loaded_model.get_forecast(steps=forecast_steps)
        forecast_mean = forecast.predicted_mean

        # Exclude Sundays from forecast dates
        last_date = pd.to_datetime(price_data.index[-1])
        future_dates = []
        current_date = last_date + pd.Timedelta(days=1)

        while len(future_dates) < forecast_steps:
            if current_date.weekday() != 6:  # Skip Sundays
                future_dates.append(current_date)
            current_date += pd.Timedelta(days=1)

        # Store results in response data
        if category not in response_data:
            response_data[category] = {}

        response_data[category][crop_name] = {
            "dates": [date.strftime("%d-%m-%Y") for date in price_data.index],
            "observed": [float(val) for val in price_data.values],
            "predicted": [float(val) for val in pred_mean.values],
            "forecast_dates": [date.strftime("%d-%m-%Y") for date in future_dates],
            "forecast": [float(val) for val in forecast_mean.values],
        }

    return jsonify(response_data)


if __name__ == "__main__":
    app.run(debug=True, port=os.getenv("PORT"), host=os.getenv("ALLHOST"))