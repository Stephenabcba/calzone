from dis import dis
from flask import render_template, request, redirect, session, jsonify
from flask_app import app, bcrypt
from flask_app.models import model_user
import os
import requests



@app.route('/register', methods=['POST'])
def register():
    is_valid = model_user.User.validate_register(request.form)
    if not is_valid:
        return redirect('/signup')
    pw_hash = bcrypt.generate_password_hash(request.form['password'])
    vegetarian = 0
    if 'vegetarian_check' in request.form:
        vegetarian = 1
    gluten_free = 0
    if 'gluten_free_check' in request.form:
        gluten_free = 1
    data = {
        **request.form,
        'vegetarian':vegetarian,
        'gluten_free':gluten_free,
        'password': pw_hash
    }
    del data['password_confirm']
    uuid = model_user.User.create(data)
    if (uuid):
        session['uuid'] = uuid
        session['name'] = data['name']
        return redirect('/')
    return redirect('/signup')

@app.route('/login', methods=['POST'])
def login():
    is_valid = model_user.User.validate_login(request.form)
    if not is_valid:
        return redirect('/signup')
    user = model_user.User.get_one_by_email(request.form)
    if user:
        session['uuid'] = user.id
        session['name'] = user.name
        return redirect('/')
    else:
        return redirect('/signup')

@app.route('/favorite/<dish_id>', methods=['POST'])
def favorite_dish(dish_id):
    if 'uuid' in session:
        dish_id_db = model_user.User.add_favorite({'dish_id':dish_id,'user_id':session['uuid']})
        return jsonify({'dish_id_db':dish_id_db})
    return False

@app.route('/user/favorites')
def favorites():
    if 'uuid' not in session:
        return redirect('/')
    favorite_list = model_user.User.get_favorites({"user_id":session['uuid']})
    dish_list = []
    if favorite_list:
        for favorite in favorite_list:
            query = f"?nix_item_id={favorite}"
            headers = {
                    'x-app-id' : os.environ.get('FLASK_NUTRITIONIX_APP'),
                    'x-app-key' : os.environ.get('FLASK_NUTRITIONIX_ID'),
                }
            response = requests.get('https://trackapi.nutritionix.com/v2/search/item'+query, headers=headers)
            r_json = response.json()
            if 'foods' in r_json:
                dish = {
                    "dish_name":r_json['foods'][0]['food_name'],
                    "restaurant_name":r_json['foods'][0]['brand_name'],
                    "calories":r_json['foods'][0]['nf_calories'],
                    "img_url":r_json['foods'][0]['photo']['thumb'],
                    "dish_id":favorite
                    }
                dish_list.append(dish)
    return render_template('favorites.html', dish_list=dish_list)


@app.route('/user/remove_favorite/<dish_id>')
def remove_favorite(dish_id):
    print(f"deleting {dish_id}")
    model_user.User.delete_favorite({'user_id':session['uuid'],'dish_id':dish_id})
    return jsonify({'message':'success'})