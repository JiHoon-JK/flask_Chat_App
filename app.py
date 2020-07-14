# chat-app 서버

from flask import Flask, render_template, request, redirect, url_for
from flask_login import LoginManager, current_user, login_user, login_required, logout_user
from flask_socketio import SocketIO, join_room

from db import get_user, save_user
from pymongo.errors import DuplicateKeyError

app = Flask(__name__)
app.secret_key = "JH key"
socketio = SocketIO(app)

# flask_login 을 시작한다.
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


# 메인 페이지
@app.route('/')
def home():
	return render_template('index.html')

# 로그인
@app.route('/login', methods=['GET','POST'])
def login():

	# current_user 에 is_authenticated 라는 속성이 있다면,
	if current_user.is_authenticated:
		return redirect(url_for('home'))

	message = ''

	if request.method == "POST":
		username = request.form.get('username')
		password_input = request.form.get('password')
		user = get_user(username)

		# ? 이해가 안되는 부분 ?
		if (user and user.check_password(password_input)):
			login_user(user)
			return redirect(url_for('home'))
		else:
			message = 'Failed to login!'

	return render_template('login.html', message=message)

# 회원가입
@app.route('/signup', methods=['GET','POST'])
def signup():
	if current_user.is_authenticated:
		return redirect(url_for('home'))

	message = ''

	if request.method == "POST":
		username = request.form.get('username')
		email = request.form.get('email')
		password= request.form.get('password')
		# signup 폼으로 작성한 데이터를 저장하고, 성공하면, login 페이지로 이동
		try:
			save_user(username, email, password)
			return redirect(url_for('login'))	

		# 이미 있는 사용자라면, message 로 해당 문구를 보여준다.
		except DuplicateKeyError:
			message = "User already exists!"
		
	return render_template('signup.html', message=message)

@app.route('/logout')
# login 이 되어있어야 이동할 수 있음.
@login_required
def logout():
	# 로그아웃하는 logout_user()
	logout_user()
	# 성공하면, home으로 돌아가기
	return redirect(url_for('home'))

@app.route('/create-room', methods=['GET','POST'])
@login_required
def create_room():

	if request.method == 'POST':
		room_name = request.form.get('room_name')
		members = [username.strip() for username in request.form.get('members').split(',')]

		if len(room_name) and len(usernames):
			room_id =save_room(room_name, current_user.username)

			if current_user.username in usernames:
				usernames.remove(current_user.username)
				# 26분 45초 여기까지!
				add_room_members()


	return render_template('create_room.html')

@app.route('/chat')
# login 이 되어있어야 이동할 수 있음.
@login_required
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

# 입력한 유저가 있는 지 파악하는 handler
@login_manager.user_loader
def load_user(username):
	# db.py에 있는 get_user()를 사용해서 db에 있는 지 확인한다.
	return get_user(username)


# socketio.run 로 작동시키기.
if __name__ == '__main__':
	socketio.run(app, debug=True)