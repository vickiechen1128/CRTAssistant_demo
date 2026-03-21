from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Optional, Any, Dict, List


BASE_DIR = Path(__file__).resolve().parents[2]
DATA_DIR = BASE_DIR / "data"
DB_PATH = DATA_DIR / "app.db"


def ensure_data_directory_exists() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)


def get_connection() -> sqlite3.Connection:
    ensure_data_directory_exists()
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def init_db() -> None:
    """初始化数据库表结构"""
    ensure_data_directory_exists()
    with get_connection() as connection:
        cursor = connection.cursor()
        # 示例表：items
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT,
                status TEXT DEFAULT 'pending',
                created_at TEXT DEFAULT (datetime('now')),
                updated_at TEXT DEFAULT (datetime('now'))
            );
            """
        )
        connection.commit()


# ===== Item CRUD Operations =====

def insert_item(title: str, description: Optional[str] = None) -> int:
    with get_connection() as connection:
        cursor = connection.cursor()
        cursor.execute(
            "INSERT INTO items (title, description) VALUES (?, ?)",
            (title, description),
        )
        connection.commit()
        return int(cursor.lastrowid)


def list_items() -> List[sqlite3.Row]:
    with get_connection() as connection:
        cursor = connection.cursor()
        cursor.execute(
            "SELECT id, title, description, status, created_at, updated_at FROM items ORDER BY id DESC"
        )
        return list(cursor.fetchall())


def get_item(item_id: int) -> Optional[sqlite3.Row]:
    with get_connection() as connection:
        cursor = connection.cursor()
        cursor.execute(
            "SELECT id, title, description, status, created_at, updated_at FROM items WHERE id = ?",
            (item_id,),
        )
        return cursor.fetchone()


def update_item(item_id: int, data: Dict[str, Any]) -> bool:
    allowed_fields = {"title", "description", "status"}
    updates = {k: v for k, v in data.items() if k in allowed_fields}
    if not updates:
        return False
    
    set_clause = ", ".join([f"{k} = ?" for k in updates.keys()])
    values = list(updates.values()) + [item_id]
    
    with get_connection() as connection:
        cursor = connection.cursor()
        cursor.execute(
            f"UPDATE items SET {set_clause}, updated_at = datetime('now') WHERE id = ?",
            values,
        )
        connection.commit()
        return cursor.rowcount > 0


def delete_item(item_id: int) -> bool:
    with get_connection() as connection:
        cursor = connection.cursor()
        cursor.execute("DELETE FROM items WHERE id = ?", (item_id,))
        connection.commit()
        return cursor.rowcount > 0
