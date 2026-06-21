from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, PageBreak, KeepTogether
)
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import os

# ── Fonts ──────────────────────────────────────────────────────────────────────
FONT_DIR = r"C:\Windows\Fonts"
pdfmetrics.registerFont(TTFont("TH", os.path.join(FONT_DIR, "tahoma.ttf")))
pdfmetrics.registerFont(TTFont("TH-Bold", os.path.join(FONT_DIR, "tahomabd.ttf")))

W, H = A4

# ── Palette ────────────────────────────────────────────────────────────────────
NAVY   = colors.HexColor("#1a3a52")
TEAL   = colors.HexColor("#1f6b8e")
GOLD   = colors.HexColor("#c4956a")
LGRAY  = colors.HexColor("#f0f4f7")
MGRAY  = colors.HexColor("#dde6ec")
DKGRAY = colors.HexColor("#5c7e95")
WHITE  = colors.white
GREEN  = colors.HexColor("#2d7a4f")
RED    = colors.HexColor("#c0392b")

# ── Styles ─────────────────────────────────────────────────────────────────────
def S(name, **kw):
    base = dict(fontName="TH", fontSize=11, leading=18, textColor=NAVY,
                spaceAfter=4, wordWrap='CJK')
    base.update(kw)
    return ParagraphStyle(name, **base)

sTitle    = S("title",   fontName="TH-Bold", fontSize=22, leading=30,
              textColor=WHITE, alignment=1, spaceAfter=6)
sSubtitle = S("sub",     fontName="TH",      fontSize=13, leading=20,
              textColor=MGRAY, alignment=1, spaceAfter=0)
sH1       = S("h1",      fontName="TH-Bold", fontSize=15, leading=22,
              textColor=WHITE, spaceBefore=0, spaceAfter=0)
sH2       = S("h2",      fontName="TH-Bold", fontSize=13, leading=20,
              textColor=GOLD, spaceBefore=14, spaceAfter=4)
sH3       = S("h3",      fontName="TH-Bold", fontSize=11, leading=18,
              textColor=TEAL, spaceBefore=8, spaceAfter=2)
sBody     = S("body",    fontSize=10.5, leading=17, textColor=NAVY, spaceAfter=4)
sCode     = S("code",    fontName="TH", fontSize=9.5, leading=15,
              textColor=colors.HexColor("#2c3e50"),
              backColor=LGRAY, leftIndent=10, rightIndent=10,
              borderPad=6, spaceAfter=6)
sBullet   = S("bullet",  fontSize=10.5, leading=17, textColor=NAVY,
              leftIndent=16, bulletIndent=6, spaceAfter=2)
sCaption  = S("caption", fontSize=9, leading=14, textColor=DKGRAY,
              alignment=1, spaceAfter=8)
sMuted    = S("muted",   fontSize=9.5, leading=15, textColor=DKGRAY, spaceAfter=2)
sNote     = S("note",    fontSize=9.5, leading=15, textColor=GREEN,
              leftIndent=10, spaceAfter=6)

def P(text, style=None):
    return Paragraph(text, style or sBody)

def H1(text):
    inner = Paragraph(text, sH1)
    tbl = Table([[inner]], colWidths=[W - 4*cm])
    tbl.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), NAVY),
        ('TOPPADDING',    (0,0), (-1,-1), 8),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
        ('LEFTPADDING',   (0,0), (-1,-1), 14),
        ('RIGHTPADDING',  (0,0), (-1,-1), 14),
        ('ROUNDEDCORNERS', [6]),
    ]))
    return tbl

def H2(text): return P(text, sH2)
def H3(text): return P(text, sH3)
def Bullet(text): return P(f"• {text}", sBullet)
def Code(text): return P(text, sCode)
def HR(): return HRFlowable(width="100%", thickness=0.5, color=MGRAY, spaceAfter=8, spaceBefore=4)
def SP(n=6): return Spacer(1, n)

def table(rows, col_widths, header=True):
    tbl = Table(rows, colWidths=col_widths)
    style = [
        ('FONTNAME',    (0,0), (-1,-1), 'TH'),
        ('FONTSIZE',    (0,0), (-1,-1), 10),
        ('LEADING',     (0,0), (-1,-1), 16),
        ('TEXTCOLOR',   (0,0), (-1,-1), NAVY),
        ('ROWBACKGROUNDS', (0,0), (-1,-1), [WHITE, LGRAY]),
        ('GRID',        (0,0), (-1,-1), 0.3, MGRAY),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
        ('RIGHTPADDING',(0,0), (-1,-1), 8),
        ('TOPPADDING',  (0,0), (-1,-1), 6),
        ('BOTTOMPADDING',(0,0),(-1,-1), 6),
        ('VALIGN',      (0,0), (-1,-1), 'MIDDLE'),
    ]
    if header:
        style += [
            ('BACKGROUND', (0,0), (-1,0), TEAL),
            ('TEXTCOLOR',  (0,0), (-1,0), WHITE),
            ('FONTNAME',   (0,0), (-1,0), 'TH-Bold'),
            ('FONTSIZE',   (0,0), (-1,0), 10.5),
        ]
    tbl.setStyle(TableStyle(style))
    return tbl

def cover_table(title_text, subtitle_text):
    t = Table(
        [[Paragraph(title_text, sTitle)],
         [Paragraph(subtitle_text, sSubtitle)]],
        colWidths=[W - 4*cm]
    )
    t.setStyle(TableStyle([
        ('BACKGROUND',    (0,0), (-1,-1), NAVY),
        ('TOPPADDING',    (0,0), (-1,-1), 22),
        ('BOTTOMPADDING', (0,0), (-1,-1), 22),
        ('LEFTPADDING',   (0,0), (-1,-1), 20),
        ('RIGHTPADDING',  (0,0), (-1,-1), 20),
        ('ROUNDEDCORNERS', [8]),
    ]))
    return t

# ── Content ────────────────────────────────────────────────────────────────────
story = []

# ───── Cover ─────
story += [
    SP(30),
    cover_table(
        "ระบบคำพ้องความหมายภาษาไทย",
        "Thai Synonym &amp; กลอนแปด Analyzer — เอกสารโครงสร้างโปรเจค"
    ),
    SP(14),
    P("เวอร์ชัน: v2  •  สร้างด้วย Flask + pythainlp  •  2026", sMuted),
    HR(),
    SP(6),
]

# ───── ภาพรวม ─────
story += [
    H1("1. ภาพรวมระบบ"),
    SP(10),
    P("เว็บแอปพลิเคชัน Flask ภาษาไทย ประกอบด้วย 2 ฟีเจอร์หลัก:", sBody),
    SP(4),
    Bullet("<b>ค้นหาคำพ้องความหมาย</b> — แนะนำคำพ้องและไฮไลท์คำที่มีจำนวนพยางค์และเสียงท้ายตรงกัน"),
    Bullet("<b>วิเคราะห์ฉันทลักษณ์กลอนแปด</b> — ตรวจสัมผัสอัตโนมัติ พร้อมไฮไลท์ผิด/ถูก และแผนผัง"),
    SP(10),
]

# ───── โครงสร้างไฟล์ ─────
story += [
    H1("2. โครงสร้างไฟล์"),
    SP(10),
    Code(
        "setup_python/<br/>"
        "├── app.py                  # Flask app factory + page routes<br/>"
        "├── requirements.txt        # Dependencies: flask, pythainlp, flask-cors<br/>"
        "├── synonyms.db             # SQLite DB (สร้างจาก database_setup.py)<br/>"
        "├── data.csv                # ข้อมูลดิบ (word, pos, synonyms)<br/>"
        "├── synonym.py              # กลุ่มคำพ้องเพิ่มเติม (Python list)<br/>"
        "├── database_setup.py       # Script สร้าง synonyms.db จาก data.csv + synonym.py<br/>"
        "├── merge.py                # Script export merged.csv (reference)<br/>"
        "├── blacklist.txt           # คำที่ไม่ต้องการ<br/>"
        "├── api/<br/>"
        "│   ├── synonym/<br/>"
        "│   │   ├── repository.py   # query synonyms.db → SQL lookup<br/>"
        "│   │   ├── service.py      # lookup + คำนวณ recommended<br/>"
        "│   │   └── routes.py       # GET /api/synonym, /api/dictionary<br/>"
        "│   └── poem/<br/>"
        "│       ├── service.py      # engine วิเคราะห์ฉันทลักษณ์<br/>"
        "│       └── routes.py       # POST /api/poem/analyze<br/>"
        "└── frontend/<br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;├── symnonym.html       # หน้าค้นหาคำพ้อง /<br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;├── dictionary.html     # ตารางคำศัพท์ /dictionary<br/>"
        "&nbsp;&nbsp;&nbsp;&nbsp;└── poem.html           # แต่งกลอนแปด /poem"
    ),
    SP(10),
]

# ───── ฐานข้อมูล ─────
story += [
    H1("3. ฐานข้อมูลคำพ้อง"),
    SP(10),
    H2("3.1  synonyms.db — ฐานข้อมูล SQLite (runtime)"),
    P("ไฟล์หลักที่ระบบใช้งาน มี 2 ตาราง:"),
    table(
        [["ตาราง", "คอลัมน์", "คำอธิบาย"],
         ["synonym_groups", "group_id, source", "แต่ละแถวคือกลุ่มคำพ้อง 1 กลุ่ม"],
         ["word_mappings", "word, group_id", "แต่ละคำ → อ้างอิง group_id"]],
        [4*cm, 4.5*cm, 8*cm]
    ),
    P("<b>สำคัญ:</b> ต้องรัน <code>python database_setup.py</code> ใหม่ทุกครั้งที่แก้ไข data.csv หรือ synonym.py", sNote),
    SP(6),

    H2("3.2  data.csv — ข้อมูลดิบ"),
    P("รูปแบบ: word, pos (noun/verb/adj), synonyms คั่นด้วย |"),
    SP(6),

    H2("3.3  synonym.py — กลุ่มคำพ้องเพิ่มเติม"),
    P("Python list of lists จัดหมวดหมู่ (บุคคล, ธรรมชาติ, สัตว์, พืช, กริยา, ความรู้สึก, ลักษณะ):"),
    Code("[ ['มนุษย์', 'คน', 'นรชน', 'บุรุษ'],<br/>"
         "  ['ผู้หญิง', 'นารี', 'อนงค์', 'สตรี'],<br/>"
         "  ... ]"),
    SP(6),

    H2("3.4  database_setup.py — สคริปต์สร้างฐานข้อมูล"),
    P("ใช้ logic เดียวกับ merge.py แต่บันทึกลง SQLite แทน CSV:"),
    Bullet("อ่าน data.csv และ synonym.py"),
    Bullet("Match กลุ่มคำพ้องที่มีคำตรงกัน → รวม synonyms"),
    Bullet("กลุ่มที่ไม่มีใน data.csv → เพิ่มเป็น entry ใหม่"),
    Bullet("บันทึกลง synonyms.db + สร้าง INDEX + ลบคำใน blacklist.txt"),
    SP(10),
]

story.append(PageBreak())

# ───── API ─────
story += [
    H1("4. API Layer"),
    SP(10),
    H2("4.1  Synonym API"),
    table(
        [["Endpoint", "Method", "คำอธิบาย"],
         ["/api/synonym?word=xxx", "GET", "ค้นหาคำพ้อง คืน synonyms + recommended"],
         ["/api/dictionary", "GET", "คืน entry ทั้งหมดในฐานข้อมูล"],
         ["/api/health", "GET", "ตรวจสอบสถานะ คืนจำนวน entry"]],
        [5.5*cm, 2.5*cm, 8.5*cm]
    ),
    SP(10),

    H2("4.2  Poem API"),
    table(
        [["Endpoint", "Method", "Body / คำอธิบาย"],
         ["/api/poem/analyze", "POST", '{"text": "บทกลอน..."} → stanzas + annotations']],
        [5.5*cm, 2.5*cm, 8.5*cm]
    ),
    SP(10),

    H2("4.3  SynonymRepository (repository.py)"),
    P("เปิด connection ไปยัง synonyms.db ตอน init แล้ว query ด้วย SQL JOIN:"),
    Bullet("<b>get_synonyms(word)</b>: JOIN word_mappings หา peers ใน group เดียวกัน"),
    Bullet("<b>get_all()</b>: single JOIN query คืน dict ทุก word (ไม่โหลดเข้า memory)"),
    Bullet("<b>entry_count()</b>: COUNT(DISTINCT word) จาก DB"),
    SP(6),

    H2("4.4  SynonymService (service.py)"),
    P("Logic การค้นหา:"),
    Bullet("ถ้าพบ word โดยตรง → คืน synonyms"),
    Bullet("ถ้าไม่พบ → ลอง reverse lookup หา canonical แล้วคืน synonyms ของ canonical"),
    Bullet("คำนวณ <b>recommended</b>: คำที่จำนวนพยางค์เท่ากัน AND เสียงท้าย (rhyme key) ตรงกัน"),
    SP(10),
]

# ───── Poem Engine ─────
story += [
    H1("5. Poem Analysis Engine (poem/service.py)"),
    SP(10),
    H2("5.1  ตารางข้อมูลหลัก"),
    table(
        [["ตัวแปร", "คำอธิบาย"],
         ["FINAL_CLASS", "พยัญชนะ → แม่ตัวสะกด (กก กง กด กบ กน กม เกย เกอว)"],
         ["VOWEL_RULES", "regex → ชื่อสระ (อา อิ อี เอ แอ เอือ เอา อำ ฯลฯ)"],
         ["CLUSTERS", "พยัญชนะควบกล้ำ (กร กล กว ขร พร สร ตร ฯลฯ)"],
         ["_LOW_CLASS", "อักษรต่ำ ใช้ตรวจ อักษรนำ (เสมือน → ส+เมือน)"]],
        [4*cm, 12.5*cm]
    ),
    SP(10),

    H2("5.2  Functions หลัก"),
    table(
        [["Function", "คำอธิบาย"],
         ["_strip_silent(s)", "ตัด tone marks และ X์ (อักษรเป็นเสียง)"],
         ["_vowel_of(syl)", "หาชื่อสระของพยางค์ โดยจับ regex ตาม VOWEL_RULES"],
         ["_final_class_of(syl)", "หาแม่ตัวสะกด (last Thai consonant → class)"],
         ["_get_rhyme_key(syl)", "vowel_name + final_class เช่น 'อาเกอว', 'อุกด'"],
         ["_rhymes(a, b)", "เปรียบเทียบ rhyme key ของ 2 พยางค์"],
         ["_syllabify(text)", "แบ่งพยางค์ด้วย pythainlp + post-processing"],
         ["_split_halves(line)", "แบ่ง 1 บรรทัด → 2 วรรค ตาม tab / 2+ spaces / |"],
         ["analyze(text)", "วิเคราะห์บทกลอนทั้งหมด คืน stanzas พร้อม annotations"]],
        [5*cm, 11.5*cm]
    ),
    SP(10),

    H2("5.3  กฎฉันทลักษณ์กลอนแปด"),
    table(
        [["กฎ", "รายละเอียด"],
         ["สัมผัสใน (วรรคสดับ→รับ)", "ท้ายวรรคสดับ ต้องสัมผัสกับพยางค์ที่ 3 หรือ 5 ของวรรครับ"],
         ["สัมผัสนอก", "ท้ายวรรครับ ↔ ท้ายวรรครอง (ต้องสัมผัสกัน)"],
         ["สัมผัสใน (วรรครอง→ส่ง)", "ท้ายวรรครอง ต้องสัมผัสกับพยางค์ที่ 3 หรือ 5 ของวรรคส่ง"],
         ["สัมผัสระหว่างบท", "ท้ายวรรคส่ง ต้องสัมผัสกับท้ายวรรครับของบทถัดไป"],
         ["จำนวนพยางค์", "แต่ละวรรคควรมี 7–9 พยางค์"]],
        [5.5*cm, 11*cm]
    ),
    SP(10),
]

story.append(PageBreak())

# ───── Frontend ─────
story += [
    H1("6. Frontend"),
    SP(10),
    P("ทั้ง 3 ไฟล์เป็น single-file HTML (CSS + JavaScript รวมอยู่ภายใน) ไม่มี framework ภายนอก"),
    SP(8),

    H2("6.1  symnonym.html — หน้าค้นหาคำพ้อง (/)"),
    Bullet("Input box ค้นหาคำ → แสดง synonym tags"),
    Bullet("Tag สีเขียว = recommended (จำนวนพยางค์ + เสียงท้ายตรงกัน)"),
    Bullet("กดที่ tag → copy to clipboard"),
    SP(6),

    H2("6.2  dictionary.html — ตารางคำศัพท์ (/dictionary)"),
    Bullet("แสดงทุก entry จาก /api/dictionary ในรูปตาราง"),
    Bullet("รองรับ search/filter"),
    SP(6),

    H2("6.3  poem.html — แต่งกลอนแปด (/poem)"),
    table(
        [["ฟีเจอร์", "คำอธิบาย"],
         ["Auto-analyze", "วิเคราะห์อัตโนมัติเมื่อเริ่มพิมพ์วรรคที่ 2 (debounce 700ms)"],
         ["Tab เป็น separator", "กด Tab ใน textarea แทรก \\t แบ่งวรรค 1 และ 2"],
         ["Ctrl+Z", "ย้อนกลับการแทนที่คำได้ (ใช้ execCommand ไม่ใช่ value=)"],
         ["Synonym panel", "คลุมดำคำ → โหลดคำแนะนำ กดที่ tag → แทนที่คำใน textarea"],
         ["Dark / Light mode", "Toggle โหมดสว่าง/มืด บันทึกใน localStorage"],
         ["แผนผัง", "Checkbox แสดง/ซ่อนแผนผังสัมผัสแต่ละบท"]],
        [4.5*cm, 12*cm]
    ),
    SP(10),

    H2("6.4  สีไฮไลท์สัมผัส"),
    table(
        [["Class", "สี", "ความหมาย"],
         ["r-sut / r-ton", "น้ำเงิน", "สัมผัสใน (คำส่ง / คำรับ)"],
         ["r-nai", "น้ำเงิน", "สัมผัสนอก"],
         ["r-son", "เขียว", "สัมผัสระหว่างบท"],
         ["r-bad", "แดงเส้นประ", "สัมผัสผิด"],
         ["word-err", "แดง", "คำผิดรูปแบบ"]],
        [3*cm, 3*cm, 10.5*cm]
    ),
    SP(10),
]

# ───── Data Flow ─────
story += [
    H1("7. Data Flow"),
    SP(10),

    H2("7.1  วิเคราะห์กลอน"),
    Code(
        "ผู้ใช้พิมพ์กลอน<br/>"
        "  → textarea input event (debounce 700ms)<br/>"
        "  → POST /api/poem/analyze {text: '...'}<br/>"
        "  → _syllabify() แบ่งพยางค์<br/>"
        "  → _rhymes() ตรวจสัมผัส<br/>"
        "  → analyze() คืน stanzas + annotations<br/>"
        "  → render ไฮไลท์ + ข้อสังเกต + แผนผัง"
    ),
    SP(6),

    H2("7.2  ค้นหาคำพ้อง / แทนที่คำ"),
    Code(
        "คลุมดำคำใน textarea<br/>"
        "  → mouseup → บันทึก selectionStart / selectionEnd<br/>"
        "  → GET /api/synonym?word=xxx<br/>"
        "  → lookup() + _is_recommended()<br/>"
        "  → คืน {synonyms, recommended}<br/>"
        "  → แสดง tags (เขียว = recommended)<br/>"
        "  → กดที่ tag → execCommand('insertText') แทนที่คำ<br/>"
        "  → trigger auto-analyze"
    ),
    SP(10),
]

# ───── การรัน ─────
story += [
    H1("8. การติดตั้งและรันระบบ"),
    SP(10),

    H2("8.1  ติดตั้ง"),
    Code("pip install flask pythainlp flask-cors"),
    SP(6),

    H2("8.2  สร้างฐานข้อมูล (ครั้งแรก)"),
    Code("python database_setup.py"),
    SP(6),

    H2("8.3  รัน server"),
    Code("python app.py<br/># เปิด http://localhost:5000"),
    SP(6),

    H2("8.4  อัปเดตฐานข้อมูลคำพ้อง"),
    P("เมื่อแก้ไข data.csv หรือ synonym.py ต้องรัน:"),
    Code("python database_setup.py"),
    P("แล้ว restart server ใหม่", sNote),
    SP(10),

    H2("8.5  Dependencies"),
    table(
        [["Package", "เวอร์ชัน", "การใช้งาน"],
         ["flask", "latest", "Web framework + Blueprint routing"],
         ["flask-cors", "latest", "CORS headers สำหรับ API"],
         ["pythainlp", "latest", "แบ่งพยางค์ภาษาไทย (syllable_tokenize)"],
         ["reportlab", "4.x", "สร้างเอกสาร PDF (ใช้ generate_pdf.py เท่านั้น)"]],
        [3.5*cm, 3*cm, 10*cm]
    ),
    SP(10),
]

# ── Build ──────────────────────────────────────────────────────────────────────
OUT = os.path.join(os.path.dirname(__file__), "โครงสร้างโปรเจค.pdf")

doc = SimpleDocTemplate(
    OUT,
    pagesize=A4,
    leftMargin=2*cm, rightMargin=2*cm,
    topMargin=2*cm, bottomMargin=2.2*cm,
    title="โครงสร้างโปรเจค Thai Synonym Analyzer",
    author="System Documentation",
)

def footer(canvas, doc):
    canvas.saveState()
    canvas.setFont("TH", 8)
    canvas.setFillColor(DKGRAY)
    canvas.drawString(2*cm, 1.2*cm, "Thai Synonym & กลอนแปด Analyzer — เอกสารโครงสร้างโปรเจค")
    canvas.drawRightString(W - 2*cm, 1.2*cm, f"หน้า {doc.page}")
    canvas.setStrokeColor(MGRAY)
    canvas.setLineWidth(0.5)
    canvas.line(2*cm, 1.6*cm, W - 2*cm, 1.6*cm)
    canvas.restoreState()

doc.build(story, onFirstPage=footer, onLaterPages=footer)
import sys
sys.stdout.buffer.write(f"OK: {OUT}\n".encode('utf-8'))
