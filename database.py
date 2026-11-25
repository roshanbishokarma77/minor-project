import sqlite3
import pandas as pd
import ast

# Connect to database
conn = sqlite3.connect("project.db")
cursor = conn.cursor()

# Delete old tables (optional during development)
# cursor.execute("DROP TABLE IF EXISTS MANAGE")
# cursor.execute("DROP TABLE IF EXISTS SEARCH")
# cursor.execute("DROP TABLE IF EXISTS ADMIN")
#cursor.execute("DROP TABLE IF EXISTS USER")
# cursor.execute("DROP TABLE IF EXISTS DESTINATION")

# ================= USER TABLE =================
cursor.execute("""
CREATE TABLE IF NOT EXISTS USER (
    user_ID INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL
)
""")

# ================= ADMIN TABLE =================
cursor.execute("""
CREATE TABLE IF NOT EXISTS ADMIN (
    admin_ID INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL
)
""")

# ================= DESTINATION TABLE =================
# Schema updated to match cleaned_travel_DATASET.csv exactly.
# - best_month_to_visit / estimated_travel_days / estimated_cost_per_person
#   (raw range-strings) are replaced with the parsed numeric/list columns
#   we engineered during preprocessing.
# - tags / tags_clean now stored as TEXT (tags_clean_list stored as a
#   comma-separated string since SQLite has no native list/array type).
cursor.execute("""
CREATE TABLE IF NOT EXISTS DESTINATION (
    pID INTEGER PRIMARY KEY,
    pName TEXT NOT NULL,
    province INTEGER,
    history REAL,
    culture REAL,
    sightseeing REAL,
    wildlife REAL,
    adventure REAL,
    tags_clean TEXT,
    tags_clean_list TEXT,
    best_months TEXT,
    min_travel_days INTEGER,
    max_travel_days INTEGER,
    min_estimated_cost_per_person INTEGER,
    max_estimated_cost_per_person INTEGER
)
""")

# ================= SEARCH TABLE =================
cursor.execute("""
CREATE TABLE IF NOT EXISTS SEARCH (
    search_ID INTEGER PRIMARY KEY AUTOINCREMENT,
    user_ID INTEGER,
    pID INTEGER,

    FOREIGN KEY(user_ID)
        REFERENCES USER(user_ID),

    FOREIGN KEY(pID)
        REFERENCES DESTINATION(pID)
)
""")

# ================= MANAGE TABLE =================
# Tracks admin actions on destinations (add / edit / delete) for auditing.
cursor.execute("""
CREATE TABLE IF NOT EXISTS MANAGE (
    manage_ID INTEGER PRIMARY KEY AUTOINCREMENT,
    admin_ID INTEGER,
    pID INTEGER,
    action TEXT,
    action_date TEXT DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY(admin_ID)
        REFERENCES ADMIN(admin_ID),

    FOREIGN KEY(pID)
        REFERENCES DESTINATION(pID)
)
""")

conn.commit()

# ================= POPULATE DESTINATION TABLE FROM CSV =================
df = pd.read_csv("cleaned_travel_DATASET.csv")

# tags_clean_list and best_months come out of the CSV as string-repr lists
# e.g. "['hindu', 'temple']" -> convert to real lists, then join as CSV text
# for storage (SQLite has no array type).
def to_csv_string(value):
    if isinstance(value, str):
        try:
            parsed = ast.literal_eval(value)
            if isinstance(parsed, list):
                return ", ".join(parsed)
        except (ValueError, SyntaxError):
            pass
    return value

df["tags_clean_list"] = df["tags_clean_list"].apply(to_csv_string)
df["best_months"] = df["best_months"].apply(to_csv_string)

rows = df[[
    "pID", "pName", "province", "history", "culture", "sightseeing",
    "wildlife", "adventure", "tags_clean", "tags_clean_list", "best_months",
    "min_travel_days", "max_travel_days",
    "min_estimated_cost_per_person", "max_estimated_cost_per_person"
]].values.tolist()

cursor.executemany("""
INSERT OR REPLACE INTO DESTINATION (
    pID, pName, province, history, culture, sightseeing,
    wildlife, adventure, tags_clean, tags_clean_list, best_months,
    min_travel_days, max_travel_days,
    min_estimated_cost_per_person, max_estimated_cost_per_person
) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
""", rows)

conn.commit()

# Print table structures
cursor.execute("PRAGMA table_info(USER)")
print("USER TABLE:")
print(cursor.fetchall())

cursor.execute("PRAGMA table_info(ADMIN)")
print("ADMIN TABLE:")
print(cursor.fetchall())

cursor.execute("PRAGMA table_info(DESTINATION)")
print("DESTINATION TABLE:")
print(cursor.fetchall())

cursor.execute("SELECT COUNT(*) FROM DESTINATION")
print(f"\nDESTINATION rows inserted: {cursor.fetchone()[0]}")

cursor.execute("SELECT * FROM DESTINATION LIMIT 2")
print("\nSample rows:")
for row in cursor.fetchall():
    print(row)

conn.close()

print("\nDatabase created and populated successfully!")