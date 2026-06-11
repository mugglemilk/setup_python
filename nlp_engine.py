import re
import sqlite3
from functools import lru_cache
from pythainlp.tokenize import word_tokenize, syllable_tokenize
from pythainlp.corpus import thai_synonyms

TONE_MARKS = r'[่-๋]' # วรรณยุกต์ 
TAIL_CONSONANTS = r'[ก-ฮ]'  # พยัญชนะต้นและตัวสะกด
CONS  = r'[ก-ฮ]'
CONS2 = r'[ก-ฮ]{1,2}'
VOWEL_RULES = [
    (re.compile(rf'แ{TAIL_CONSONANTS}{TONE_MARKS}?ะ'), 'สระแอะ'),
    (re.compile(rf'โ{TAIL_CONSONANTS}{TONE_MARKS}?ะ'), 'สระโอะ'),
    (re.compile(rf'เ{TAIL_CONSONANTS}{TONE_MARKS}?ะ'), 'สระเอะ'),
    (re.compile(rf'เ{TAIL_CONSONANTS}{TONE_MARKS}?็'), 'สระเอะ'),
    
    (re.compile(rf'เ{CONS2}{TONE_MARKS}?ี{TONE_MARKS}?ย'),  'สระเอีย'),
    (re.compile(rf'เ{CONS2}{TONE_MARKS}?ื{TONE_MARKS}?อ'),  'สระเอือ'),
    (re.compile(rf'เ{CONS2}{TONE_MARKS}?ือ'),  'สระเอือ'),
    (re.compile(rf'เ{CONS2}{TONE_MARKS}?ืน'),   'สระเอือ'),
    (re.compile(rf'เ{CONS2}{TONE_MARKS}?ือ{CONS}'),  'สระเอือ'),
    
    (re.compile(rf'{TAIL_CONSONANTS}{TONE_MARKS}?ั{TONE_MARKS}?ว'), 'สระอัว'),
    (re.compile(rf'เ{TAIL_CONSONANTS}{TONE_MARKS}?า'), 'สระเอา'),
    
    (re.compile(rf'เ{TAIL_CONSONANTS}{TONE_MARKS}?[ก-ฮ]{{1,2}}(?:์)?'), 'สระเอะ'), 
    (re.compile(rf'เ[ก-ฮ]{{1,2}}{TONE_MARKS}?[ก-ฮ]{{1,2}}'), 'สระเอะ'),
    (re.compile(rf'แ{TAIL_CONSONANTS}{TONE_MARKS}?ะ'), 'สระแอะ'),
    (re.compile(rf'โ{TAIL_CONSONANTS}{TONE_MARKS}?ะ'), 'สระโอะ'),
    (re.compile(r'ะ'), 'สระอะ'),
    (re.compile(r'า'), 'สระอา'),
    (re.compile(r'ิ'), 'สระอิ'),
    (re.compile(r'ี'), 'สระอี'),
    (re.compile(r'ึ'), 'สระอึ'),
    (re.compile(r'ื'), 'สระอือ'),
    (re.compile(r'ุ'), 'สระอุ'),
    (re.compile(r'ู'), 'สระอู'),
    (re.compile(rf'เ[ก-ฮ][่-๋]?[ก-ฮ]$'), 'สระเอะ'),
    (re.compile(r'เ'), 'สระเอ'),
    (re.compile(r'แ'), 'สระแอ'),
    (re.compile(r'โ'), 'สระโอ'),
    (re.compile(r'ำ'), 'สระอำ'),
    (re.compile(r'[ไใ]'), 'สระไอ'),
    (re.compile(r'็'), 'สระโอะ'), 
]
# แคช
_vowel_cache = {}
_thai_synonyms_cache = None
_db_connection = None

def get_db_connection():
    """เปิดการเชื่อมต่อ SQLite เพียงครั้งเดียว (connection pooling)"""
    global _db_connection
    if _db_connection is None:
        _db_connection = sqlite3.connect('synonyms.db', check_same_thread=False)
        _db_connection.row_factory = sqlite3.Row
    return _db_connection

def close_db_connection():
    """ปิดการเชื่อมต่อเมื่อจบการใช้งาน"""
    global _db_connection
    if _db_connection is not None:
        _db_connection.close()
        _db_connection = None

def get_thai_synonyms_cached():
    """โหลด thai_synonyms เพียงครั้งเดียว"""
    global _thai_synonyms_cache
    if _thai_synonyms_cache is None:
        _thai_synonyms_cache = thai_synonyms()
    return _thai_synonyms_cache

@lru_cache(maxsize=2000)
def syllable_tokenize_cached(word):
    """Cache ผลลัพธ์ syllable_tokenize"""
    return tuple(syllable_tokenize(word, engine="dict"))

def get_vowel(word):
    """คำนวณสระจากพยางค์สุดท้ายของคำ (เร็วขึ้น)"""
    if word in _vowel_cache:
        return _vowel_cache[word]
    try:
        syllables = syllable_tokenize_cached(word) 
        last_syllable = syllables[-1] if syllables else word
        
        # ปรับปรุง Logic การรวมตัวสะกดเดี่ยวที่ถูกตัดแยกท้ายพยางค์
        i = len(syllables) - 1
        while i > 0 and not any(v in syllables[i] for v in 'ะาิีึืุูเแโใไำ'):
            last_syllable = syllables[i-1] + last_syllable
            i -= 1
            
        for pattern, vowel_name in VOWEL_RULES:
            if pattern.search(last_syllable):
                _vowel_cache[word] = vowel_name
                return vowel_name
        result = 'สระโอะ'
        _vowel_cache[word] = result
        return result
    except Exception:
        result = 'ไม่ระบุ'
        _vowel_cache[word] = result
        return result


def count_syllables_list(text):
    """นับพยางค์โดยใช้หลักการว่าพยางค์ต้องมีสระเสมอ"""
    VOWELS = set('ะาิีึืุูเแโใไำ็')
    THAI_CONS = set('กขฃคฅฆงจฉชซฌญฎฏฐฑฒณดตถทธนบปผฝพฟภมยรลวศษสหฬอฮ')
    
    CLUSTERS = {
        ('ก','ร'),('ก','ล'),('ก','ว'),
        ('ข','ร'),('ข','ล'),('ข','ว'),
        ('ค','ร'),('ค','ล'),('ค','ว'),
        ('ป','ร'),('ป','ล'),
        ('ผ','ล'),('พ','ร'),('พ','ล'),('พ','ว'),
        ('ส','ร'),
    }
    CLUSTER_NO_FINAL = {('ต','ร')}
    FINAL_GROUPS = {
        'แม่กก': set('กขคฆ'),
        'แม่กด': set('ดตถทธฎฏจชซฌศษส'),
        'แม่กบ': set('บปพฟภ'),
        'แม่กน': set('นณรลฬ'),
        'แม่กง': set('ง'),
        'แม่กม': set('ม'),
        'แม่เกย': set('ย'),
        'แม่เกอว': set('ว'),
    }
    CLUSTER_INCOMPATIBLE_FINALS = {'แม่เกย', 'แม่เกอว'}

    lines = text.split('\n')
    counts = []
    for line in lines:
        trimmed = line.strip()
        if  trimmed:
            syllables = list(syllable_tokenize_cached(trimmed))
            print("DEBUG:", trimmed)
            print("SYLLABLES:", syllables)
            expanded = []
            #counts.append(0)
            #continue
            for s in syllables:
                s = s.strip()
                if not s:
                    continue
                # หาตัวสะกดที่แท้จริง (พยัญชนะตัวสุดท้ายของพยางค์นี้)
                final_char = None
                for char in reversed(s):
                    if char in THAI_CONS:
                        final_char = char
                        break
                # หามาตราตัวสะกด
                final_group = next((g for g, chars in FINAL_GROUPS.items() 
                                    if final_char in chars), None)
                # ตรวจสอบตัวไม่เข้าพวก ตราย, ตราว ถ้าใช่ จะส่งผลให้โดนหั่นแยกพยางค์
                is_cluster_incompatible = (
                    len(s) >= 2 and
                    (s[0], s[1]) in CLUSTER_NO_FINAL and
                    final_group in CLUSTER_INCOMPATIBLE_FINALS
                )
                # เช็กว่าเป็นคำควบกล้ำปกติที่ถูกต้องตามระบบเสียง
                is_valid_cluster = (
                    len(s) >= 2 and
                    (s[0], s[1]) in CLUSTER_NO_FINAL and
                    not is_cluster_incompatible
                )
                # เงื่อนไขการแยกพยางค์อักษรนำกับลดรูป 
                # รองรับสระนำหน้า 
                LEADING_VOWELS = set('โเแไใ')
                ALL_FINALS = set().union(*FINAL_GROUPS.values())

                if (
                    len(s) >= 3 and
                    s[0] in LEADING_VOWELS and
                    s[1] in THAI_CONS and
                    s[1] != 'ห' and
                    s[2] in THAI_CONS and
                    (s[1], s[2]) not in CLUSTERS and
                    not any(v in s[1:] for v in VOWELS) and
                    (len(s) >= 4 or s[-1] not in ALL_FINALS)
                ):
                    expanded.append((s[1], True))
                    expanded.append((s[0] + s[2:], False))
                # รองรับพยัญชนะนำหน้าสระ
                elif (len(s) >= 3 and s[0] in THAI_CONS and s[1] 
                      in LEADING_VOWELS and s[2] 
                      in THAI_CONS and not any(v in s[0] for v in VOWELS)
                    and s[1] != 'อ'): 
                    expanded.append((s[0], True))
                    expanded.append((s[1:], False))

                elif (
                    len(s) >= 3 and
                    s[0] in THAI_CONS and
                    s[1] in THAI_CONS and
                    s[0] not in ('ห', 'อ') and
                    s[1] != 'อ' and
                    '์' not in s[0:2] and
                    (s[0], s[1]) not in CLUSTERS and not is_valid_cluster
                ):
                    expanded.append((s[0], True))
                    expanded.append((s[1:], False))
                
                else:
                    expanded.append((s, False))
            # รวมพยัญชนะเดี่ยวที่ไม่มีสระและมีแค่ 1 ตัว เข้ากับพยางค์ก่อนหน้า
            merged = []
            for s, is_split in expanded:
                has_vowel = any(v in s for v in VOWELS)
                cons_count = sum(1 for c in s if c in THAI_CONS)
                print(
                    f"s={s}, is_split={is_split}, "
                    f"has_vowel={has_vowel}, cons_count={cons_count}"
                )
                if not has_vowel and cons_count <= 1 and merged and not is_split:
                    merged[-1] = merged[-1] + s
                else:
                    merged.append(s)

            print("EXPANDED:", expanded)
            print("MERGED:", merged)
            print("COUNT:", len(merged))

            counts.append(len(merged))
        else:
            counts.append(0)
    return counts

def analyze_word_details(text):
    """ ตัดคำเพื่อให้ผู้ใช้เลือกคำไปหาคำไวพจน์ต่อได้ """
    words = word_tokenize(text, engine="newmm")
    fixed_words = []
    THAI_CONS = set('กขฃคฅฆงจฉชซฌญฎฏฐฑฒณดตถทธนบปผฝพฟภมยรลวศษสหฬอฮ')
    i = 0
    while i < len(words):
        # คำถัดไปเป็นพยัญชนะเดี่ยว ๆ หรือติดการันต์ที่ไม่มีรูปสระ
        if (i < len(words) - 1 and 
            all(c in THAI_CONS or c == '์' for c in words[i+1].strip()) and 
            not any(v in words[i+1] for v in 'ะาิีึืุูเแโใไำ็')):
            # รวบกลับไปต่อท้ายคำข้างหน้าทันที
            fixed_words.append(words[i] + words[i+1])
            i += 2
            continue
            
        fixed_words.append(words[i])
        i += 1
    words = fixed_words
    return [w for w in words if w.strip()]

@lru_cache(maxsize=1000)
def get_synonyms(word):
    """ ค้นหาคำไวพจน์จาก synonyms.db แบบไร้หมวดหมู่ (เร็วขึ้น)"""
    if not word:
        return None

    conn = get_db_connection()
    cursor = conn.cursor()
    query = """
        SELECT DISTINCT wm2.word
        FROM word_mappings wm1
        JOIN word_mappings wm2 ON wm1.group_id = wm2.group_id
        WHERE wm1.word = ?
    """
    cursor.execute(query, (word,))
    results = cursor.fetchall()

    if results:
        syn_list = sorted(list(set([row[0] for row in results if row[0] != word])))
        rhyme = get_vowel(word)
        return {
            "synonyms": syn_list,
            "category": "คำไวพจน์",
            "rhyme_group": rhyme
        }
    all_external_syns = get_thai_synonyms_cached()
    if word in all_external_syns:
        return {
            "synonyms": sorted(list(set(all_external_syns[word]))),
            "category": "คำไวพจน์ (Dataset)",
            "rhyme_group": get_vowel(word)
        }

    return None

def get_all_words():
    """ ดึงคำศัพท์ทั้งหมดรายตัวพร้อมคำไวพจน์ (เร็วขึ้น)"""
    conn = get_db_connection()
    cursor = conn.cursor()
    query = """
        SELECT wm1.word, wm2.word as synonym
        FROM word_mappings wm1
        JOIN word_mappings wm2 ON wm1.group_id = wm2.group_id
        WHERE wm1.word != wm2.word
    """
    cursor.execute(query)
    rows = cursor.fetchall()

    temp_dict = {}
    for word, syn in rows:
        if word not in temp_dict:
            temp_dict[word] = []
        temp_dict[word].append(syn)

    return {word: ", ".join(sorted(list(set(syns)))) for word, syns in temp_dict.items()}

def search_words_by_prefix(prefix):
    """ ค้นหาคำศัพท์ที่ขึ้นต้นด้วยตัวอักษรที่ระบุ (เร็วขึ้น)"""
    if not prefix:
        return []

    conn = get_db_connection()
    cursor = conn.cursor()
    # ใช้ INDEX บน word column สำหรับ LIKE query
    query = """
        SELECT wm1.word, wm2.word as synonym
        FROM word_mappings wm1
        JOIN word_mappings wm2 ON wm1.group_id = wm2.group_id
        WHERE wm1.word LIKE ? AND wm1.word != wm2.word
    """
    cursor.execute(query, (prefix + '%',))
    rows = cursor.fetchall()

    results = {}
    for word, syn in rows:
        if word not in results:
            results[word] = []
        results[word].append(syn)

    return [
        {"word": word, "syns": ", ".join(sorted(list(set(results[word]))))}
        for word in sorted(results.keys())
    ]
