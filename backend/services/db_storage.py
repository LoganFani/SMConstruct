import sqlite3
from typing import Optional
from utils import paths


def get_db_connection():
    conn = sqlite3.connect(paths.DATA_BASE_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    with get_db_connection() as conn:
        cursor = conn.cursor()

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS language_configs (
                id        INTEGER PRIMARY KEY AUTOINCREMENT,
                name      TEXT NOT NULL,
                from_lang TEXT NOT NULL,
                to_lang   TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS videos (
                id         TEXT PRIMARY KEY,
                title      TEXT NOT NULL,
                from_lang  TEXT NOT NULL,
                to_lang    TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS cards (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                video_id    TEXT NOT NULL REFERENCES videos(id),
                word        TEXT NOT NULL,
                context     TEXT,
                translation TEXT,
                frame_path  TEXT,
                audio_path  TEXT,
                created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        conn.commit()


# ── Language Configs ──────────────────────────────────────────────────────────

def insert_language_config(name: str, from_lang: str, to_lang: str) -> dict:
    with get_db_connection() as conn:
        cursor = conn.execute(
            "INSERT INTO language_configs (name, from_lang, to_lang) VALUES (?, ?, ?)",
            (name, from_lang, to_lang)
        )
        conn.commit()
        row = conn.execute(
            "SELECT * FROM language_configs WHERE id = ?", (cursor.lastrowid,)
        ).fetchone()
        return dict(row)


def get_all_language_configs() -> list:
    with get_db_connection() as conn:
        rows = conn.execute(
            "SELECT * FROM language_configs ORDER BY created_at DESC"
        ).fetchall()
        return [dict(r) for r in rows]


def delete_language_config(config_id: int) -> bool:
    with get_db_connection() as conn:
        cursor = conn.execute(
            "DELETE FROM language_configs WHERE id = ?", (config_id,)
        )
        conn.commit()
        return cursor.rowcount > 0


# ── Videos ───────────────────────────────────────────────────────────────────

def insert_video(video_id: str, title: str, from_lang: str, to_lang: str) -> None:
    with get_db_connection() as conn:
        conn.execute(
            "INSERT OR IGNORE INTO videos (id, title, from_lang, to_lang) VALUES (?, ?, ?, ?)",
            (video_id, title, from_lang, to_lang)
        )
        conn.commit()


def get_all_videos() -> list:
    with get_db_connection() as conn:
        rows = conn.execute(
            "SELECT * FROM videos ORDER BY created_at DESC"
        ).fetchall()
        return [dict(r) for r in rows]


def get_video(video_id: str) -> Optional[dict]:
    with get_db_connection() as conn:
        row = conn.execute(
            "SELECT * FROM videos WHERE id = ?", (video_id,)
        ).fetchone()
        return dict(row) if row else None


# ── Cards ─────────────────────────────────────────────────────────────────────

def insert_card(
    video_id: str,
    word: str,
    context: str,
    translation: str,
    frame_path: Optional[str] = None,
    audio_path: Optional[str] = None,
) -> int:
    with get_db_connection() as conn:
        cursor = conn.execute(
            '''INSERT INTO cards
               (video_id, word, context, translation, frame_path, audio_path)
               VALUES (?, ?, ?, ?, ?, ?)''',
            (video_id, word, context, translation, frame_path, audio_path)
        )
        conn.commit()
        return cursor.lastrowid


def get_cards_for_video(video_id: str) -> list:
    with get_db_connection() as conn:
        rows = conn.execute(
            "SELECT * FROM cards WHERE video_id = ? ORDER BY created_at DESC",
            (video_id,)
        ).fetchall()
        return [dict(r) for r in rows]


def delete_card(card_id: int) -> bool:
    with get_db_connection() as conn:
        cursor = conn.execute("DELETE FROM cards WHERE id = ?", (card_id,))
        conn.commit()
        return cursor.rowcount > 0


init_db()