from psycopg2.extras import DictCursor


class User:
    # ユーザーマスタ一覧取得
    def userGetAll(self, conn):
        with conn:
            with conn.cursor(cursor_factory=DictCursor) as cur:
                cur.execute("""
                    SELECT
                        u.user_id
                        , u.name
                        , u.mail
                        , u.created_at
                    FROM
                        users AS u
                    ORDER BY
                        u.created_at
                """)
                return cur.fetchall()

    # ユーザーが持つ資格を取得
    def getUserShikaku(self, conn):
        with conn:
            with conn.cursor(cursor_factory=DictCursor) as cur:
                cur.execute("""
                    SELECT
                        us.user_id
                        , s.shikaku_name
                    FROM
                        user_shikaku AS us
                        LEFT JOIN shikaku AS s
                            ON s.shikaku_code = us.shikaku_code
                """)
                return cur.fetchall()
