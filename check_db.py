import sqlite3
conn = sqlite3.connect('synonyms.db')
cursor = conn.cursor()

cursor.execute('SELECT COUNT(*) FROM word_mappings')
print(f"จำนวนคำทั้งหมด: {cursor.fetchone()[0]} คำ")

cursor.execute('SELECT COUNT(*) FROM synonym_groups')
print(f"จำนวนกลุ่มคำ: {cursor.fetchone()[0]} กลุ่ม")

conn.close()