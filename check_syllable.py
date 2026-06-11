from pythainlp.tokenize import syllable_tokenize

word = "พระสรรเพชญโพธิญาณประมาณหมาย"
syllables = syllable_tokenize(word, engine="dict")
print(f"คำ: {word}")
print(f"พยางค์: {syllables}")
# เปลี่ยนตรงนี้ ↓
cleaned = [s for s in syllables if s.strip() and len(s.strip()) > 1]
print(f"จำนวน: {len(cleaned)}")