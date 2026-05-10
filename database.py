import sqlite3
from datetime import datetime
import hashlib
import os

DB_PATH = 'anomaly_detection.db'

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    if not os.path.exists(DB_PATH):
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE predictions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                filename TEXT NOT NULL,
                file_type TEXT NOT NULL,
                prediction_result TEXT NOT NULL,
                anomaly_type TEXT,
                anomaly_score REAL,
                frame_details TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        conn.commit()
        conn.close()
        print("Database created successfully")
    else:
        print("Database already exists")

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def create_user(username, email, password):
    conn = get_db_connection()
    cursor = conn.cursor()
    hashed_pw = hash_password(password)
    try:
        cursor.execute('INSERT INTO users (username, email, password) VALUES (?, ?, ?)',
                      (username, email, hashed_pw))
        conn.commit()
        conn.close()
        return True
    except sqlite3.IntegrityError:
        conn.close()
        return False

def verify_user(username, password):
    conn = get_db_connection()
    cursor = conn.cursor()
    hashed_pw = hash_password(password)
    cursor.execute('SELECT * FROM users WHERE username = ? AND password = ?',
                  (username, hashed_pw))
    user = cursor.fetchone()
    conn.close()
    return user

def get_user_by_id(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))
    user = cursor.fetchone()
    conn.close()
    return user

def save_prediction(user_id, filename, file_type, prediction_result, anomaly_type, anomaly_score, frame_details=None):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO predictions (user_id, filename, file_type, prediction_result, anomaly_type, anomaly_score, frame_details)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (user_id, filename, file_type, prediction_result, anomaly_type, anomaly_score, frame_details))
    prediction_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return prediction_id

def get_user_predictions(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM predictions WHERE user_id = ? ORDER BY created_at DESC', (user_id,))
    predictions = cursor.fetchall()
    conn.close()
    return predictions

def get_prediction_by_id(prediction_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM predictions WHERE id = ?', (prediction_id,))
    prediction = cursor.fetchone()
    conn.close()
    return prediction