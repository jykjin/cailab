
from flask_sqlalchemy import SQLAlchemy
# from flask_migrate import Migrate
#
db = SQLAlchemy()           #SQLAlchemy를 사용해 데이터베이스 저장
# migrate = Migrate()
class Fcuser(db.Model):
    __tablename__ = 'fcuser'   #테이블 이름 : fcuser
    id = db.Column(db.Integer, primary_key = True)   #id를 프라이머리키로 설정
    password = db.Column(db.String(64))     #패스워드를 받아올 문자열길이
    userid = db.Column(db.String(32))       #이하 위와 동일
    username = db.Column(db.String(8))

class User_db(db.Model):
    __tablename__ = 'user_db'
    ind = db.Column(db.Integer, primary_key = True)
    p1 = db.Column(db.String(64))
    p2 = db.Column(db.String(64))



class player_DB(db.Model):
    __tablename__ = 'team1'
    ind = db.Column(db.Integer, primary_key=True)
    player1 = db.Column(db.String(64))
    player2 = db.Column(db.String(64))
    pick_1 = db.Column(db.String(64))
    pick_2 = db.Column(db.String(64))
    result_1 = db.Column(db.Integer)
    result_2 = db.Column(db.Integer)
# class match(db.Model):
#     __tablename__='match'
#