import ast
import re
import sqlite3
from collections import defaultdict


def load_csv(path):
    data = []
    with open(path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    for line in lines[1:]:
        line = line.strip()
        if not line:
            continue
        parts = line.split(',', 2)
        if len(parts) >= 3:
            word = parts[0].strip()
            pos = parts[1].strip()
            syns = set(s.strip() for s in parts[2].split('|') if s.strip())
            data.append((word, pos, syns))
    return data


def load_synonym_py(path):
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()
    clean = re.sub(r'#[^\n]*', '', content)
    return ast.literal_eval(clean.strip())


def merge(csv_data, py_groups):
    py_word_to_groups = defaultdict(set)
    for gi, group in enumerate(py_groups):
        for w in group:
            py_word_to_groups[w].add(gi)

    csv_map = {}
    csv_order = []
    for word, pos, syns in csv_data:
        csv_map[word] = [pos, set(syns)]
        csv_order.append(word)

    consumed = set()
    for word in csv_order:
        pos, syns = csv_map[word]
        for gi in py_word_to_groups.get(word, set()):
            if gi not in consumed:
                consumed.add(gi)
                syns.update(set(py_groups[gi]) - {word})

    for gi, group in enumerate(py_groups):
        if gi not in consumed and group:
            canonical = group[0]
            csv_map[canonical] = ['n', set(group[1:])]
            csv_order.append(canonical)

    return csv_map, csv_order


def create_db():
    print("โหลดข้อมูลจาก data.csv ...")
    csv_data = load_csv('data.csv')
    print(f"  {len(csv_data)} entries")

    print("โหลดข้อมูลจาก synonym.py ...")
    py_groups = load_synonym_py('synonym.py')
    print(f"  {len(py_groups)} groups")

    print("Merge ข้อมูล ...")
    csv_map, csv_order = merge(csv_data, py_groups)
    print(f"  {len(csv_order)} total entries after merge")

    conn = sqlite3.connect('synonyms.db')
    cursor = conn.cursor()

    cursor.execute('DROP TABLE IF EXISTS word_mappings')
    cursor.execute('DROP TABLE IF EXISTS synonym_groups')
    cursor.execute('''
        CREATE TABLE synonym_groups (
            group_id INTEGER PRIMARY KEY AUTOINCREMENT,
            source TEXT
        )
    ''')
    cursor.execute('''
        CREATE TABLE word_mappings (
            word TEXT,
            group_id INTEGER,
            is_canonical INTEGER DEFAULT 0,
            FOREIGN KEY (group_id) REFERENCES synonym_groups(group_id),
            PRIMARY KEY (word, group_id)
        )
    ''')

    print("บันทึกลง SQLite ...")
    for word in csv_order:
        pos, syns = csv_map[word]
        all_words = [word] + list(syns)
        cursor.execute('INSERT INTO synonym_groups (source) VALUES (?)', (pos,))
        group_id = cursor.lastrowid
        for i, w in enumerate(all_words):
            cursor.execute(
                'INSERT OR IGNORE INTO word_mappings (word, group_id, is_canonical) VALUES (?, ?, ?)',
                (w, group_id, 1 if i == 0 else 0)
            )

    print("สร้าง INDEX ...")
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_word ON word_mappings(word)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_group_id ON word_mappings(group_id)')

    print("ลบคำ blacklist ...")
    try:
        with open('blacklist.txt', 'r', encoding='utf-8') as f:
            blacklist = [line.strip() for line in f if line.strip()]
        removed = 0
        for w in blacklist:
            cursor.execute('DELETE FROM word_mappings WHERE word = ?', (w,))
            removed += cursor.rowcount
        print(f"  ลบออก {removed} คำ")
    except FileNotFoundError:
        print("  ไม่พบ blacklist.txt ข้ามขั้นตอนนี้")

    conn.commit()
    conn.close()
    print("\nสร้างฐานข้อมูลเสร็จสิ้น!")


if __name__ == "__main__":
    create_db()
