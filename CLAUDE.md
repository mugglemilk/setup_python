# โครงสร้างโปรเจค: ระบบคำพ้องความหมายภาษาไทย + วิเคราะห์กลอนแปด

## ภาพรวม

เว็บแอปพลิเคชัน Flask สำหรับ 2 ฟีเจอร์หลัก:
1. **ค้นหาคำพ้องความหมาย** พร้อมแนะนำคำที่มีจำนวนพยางค์และเสียงท้ายตรงกัน
2. **วิเคราะห์ฉันทลักษณ์กลอนแปด** พร้อมไฮไลท์สัมผัสและแสดงข้อผิดพลาด

---

## โครงสร้างไฟล์

```
setup_python/
├── app.py                  # Flask app factory + page routes
├── requirements.txt        # Dependencies: flask, pythainlp
│
├── synonyms.db             # SQLite DB (สร้างจาก database_setup.py)
├── data.csv                # ข้อมูลดิบ (word, pos, synonyms)
├── synonym.py              # กลุ่มคำพ้องเพิ่มเติม (Python list of lists)
├── merge.py                # Script รวม data.csv + synonym.py → merged.csv
├── database_setup.py       # Script สร้าง synonyms.db จาก data.csv + synonym.py
├── blacklist.txt           # คำที่ไม่ต้องการใช้
│
├── api/
│   ├── synonym/
│   │   ├── repository.py   # query synonyms.db → lookup
│   │   ├── service.py      # logic: lookup + คำนวณ recommended
│   │   └── routes.py       # Blueprint: GET /api/synonym, /api/dictionary
│   └── poem/
│       ├── service.py      # engine วิเคราะห์ฉันทลักษณ์กลอนแปด
│       └── routes.py       # Blueprint: POST /api/poem/analyze
│
└── frontend/
    ├── symnonym.html       # หน้าค้นหาคำพ้อง (หน้าแรก /)
    ├── dictionary.html     # หน้าตารางคำศัพท์ /dictionary
    └── poem.html           # หน้าแต่งกลอนแปด /poem
```

---

## รายละเอียดแต่ละส่วน

### `app.py` — Entry Point
- สร้าง Flask app ด้วย factory pattern (`create_app()`)
- โหลด `SynonymRepository` → `SynonymService` ครั้งเดียวตอน startup แล้วเก็บใน `app.config`
- Register 2 blueprints: `synonym_bp` และ `poem_bp` ที่ prefix `/api`
- Serve HTML จากโฟลเดอร์ `frontend/`

---

### ฐานข้อมูลคำพ้อง

#### `synonyms.db` (SQLite — runtime DB)
มี 2 ตาราง:
- `synonym_groups(group_id, source)` — แต่ละแถวคือกลุ่มคำพ้อง 1 กลุ่ม
- `word_mappings(word, group_id)` — แต่ละคำ → อ้างอิง group_id

สร้างจาก `database_setup.py` — **ต้องรัน database_setup.py ใหม่ทุกครั้งที่แก้ data.csv หรือ synonym.py**

#### `data.csv` (raw data)
รูปแบบ: `word,pos,synonym1|synonym2|...`

#### `synonym.py` (กลุ่มคำพ้องเพิ่มเติม)
Python list of lists: `[['คำ1', 'คำ2', 'คำ3'], ...]` แบ่งเป็นหมวดหมู่
เช่น หมวดบุคคล, ธรรมชาติ, สัตว์, พืช, กริยา, ความรู้สึก, ลักษณะ

#### `database_setup.py` (script)
รวม data.csv + synonym.py → synonyms.db โดยใช้ logic เดียวกับ merge.py:
1. อ่าน data.csv เป็น dict
2. อ่าน synonym.py เป็น groups
3. Match กลุ่มที่มี word ตรงกัน → merge synonyms เข้าด้วยกัน
4. Group ที่ไม่มีใน data.csv → เพิ่มเป็น entry ใหม่
5. บันทึกลง SQLite + สร้าง INDEX + ลบคำใน blacklist.txt

#### `merge.py` (script เดิม — สำหรับ export CSV)
รวม data.csv + synonym.py → merged.csv (ใช้สำหรับ reference เท่านั้น)

---

### `api/synonym/`

#### `repository.py` — SynonymRepository
- เปิด connection ไปยัง `synonyms.db` ตอน init (sqlite3, check_same_thread=False)
- Query ด้วย SQL JOIN บน `word_mappings` โดยตรง (ไม่โหลดทั้งหมดเข้า memory)
- Methods:
  - `get_synonyms(word)` → JOIN หา peers ใน group เดียวกัน, คืน `None` ถ้าไม่พบ
  - `get_canonical(word)` → คืน `None` เสมอ (ไม่จำเป็นแล้วเพราะ DB เป็น flat groups)
  - `get_all()` → single JOIN query คืน dict ทุก word
  - `entry_count()` → `COUNT(DISTINCT word)`

#### `service.py` — SynonymService
- `lookup(word)`:
  1. ถ้าพบ word โดยตรง → คืน synonyms
  2. ถ้าไม่พบ → ลอง reverse lookup หา canonical word แล้วคืน synonyms ของ canonical
- คำนวณ `recommended`: list คำที่ **จำนวนพยางค์เท่ากัน** และ **เสียงท้าย (rhyme key) ตรงกัน** กับคำที่ค้นหา
- ใช้ `_syllabify` และ `_rhymes` จาก `poem/service.py`

#### `routes.py`
- `GET /api/synonym?word=xxx` → `{"word", "synonyms", "recommended"}`
- `GET /api/dictionary` → list ทุก entry
- `GET /api/health` → จำนวน entry

---

### `api/poem/`

#### `service.py` — engine วิเคราะห์กลอนแปด

**ตารางข้อมูลหลัก:**
- `TONE_MARKS` — วรรณยุกต์ (่ ้ ๊ ๋)
- `THAI_CONS` — พยัญชนะไทยทั้งหมด
- `LEADING_VOWELS` — สระนำ (เ แ โ ไ ใ)
- `FINAL_CLASS` — แม่ตัวสะกด: พยัญชนะ → class (กก กง กด กบ กน กม เกย เกอว)
- `VOWEL_RULES` — regex rules สระ → ชื่อสระ (อา อิ เอ ฯลฯ)
- `CLUSTERS` — พยัญชนะควบกล้ำที่ใช้ได้ (กร กล กว ฯลฯ)
- `_LOW_CLASS` — อักษรต่ำ (ง ค ช น ม ย ร ล ว ฯลฯ) สำหรับตรวจ อักษรนำ

**Functions หลัก:**
- `_strip_silent(s)` — ตัด tone marks และ X์ (อักษรเป็นเสียง)
- `_vowel_of(syl)` — หาชื่อสระของพยางค์
- `_final_class_of(syl)` — หาแม่ตัวสะกด
- `_get_rhyme_key(syl)` — `vowel_name + final_class` เช่น `"อาเกอว"`, `"อุกด"`
- `_rhymes(a, b)` — เปรียบเทียบ rhyme key ของ 2 พยางค์
- `_syllabify(text)` — แบ่งพยางค์ด้วย pythainlp `engine='dict'` + post-processing
  - จัดการ อักษรนำ + สระนำ (เสมือน → ส + เมือน)
  - Merge fragment พยัญชนะเดี่ยวเข้ากับพยางค์ก่อนหน้า
- `_split_halves(line)` — แบ่ง 1 บรรทัด → 2 วรรค (ตาม `\s{2,}` หรือ tab หรือ `|`)
- `analyze(text)` — วิเคราะห์บทกลอนทั้งหมด คืน stanzas พร้อม annotations

**กฎฉันทลักษณ์กลอนแปด:**
| กฎ | รายละเอียด |
|---|---|
| สัมผัสใน | ท้ายวรรคสดับ → พยางค์ที่ 3 หรือ 5 ของวรรครับ |
| สัมผัสนอก | ท้ายวรรครับ ↔ ท้ายวรรครอง |
| สัมผัสใน | ท้ายวรรครอง → พยางค์ที่ 3 หรือ 5 ของวรรคส่ง |
| ระหว่างบท | ท้ายวรรคส่ง → ท้ายวรรครับบทถัดไป |
| จำนวนพยางค์ | แต่ละวรรคควรมี 7–9 พยางค์ |

#### `routes.py`
- `POST /api/poem/analyze` body: `{"text": "..."}` → stanzas พร้อม annotations

---

### `frontend/`

ทั้ง 3 ไฟล์เป็น single-file HTML (CSS + JS รวมอยู่ภายใน) ไม่มี framework

#### `symnonym.html` — หน้าค้นหาคำพ้อง (`/`)
- Input box ค้นหาคำ → แสดง synonym tags
- คำที่ recommended (สีเขียว) = จำนวนพยางค์ + เสียงท้ายตรงกัน
- กดที่ tag → copy to clipboard

#### `dictionary.html` — ตารางคำศัพท์ (`/dictionary`)
- แสดงทุก entry จาก `/api/dictionary` ในรูปตาราง
- Search/filter

#### `poem.html` — แต่งกลอนแปด (`/poem`)
**UI:**
- Textarea (main): พิมพ์กลอน — รองรับ Tab เป็น separator วรรค
- Panel ขวา: คำไวพจน์ที่แนะนำ (คลุมดำคำใน textarea → โหลดคำแนะนำ)
- ผลวิเคราะห์: แสดงทีละบท พร้อม rhyme highlights + ข้อสังเกต + แผนผัง

**Auto-analyze logic:**
- trigger เมื่อเริ่มพิมพ์วรรคที่ 2 (มีตัวอักษรหลัง tab หรือ 2+ spaces บนบรรทัดแรก)
- debounce 700ms
- ทำงานต่อเนื่องทุกครั้งที่พิมพ์ต่อ

**Synonym panel:**
- `mouseup` บน textarea → บันทึก `selectionStart`/`selectionEnd` + โหลดคำแนะนำ
- กดที่ tag → `replaceSelection()` แทนที่คำที่คลุมดำ ผ่าน `execCommand('insertText')`
- Ctrl+Z ย้อนกลับได้ (ใช้ native undo stack ผ่าน execCommand)

**CSS themes:** dark (default) / light — toggle ได้, บันทึกใน localStorage

---

## การรัน

```bash
pip install flask pythainlp flask-cors

# ครั้งแรก (สร้างฐานข้อมูล)
python database_setup.py

# รัน server
python app.py
# เปิด http://localhost:5000
```

ถ้าแก้ `data.csv` หรือ `synonym.py` ต้องรัน:
```bash
python database_setup.py
```
ก่อนเริ่ม server ใหม่

---

## Data Flow

```
ผู้ใช้พิมพ์กลอน
    → textarea input event (debounce 700ms)
    → POST /api/poem/analyze
    → poem/service.py: _syllabify → _rhymes → analyze()
    → คืน stanzas + annotations (cls, tip)
    → frontend render ไฮไลท์สัมผัส

ผู้ใช้คลุมดำคำ
    → mouseup → บันทึก selection range
    → GET /api/synonym?word=xxx
    → synonym/service.py: lookup() + _is_recommended()
    → คืน {"synonyms", "recommended"}
    → แสดง tags (สีเขียว = recommended)
    → กดที่ tag → execCommand('insertText') แทนที่คำ → trigger analyze
```
