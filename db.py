from pymongo import MongoClient
from werkzeug.security import generate_password_hash

from user import User

# mongoDB는 27017 포트로 들어간다.
client = MongoClient('localhost', 27017)

# ChatDB 와 연결
chat_db = client.get_database("ChatDB")
# 데이터에비스에서 users 라는 컬렉션의 값들을 모두 가져온다.
users_collection = chat_db.get_collection("users")

# 사용자의 정보를 저장하는 def
def save_user(username, email, password):
	# 비밀번호는 암호화 처리를 위해서, hashing 처리를 해준다.
	password_hash = generate_password_hash(password)
	# users_collection 에 해당 데이터 값의 형태로 데이터베이스에 저장한다.
	users_collection.insert_one({'_id':username, 'email':email, 'password': password_hash })

def get_user(username):
	user_data = users_collection.find_one({'_id':username})
	return User(user_data['_id'], user_data['email'], user_data['password']) if user_data else None