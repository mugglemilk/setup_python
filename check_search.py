import sqlite3

conn = sqlite3.connect('synonyms.db')
cursor = conn.cursor()

cursor.execute('''
    SELECT sg.group_id, sg.source, COUNT(wm.word) as word_count
    FROM synonym_groups sg
    JOIN word_mappings wm ON sg.group_id = wm.group_id
    GROUP BY sg.group_id
    HAVING word_count <= 2
    ORDER BY word_count
    LIMIT 20
''')
rows = cursor.fetchall()
print(f"กลุ่มที่มีคำน้อยเกินไป: {len(rows)} กลุ่ม")
for r in rows:
    cursor.execute('SELECT word FROM word_mappings WHERE group_id = ?', (r[0],))
    words = [w[0] for w in cursor.fetchall()]
    print(f"  group {r[0]} ({r[2]} คำ) [{r[1]}]: {words}")

conn.close()