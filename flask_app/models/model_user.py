from flask_app.config.mysqlconnection import connectToMySQL
from flask_app import DATABASE, bcrypt
from flask import flash
from datetime import date, timedelta

# build regex objects for input validation
import re
EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$') 
DATE_REGEX = re.compile(r'^[0-9]{4}-[0-9]{2}-[0-9]{2}')

class User:
    def __init__( self , data):
        self.id = data['id']
        self.name = data['name']
        self.email = data['email']
        self.vegetarian = data['vegetarian']
        self.gluten_free = data['gluten_free']
        self.created_at = data['created_at']
        self.updated_at = data['updated_at']
        self.pw_hash = data['password']
    
    # Create
    @classmethod
    def create(cls,data:dict) -> int:
        query = "INSERT INTO users (name, email, password, vegetarian, gluten_free) VALUES (%(name)s, %(email)s, %(password)s, %(vegetarian)s, %(gluten_free)s);"
        user_id = connectToMySQL(DATABASE).query_db(query,data)
        return user_id

    @classmethod
    def add_favorite(cls,data:dict) -> int:
        query = "INSERT INTO fave_dishes (dish_id,user_id) VALUES (%(dish_id)s, %(user_id)s);"
        dish_id = connectToMySQL(DATABASE).query_db(query,data)
        return dish_id


    # Retrieve
    @classmethod
    def get_all(cls):
        query = "SELECT * FROM users;"
        results = connectToMySQL(DATABASE).query_db(query)
        users = []
        for user in results:
            users.append(cls(user))
        return users

    @classmethod
    def get_one(cls, data):
        query = "SELECT * FROM users WHERE id=%(id)s;"
        results = connectToMySQL(DATABASE).query_db(query, data)
        if results:
            return cls(results[0])
        return False

    @classmethod
    def get_one_by_email(cls, data):
        query = "SELECT * FROM users WHERE email=%(email)s;"
        results = connectToMySQL(DATABASE).query_db(query, data)
        if results:
            return cls(results[0])
        return False

    @classmethod
    def get_favorites(cls,data:dict) -> int:
        query = "SELECT * FROM fave_dishes WHERE user_id=%(user_id)s;"
        results = connectToMySQL(DATABASE).query_db(query,data)
        favorite_list = []
        if results:
            for favorite in results:
                favorite_list.append(favorite['dish_id'])
        return favorite_list

    # Update
    @classmethod
    def update_preferences(cls, data):
        query = "UPDATE users SET vegetarian=%(vegetarian)s, gluten_free=%(gluten_free)s WHERE id = %(id)s;"
        return connectToMySQL(DATABASE).query_db( query, data )

    #Delete
    @classmethod
    def delete_one(cls, data):
        query = "DELETE FROM users WHERE id = %(id)s;"
        return connectToMySQL(DATABASE).query_db( query, data )

    @classmethod
    def delete_favorite(cls, data):
        query = "DELETE FROM fave_dishes WHERE dish_id=%(dish_id)s AND user_id=%(user_id)s;"
        return connectToMySQL(DATABASE).query_db( query, data )

    #Validation
    @staticmethod
    def validate_register(data):
        is_valid = True
        if len(data['name']) < 2 or len(data['name']) > 45:
            flash("Name must be between 2 and 45 letters and be capitalized.", 'err_register')
            is_valid = False

        if len(data['email']) < 2:
            flash("Email must be 2 characters or longer.", 'err_register')
            is_valid = False
        elif not EMAIL_REGEX.match(data['email']):
            flash("Email must be in the proper xyz@email.com format.", 'err_register')
            is_valid = False
        else:
            user = User.get_one_by_email(data)
            if user:
                flash("Email is already registered.", 'err_register')
                is_valid = False

        if len(data['password']) < 8:
            flash("Password must be at least 8 characters.", 'err_register')
            is_valid = False
        if len(data['password_confirm']) != len(data['password']) or data['password_confirm'] != data['password']:
            flash("Confirm password does not match Password.", 'err_register')
            is_valid = False

        return is_valid

    @staticmethod
    def validate_login(data):
        is_valid = True
        if len(data['email']) < 2:
            flash("Email must be 2 characters or longer.", 'err_login')
            is_valid = False
        elif not EMAIL_REGEX.match(data['email']):
            flash("Email must be in the proper xyz@email.com format.", 'err_login')
            is_valid = False
        else:
            user = User.get_one_by_email(data)
            if user:
                if not bcrypt.check_password_hash(user.pw_hash, data['password']):
                    flash("Invalid Credentials.", 'err_login')
                    is_valid = False
            else:
                flash("Invalid Credentials.", 'err_login')
                is_valid = False
        return is_valid