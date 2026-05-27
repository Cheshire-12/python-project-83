import psycopg2
from contextlib import contextmanager
from datetime import datetime

from psycopg2.extras import DictCursor


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
        force_close = False
        try:
            yield conn
            if commit:
                conn.commit()
        except (psycopg2.OperationalError, psycopg2.InterfaceError):
            force_close = True
            raise
        except Exception:
            if conn and not conn.closed:
                conn.rollback()
            raise
        finally:
            if conn:
                self.pool.putconn(conn, close=force_close or bool(conn.closed))

    def get_content(self):
        """Получение списка всех URL и их последних проверок"""
        with self._get_conn() as conn:
            with conn.cursor(cursor_factory=DictCursor) as cur:
                query = """
                SELECT DISTINCT ON (urls.id)
                    urls.id,
                    urls.name,
                    url_checks.created_at AS last_check_date,
                    url_checks.status_code AS last_status_code
                FROM urls
                LEFT JOIN url_checks ON urls.id = url_checks.url_id
                ORDER BY urls.id DESC;
                """
                cur.execute(query)
                return [dict(row) for row in cur.fetchall()]

    def get_one_url(self, id):
        """Получение информации о конкретном URL"""
        with self._get_conn() as conn:
            with conn.cursor(cursor_factory=DictCursor) as cur:
                cur.execute("SELECT * FROM urls WHERE id = %s", (id,))
                row = cur.fetchone()
                return dict(row) if row else None
    
    def check_url_exists(self, url):
        """Проверка существования URL"""
        with self._get_conn() as conn:
            with conn.cursor(cursor_factory=DictCursor) as cur:
                cur.execute("SELECT id FROM urls WHERE name = %s", (url,))
                row = cur.fetchone()
                return dict(row) if row else None

    def create(self, url_data):
        """Создание новой записи URL и возврат ее ID"""
        with self._get_conn(commit=True) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO urls (name, created_at)
                    VALUES (%s, %s)
                    RETURNING id
                    """,
                    (url_data.get("url"), datetime.now())
                    )
                return cur.fetchone()[0]

    def delete(self, id):
        """Удаление записи URL"""
        with self._get_conn(commit=True) as conn:
            with conn.cursor() as cur:
                cur.execute("DELETE FROM urls WHERE id = %s", (id,))
    
    def create_check(self, id, gathered_data):
        """Создание новой записи проверки URL"""
        with self._get_conn(commit=True) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO url_checks
                    (url_id, status_code, h1, title, description, created_at)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    """,
                    (
                        id,
                        gathered_data.get("status_code"),
                        gathered_data.get("h1"),
                        gathered_data.get("title"),
                        gathered_data.get("description"),
                        datetime.now()
                    )
                )

    def get_analyze_results(self, url_id):
        """Получение всех проверок для конкретного URL"""
        with self._get_conn() as conn:
            from psycopg2.extras import DictCursor
            with conn.cursor(cursor_factory=DictCursor) as cur:
                cur.execute(
                    "SELECT * FROM url_checks WHERE url_id = %s ORDER BY id",
                    (url_id,)
                )
                return [dict(row) for row in cur.fetchall()]