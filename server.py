import gevent.monkey
gevent.monkey.patch_all()
from requests.packages.urllib3.util.ssl_ import create_urllib3_context
create_urllib3_context()
from app import app, db, socketio
from app.models import User, Rooms
from app.fill_forms import LoginForm, RegistrationForm, JoinForm, HostForm
from flask import render_template, flash, request, redirect, url_for, session
from flask_login import current_user, login_user, logout_user, login_required
from werkzeug.urls import url_parse
from flask_socketio import disconnect, emit, join_room, leave_room, SocketIO, close_room
import functools
import time


@app.route('/',methods = ['GET','POST'])
@login_required
def index():
	join_form = JoinForm()
	if join_form.validate_on_submit():
		roomtemp = Rooms.query.filter_by(roomname = join_form.room_name.data).first()
		if roomtemp is not None:
			# return "Congrats you have joined room :" + join_form.room_name.data
			session['room'] = join_form.room_name.data
			return redirect(url_for('chat'))
		else :
			flash("Invalid room name entered")
			return redirect(url_for('index'))
	host_form = HostForm(prefix = "host_form")
	if host_form.validate_on_submit():
		roomtemp = Rooms.query.filter_by(roomname = host_form.room_name.data).first()
		if roomtemp is None:
			roomh = Rooms(roomname = host_form.room_name.data, hostname = current_user.username)
			db.session.add(roomh)
			db.session.commit()
			flash('Congrats You host a room now')
			session['room'] = host_form.room_name.data
			# return "Welcome to room : " + host_form.room_name.data
			return redirect(url_for('chat'))
		else:
			flash('Room Already exist')
			return redirect(url_for('index'))
	return render_template("index.html", title='Home Page',join_form = join_form, host_form = host_form)

@app.route('/chat')
@login_required
def chat():
	room = session.get('room')
	name = current_user.username
	return render_template('chat.html',name = name,room = room)

#events for chat###############################################

def authenticated_only(f):
    @functools.wraps(f)
    def wrapped(*args, **kwargs):
        if not current_user.is_authenticated:
            disconnect()
        else:
            return f(*args, **kwargs)
    return wrapped

@socketio.on('joined',namespace = '/chat')
@authenticated_only
def joined(message):
	room = session.get('room')
	join_room(room)
	emit('status',{'msg':"" + current_user.username + " has entered the room."}, room = room)


@socketio.on('text', namespace='/chat')
@authenticated_only
def text(message):
    """Sent by a client when the user entered a new message.
    The message is sent to all people in the room."""
    room = session.get('room')
    emit('message_recieve', {'msg': '' + current_user.username + ':' + message['msg']}, room=room)


@socketio.on('left', namespace='/chat')
@authenticated_only
def left(message):
    """Sent by clients when they leave a room.
    A status message is broadcast to all people in the room."""
    room = session.get('room')
    leave_room(room)
    emit('status', {'msg': '' + current_user.username + ' has left the room.'}, room=room)

@socketio.on('delete', namespace = '/chat')
@authenticated_only
def delete(message):
	room = session.get('room')
	name = current_user.username
	lopaa = Rooms.query.filter_by(roomname = room).first()
	if lopaa.hostname == name:
		emit('dis_all',{'msg' : 'disconnect all users'}, room = room)
		emit('status',{'msg':"" + current_user.username + " has deleted this room"}, room = room)
		time.sleep(.200)
		close_room(room,namespace = '/chat')
		rooma = Rooms.query.filter_by(roomname = room).first()
		db.session.delete(rooma)
		db.session.commit()
	else:
		emit('status',{'msg':"" + current_user.username + " cannot delete this room"}, room = room)
################################################




@app.route('/login', methods = ['GET','POST'])
def login():
	if current_user.is_authenticated:
		return redirect(url_for('index'))
	form = LoginForm()
	if form.validate_on_submit():
		user = User.query.filter_by(username = form.username.data).first()
		if user is None or not user.check_password(form.password.data):
			print("USER = ",user is None)
			flash('Invalid username or password')
			return redirect(url_for('login'))
		login_user(user, remember = form.remember_me.data)
		next_page = request.args.get('next')
		if not next_page or url_parse(next_page).netloc != '':
			next_page = url_for('index')
		return redirect(next_page)
	return render_template('login.html', title  = 'Login',form  = form)

@app.route('/logout')
def logout():
	logout_user()
	return redirect(url_for('index'))

@app.route('/register',methods = ['GET','POST'])
def register():
	if current_user.is_authenticated:
		return redirect(url_for('index'))
	form = RegistrationForm()
	if form.validate_on_submit():
		user = User(username = form.username.data)
		user.set_password(form.password.data)
		db.session.add(user)
		db.session.commit()
		flash('Congrats, you are now a register user!')
		return redirect(url_for('login'))
	return render_template('register.html',title = 'Register' , form = form)



if __name__ == '__main__':
	# app.run(debug = True)
	# socketio.run(app, host = 'localhost', port = 5000)
	socketio.init_app(app)
	socketio.run(app,debug = True)
