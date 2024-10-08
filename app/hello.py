from flask import Flask, render_template, request, session, redirect, url_for
import psycopg2
from psycopg2 import extras
from psycopg2.extensions import connection
from psycopg2.extras import DictCursor
import random
import string
from form import Form
from models import User
from collections import defaultdict

app = Flask(__name__)
app.secret_key = "my_secret_key"


# DB接続
def get_connection() -> connection:
    return psycopg2.connect("postgresql://postgres:ny88NY99@localhost:5432/testdb")


userModel = User.User()


# 関数
# id用のランダム値作成
def randomname(n):
    return "".join(random.choices(string.ascii_letters + string.digits, k=n))


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

    loginUserMail = userModel.getUserMail(get_connection(), email, password)

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
    users = userModel.userGetAll(get_connection())
    shikakus = userModel.getUserShikaku(get_connection())

    # 取得したshikakusの形式を変更
    grouped_shikakus = defaultdict(list)
    for shikaku in shikakus:
        grouped_shikakus[shikaku["user_id"]].append(shikaku["shikaku_name"])

    return render_template(
        "master.html", users=users, grouped_shikakus=grouped_shikakus
    )


# 新規登録画面表示
@app.get("/new")
def new_get():
    form = Form()
    # 資格一覧取得
    with get_connection() as conn:
        with conn.cursor(cursor_factory=DictCursor) as cur:
            cur.execute(
                """
                SELECT
                    shikaku_code
                    , shikaku_name
                FROM
                    shikaku
            """
            )
            shikakus = cur.fetchall()

    return render_template("new.html", form=form, shikakus=shikakus)


# 新規登録処理
@app.post("/new")
def new_post():
    form = Form()
    # バリデーションチェック
    if form.validate_on_submit():
        # 新規登録処理
        userId = randomname(6)
        username = form.name.data
        email = form.email.data
        password = form.password.data
        gender = form.gender.data
        postCode = form.post_code.data
        address = form.address.data
        phoneNumber = form.phone_number.data
        shikakuCode = request.form.getlist("license")

        userShikaku_values = [(userId, item) for item in shikakuCode]

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
                cur.execute(
                    query, (userId, gender, postCode, address, phoneNumber, "有")
                )
                query = """
                    INSERT
                    INTO user_shikaku(user_id, shikaku_code)
                    VALUES %s
                """
                extras.execute_values(cur, query, userShikaku_values)
            conn.commit()

        # ユーザーマスタ一覧へ遷移
        message = "ユーザー登録が完了しました。"
        users = userModel.userGetAll(get_connection())
        shikakus = userModel.getUserShikaku(get_connection())
        # 取得したshikakusの形式を変更
        grouped_shikakus = defaultdict(list)
        for shikaku in shikakus:
            grouped_shikakus[shikaku["user_id"]].append(shikaku["shikaku_name"])

        return render_template(
            "master.html",
            message=message,
            users=users,
            grouped_shikakus=grouped_shikakus,
        )
    else:
        errorMessage = "入力エラーがあります。"
        with get_connection() as conn:
            with conn.cursor(cursor_factory=DictCursor) as cur:
                cur.execute(
                    """
                    SELECT
                        shikaku_code
                        , shikaku_name
                    FROM
                        shikaku
                """
                )
                shikakus = cur.fetchall()

        # 資格一覧をセレクトボックスに格納
        form.license.choices = [
            (shikaku["shikaku_code"], shikaku["shikaku_name"]) for shikaku in shikakus
        ]
        return render_template("new.html", form=form, errorMessage=errorMessage)


# 更新、削除画面表示
@app.get("/update/<id>")
def update_get(id):
    form = Form()
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

    form.email.data = user["mail"]
    form.name.data = user["name"]

    return render_template("update.html", id=id, form=form)


# 更新、削除処理
@app.post("/update/<id>")
def update_post(id):
    # 更新処理
    if request.form["method"] == "PUT":
        form = Form()
        # バリデーションチェック
        if form.validate_on_submit():
            username = form.name.data
            email = form.email.data
            password = form.password.data

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

            # ユーザーマスタ一覧へ遷移
            message = "ユーザーの更新が完了しました。"
            users = userModel.userGetAll(get_connection())
            shikakus = userModel.getUserShikaku(get_connection())
            # 取得したshikakusの形式を変更
            grouped_shikakus = defaultdict(list)
            for shikaku in shikakus:
                grouped_shikakus[shikaku["user_id"]].append(shikaku["shikaku_name"])

            return render_template(
                "master.html",
                users=users,
                message=message,
                grouped_shikakus=grouped_shikakus,
            )
        else:
            message = "入力エラーがあります。"
            return render_template("update.html", id=id, form=form, message=message)

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

        # ユーザーマスタ一覧へ遷移
        message = "ユーザーの削除が完了しました。"
        users = userModel.userGetAll(get_connection())
        shikakus = userModel.getUserShikaku(get_connection())
        # 取得したshikakusの形式を変更
        grouped_shikakus = defaultdict(list)
        for shikaku in shikakus:
            grouped_shikakus[shikaku["user_id"]].append(shikaku["shikaku_name"])

        return render_template(
            "master.html",
            users=users,
            message=message,
            grouped_shikakus=grouped_shikakus,
        )
    else:
        return render_template("update.html", id="例外エラーです")


# 資格登録画面表示
@app.get("/shikaku_new")
def shikaku_new_get():
    return render_template("shikaku_new.html")


# 新規登録処理
@app.post("/shikaku_new")
def shikaku_new_post():
    shikakuCode = randomname(2)
    shikakuName = request.form["license"]

    with get_connection() as conn:
        with conn.cursor() as cur:
            query = """
                INSERT
                INTO shikaku(shikaku_code, shikaku_name)
                VALUES (%s, %s)
            """
            cur.execute(query, (shikakuCode, shikakuName))
        conn.commit()

    message = "資格を登録しました。"
    return render_template("index.html", message=message)
