from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:ny88NY99@localhost/testdb'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# モデルの定義
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)

    def __repr__(self):
        return f'<User {self.username}>'

# テーブルの作成
with app.app_context():
    db.create_all()

# ルートの定義
# メニュー
@app.route("/")
def index():
    return render_template('index.html')

# ログイン
@app.get('/login')
def login_get():
    return render_template('login.html')

@app.post('/login')
def login_post():
    username = request.form["username"]
    email = request.form["email"]

    loginUser = User.query.filter(User.username == username).filter(User.email == email).first()

    if not loginUser:
        message = "ログイン情報が間違っています。"
        return render_template('login.html', message=message, username=username, email=email)
    else:
        message = "ログインしました。"
        users = User.query.all()
        return render_template('index.html', message=message, users=users)

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
    users = User.query.all()
    return render_template('master.html', users=users)

# 新規登録
@app.get('/new')
def new_get():
    return render_template('new.html')

@app.post('/new')
def new_post():
    username = request.form["username"]
    email = request.form["email"]

    newUser = User(username=username, email=email)
    db.session.add(newUser)
    db.session.commit()

    message = "ユーザー登録が完了しました。"
    users = User.query.all()
    return render_template('index.html', message=message, users=users)
