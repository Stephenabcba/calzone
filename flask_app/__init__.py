from flask import Flask
from flask_bcrypt import Bcrypt

app = Flask(__name__)
app.secret_key = "faewofjhoi3oprh23908rhag12-1g!" # keep it secret keep it safe
DATABASE = "calzone_db"
bcrypt = Bcrypt(app)