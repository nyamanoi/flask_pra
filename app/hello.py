from flask import Flask, render_template, request, session, redirect, url_for
import psycopg2
from psycopg2.extensions import connection
from psycopg2.extras import DictCursor
import random
import string

app = Flask(__name__)
app.secret_key = "my_secret_key"


# DB接続
def get_connection() -> connection:
    return psycopg2.connect(
        "postgresql://postgres:ny88NY99@localhost:5432/testdb"
    )


# 関数
# id用のランダム値作成
def randomname(n):
    return "".join(random.choices(string.ascii_letters + string.digits, k=n))


# ユーザーマスタ一覧取得
def userGetAll():
    with get_connection() as conn:
        with conn.cursor(cursor_factory=DictCursor) as cur:
            cur.execute(
                """
                SELECT
                    u.user_id
                    , u.name
                    , u.mail
                    , s.shikaku_name
                    , u.created_at
                FROM
                    users AS u
                    LEFT JOIN user_shikaku AS us
                        ON u.user_id = us.user_id
                    LEFT JOIN shikaku AS s
                        ON us.shikaku_code = s.shikaku_code
                ORDER BY
                    u.created_at
            """
            )
            return cur.fetchall()


# ルートの定義
# メニュー画面表示
@app.route("/")
def index():
    # セッションがあればメニュー画面表示
    if session.get("login_user_mail") is not None:
        return render_template("index.html")
    else:
        return redirect(url_for("login_get"))


# ログイン画面表示
@app.get("/login")
def login_get():
    # セッションがなければメニュー画面表示しない
    if session.get("login_user_mail") is not None:
        return redirect(url_for("index"))
    else:
        return render_template("login.html")


# ログイン処理
@app.post("/login")
def login_post():
    email = request.form["email"]
    password = request.form["password"]

    with get_connection() as conn:
        with conn.cursor(cursor_factory=DictCursor) as cur:
            query = """
                SELECT
                    mail
                FROM
                    users
                WHERE
                    mail = %s
                    AND password = %s
            """
            cur.execute(query, (email, password))
            loginUserMail = cur.fetchone()

    # メアドとパスワードがあっている場合
    if loginUserMail is not None:
        # ログイン状態保持のためセッションに保存
        session["login_user_mail"] = loginUserMail
        message = "ログインしました。"
        return render_template("index.html", message=message)
    else:
        with get_connection() as conn:
            with conn.cursor(cursor_factory=DictCursor) as cur:
                query = """
                    SELECT
                        user_id
                        , lock_flag
                    FROM
                        users
                    WHERE
                        mail = %s
                """
                cur.execute(query, (email,))
                user = cur.fetchone()

        # メアドのみ合っている場合
        if user is not None:
            # 3回間違えたらロック
            if user["lock_flag"] is None:
                lockFlag = "1"
                message = "ログイン情報が間違っています。１回目"
            elif user["lock_flag"] == "1":
                lockFlag = "2"
                message = "ログイン情報が間違っています。２回目"
            elif user["lock_flag"] == "2":
                lockFlag = "3"
                message = "ロックされました。"

            with get_connection() as conn:
                with conn.cursor() as cur:
                    query = """
                        UPDATE users
                        SET
                            lock_flag = %s
                        WHERE
                            mail = %s
                    """
                    cur.execute(query, (lockFlag, email))
                conn.commit()
        # メアドもパスワードも間違っている場合
        else:
            message = "ログイン情報が間違っています。"

        return render_template("login.html", message=message, email=email)


# ログアウト処理
@app.get("/logout")
def logout_get():
    # セッションも削除
    session.clear()
    message = "ログアウトしました。"
    return render_template("login.html", message=message)


# パスワードリセット画面表示
@app.get("/password_reset")
def password_reset_get():
    return render_template("password_reset.html")


# パスワードリセット処理
@app.post("/password_reset")
def password_reset_post():
    password = request.form["password"]
    newPassword = request.form["new_password"]

    with get_connection() as conn:
        with conn.cursor(cursor_factory=DictCursor) as cur:
            query = """
                SELECT
                    mail
                FROM
                    users
                WHERE
                    password = %s
            """
            cur.execute(query, (password,))
            result = cur.fetchone()

    # 既存パスワードが合っていれば変更処理実行
    if result is not None:
        with get_connection() as conn:
            with conn.cursor() as cur:
                query = """
                    UPDATE users
                    SET
                        password = %s
                    WHERE
                        mail = %s
                """
                cur.execute(query, (newPassword, result["mail"]))
            conn.commit()
        message = "パスワードを変更しました。"
        return render_template("login.html", message=message)
    # 違っていれば何もしない
    else:
        message = "現在のパスワードが違います。"
        return render_template("password_reset.html", message=message)


# ユーザーマスタ画面表示
@app.get("/master")
def master_get():
    users = userGetAll()
    return render_template("master.html", users=users)


# 新規登録画面表示
@app.get("/new")
def new_get():
    return render_template("new.html")


# 新規登録処理
@app.post("/new")
def new_post():
    # 新規登録処理
    userId = randomname(6)
    username = request.form["username"]
    email = request.form["email"]
    password = request.form["password"]
    gender = request.form["gender"]
    postCode = request.form["post_code"]
    address = request.form["address"]
    phoneNumber = request.form["phone_number"]
    shikakuCode = randomname(2)
    license = request.form["license"]

    with get_connection() as conn:
        with conn.cursor() as cur:
            query = """
                INSERT
                INTO users(user_id, name, mail, password, status)
                VALUES (%s, %s, %s, %s, %s)
            """
            cur.execute(query, (userId, username, email, password, "有"))
            query = """
                INSERT
                INTO user_info(user_id, gender, yubin, jyusyo, tel, status)
                VALUES (%s, %s, %s, %s, %s, %s)
            """
            cur.execute(query, (userId, gender, postCode,
                        address, phoneNumber, "有"))
            query = """
                INSERT
                INTO shikaku(shikaku_code, shikaku_name)
                VALUES (%s, %s)
            """
            cur.execute(query, (shikakuCode, license))
            query = """
                INSERT
                INTO user_shikaku(user_id, shikaku_code)
                VALUES (%s, %s)
            """
            cur.execute(query, (userId, shikakuCode))
        conn.commit()

    message = "ユーザー登録が完了しました。"
    users = userGetAll()
    return render_template("master.html", message=message, users=users)


# 更新、削除画面表示
@app.get("/update/<id>")
def update_get(id):
    with get_connection() as conn:
        with conn.cursor(cursor_factory=DictCursor) as cur:
            query = """
                SELECT
                    mail
                    , name
                    , password
                FROM
                    users
                WHERE
                    user_id = %s
            """
            cur.execute(query, (id,))
            user = cur.fetchone()
    return render_template("update.html", id=id, user=user)


# 更新、削除処理
@app.post("/update/<id>")
def update_post(id):
    # 更新処理
    if request.form["method"] == "PUT":
        username = request.form["username"]
        email = request.form["email"]
        password = request.form["password"]

        with get_connection() as conn:
            with conn.cursor() as cur:
                query = """
                    UPDATE users
                    SET
                        name = %s
                        , mail = %s
                        , password = %s
                    WHERE
                        user_id = %s
                """
                cur.execute(query, (username, email, password, id))
            conn.commit()

        message = "ユーザーの更新が完了しました。"
        users = userGetAll()
        return render_template(
            "master.html", id=id, users=users, message=message
        )

    # 削除処理
    elif request.form["method"] == "DELETE":
        with get_connection() as conn:
            with conn.cursor() as cur:
                query = """
                    DELETE
                    FROM
                        user_shikaku
                    WHERE
                        user_id = %s
                """
                cur.execute(query, (id,))
                query = """
                    DELETE
                    FROM
                        user_info
                    WHERE
                        user_id = %s
                """
                cur.execute(query, (id,))
                query = """
                    DELETE
                    FROM
                        users
                    WHERE
                        user_id = %s
                """
                cur.execute(query, (id,))
            conn.commit()

        message = "ユーザーの削除が完了しました。"
        users = userGetAll()
        return render_template(
            "master.html", id=id, users=users, message=message
        )
    else:
        return render_template("update.html", id="例外エラーです")
