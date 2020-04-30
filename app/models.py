from app import app, db, login_manager
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash



class User(UserMixin, db.Model):
	id = db.Column(db.Integer,primary_key = True)
	username = db.Column(db.String(100),unique = True)
	password_hash = db.Column(db.String(128))

	def set_password(self,password):
		self.password_hash = generate_password_hash(password)

	def check_password(self,password):
		return check_password_hash(self.password_hash,password)


class Rooms(db.Model):
	id = db.Column(db.Integer,primary_key = True)
	roomname = db.Column(db.String(100),unique = True)
	hostname = db.Column(db.String(100))


@login_manager.user_loader
def load_user(id):
	return User.query.get(int(id))