import sqlite3

conn = sqlite3.connect("users.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    username TEXT,
    password TEXT
)
""")

cursor.execute("INSERT INTO users VALUES ('admin', 'admin')")

conn.commit()
conn.close()

print("User created!")