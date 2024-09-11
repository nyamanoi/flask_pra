from flask import Flask, render_template, request
import psycopg2
from psycopg2.extensions import connection
import random, string

app = Flask(__name__)

# DB接続
def get_connection() -> connection:
    return psycopg2.connect('postgresql://postgres:ny88NY99@localhost:5432/testdb')

# 関数
def randomname(n):
   return ''.join(random.choices(string.ascii_letters + string.digits, k=n))

def fetch_data_as_dict(cursor):
    """カスタムキー名で辞書形式に変換する関数"""
    columns = [desc[0] for desc in cursor.description]
    rows = cursor.fetchall()
    return [dict(zip(columns, row)) for row in rows]

# ルートの定義
# メニュー
@app.route("/")
def index():
    return render_template('index.html')

# ログイン
@app.get('/login')
def login_get():
    return render_template('login.html')

# @app.post('/login')
# def login_post():
#     username = request.form["username"]
#     email = request.form["email"]

#     loginUser = User.query.filter(User.username == username).filter(User.email == email).first()

#     if not loginUser:
#         message = "ログイン情報が間違っています。"
#         return render_template('login.html', message=message, username=username, email=email)
#     else:
#         message = "ログインしました。"
#         users = User.query.all()
#         return render_template('index.html', message=message, users=users)

# パスワードリセット
@app.get('/password_reset')
def password_reset_get():
    return render_template('password_reset.html')

@app.post('/password_reset')
def password_reset_post():

    return render_template('login.html')

# ユーザーマスタ一覧
@app.get("/master")
def master_get():
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute('SELECT user_id, name, mail, created_at FROM users')
            users = fetch_data_as_dict(cur)

    return render_template('master.html', users=users)

# 新規登録
@app.get('/new')
def new_get():
    return render_template('new.html')

@app.post('/new')
def new_post():
    userId = randomname(6)
    username = request.form["username"]
    email = request.form["email"]
    password = request.form["password"]

    with get_connection() as conn:
        with conn.cursor() as cur:
            query = 'INSERT INTO users (user_id, name, mail, password, status) VALUES (%s, %s, %s, %s, %s)'
            cur.execute(query, (userId, username, email, password, '有'))
        conn.commit()

    message = "ユーザー登録が完了しました。"
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute('SELECT * FROM users')
            users = cur.fetchall()
    return render_template('master.html', message=message, users=users)

# 更新、削除
@app.get('/update/<id>')
def update_get(id):

    return render_template('update.html', id=id)

@app.post('/update/<id>')
def update_post(id):
    if request.form['method'] == 'PUT':
        return render_template('update.html', id='更新です')
    elif request.form['method'] == 'DELETE':
        return render_template('update.html', id='削除です')
    else:
        return render_template('update.html', id='例外エラーです')