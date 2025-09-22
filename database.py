# database.py
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

DB_NAME = 'chat_app.db'

def get_db_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initializes the database by creating necessary tables."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            profile_pic_url TEXT
        );
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS friendships (
            id INTEGER PRIMARY KEY,
            user1_id INTEGER,
            user2_id INTEGER,
            status TEXT,
            FOREIGN KEY(user1_id) REFERENCES users(id),
            FOREIGN KEY(user2_id) REFERENCES users(id)
        );
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY,
            sender_id INTEGER,
            recipient_id INTEGER,
            content TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            message_type TEXT,
            FOREIGN KEY(sender_id) REFERENCES users(id),
            FOREIGN KEY(recipient_id) REFERENCES users(id)
        );
    """)
    conn.commit()
    conn.close()

def create_user(username, email, password):
    """Inserts a new user into the database."""
    conn = get_db_connection()
    cursor = conn.cursor()
    hashed_password = generate_password_hash(password)
    try:
        cursor.execute("INSERT INTO users (username, email, password_hash) VALUES (?, ?, ?)",
                       (username, email, hashed_password))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False  # Username or email already exists
    finally:
        conn.close()

def get_user_by_username(username):
    """Retrieves a user's details by their username."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
    user = cursor.fetchone()
    conn.close()
    return user

def get_user_by_id(user_id):
    """Retrieves a user's details by their ID."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    user = cursor.fetchone()
    conn.close()
    return user

def authenticate_user(username, password):
    """Checks if a username and password match."""
    user = get_user_by_username(username)
    if user and check_password_hash(user['password_hash'], password):
        return user
    return None

def save_message(sender_id, recipient_id, content, message_type):
    """Saves a new message to the database."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO messages (sender_id, recipient_id, content, message_type) VALUES (?, ?, ?, ?)",
                   (sender_id, recipient_id, content, message_type))
    conn.commit()
    conn.close()