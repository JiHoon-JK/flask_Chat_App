import datetime

from bson import ObjectId
from pymongo import MongoClient
from werkzeug.security import generate_password_hash

from user import User

# mongoDB는 27017 포트로 들어간다.
client = MongoClient('localhost', 27017)

# ChatDB 와 연결
chat_db = client.get_database("ChatDB")
# 데이터에비스에서 users, rooms, room_members 라는 컬렉션의 값들을 모두 가져온다.
users_collection = chat_db.get_collection("users")
rooms_collection = chat_db.get_collection("rooms")
room_members_collection = chat_db.get_collection("room_members")

# 사용자의 정보를 저장하는 def
def save_user(username, email, password):
	# 비밀번호는 암호화 처리를 위해서, hashing 처리를 해준다.
	password_hash = generate_password_hash(password)
	# users_collection 에 해당 데이터 값의 형태로 데이터베이스에 저장한다.
	users_collection.insert_one({'_id':username, 'email':email, 'password': password_hash })

# db에서 입력한 username의 데이터가 있는지 파악하는 def
def get_user(username):
	user_data = users_collection.find_one({'_id':username})
	# print(user_data)
	return User(user_data['_id'], user_data['email'], user_data['password']) if user_data else None

def save_room(room_name, created_by):
	room_id = rooms_collection.insert_one(
		{'name': room_name, 'created_by': created_by, 'created_at' : datetime.datetime.now()}
	).inserted_id

	add_room_member(room_id, room_name, created_by, created_by, is_room_admin=True)
	return  room_id


def update_room(room_id, room_name):
	rooms_collection.update_one({'_id':ObjectId(room_id)},{'$set':{'name':room_name}})

def get_room(room_id):
	return rooms_collection.find_one({'_id': ObjectId(room_id)})

def add_room_member(room_id, room_name, username, added_by, is_room_admin=False):
	room_members_collection.insert_one({'_id':{'room_id':ObjectId(room_id), 'username':username},'room_name':room_name, 'added_by': added_by, 'added_at':datetime.datetime.now(), 'is_room_admin': is_room_admin})

def add_room_members(room_id, room_name, usernames, added_by):
	room_members_collection.insert_many([{'_id':{'room_id':ObjectId(room_id), 'username':username},'room_name':room_name, 'added_by': added_by, 'added_at':datetime.datetime.now(), 'is_room_admin': False} for username in usernames])

def remove_room_members(room_id, usernames):
	room_members_collection.delete_many(
		{'_id':{'$in':[{'room_id':room_id,'username':username}for username in usernames]}})

def get_room_members(room_id):
	return list(room_members_collection.find({'_id.room_id':ObjectId(room_id)}))

def get_rooms_for_user(username):
	rooms_in_user = list(room_members_collection.find({'_id.username':username}))
	return rooms_in_user

def is_room_member(room_id, username):
	return room_members_collection.count_documents({'_id':{'room_id': ObjectId(room_id), 'username': username}})

def is_room_admin(room_id, username):
	return room_members_collection.count_documents({'_id': {'room_id': ObjectId(room_id), 'username': username}, 'is_room_admin':True})
