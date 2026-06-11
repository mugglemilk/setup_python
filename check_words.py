import sqlite3
conn = sqlite3.connect('synonyms.db')
cursor = conn.cursor()
cursor.execute('SELECT word FROM word_mappings ORDER BY word')
rows = cursor.fetchall()
conn.close()
for row in rows:
    print(row[0])