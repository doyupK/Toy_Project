import hashlib
import jwt as jwt
import certifi
from pymongo import MongoClient
from flask import Flask, render_template, request, jsonify, redirect, url_for

ca = certifi.where()
client = MongoClient('mongodb+srv://test:sparta@cluster0.kxazb.mongodb.net/Cluster0?retryWrites=true&w=majority', tlsCAFile=ca) #main
#client = MongoClient('mongodb+srv://test:sparta@cluster0.feuh6.mongodb.net/Cluster0?retryWrites=true&w=majority', tlsCAFile=ca) #minsu
db = client.dbsparta

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

# 회원 가입 by minsu
@app.route("/users_signup", methods=["POST"])
def users():
    id_receive = request.form['id_give']
    pw_receive = request.form['pw_give']
    name_receive = request.form['name_give']
    email_receive = request.form['email_give']
    address_receive = request.form['address_give']

    doc = {
        'id': id_receive,
        'pw': pw_receive,
        'name': name_receive,
        'email': email_receive,
        'address': address_receive
    }
    db.users.insert_one(doc)

    return jsonify({'msg':'회원 가입 완료!'})

# 아이디 중복 확인 by minsu
@app.route("/users_idCheck", methods=["GET"])
def getId():
    id_receive = request.values.get('id_give')
    user = db.users.find_one({'id': id_receive})
    if user is None:    #datatype 이 none일경우 []를 통한 접근 불가 ex) user is None <- ok but, user['id'] is None <- 데이터 타입 오류
        return jsonify({'user':True})
    else:
        return jsonify({'user':False})



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

#인덱스 페이지로 이동
@app.route('/index')
def index():
    return render_template('index.html')

#인덱스 페이지의 코멘트 저장
@app.route("/comments", methods=["POST"])
def comment_post():
    recommender_receive = request.form['recommender_give']
    # emailaddress_receive = request.form['emailaddress_give']
    reason_receive = request.form['reason_give']

    doc = {
        '성함': recommender_receive,
        # '이메일 주소': emailaddress_receive,
        '코멘트내용': reason_receive,
    }
    # db.users가 아님!
    db.wines.insert_one(doc)
    return jsonify({'msg': '저장완료'})

@app.route("/comments", methods=["GET"])
def comment_get():
    comment_list = list(db.wines.find({}, {'_id': False}))
    return jsonify({'recommends': comment_list})

if __name__ == '__main__':
   app.run('0.0.0.0', port=5000, debug=True)

# Branch Test Update 20220411 10:40
# 이동재 테스트. 저도 커밋하고 푸시 해볼게요 20220411 10:56
# 이동재 테스트. 저도 커밋하고 푸시 해볼게요 20220411 10:47
# 김민수 테스트 20220411 10:50