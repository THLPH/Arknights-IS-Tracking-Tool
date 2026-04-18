import sqlite3

conn = sqlite3.connect('rhodes.db')
cursor = conn.cursor()

# Remove quotes from relic names
cursor.execute("UPDATE Relic SET Name = REPLACE(REPLACE(Name, '\'', ''), '\"', '')")
# Remove quotes from operator names
cursor.execute("UPDATE Operator SET Name = REPLACE(REPLACE(Name, '\'', ''), '\"', '')")

conn.commit()
conn.close()
print("Quotes removed from names.")