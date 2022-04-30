import hashlib

import jwt as jwt
import certifi
from django.core.paginator import Paginator
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
@app.route('/home')
def home():
    posts = list(db.Reviews.find({}, {'_id': False}).sort('post_num', -1).limit(4))
    vivino_wines = list(db.vivino_wines.find({}).limit(4))
    weinco_wines = list(db.weinco_wines.find({}).limit(4))
    xtra_wines = list(db.xtra_wines_list.find({}).limit(4))
    wine21_wines = list(db.wine21.find({}).limit(4))

    token_receive = request.cookies.get('mytoken')

    if token_receive is not None:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        user_info = db.users.find_one({"id": payload["id"]})
        login_status = 1
        return render_template('index.html',
                               posts=posts, vivino_wines=vivino_wines, weinco_wines=weinco_wines, xtra_wines=xtra_wines,
                               user_info=user_info, login_status=login_status)
    else:
        login_status = 0
        return render_template('index.html',
                               posts=posts, vivino_wines=vivino_wines, weinco_wines=weinco_wines, xtra_wines=xtra_wines,
                               login_status=login_status)


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
    token_receive = request.cookies.get('mytoken')
    if token_receive is not None:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        user_info = db.users.find_one({"id": payload["id"]})
        login_status = 1
        return render_template('editprofile.html', user_info=user_info, login_status=login_status)
    else:
        login_status = 0
        return render_template('editprofile.html', login_status=login_status)


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

        token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')  # .decode('utf8')
        # .decode('utf8')  # 토큰을 건내줌.

        return jsonify({'result': 'success', 'token': token, 'msg': '환영합니다.'})
    else:  # 동일한 유저가 없으면,
        return jsonify({'result': 'fail', 'msg': '아이디/패스워드가 일치하지 않습니다.'})


# 크롤링 상세페이지  -  220429 DY
@app.route('/crawling_detail/<keyword>/<site>')
def crawling_detail(keyword, site):
    # 로그인 정보 불러오기
    global comments_name, review
    print(keyword)
    print(site)
    find_keyword = int(keyword)
    site = str(site)
    token_receive = request.cookies.get('mytoken')
    if site == 'vivino_recommend':
        # 코멘트 불러오기
        comments_name = db.vivino_wines.find_one({'post_num': find_keyword}, {'COMMENT': 1, '_id': False})
        # 해당(keyword) 게시물 정보 불러오기
        review = db.vivino_wines.find_one({'post_num': find_keyword})

    elif site == 'vivino_list':
        # 코멘트 불러오기
        comments_name = db.vivino_wines_list.find_one({'post_num': find_keyword}, {'COMMENT': 1, '_id': False})
        # 해당(keyword) 게시물 정보 불러오기
        review = db.vivino_wines_list.find_one({'post_num': find_keyword})

    elif site == 'weinco_recommend':
        # 코멘트 불러오기
        comments_name = db.weinco_wines.find_one({'post_num': find_keyword}, {'COMMENT': 1, '_id': False})
        # 해당(keyword) 게시물 정보 불러오기
        review = db.weinco_wines.find_one({'post_num': find_keyword})

    elif site == 'weinco_list':
        # 코멘트 불러오기
        comments_name = db.weinco_wines_list.find_one({'post_num': find_keyword}, {'COMMENT': 1, '_id': False})
        # 해당(keyword) 게시물 정보 불러오기
        review = db.weinco_wines_list.find_one({'post_num': find_keyword})

    elif site == 'xtra_recommend':
        # 코멘트 불러오기
        comments_name = db.xtra_wines.find_one({'post_num': find_keyword}, {'COMMENT': 1, '_id': False})
        # 해당(keyword) 게시물 정보 불러오기
        review = db.xtra_wines.find_one({'post_num': find_keyword})

    elif site == 'xtra_list':
        # 코멘트 불러오기
        comments_name = db.xtra_wines_list.find_one({'post_num': find_keyword}, {'COMMENT': 1, '_id': False})
        # 해당(keyword) 게시물 정보 불러오기
        review = db.xtra_wines_list.find_one({'post_num': find_keyword})

    # 로그인 정보(token)있을 시
    if token_receive is not None:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        user_info = db.users.find_one({"id": payload["id"]})
        login_status = 1
        if len(comments_name) == 0:
            return render_template('crawling_detail.html',
                                   review=review, user_info=user_info,
                                   login_status=login_status)
        else:
            comments = list(comments_name['COMMENT'])
            return render_template('crawling_detail.html',
                                   review=review, comments=comments,
                                   user_info=user_info, login_status=login_status)
    # 로그인 정보(token)없을 시
    else:
        user_info = None
        login_status = 0
        if len(comments_name) == 0:
            return render_template('crawling_detail.html',
                                   review=review, user_info=user_info,
                                   login_status=login_status)
        else:
            comments = list(comments_name['COMMENT'])
            return render_template('crawling_detail.html',
                                   review=review, comments=comments,
                                   user_info=user_info, login_status=login_status)


# Wine NOT 상세페이지   - 220423 DY
@app.route('/detail/<keyword>')
def detail(keyword):
    # 로그인 정보 불러오기
    find_keyword = int(keyword)
    token_receive = request.cookies.get('mytoken')
    # 코멘트 불러오기
    comments_name = db.Reviews.find_one({'post_num': find_keyword}, {'COMMENT': 1, '_id': False})
    # 해당(keyword) 게시물 정보 불러오기
    review = db.Reviews.find_one({'post_num': find_keyword})
    # 로그인 정보(token)있을 시
    if token_receive is not None:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        user_info = db.users.find_one({"id": payload["id"]})
        login_status = 1
        if len(comments_name) == 0:
            return render_template('detail.html',
                                   review=review, user_info=user_info,
                                   login_status=login_status)
        else:
            comments = list(comments_name['COMMENT'])
            return render_template('detail.html',
                                   review=review, comments=comments,
                                   user_info=user_info, login_status=login_status)
    # 로그인 정보(token)없을 시
    else:
        user_info = None
        login_status = 0
        if len(comments_name) == 0:
            return render_template('detail.html',
                                   review=review, user_info=user_info,
                                   login_status=login_status)
        else:
            comments = list(comments_name['COMMENT'])
            return render_template('detail.html',
                                   review=review, comments=comments,
                                   user_info=user_info, login_status=login_status)


# Wine NOT 게시글 저장 - 220419 DY
@app.route('/pictures', methods=['POST'])
def save_pictures():
    token_receive = request.cookies.get('mytoken')

    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        user_info = db.users.find_one({"id": payload["id"]})

        review_list = list(db.Reviews.find({}, {'_id': False}))

        if len(review_list) == 0:
            count = 1
        else:
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
        save_to = f'static/img/{filename}.{extension}'
        file.save(save_to)

        doc = {
            'post_num': count,
            'username': user_info["id"],
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

# 코멘트 저장 220429 DY
@app.route('/saveComment', methods=['POST'])
def save_comment():
    global comments
    pageInfo_receive = request.form['pageInfo_give']
    postNum_receive = int(request.form['postNum_give'])
    userName_receive = request.form['userName_give']
    comment_receive = request.form['comment_give']

    if pageInfo_receive == "WineNOT":
        # DB에 코멘트의 마지막 ID 값 읽어서 +1
        comments = db.Reviews.find_one({'post_num': postNum_receive}, {'COMMENT': 1, '_id': False})
    elif pageInfo_receive == "vivino_recommend":
        # DB에 코멘트의 마지막 ID 값 읽어서 +1
        comments = db.vivino_wines.find_one({'post_num': postNum_receive}, {'COMMENT': 1, '_id': False})
    elif pageInfo_receive == "vivino_list":
        # DB에 코멘트의 마지막 ID 값 읽어서 +1
        comments = db.vivino_wines_list.find_one({'post_num': postNum_receive}, {'COMMENT': 1, '_id': False})
    elif pageInfo_receive == "weinco_recommend":
        # DB에 코멘트의 마지막 ID 값 읽어서 +1
        comments = db.weinco_wines.find_one({'post_num': postNum_receive}, {'COMMENT': 1, '_id': False})
    elif pageInfo_receive == "weinco_list":
        # DB에 코멘트의 마지막 ID 값 읽어서 +1
        comments = db.weinco_wines_list.find_one({'post_num': postNum_receive}, {'COMMENT': 1, '_id': False})
    elif pageInfo_receive == "xtra_recommend":
        # DB에 코멘트의 마지막 ID 값 읽어서 +1
        comments = db.xtra_wines.find_one({'post_num': postNum_receive}, {'COMMENT': 1, '_id': False})
    elif pageInfo_receive == "xtra_list":
        # DB에 코멘트의 마지막 ID 값 읽어서 +1
        comments = db.xtra_wines_list.find_one({'post_num': postNum_receive}, {'COMMENT': 1, '_id': False})

    if len(comments) == 0:
        doc = {
            'comment_id': 1,
            'username': userName_receive,
            'comment': comment_receive
        }
    else:
        list_comment = list(comments['COMMENT'])
        last_comment = list_comment[-1]
        new_comment_id = int(last_comment.get('comment_id')) + 1

        doc = {
            'comment_id': new_comment_id,
            'username': userName_receive,
            'comment': comment_receive
        }

    if pageInfo_receive == "WineNOT":
        db.Reviews.update_many({'post_num': postNum_receive}, {'$addToSet': {'COMMENT': doc}})
    elif pageInfo_receive == "vivino_recommend":
        db.vivino_wines.update_many({'post_num': postNum_receive}, {'$addToSet': {'COMMENT': doc}})
    elif pageInfo_receive == "vivino_list":
        db.vivino_wines_list.update_many({'post_num': postNum_receive}, {'$addToSet': {'COMMENT': doc}})
    elif pageInfo_receive == "weinco_recommend":
        db.weinco_wines.update_many({'post_num': postNum_receive}, {'$addToSet': {'COMMENT': doc}})
    elif pageInfo_receive == "weinco_list":
        db.weinco_wines_list.update_many({'post_num': postNum_receive}, {'$addToSet': {'COMMENT': doc}})
    elif pageInfo_receive == "xtra_recommend":
        db.xtra_wines.update_many({'post_num': postNum_receive}, {'$addToSet': {'COMMENT': doc}})
    elif pageInfo_receive == "xtra_list":
        db.xtra_wines_list.update_many({'post_num': postNum_receive}, {'$addToSet': {'COMMENT': doc}})

    return jsonify({'msg': '저장 완료!'})


# Detail Page Comment 삭제 - 0429 DY
@app.route('/delete_comment', methods=['POST'])
def delete_comment():
    pageInfo_receive = request.form['pageInfo_give']
    postNum_receive = int(request.form['postNum_give'])
    commentNum_receive = int(request.form['commentNum_give'])

    # post Number 찾아서 해당 게시글 DB 정보에서 삭제
    if pageInfo_receive == "WineNOT":
        db.Reviews.update_many({'post_num': postNum_receive},
                               {'$pull': {'COMMENT': {'comment_id': commentNum_receive}}})
    elif pageInfo_receive == "vivino_recommend":
        db.vivino_wines.update_many({'post_num': postNum_receive},
                                    {'$pull': {'COMMENT': {'comment_id': commentNum_receive}}})
    elif pageInfo_receive == "vivino_list":
        db.vivino_wines_list.update_many({'post_num': postNum_receive},
                                         {'$pull': {'COMMENT': {'comment_id': commentNum_receive}}})
    elif pageInfo_receive == "weinco_recommend":
        db.weinco_wines.update_many({'post_num': postNum_receive},
                                    {'$pull': {'COMMENT': {'comment_id': commentNum_receive}}})
    elif pageInfo_receive == "weinco_list":
        db.weinco_wines_list.update_many({'post_num': postNum_receive},
                                         {'$pull': {'COMMENT': {'comment_id': commentNum_receive}}})
    elif pageInfo_receive == "xtra_recommend":
        db.xtra_wines.update_many({'post_num': postNum_receive},
                                  {'$pull': {'COMMENT': {'comment_id': commentNum_receive}}})
    elif pageInfo_receive == "xtra_list":
        db.xtra_wines_list.update_many({'post_num': postNum_receive},
                                       {'$pull': {'COMMENT': {'comment_id': commentNum_receive}}})

    return jsonify({'msg': '삭제 완료!'})


#  Wine NOT 페이지 - 220419 DY
@app.route('/winenotPage')
def winenotpage():
    token_receive = request.cookies.get('mytoken')
    posts_list = list(db.Reviews.find({}, {'_id': False}).sort('post_num', -1))
    page = request.args.get('page', type=int, default=1)
    paginator = Paginator(posts_list, 8)
    posts = paginator.page(page)

    page_numbers_range = 10  # 페이지 메뉴에 표현 될 페이지 수 제한
    max_index = paginator.num_pages  # 전체 페이지 수
    current_page = int(page) if page else 1  # 현재 페이지 / 기본값 1
    start_index = int((current_page - 1) / page_numbers_range) * page_numbers_range  # 페이지 메뉴의 시작 번호
    end_index = start_index + page_numbers_range  # 페이지 메뉴의 끝 번호

    if end_index >= max_index:
        end_index = max_index
    page_numbers_range = paginator.page_range[start_index:end_index]

    if token_receive is not None:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        user_info = db.users.find_one({"id": payload["id"]})
        login_status = 1
        return render_template('wineNot.html', user_info=user_info, login_status=login_status, posts=posts,
                               page_numbers_range=page_numbers_range)
    else:
        login_status = 0
        return render_template('wineNot.html', login_status=login_status, posts=posts,
                               page_numbers_range=page_numbers_range)


# 김민수 : wine list 페이지 ====================================================================================
# wine list 페이지 이동
@app.route("/winelist", methods=["GET"])
def winelist():
    board_name = request.values.get('board_name')
    posts_list = None
    if board_name == 'vivino':
        posts_list = list(db.vivino_wines_list.find({}, {'_id': False}).sort('post_num', 1))
    elif board_name == 'weinco':
        posts_list = list(db.weinco_wines_list.find({}, {'_id': False}).sort('post_num', 1))
    elif board_name == 'xtrawine':
        posts_list = list(db.xtra_wines_list.find({}, {'_id': False}).sort('post_num', 1))
    elif board_name == 'wine21':
        posts_list = list(db.wine21.find({}).limit({}, {'_id': False}).sort('post_num', 1))

    print(posts_list)

    token_receive = request.cookies.get('mytoken')
    page = request.args.get('page', type=int, default=1)
    paginator = Paginator(posts_list, 8)
    posts = paginator.page(page)

    page_numbers_range = 10  # 페이지 메뉴에 표현 될 페이지 수 제한
    max_index = paginator.num_pages  # 전체 페이지 수
    current_page = int(page) if page else 1  # 현재 페이지 / 기본값 1
    start_index = int((current_page - 1) / page_numbers_range) * page_numbers_range  # 페이지 메뉴의 시작 번호
    end_index = start_index + page_numbers_range  # 페이지 메뉴의 끝 번호

    if end_index >= max_index:
        end_index = max_index
    page_numbers_range = paginator.page_range[start_index:end_index]

    if token_receive is not None:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        user_info = db.users.find_one({"id": payload["id"]})
        login_status = 1
        return render_template('winelist.html', board_name=board_name, user_info=user_info, login_status=login_status,
                               posts=posts,
                               page_numbers_range=page_numbers_range)
    else:
        login_status = 0
        return render_template('winelist.html', board_name=board_name, login_status=login_status, posts=posts,
                               page_numbers_range=page_numbers_range)


# 김민수 : wine list 페이지 ====================================================================================

# intro page - 숙영 ==========================================================================================
@app.route('/')
def intro():
    token_receive = request.cookies.get('mytoken')
    if token_receive is not None:
        login_status = 1
        return render_template('intro2.html', login_status=login_status)
    else:
        login_status = 0
        return render_template('intro2.html', login_status=login_status)


if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)
