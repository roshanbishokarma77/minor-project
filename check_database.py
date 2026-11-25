import sqlite3

conn = sqlite3.connect("project.db")
cursor = conn.cursor()

# Check total rows
cursor.execute("SELECT COUNT(*) FROM DESTINATION")
count = cursor.fetchone()[0]

print("Total rows in DESTINATION table:", count)

# Display first 5 rows
cursor.execute("SELECT * FROM DESTINATION LIMIT 5")
rows = cursor.fetchall()

for row in rows:
    print(row)

conn.close()