import sqlite3
from pathlib import Path

# Use the existing database folder in the project root
BASE_DIR = Path(__file__).resolve().parent.parent
DB_DIR = BASE_DIR / "database"

DB_DIR.mkdir(parents=True, exist_ok=True)

DB_PATH = DB_DIR / "pharma.db"


def get_connection():
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def initialize_db():

    with get_connection() as connection:

        connection.execute("""
            CREATE TABLE IF NOT EXISTS search_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                search_type TEXT NOT NULL,
                search_value TEXT NOT NULL,
                searched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        connection.execute("""
            CREATE TABLE IF NOT EXISTS references_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                search_id INTEGER,
                source_name TEXT NOT NULL,
                reference_url TEXT NOT NULL,
                source_type TEXT,
                verification_status TEXT DEFAULT 'pending',
                verified_at TIMESTAMP,
                FOREIGN KEY (search_id)
                REFERENCES search_history(id)
            )
        """)


def save_search(search_type, search_value):

    with get_connection() as connection:

        cursor = connection.execute("""
            INSERT INTO search_history
            (search_type, search_value)
            VALUES (?, ?)
        """, (search_type, search_value))

        return cursor.lastrowid


def save_references(search_id, references):

    with get_connection() as connection:

        for reference in references:

            connection.execute("""
                INSERT INTO references_data
                (search_id, source_name, reference_url, source_type)
                VALUES (?, ?, ?, ?)
            """, (
                search_id,
                reference["source_name"],
                reference["reference_url"],
                reference["source_type"]
            ))


def get_search_history():

    with get_connection() as connection:

        cursor = connection.execute("""
            SELECT *
            FROM search_history
            ORDER BY searched_at DESC
        """)

        return [dict(row) for row in cursor.fetchall()]


def get_references(search_id):

    with get_connection() as connection:

        cursor = connection.execute("""
            SELECT *
            FROM references_data
            WHERE search_id = ?
        """, (search_id,))

        return [dict(row) for row in cursor.fetchall()]


def update_verification(reference_id, status):

    if status not in ["pending", "verified", "rejected"]:
        raise ValueError("Invalid verification status")

    with get_connection() as connection:

        cursor = connection.execute("""
            UPDATE references_data
            SET verification_status = ?,
                verified_at = CASE
                    WHEN ? = 'verified' THEN CURRENT_TIMESTAMP
                    ELSE NULL
                END
            WHERE id = ?
        """, (status, status, reference_id))

        return cursor.rowcount > 0