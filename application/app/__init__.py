from flask import Flask
from os import path
app = Flask(__name__, static_folder='static')
app.config['SECRET_KEY'] = 'LOntoCA'

APP_ROOT = path.dirname(path.abspath(__file__))

STATIC_PATH = path.join(APP_ROOT, "static\\")

from application.app import routes