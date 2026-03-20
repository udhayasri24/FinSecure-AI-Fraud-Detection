import sqlite3

conn = sqlite3.connect("fraud.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS transactions (
    id TEXT,
    time TEXT,
    probability REAL,
    label TEXT
)
""")

def save_transaction(txn_id, time, prob, label):
    cursor.execute(
        "INSERT INTO transactions VALUES (?, ?, ?, ?)",
        (txn_id, time, prob, label)
    )
    conn.commit()
def get_all_transactions():
    cursor.execute("SELECT * FROM transactions")
    return cursor.fetchall()