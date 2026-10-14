import sqlite3

conn = sqlite3.connect("portfolio.db")
cursor = conn.cursor()

cursor.execute("""
    CREATE TABLE IF NOT EXISTS purchases (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ticker TEXT NOT NULL,
        quantity REAL NOT NULL,
        price REAL NOT NULL,
        purchase_date TEXT NOT NULL
    )
""")
conn.commit()

from db import init_db, add_purchase, get_positions

init_db()
add_purchase("VUAA", 2.5, 98.47, "2026-10-12")

for position in get_positions():
    print(position)