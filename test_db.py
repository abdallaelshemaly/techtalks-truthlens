import sqlite3

# connect to database (it will be created if it doesn’t exist)
conn = sqlite3.connect("test.db")

# create a cursor
cursor = conn.cursor()

# create a test table
cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY,
    name TEXT
)
""")

# insert test data
cursor.execute("INSERT INTO users (name) VALUES (?)", ("Test User",))

# read data
cursor.execute("SELECT * FROM users")
rows = cursor.fetchall()

print(rows)

conn.commit()
conn.close()