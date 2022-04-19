import hashlib
import jwt as jwt
import certifi
from pymongo import MongoClient
from flask import Flask, render_template, request, jsonify, redirect, url_for
from datetime import datetime, timedelta

ca = certifi.where()
client = MongoClient('mongodb+srv://test:sparta@cluster0.kxazb.mongodb.net/Cluster0?retryWrites=true&w=majority',
                     tlsCAFile=ca)  # main
# client = MongoClient('mongodb+srv://test:sparta@cluster0.feuh6.mongodb.net/Cluster0?retryWrites=true&w=majority', tlsCAFile=ca) #minsu
# client = MongoClient('mongodb+srv://test:sparta@sparta.eacl0.mongodb.net/sparta?retryWrites=true&w=majority', tlsCAFile=ca) #이동재
db = client.dbsparta
app = Flask(__name__)

# app.config["TEMPLATES_AUTO_RELOAD"] = True

# 비밀 키 설정
SECRET_KEY = 'SPARTA'


# 홈 페이지 - 220419 DY
@app.route('/')
def home():
    posts = list(db.Reviews.find({}, {'_id': False}).limit(4).sort('post_num', -1))
    weincos = list(db.wine.find({}).limit(4))
    return render_template('index.html', posts=posts, weincos=weincos)


# 회원 가입 페이지 이동
@app.route('/signup')
def signup():
    return render_template('signup.html')


# 김민수 : 회원가입 및 관리 기능 ====================================================================================
# 회원 가입 by minsu
@app.route("/users_signup", methods=["POST"])
def users():
    id_receive = request.form['id_give']
    pw_receive = request.form['pw_give']
    name_receive = request.form['name_give']
    email_receive = request.form['email_give']
    address_receive = request.form['address_give']

    # Encrypt
    pw_encode = pw_receive.encode()
    pw_hash = hashlib.sha256(pw_encode).hexdigest()
    print('암호화 : ', pw_hash)

    doc = {
        'id': id_receive,
        'pw': pw_hash,
        'name': name_receive,
        'email': email_receive,
        'address': address_receive
    }
    db.users.insert_one(doc)

    return jsonify({'msg': '회원 가입 완료!'})


# 아이디 중복 확인 by minsu
@app.route("/users_idCheck", methods=["GET"])
def getId():
    id_receive = request.values.get('id_give')
    user = db.users.find_one({'id': id_receive})
    if user is None:  # datatype 이 none일경우 []를 통한 접근 불가 ex) user is None <- ok but, user['id'] is None <- 데이터 타입 오류
        return jsonify({'user': True})
    else:
        return jsonify({'user': False})


# 회원 정보 수정 페이지 이동
@app.route('/editprofile')
def editprofile():
    return render_template('editprofile.html')


# 회원 정보 불러 오기
@app.route("/show_user", methods=["GET"])
def show_user():
    id_receive = 'minsu1'
    user = db.users.find_one({'id': id_receive}, {'_id': False})
    return jsonify({'user_info': user})


# 회원 정보 수정
@app.route("/users_update", methods=["POST"])
def users_update():
    id_receive = request.form['id_give']
    pw_receive = request.form['pw_give']
    email_receive = request.form['email_give']
    address_receive = request.form['address_give']

    # Encrypt
    pw_encode = pw_receive.encode()
    pw_hash = hashlib.sha256(pw_encode).hexdigest()

    db.users.update_one({'id': id_receive}, {'$set': {'pw': pw_hash}})
    db.users.update_one({'id': id_receive}, {'$set': {'email': email_receive}})
    db.users.update_one({'id': id_receive}, {'$set': {'address': address_receive}})

    return jsonify({'msg': '회원 정보 수정 완료!'})


# 회원 정보 삭제
@app.route("/users_delete", methods=["POST"])
def users_delete():
    id_receive = request.form['id_give']
    db.users.delete_one({'id': id_receive})

    return jsonify({'msg': '회원 정보 삭제 완료!'})


# 김민수 : 회원가입 및 관리 기능 ====================================================================================

# 회원 가입 페이지 이동 - dy
@app.route('/login')
def login():
    return render_template('login.html')


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


# 인덱스 페이지로 이동
@app.route('/index')
def index():
    return render_template('index.html')


# 인덱스 페이지의 코멘트 저장   ---------------------------------------------> 확인 필요
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
    db.recommend.insert_one(doc)
    return jsonify({'msg': '저장완료'})


@app.route("/comments", methods=["GET"])
def comment_get():
    comment_list = list(db.wines.find({}, {'_id': False}))
    return jsonify({'recommends': comment_list})


# WEINCO 상세페이지  -  220419 DY
@app.route('/crawling_detail/<keyword>')
def crawling_detail(keyword):
    comments = list(db.wine.find({'post_num': keyword}, {'_id': False}))
    review = db.wine.find_one({'post_num': keyword})
    posts = list(db.Reviews.find({}, {'_id': False}).limit(4).sort('post_num', -1))
    print(posts)
    print(comments)
    if comments is not None:
        return render_template('Crawling_detail.html', review=review)
    else:
        return render_template('Crawling_detail.html', review=review)


# 상세페이지   - 220419 DY
@app.route('/detail/<keyword>')
def detail(keyword):
    review_num = db.Reviews.find_one({'post_num': keyword})

    return render_template('detail.html', review_num=review_num)


# Wine NOT 게시글 저장 - 220419 DY
@app.route('/pictures', methods=['POST'])
def save_pictures():
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        user_info = db.DYTestusers.find_one({"username": payload["id"]})

        review_list = list(db.Reviews.find({}, {'_id': False}))
        last_post_no = review_list[-1]['post_num']
        count = int(last_post_no) + 1

        type_receive = request.form['type_give']
        name_receive = request.form['name_give']
        country_receive = request.form['country_give']
        grape_receive = request.form['grape_give']
        content_receive = request.form['content_give']

        file = request.files["file_give"]
        # 확장자명 만듬
        extension = file.filename.split('.')[-1]

        # datetime 클래스로 현재 날짜와시간 만들어줌 -> 현재 시각을 출력하는 now() 메서드
        today = datetime.now()
        mytime = today.strftime('%Y-%m-%d-%H-%M-%S')

        filename = f'file-{mytime}'
        # 파일에 시간붙여서 static폴더에 filename 으로 저장
        save_to = f'static/{filename}.{extension}'
        file.save(save_to)

        doc = {
            'post_num': count,
            'username': user_info["username"],
            'profile_name': user_info["name"],
            'wine_type': type_receive,
            'wine_name': name_receive,
            'wine_country': country_receive,
            'wine_grape': grape_receive,
            'content': content_receive,
            'file': f'{filename}.{extension}',
            'time': today.strftime('%Y.%m.%d')
        }
        # pictures collection에 저장
        db.Reviews.insert_one(doc)

        return jsonify({'msg': '저장 완료!'})
    except(jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for("home"))


@app.route('/saveComment', methods=['POST'])
def save_comment():
    postNum_receive = request.form['postNum_give']
    userName_receive = request.form['userName_give']
    comment_receive = request.form['comment_give']

    doc = {
        'comment_id': '2',
        'username': userName_receive,
        'comment': comment_receive
    }
    # post Number 찾아서 해당 게시글 DB 정보에 업데이트
    db.wine.update_many({'post_num': postNum_receive}, {'$push': {'COMMENT': doc}})

    return jsonify({'msg': '저장 완료!'})


#  Wine NOT 페이지 - 220419 DY
@app.route('/winenotPage')
def winenotpage():
    posts = list(db.Reviews.find({}, {'_id': False}).sort('post_num', -1))

    return render_template('wineNot.html', posts=posts)


if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)
