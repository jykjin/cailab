from flask import Flask, render_template, request, redirect
import os
from models import db
import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from models import Fcuser
from models import player_DB, User_db
from flask import session
from flask_wtf.csrf import CSRFProtect
from forms import RegisterForm, LoginForm
import sqlite3
from sqlalchemy.sql import func

from game_functions import prisoner_dilemma
from itertools import *
app = Flask(__name__)


@app.route('/')
def basic():
    userid = session.get('userid', None)
    return render_template("index.html", userid=userid)

@app.route('/setting', methods=['GET','POST'])
def setting(): #db세팅
    if 'userid' in session:
        userid = session.get('userid', None)
        if userid == 'master': #이미 값이 있으면 해당 부분을 경고창 띄우고, 지우고 다시 올리는작업이 필요함
            conn = sqlite3.connect('db.sqlite')
            c = conn.cursor()
            # 막 눌리지 않게 리셋 제약조건 만들어야함...
            delete_query = "delete from user_db"
            c.execute(delete_query)
            conn.commit()

            id_query = "select userid from fcuser"
            c.execute(id_query)
            id_ = c.fetchall()
            ids = [id[0] for id in id_]
            cc = list(combinations(ids, 2))
            c_list = []
            for i, t in enumerate(cc):
                c_list.append((i + 1, t[0], t[1]))

            insert_query = "INSERT INTO user_db (ind, p1, p2) VALUES (?,?,?)"
            c.executemany(insert_query, c_list)
            conn.commit()
            conn.close()
            return redirect('/')
        else:
            return redirect('/')
    else:
        return redirect('/')
@app.route('/setting2', methods=['GET','POST'])
def setting2():
    try:
        userid = session.get('userid', None)
        if userid =='master':
            conn = sqlite3.connect('db.sqlite')
            c = conn.cursor()
            delete_query = "delete from team1"
            c.execute(delete_query)
            conn.commit()

            update_query = "select * from user_db"
            c.execute(update_query)
            playerlist = c.fetchall()
            insert_query = "INSERT INTO team1 (ind, player1, player2) VALUES (?,?, ?)"
            c.executemany(insert_query, playerlist)
            conn.commit()
            conn.close()
            #db 기록 리셋하고, user_db에서 가져오려함.
            return redirect('/')
        else:
            return redirect('/')
    except:
        return redirect('/')




@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()  # 로그인 폼 생성
    if form.validate_on_submit():  # 유효성 검사
        session['userid'] = form.data.get('userid')  # form에서 가져온 userid를 session에 저장
        return redirect('/')  # 로그인에 성공하면 홈화면으로 redirect
    return render_template('login.html', form=form)

@app.route('/logout', methods=['GET'])
def logout():
    session.pop('userid', None)
    return redirect('/')

@app.route('/score', methods=['GET', 'POST'])
def check_score(): #sore를 누르면 결과계산
    if 'userid' in session:
        userid = session.get('userid', None)

        result = db.session.query(func.sum(player_DB.result_1)).filter_by(player1=userid).first()[0]
        try:
            if result is None:
                result = 0
                result += db.session.query(func.sum(player_DB.result_2)).filter_by(player2=userid).first()[0]
            else:
                result2 = db.session.query(func.sum(player_DB.result_2)).filter_by(player2=userid).first()[0]
                if result2 is None:
                    pass
                else:
                    result += result2
        except:
            result = '값이 없습니다'
        return render_template('check_score.html', userid=userid, result=result)  # 형량 정보 가져와야함..
    else:
        return redirect('/login')

@app.route('/game1', methods=["GET", 'POST'])
def game1():
    if 'userid' in session:
        my_id = request.args.get('userid')# print('로그인 확인')
        return render_template('basic.html', my_id=my_id)
    else:
        return redirect('/login')

@app.route('/subgame', methods=["GET", "POST"])  # 선택화면 쪽
def subgame():
    vsteam = request.args.get('vsteam')
    my_id = session.get('userid', None)
    print(vsteam, my_id)
    if vsteam == my_id:  # 클릭 불가능
        return redirect('/game1')
    else:
        players = (my_id, vsteam)
        DBdata = True
        conn = sqlite3.connect('db.sqlite')
        c = conn.cursor()
        find_query = "select count(*) from team1 where player1 = ? and player2 = ?"
        c.execute(find_query, players)
        here = c.fetchall()
        if here[0][0] ==0: # 데이터 조회 안되는거
            players = (vsteam, my_id)
            update_query = "select pick_2 from team1 where player1=? and player2 =?"
        else:
            players = (my_id, vsteam)
            update_query = "select pick_1 from team1 where player1=? and player2 =?"
        c.execute(update_query, players)
        data = c.fetchall()
        if data[0][0] is not None:
            DBdata = False
            return redirect('/game1')

        if DBdata:
            session['vsteam'] = vsteam
            return render_template('/subgame.html', vsteam=vsteam, my_id=my_id)

@app.route('/choose', methods=['GET', 'POST'])
def choose():
    if request.method == 'GET':
        choice = request.args["conf_or_deny"]  # deny, conf 나옴
        my_team = session.get('userid')
        vsteam = session.get('vsteam')
        PDB = player_DB()

        conn = sqlite3.connect('db.sqlite')
        c = conn.cursor()

        if PDB.query.filter_by(player1=my_team, player2=vsteam).count() > 0:
            update_query = 'update team1 set pick_1 =? where player1 = ? and player2 =?'
            update = (choice, my_team, vsteam)
            c.execute(update_query, update)
            conn.commit()
            p1 = my_team
            p2 = vsteam
            conn.close()
        else:
            update_query = "update team1 set pick_2 =? where player1 = ? and player2 =?"
            update = (choice, vsteam, my_team)
            c.execute(update_query, update)
            conn.commit()
            p1 = vsteam
            p2 = my_team
            conn.close()
    try:
        PDB = player_DB()
        conn = sqlite3.connect('db.sqlite')
        c = conn.cursor()

        team1 = PDB.query.filter_by(player1 = p1, player2 =p2).first()
        r_1, r_2 = prisoner_dilemma(team1.pick_1, team1.pick_2)
        update_query2 = "update team1 set result_1 = ? where player1 =? and player2=?"
        update2 = (r_1, p1, p2)
        c.execute(update_query2, update2)
        conn.commit()
        update_query3 = "update team1 set result_2 = ? where player1 =? and player2=?"
        update3 = (r_2, p1, p2)
        c.execute(update_query3, update3)
        conn.commit()
        conn.close()
    except:
        pass

    session.pop('vsteam')
    return redirect('/game1')



# @app.route('/game1', methods=['GET','POST'])
# def gamevalue():
#     if request.method == 'GET':
#         value = request.form
#         value = str(value)
#         print(value, value)
# @app.route('/register', methods=['GET', 'POST'])  # 겟, 포스트 메소드 둘다 사용
# def register():  # get 요청 단순히 페이지 표시 post요청 회원가입-등록을 눌렀을때 정보 가져오는것
#     form = RegisterForm()
#     if form.validate_on_submit():  # POST검사의 유효성검사가 정상적으로 되었는지 확인할 수 있다. 입력 안한것들이 있는지 확인됨.
#         # 비밀번호 = 비밀번호 확인 -> EqulaTo
#
#         fcuser = Fcuser()  # models.py에 있는 Fcuser
#         fcuser.userid = form.data.get('userid')
#         fcuser.username = form.data.get('username')
#         fcuser.password = form.data.get('password')
#
#         print(fcuser.userid, fcuser.password)  # 회원가입 요청시 콘솔창에 ID만 출력 (확인용, 딱히 필요없음)
#         db.session.add(fcuser)  # id, name 변수에 넣은 회원정보 DB에 저장
#         db.session.commit()  # 커밋
#         return "가입 완료"  # post요청일시는 '/'주소로 이동. (회원가입 완료시 화면이동)
#     return render_template('register.html', form=form)
if __name__ == '__main__':
    basedir = os.path.abspath(os.path.dirname(__file__))  # db파일을 절대경로로 생성
    dbfile = os.path.join(basedir, 'db.sqlite')  # db파일을 절대경로로 생성

    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + dbfile
    # sqlite를 사용함. (만약 mysql을 사용한다면, id password 등... 더 필요한게많다.)
    app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
    # 사용자 요청의 끝마다 커밋(데이터베이스에 저장,수정,삭제등의 동작을 쌓아놨던 것들의 실행명령)을 한다.
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    # 수정사항에 대한 track을 하지 않는다. True로 한다면 warning 메시지유발
    app.config['SECRET_KEY'] = 'wcsfeufhwiquehfdx'
    app.config['PERMANET_SESSION_LIFETIME'] = datetime.timedelta(minutes=30)

    csrf = CSRFProtect()
    csrf.init_app(app)

    db.init_app(app)
    db.app = app
    db.create_all()  # db 생성

    app.run(debug=False)
