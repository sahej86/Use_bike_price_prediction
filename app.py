from flask import Flask, render_template, request, session, redirect, url_for
import numpy as np
import joblib
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Needed for session storage

# Load model
model = joblib.load(os.path.join("model", "usebike_model_fixed.pkl"))

# Mappings
brand_category_map = {
    'bajaj': 'budget', 'hero': 'budget', 'honda': 'budget', 'tvs': 'budget',
    'yamaha': 'budget', 'suzuki': 'budget', 'mahindra': 'budget',
    'royal enfield': 'mid', 'ktm': 'mid', 'jawa': 'mid', 'hyosung': 'mid',
    'harley-davidson': 'premium', 'kawasaki': 'premium', 'benelli': 'premium',
    'triumph': 'premium', 'ducati': 'premium', 'bmw': 'premium'
}

brand_category_label_map = {'budget': 0, 'mid': 1, 'premium': 2}
owner_map = {'first owner': 0, 'second owner': 1, 'multiple owners': 2}


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/predict', methods=['POST'])
def predict():
    try:
        bike_name = request.form['bike_name']
        brand = request.form['brand'].lower()
        year = int(request.form['year'])
        kms_driven = int(request.form['kms_driven'])
        power = float(request.form['power'])
        owner_grouped = request.form['owner_grouped'].lower()

        # Feature engineering
        brand_category = brand_category_map.get(brand, 'budget')
        brand_enc = brand_category_label_map.get(brand_category, 0)
        owner_enc = owner_map.get(owner_grouped, 0)
        age = 2025 - year

        features = np.array([[age, kms_driven, power, brand_enc, owner_enc]])
        prediction = model.predict(features)[0]

        # Store in session for result page
        session['bike_name'] = bike_name
        session['prediction'] = round(prediction, 2)

        # Show loading screen with bike animation
        return render_template('loading.html')

    except Exception as e:
        return f"Error during prediction: {e}"


@app.route('/result')
def result():
    bike_name = session.get('bike_name', 'Unknown')
    prediction = session.get('prediction', 0)
    return render_template('result.html', bike_name=bike_name, prediction=prediction)


if __name__ == '__main__':
    app.run(debug=True)
