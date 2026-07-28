import sqlite3

def create_database():
    conn = sqlite3.connect("employees.db")
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS employees (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        department TEXT NOT NULL,
        position TEXT NOT NULL,
        salary REAL NOT NULL,
        status TEXT NOT NULL
    )
    """)

    conn.commit()
    conn.close()

    print("Database and Employee table created successfully!")

if __name__ == "__main__":
    create_database()