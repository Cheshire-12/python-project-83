from contextlib import contextmanager
from psycopg2.extras import DictCursor
from datetime import datetime

class AnalyzeRepo():
    def __init__(self, pool) -> None:
        self.pool = pool
    
    @contextmanager
    def _get_conn(self, commit=False):
        """
        Вспомогательный контекстный менеджер.
        Автоматически берет соединение из пула и возвращает его обратно.
        """
        conn = self.pool.getconn()
        try:
            yield conn
            if commit:
                conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            self.pool.putconn(conn)

    def get_content(self):
        with self._get_conn() as conn:
            with conn.cursor(cursor_factory=DictCursor) as cur:
                cur.execute("SELECT * FROM urls ORDER BY created_at DESC")
                return [dict(row) for row in cur.fetchall()]

    def get_one_url(self, id):
        with self._get_conn() as conn:
            with conn.cursor(cursor_factory=DictCursor) as cur:
                cur.execute("SELECT * FROM urls WHERE id = %s", (id,))
                row = cur.fetchone()
                return dict(row) if row else None
    
    def check_url_exists(self, url):
        with self._get_conn() as conn:
            with conn.cursor(cursor_factory=DictCursor) as cur:
                cur.execute("SELECT * FROM urls WHERE name = %s", (url,))
                row = cur.fetchone()
                return dict(row) if row else None

    def create(self, url_data):
        with self._get_conn(commit=True) as conn:
            with conn.cursor() as cur:
                cur.execute("INSERT INTO urls (name, created_at) VALUES (%s, %s) RETURNING id", (url_data.get("url"), datetime.now()))
                return cur.fetchone()[0]

    def delete(self, id):
        with self._get_conn(commit=True) as conn:
            with conn.cursor() as cur:
                cur.execute("DELETE FROM urls WHERE id = %s", (id,))