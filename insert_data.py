import pandas as pd
import sqlite3

#df = pd.read_csv(r"D:\PROJECTBYME\travel_DATASET.csv")
df = pd.read_csv(r"D:\PROJECTBYME\cleaned_travel_DATASET.csv")

print(df.columns)

conn = sqlite3.connect("project.db")

df.to_sql(
    "DESTINATION",
    conn,
    if_exists="append",
    index=False
)

conn.commit()
conn.close()

print("Data inserted successfully!")