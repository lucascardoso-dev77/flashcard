"""
database.py
Camada de acesso a dados (SQLite) para o sistema de flashcards.
Guarda o banco em %APPDATA%/FlashCardsApp/flashcards.db no Windows,
ou em ./flashcards.db se rodar fora do Windows (ex: para testes).
"""

import os
import sqlite3
import sys
from datetime import datetime


def get_db_path() -> str:
    """Retorna o caminho do arquivo do banco de dados, criando a pasta se preciso."""
    if sys.platform == "win32":
        base = os.environ.get("APPDATA", os.path.expanduser("~"))
        folder = os.path.join(base, "FlashCardsApp")
    else:
        # Fallback para desenvolvimento/teste em outros sistemas
        folder = os.path.join(os.path.expanduser("~"), ".flashcardsapp")

    os.makedirs(folder, exist_ok=True)
    return os.path.join(folder, "flashcards.db")


SCHEMA = """
CREATE TABLE IF NOT EXISTS decks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS cards (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    deck_id INTEGER NOT NULL,
    front TEXT NOT NULL,
    back TEXT NOT NULL,
    created_at TEXT NOT NULL,

    -- Campos do algoritmo de repeticao espacada (SM-2)
    ease_factor REAL NOT NULL DEFAULT 2.5,
    interval_days REAL NOT NULL DEFAULT 0,
    repetitions INTEGER NOT NULL DEFAULT 0,
    due_date TEXT NOT NULL,
    last_reviewed TEXT,

    FOREIGN KEY (deck_id) REFERENCES decks(id) ON DELETE CASCADE
);
"""


class Database:
    def __init__(self, path: str = None):
        self.path = path or get_db_path()
        self.conn = sqlite3.connect(self.path)
        self.conn.execute("PRAGMA foreign_keys = ON")
        self.conn.row_factory = sqlite3.Row
        self.conn.executescript(SCHEMA)
        self.conn.commit()

    # ---------- Decks ----------

    def create_deck(self, name: str) -> int:
        name = name.strip()
        if not name:
            raise ValueError("O nome do deck nao pode ser vazio.")
        cur = self.conn.execute(
            "INSERT INTO decks (name, created_at) VALUES (?, ?)",
            (name, datetime.now().isoformat()),
        )
        self.conn.commit()
        return cur.lastrowid

    def list_decks(self):
        return self.conn.execute(
            "SELECT * FROM decks ORDER BY name COLLATE NOCASE"
        ).fetchall()

    def delete_deck(self, deck_id: int):
        self.conn.execute("DELETE FROM decks WHERE id = ?", (deck_id,))
        self.conn.commit()

    def rename_deck(self, deck_id: int, new_name: str):
        new_name = new_name.strip()
        if not new_name:
            raise ValueError("O nome do deck nao pode ser vazio.")
        self.conn.execute("UPDATE decks SET name = ? WHERE id = ?", (new_name, deck_id))
        self.conn.commit()

    def deck_stats(self, deck_id: int):
        """Retorna (total_cards, due_now) para um deck."""
        total = self.conn.execute(
            "SELECT COUNT(*) AS c FROM cards WHERE deck_id = ?", (deck_id,)
        ).fetchone()["c"]
        now = datetime.now().isoformat()
        due = self.conn.execute(
            "SELECT COUNT(*) AS c FROM cards WHERE deck_id = ? AND due_date <= ?",
            (deck_id, now),
        ).fetchone()["c"]
        return total, due

    # ---------- Cards ----------

    def add_card(self, deck_id: int, front: str, back: str) -> int:
        front, back = front.strip(), back.strip()
        if not front or not back:
            raise ValueError("Frente e verso do card nao podem ser vazios.")
        now = datetime.now().isoformat()
        cur = self.conn.execute(
            """INSERT INTO cards
               (deck_id, front, back, created_at, ease_factor, interval_days,
                repetitions, due_date, last_reviewed)
               VALUES (?, ?, ?, ?, 2.5, 0, 0, ?, NULL)""",
            (deck_id, front, back, now, now),
        )
        self.conn.commit()
        return cur.lastrowid

    def update_card(self, card_id: int, front: str, back: str):
        front, back = front.strip(), back.strip()
        if not front or not back:
            raise ValueError("Frente e verso do card nao podem ser vazios.")
        self.conn.execute(
            "UPDATE cards SET front = ?, back = ? WHERE id = ?",
            (front, back, card_id),
        )
        self.conn.commit()

    def delete_card(self, card_id: int):
        self.conn.execute("DELETE FROM cards WHERE id = ?", (card_id,))
        self.conn.commit()

    def list_cards(self, deck_id: int):
        return self.conn.execute(
            "SELECT * FROM cards WHERE deck_id = ? ORDER BY created_at", (deck_id,)
        ).fetchall()

    def get_due_cards(self, deck_id: int):
        """Cards cuja due_date ja passou (ate agora), mais atrasados primeiro."""
        now = datetime.now().isoformat()
        return self.conn.execute(
            """SELECT * FROM cards WHERE deck_id = ? AND due_date <= ?
               ORDER BY due_date ASC""",
            (deck_id, now),
        ).fetchall()

    def save_review(self, card_id: int, ease_factor: float, interval_days: int,
                     repetitions: int, due_date: str):
        self.conn.execute(
            """UPDATE cards
               SET ease_factor = ?, interval_days = ?, repetitions = ?,
                   due_date = ?, last_reviewed = ?
               WHERE id = ?""",
            (ease_factor, interval_days, repetitions, due_date,
             datetime.now().isoformat(), card_id),
        )
        self.conn.commit()

    def close(self):
        self.conn.close()
