import sqlite3
import json
import logging
from .config import DB_PATH

class DBManager:
    def __init__(self):
        self.conn = sqlite3.connect(DB_PATH, check_same_thread=False)
        self.cursor = self.conn.cursor()
        self.create_tables()

    def create_tables(self):
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                employee_id TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                face_encoding TEXT NOT NULL,
                mac_address INTEGER NOT NULL
            )
        ''')
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                start_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                end_time TIMESTAMP,
                absence_events INTEGER DEFAULT 0,
                FOREIGN KEY(user_id) REFERENCES users(id)
            )
        ''')
        self.conn.commit()

    def add_user(self, name, employee_id, password_hash, face_encoding, mac_address):
        try:
            encoding_json = json.dumps(face_encoding)
            self.cursor.execute('''
                INSERT INTO users (name, employee_id, password_hash, face_encoding, mac_address)
                VALUES (?, ?, ?, ?, ?)
            ''', (name, employee_id, password_hash, encoding_json, mac_address))
            self.conn.commit()
            return self.cursor.lastrowid
        except sqlite3.IntegrityError:
            return None

    def delete_user(self, user_id):
        self.cursor.execute('DELETE FROM users WHERE id = ?', (user_id,))
        self.conn.commit()

    def get_user_by_id(self, employee_id):
        self.cursor.execute('SELECT * FROM users WHERE employee_id = ?', (employee_id,))
        return self.cursor.fetchone()

    def log_session_start(self, user_id):
        self.cursor.execute('INSERT INTO sessions (user_id) VALUES (?)', (user_id,))
        self.conn.commit()
        return self.cursor.lastrowid

    def update_session_stats(self, session_id, absences):
        import datetime
        end_time = datetime.datetime.now()
        self.cursor.execute('''
            UPDATE sessions 
            SET end_time = ?, absence_events = ?
            WHERE id = ?
        ''', (end_time, absences, session_id))
        self.conn.commit()

    def close(self):
        self.conn.close()
