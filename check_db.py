import sqlite3
conn = sqlite3.connect('db.sqlite3')
cursor = conn.cursor()
# List all tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
print(cursor.fetchall())
# Show auth_user contents
cursor.execute("SELECT * FROM auth_user;")
print(cursor.fetchall())
conn.close()