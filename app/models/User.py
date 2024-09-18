from psycopg2.extras import DictCursor


class User:
    # ユーザーマスタ一覧取得
    def userGetAll(self, conn):
        with conn:
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
