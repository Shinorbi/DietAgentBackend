import sqlite3
from sqlite3 import Error

def create_connection():
    """Create a database connection to a SQLite database"""
    conn = None
    try:
        conn = sqlite3.connect('diet_ai_agent.db')
        print("Connection to SQLite DB successful")
    except Error as e:
        print(f"Error: {e}")
    return conn

def create_tables(conn):
    """Create tables for the diet AI agent"""
    try:
        cursor = conn.cursor()

        # Users table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            weight REAL,
            height REAL,
            goal TEXT,
            activity_level TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)

        # Meal logs table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS meal_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            meal_type TEXT,
            foods TEXT,
            calories REAL,
            protein REAL,
            carbs REAL,
            fat REAL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
        """)

        # Diet plans table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS diet_plans (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            daily_calories INTEGER,
            protein_grams REAL,
            carbs_grams REAL,
            fat_grams REAL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
        """)

        # Progress table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS progress (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            weight REAL,
            calories_consumed INTEGER,
            calories_burned INTEGER,
            date DATE,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
        """)

        conn.commit()
        print("Tables created successfully")
    except Error as e:
        print(f"Error creating tables: {e}")