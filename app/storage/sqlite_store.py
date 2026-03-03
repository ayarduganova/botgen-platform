import json
import sqlite3
from typing import Optional

from app.runtime.session import SessionState

class SQLiteSessionStore:
    def __init__(self, db_path: str = "botgen.db") -> None:
        # путь к файлу базы
        self.db_path = db_path
        # создаём таблицу
        self._init_db()

    # соединение с sqlite
    def _connect(self) -> sqlite3.Connection:
        # открываем файл базы данных
        # check_same_thread=False — разрешает использовать соединение в разных потоках
        conn = sqlite3.connect(self.db_path, check_same_thread=False)
        # запрос - словарь
        conn.row_factory = sqlite3.Row
        return conn

    # создаём таблицу sessions, если её нет.
    def _init_db(self) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS sessions (
                    session_id TEXT PRIMARY KEY,
                    current_node_id TEXT NOT NULL,
                    slots_json TEXT NOT NULL,
                    awaiting_slot TEXT,
                    is_finished INTEGER NOT NULL
                )
                """
            )
            conn.commit()

    # возвращаем состояние сессии по session_id
    def get(self, session_id: str) -> Optional[SessionState]:
        # запрос в бд
        with self._connect() as conn:
            row = conn.execute(
                "SELECT session_id, current_node_id, slots_json, awaiting_slot, is_finished FROM sessions WHERE session_id = ?",
                (session_id,),
            ).fetchone()

        if row is None:
            return None

        # достаём слоты
        slots = json.loads(row["slots_json"]) if row["slots_json"] else {}
        # создаём SessionState
        return SessionState(
            session_id=row["session_id"],
            current_node_id=row["current_node_id"],
            slots=slots,
            awaiting_slot=row["awaiting_slot"],
            is_finished=bool(row["is_finished"]),
        )

    # сохраняем (или обновляем) состояние сессии в SQLite.
    def save(self, session: SessionState) -> None:
        # превращаем dict в JSON строку
        slots_json = json.dumps(session.slots, ensure_ascii=False)

        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO sessions (session_id, current_node_id, slots_json, awaiting_slot, is_finished)
                VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(session_id) DO UPDATE SET
                    current_node_id=excluded.current_node_id,
                    slots_json=excluded.slots_json,
                    awaiting_slot=excluded.awaiting_slot,
                    is_finished=excluded.is_finished
                """,
                (
                    session.session_id,
                    session.current_node_id,
                    slots_json,
                    session.awaiting_slot,
                    1 if session.is_finished else 0,
                ),
            )
            conn.commit()