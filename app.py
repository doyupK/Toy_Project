import hashlib

import jwt as jwt
from pymongo import MongoClient


import certifi
ca = certifi.where()
client = MongoClient('mongodb+srv://test:sparta@cluster0.kxazb.mongodb.net/Cluster0?retryWrites=true&w=majority', tlsCAFile=ca)
db = client.dbsparta

from flask import Flask, render_template, request, jsonify, redirect, url_for
app = Flask(__name__)
app.config["TEMPLATES_AUTO_RELOAD"] = True

# 비밀 키 설정
SECRET_KEY = 'SPARTA'

# 홈 페이지
@app.route('/')
def home():
    return render_template('login.html')

# 회원 가입 페이지 이동
@app.route('/signup')
def signup():
    return render_template('signup.html')

# 회원 가입
@app.route("/users_signup", methods=["POST"])
def users():
    id_receive = request.form['id_give']
    pw_receive = request.form['pw_give']
    name_receive = request.form['name_give']
    email_receive = request.form['email_give']

    doc = {
        'id': id_receive,
        'pw': pw_receive,
        'name': name_receive,
        'email': email_receive,
    }

    db.users.insert_one(doc)

    return jsonify({'msg':'회원 가입 완료!'})


@app.route('/sign_in', methods=['POST'])  # 로그인 API
def sign_in():
    id_receive = request.form['give_id']
    pw_receive = request.form['give_pw']
    pw_hash = hashlib.sha256(pw_receive.encode('utf-8')).hexdigest()  # 패스워드 암호화

    result = db.users.find_one({'id': id_receive, 'pw': pw_hash})  # 동일한 유저가 있는지 확인

    if result is not None:  # 동일한 유저가 없는게 아니면, = 동일한 유저가 있으면,
        payload = {
            'id': id_receive,

            'exp': datetime.utcnow() + timedelta(seconds=60 * 60 * 24)
        }

        token = jwt.encode(payload, SECRET_KEY, algorithm='HS256').decode('utf8')
            # .decode('utf8')  # 토큰을 건내줌.


        return jsonify({'result': 'success', 'token': token})
    else:  # 동일한 유저가 없으면,
        return jsonify({'result': 'fail', 'msg': '아이디/패스워드가 일치하지 않습니다.'})



if __name__ == '__main__':
   app.run('0.0.0.0', port=5000, debug=True)