import os
import psycopg2
import logging
DATABASE_URL = os.environ.get("DATABASE_URL")

def get_connection():
    try:
        return psycopg2.connect(DATABASE_URL)
    except Exception as e:
        print("❌ 데이터베이스 연결 실패:", e)
        raise

def init_db():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS group_chats (
            id SERIAL PRIMARY KEY,
            chat_id BIGINT UNIQUE
        )
    """)
    conn.commit()
    cur.close()
    conn.close()

def save_group_chat_id(chat_id: int):
    try:
        conn = get_connection()
        with conn:
            with conn.cursor() as cur:
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS group_chats (
                        id SERIAL PRIMARY KEY,
                        chat_id BIGINT UNIQUE
                    )
                """)
                cur.execute(
                    "INSERT INTO group_chats (chat_id) VALUES (%s) ON CONFLICT DO NOTHING",
                    (chat_id,)
                )
    except Exception as e:
        logging.warning(f"❌ 그룹 ID 저장 실패: {e}")

# 모든 그룹 ID 불러오기
def load_group_chat_ids():
    try:
        conn = get_connection()
        with conn:
            with conn.cursor() as cur:
                cur.execute("SELECT chat_id FROM group_chats")
                return [row[0] for row in cur.fetchall()]
    except Exception as e:
        logging.warning(f"❌ 그룹 ID 불러오기 실패: {e}")
        return []