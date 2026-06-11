import itertools
from pythainlp.tokenize import word_tokenize
from flask import Flask, request, render_template, jsonify
from flask_cors import CORS 
import nlp_engine  
from pythainlp.tokenize import syllable_tokenize
import re
import atexit

THAI_ORDER = 'กขฃคฅฆงจฉชซฌญฎฏฐฑฒณดตถทธนบปผฝพฟภมยรลวศษสหฬอฮ'
VOWEL_ORDER = 'าิีึืุูเแโใไั็่้๊๋'

def thai_sort_key(word):
    if not word:
        return []
    result = []
    for ch in word:
        if ch in THAI_ORDER:
            result.append((0, THAI_ORDER.index(ch)))
        elif ch in VOWEL_ORDER:
            result.append((1, VOWEL_ORDER.index(ch)))
        else:
            result.append((2, ord(ch)))
    return result

app = Flask(__name__)
CORS(app)

@atexit.register
def cleanup_db():
    nlp_engine.close_db_connection()

def fallback_vowel_name(word):
    """ฟังก์ชันสำรองสำหรับหาเสียงสระกรณีไม่พบในฐานข้อมูล"""
    if re.fullmatch(r'[ก-ฮ][ก-ฮ]', word): return "สระโอะ"
    v_map = {'ะ':'สระอะ','า':'สระอา','ิ':'สระอิ','ี':'สระอี','ึ':'สระอึ','ื':'สระอือ','ุ':'สระอุ','ู':'สระอู','เ':'สระเอ','แ':'สระแอ','โ':'สระโอ','ใ':'สระไอ','ไ':'สระไอ','ำ':'สระอำ'}
    for v, name in v_map.items():
        if v in word: return name
    return "ไม่พบรูปสระ"

@app.route("/")
def home():
    return render_template("homepage.html")

@app.route("/editor")
def editor():
    return render_template("index.html")

@app.route("/word-details")
def word_details():
    """ฟังก์ชันเดียวจบ: ดึงคำไวพจน์ตรงตัว ถ้าไม่เจอจะสลับไปประสมคำแล้วส่งไปที่กล่องแนะนำอันเดิม"""
    word = request.args.get("word", "").strip()
    if not word:
        return jsonify({"synonyms": "", "rhyme": "", "category": ""})
    res = nlp_engine.get_synonyms(word)
    
    if res:
        return jsonify({
            ##"synonyms": ", ".join(res["synonyms"]),
            "synonyms": [{"word": w, "rhyme": nlp_engine.get_vowel(w)} for w in sorted(res["synonyms"], 
                                                                                       key=thai_sort_key)],
            "rhyme": res["rhyme_group"],
            "category": res["category"]
        })
    else:
        tokens = word_tokenize(word, engine="newmm")
        
        if len(tokens) > 1:
            all_synonym_groups = []
            categories_found = []
            
            for token in tokens:
                token_res = nlp_engine.get_synonyms(token)
                if token_res and token_res["synonyms"]:
                    all_synonym_groups.append(token_res["synonyms"])
                    categories_found.append(token_res["category"])
                else:
                    all_synonym_groups.append([token])
            
            if len(categories_found) > 0:
                combined_synonyms = []
                for combination in itertools.product(*all_synonym_groups):
                    combined_synonyms.append("".join(combination))
                
                combined_synonyms = list(set(combined_synonyms))
                if word in combined_synonyms:
                    combined_synonyms.remove(word)
                
                unique_categories = " + ".join(list(set(categories_found)))
                return jsonify({
                    #"synonyms": ", ".join(combined_synonyms) if combined_synonyms else "(ไม่พบข้อมูลคำไวพจน์)",
                    "synonyms": ", ".join(sorted(combined_synonyms, key=thai_sort_key)) if combined_synonyms else "(ไม่พบข้อมูลคำไวพจน์)",
                    "rhyme": "คำผสมประสมเสียง",
                    "category": unique_categories
                })
        return jsonify({
            "synonyms": "(ไม่พบข้อมูลคำไวพจน์)",
            "rhyme": fallback_vowel_name(word),
            "category": "ไม่ระบุ"
        })

@app.route("/count-syllables", methods=["POST"])
def count_syllables_api():
    try:
        data = request.get_json()
        text = data.get("text", "")
        results = nlp_engine.count_syllables_list(text)
        return jsonify(results)
    except Exception as e:
        return jsonify({"error": str(e)}), 400
    
@app.route("/dictionary")
def dictionary():
    return render_template("dictionary.html")

@app.route("/all")
def get_all_data():
    """ดึงข้อมูลคำศัพท์ทั้งหมดจากฐานข้อมูลมาแสดงในหน้าคลังคำ"""
    all_data = nlp_engine.get_all_words()
    return jsonify(all_data)

@app.route("/search")
def search_api():
    query = request.args.get("word", "").strip()
    if not query:
        return jsonify([])
    results = nlp_engine.search_words_by_prefix(query)
    return jsonify(results) 

@app.route("/analyze-klon-v2", methods=["POST"])
def analyze_klon_v2():
    """Route ใหม่สำหรับสกัดพยางค์ หาคำลงท้าย และพยางค์ที่ 3 หรือ 5 เพื่อใช้ตรวจฉันทลักษณ์โดยเฉพาะ"""
    try:
        data = request.get_json()
        warraks = data.get("warraks", [])
        
        result = []
        for warrak in warraks:
            trimmed = warrak.strip()
            if not trimmed:
                result.append({"syllables": [], "last_word": "", "rhyme": "", "middle_words": []})
                continue
            syllables = list(nlp_engine.syllable_tokenize_cached(trimmed))
            cleaned_syllables = [s.strip() for s in syllables if s.strip()]
            
            last_word = cleaned_syllables[-1] if cleaned_syllables else ""
            rhyme = nlp_engine.get_vowel(last_word) if last_word else "ไม่ระบุ"
            middle_words = []
            middle_rhymes = []
            if len(cleaned_syllables) >= 3:
            # รวมพยางค์ที่ 3 กับพยางค์ถัดไปถ้าพยางค์ถัดไปมีแค่ 1 ตัวอักษร เช่น ญ ร ล
                syl3 = cleaned_syllables[2]
                if len(cleaned_syllables) >= 4 and len(cleaned_syllables[3]) == 1:
                    syl3 = syl3 + cleaned_syllables[3]
            middle_words.append(syl3)
            middle_rhymes.append(nlp_engine.get_vowel(syl3))
            if len(cleaned_syllables) >= 5:
                syl5 = cleaned_syllables[4]
                if len(cleaned_syllables) >= 6 and len(cleaned_syllables[5]) == 1:
                    syl5 = syl5 + cleaned_syllables[5]
                middle_words.append(syl5)
                middle_rhymes.append(nlp_engine.get_vowel(syl5))
            result.append({
                "syllables": cleaned_syllables,
                "last_word": last_word,
                "rhyme": rhyme,
                "middle_words": middle_words,
                "middle_rhymes": middle_rhymes  
            })
            
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 400

if __name__ == "__main__":
    app.run(debug=True, port=5001)
