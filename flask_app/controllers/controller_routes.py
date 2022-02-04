from flask import render_template, request, redirect, session, jsonify
from flask_app import app, bcrypt
from flask_app.models import model_user
from flask_googlemaps import Map
import requests
import os

@app.route('/')
def entry():
    return render_template('index.html')

@app.route('/show/<dish_id>')
def show(dish_id):
    query = f"?nix_item_id={dish_id}"
    headers = {
            'x-app-id' : os.environ.get('FLASK_NUTRITIONIX_APP'),
            'x-app-key' : os.environ.get('FLASK_NUTRITIONIX_ID'),
        }
    response = requests.get('https://trackapi.nutritionix.com/v2/search/item'+query, headers=headers)
    r_json = response.json()
    print(r_json)
    choices = []
    if 'foods' in r_json:
        choices.append({
            "dish_name":r_json['foods'][0]['food_name'],
            "restaurant_name":r_json['foods'][0]['brand_name'],
            "calories":r_json['foods'][0]['nf_calories'],
            "img_url":r_json['foods'][0]['photo']['thumb'],
            })
    
    return render_template('show.html', choices=choices,dish_id=dish_id)

@app.route('/signup')
def signup():
    if 'uuid' in session:
        return redirect('/')
    return render_template('signup.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

@app.route('/comingsoon')
def comingsoon():
    return render_template('comingsoon.html')

@app.route('/searchZip', methods=["post"])
def searchZip():
    zip_Validation = validate_zip(request.form)
    if zip_Validation['error']:
        return jsonify(zip_Validation)
    print("Getting longitude and latitude for zip:", request.form)
    r = requests.get(f"https://maps.googleapis.com/maps/api/geocode/json?key={os.environ.get('FLASK_GOOGLE_MAPS_KEY')}&components=postal_code:{request.form['zip_code']}")
    r_json = r.json()
    # r_json["zip"] = request.form['zip_code']
    r_json["zip_map_src"] = f"https://www.google.com/maps/embed/v1/search?key={os.environ.get('FLASK_GOOGLE_MAPS_KEY')}&q=restaurant+in+zipcode+{request.form['zip_code']}&zoom=12"
    return jsonify(r_json)

@app.route('/searchRestaurant', methods=["post"])
def searchRestaurant():
    print("Restaurant Searching")
    # validate here
    search_valid = validate_search(request.form)
    if search_valid['error']:
        return jsonify(search_valid)
    lat = request.form['lat']
    lng = request.form['lng']
    distance = '1mi'
    if 'distance_check' in request.form:
        distance = f"{request.form['distance']}mi"
    query = f"?ll={lat},{lng}&distance={distance}&limit=50"
    headers = {
            'x-app-id' : os.environ.get('FLASK_NUTRITIONIX_APP'),
            'x-app-key' : os.environ.get('FLASK_NUTRITIONIX_ID'),
            'contentType': 'application/json'
        }
    response = requests.get('https://trackapi.nutritionix.com/v2/locations'+query, headers=headers)
    r_json = response.json()
    r_json["calories"] = -1
    if 'calories_check' in request.form:
        r_json["calories"] = int(request.form['calories'])
    return jsonify(r_json)

@app.route('/searchMenu', methods=["post"])
def searchMenu():
    print("Menu Searching")
    # print(request.form)
    restaurant_name = request.form['name']
    restaurant_id = request.form['brand_id']
    query = f"?query={restaurant_name}&brand_ids={restaurant_id}&common=false"
    headers = {
            'x-app-id' : os.environ.get('FLASK_NUTRITIONIX_APP'),
            'x-app-key' : os.environ.get('FLASK_NUTRITIONIX_ID'),
        }
    response = requests.get('https://trackapi.nutritionix.com/v2/search/instant'+query, headers=headers)
    r_json = response.json()
    return jsonify(r_json)

#validation function
def validate_zip(data):
    error = False
    error_msgs = []
    if not data: 
        error = True
        error_msgs.append("There is no Data")
    elif 'zip_code' not in data:
        error = True
        error_msgs.append("You must have a zipcode")
    elif not data['zip_code'].isnumeric():
        error = True
        error_msgs.append("Zip code must be numbers")
    elif len(data['zip_code']) != 5:
        error = True
        error_msgs.append("Zip Code must be 5 digits")
    return {"error":error,"error_msgs":error_msgs}

def validate_search(data):
    # print(data)
    error = False
    error_msgs = []
    if 'calories_check' in data:
        if 'calories' not in data:
            error = True
            error_msgs.append("You must set a calories limit if you enable the option.")
        elif not data['calories'].isnumeric():
            error = True
            error_msgs.append("Calories limit must be a number.")
        elif int(data['calories']) <= 0:
            error = True
            error_msgs.append("Calories limit must be greater than 0.")
    if 'distance_check' in data:
        if 'distance' not in data:
            error = True
            error_msgs.append("You must set a distance limit if you enable the option.")
        elif not data['distance'].isnumeric():
            error = True
            error_msgs.append("Distance must be a whole number")
        elif (int(data['distance']) <= 0):
            error = True
            error_msgs.append("Distance must be a positive number")
    return {"error":error,"error_msgs":error_msgs}




@app.route('/nutrixDemo')
def nutrixDemo():
    return render_template('nutrix.html')

@app.route("/map")
def mapview():
    return render_template('maps.html')