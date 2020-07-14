# chat-app 서버

from flask import Flask, render_template, request, redirect, url_for
from flask_login import LoginManager
from flask_socketio import SocketIO, join_room

app = Flask(__name__)
socketio = SocketIO(app)

# flask_login 을 시작한다.
login_manager = LoginManager()
login_manager.init_app(app)


@app.route('/')
def home():
	return render_template('index.html')

@app.route('/login', methods=['GET','POST'])
def login():
	if request.method == "POST":
		username = request.form.get('username')
		password_input = request.form.get('password')
		user = get_user(username)

		# 14:24 분까지 들음
		if user and user.check_password(password_input)

	return render_template('login.html')

@app.route('/chat')
def chat():
	# url로 보낸, 시용자의 데이터를 전달받아서 /chat 으로 전달. 
	username = request.args.get('username')
	room = request.args.get('room')

	# username 과 room 이 있다면, chat.html으로 보내기
	if username and room:
		return render_template('chat.html', username=username, room=room)
	# 둘중에 하나라도 없다면, 다시 home으로 이동
	else:
		return redirect(url_for('home'))

#  메세지를 보내는 handler
@socketio.on('send_message')
def handle_send_message_event(data):
	# 파이참의 터미널 창에, 체크할 수 있게 나오도록 하는 구문.
	app.logger.info("{} has sent message to the rooms {}".format(data['username'], data['room'],data['message']))
	# receive_message 로 data를 보내고, room 으로 room 번호를 보낸다.
	socketio.emit('receive_message', data, room=data['room'])


@socketio.on('join_room')
def handle_join_room_event(data):
	# 파이참의 터미널 창에, 체크할 수 있게 나오도록 하는 구문.
	app.logger.info("{} has joined the rooms {}".format(data['username'], data['room']))
	# socket.io 에 있는 라이브러리 join_room 을 활용해서 사용자가 작성한 room 넘버로 들어감.
	join_room(data['room'])
	# join_room_announcement 로 data를 보낸다.
	socketio.emit('join_room_announcement', data)

@login_manager.user_loader
def load_user(username):
	return get_user(username)


# socketio.run 로 작동시키기.
if __name__ == '__main__':
	socketio.run(app, debug=True)