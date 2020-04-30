from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_socketio import SocketIO

app = Flask(__name__)

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app_data'
app.config['SECRET_KEY'] = 'you-will-never-guess'

db = SQLAlchemy(app)

socketio = SocketIO()

login_manager = LoginManager(app)

login_manager.login_view = 'login'
