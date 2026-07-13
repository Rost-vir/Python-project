import sqlite3

DB_NAME = "library.db"

def connect():
    return sqlite3.connect(DB_NAME)

def init_db():
    with connect() as conn:
        cursor = conn.cursor()

        cursor.execute('''
        CREATE TABLE IF NOT EXISTS books (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            author TEXT,
            year INTEGER
        )''')

        cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            email TEXT
        )''')

        cursor.execute('''
        CREATE TABLE IF NOT EXISTS loans (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            book_id INTEGER,
            user_id INTEGER,
            issue_date TEXT,
            return_date TEXT,
            returned INTEGER DEFAULT 0
        )''')

if __name__ == "__main__":
    init_db()