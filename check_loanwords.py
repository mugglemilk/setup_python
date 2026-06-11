import sqlite3
import re

conn = sqlite3.connect('synonyms.db')
cursor = conn.cursor()
cursor.execute('SELECT word FROM word_mappings ORDER BY word')
rows = cursor.fetchall()
conn.close()

# คำทับศัพท์มักมีตัวอักษรที่ไม่ใช่ภาษาไทยปนอยู่
# หรือเป็นคำที่ออกเสียงแบบภาษาต่างประเทศ
suspicious = []

for row in rows:
    word = row[0]
    # เช็คคำที่มีตัวอักษรภาษาอังกฤษปนอยู่
    if re.search(r'[a-zA-Z]', word):
        suspicious.append(f"[มีตัวอังกฤษ] {word}")
    # เช็คคำที่มีตัวเลขปนอยู่
    elif re.search(r'[0-9]', word):
        suspicious.append(f"[มีตัวเลข] {word}")

print(f"พบคำน่าสงสัย {len(suspicious)} คำ")
for w in suspicious:
    print(w)