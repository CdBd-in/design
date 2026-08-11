# -*- coding: utf-8 -*-
"""CdBd 기능 안내판 — 실행 계획 PPT 생성"""
from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR

# ---- 팔레트 ----
INK   = RGBColor(0x1B, 0x24, 0x32)   # 딥 슬레이트
PAPER = RGBColor(0xFF, 0xFF, 0xFF)
GREEN = RGBColor(0x3D, 0xF6, 0x9B)   # CdBd 브랜드 그린(정본)
MUTE  = RGBColor(0x6B, 0x74, 0x84)
LINE  = RGBColor(0xE3, 0xE7, 0xEC)
SOFT  = RGBColor(0xF4, 0xF6, 0xF8)
RED   = RGBColor(0xE0, 0x4F, 0x4F)
FONT  = "Apple SD Gothic Neo"

prs = Presentation()
prs.slide_width  = Inches(13.333)
prs.slide_height = Inches(7.5)
BLANK = prs.slide_layouts[6]
SW, SH = prs.slide_width, prs.slide_height

def _set(run, size, color, bold=False):
    run.font.size = Pt(size); run.font.color.rgb = color
    run.font.bold = bold; run.font.name = FONT

def box(slide, l, t, w, h, fill=None, line=None, lw=0.75):
    from pptx.enum.shapes import MSO_SHAPE
    sp = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, l, t, w, h)
    sp.shadow.inherit = False
    if fill is None:
        sp.fill.background()
    else:
        sp.fill.solid(); sp.fill.fore_color.rgb = fill
    if line is None:
        sp.line.fill.background()
    else:
        sp.line.color.rgb = line; sp.line.width = Pt(lw)
    return sp

def text(slide, l, t, w, h, runs, align=PP_ALIGN.LEFT, anchor=MSO_ANCHOR.TOP, sp_after=6, line_sp=1.05):
    tb = slide.shapes.add_textbox(l, t, w, h); tf = tb.text_frame
    tf.word_wrap = True; tf.vertical_anchor = anchor
    for i, para in enumerate(runs):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = align; p.space_after = Pt(sp_after); p.space_before = Pt(0)
        p.line_spacing = line_sp
        for (s, size, color, bold) in para:
            r = p.add_run(); r.text = s; _set(r, size, color, bold)
    return tb

def header(slide, kicker, title, dark=False):
    box(slide, 0, 0, SW, Inches(1.35), fill=(INK if dark else PAPER))
    box(slide, Inches(0.6), Inches(0.42), Inches(0.14), Inches(0.5), fill=GREEN)
    text(slide, Inches(0.9), Inches(0.3), Inches(11.8), Inches(0.9),
         [[(kicker, 12, GREEN, True)], [(title, 26, (PAPER if dark else INK), True)]],
         sp_after=3)

def footer(slide, n):
    text(slide, Inches(0.6), Inches(7.02), Inches(9), Inches(0.35),
         [[("CdBd 기능 안내판 — 실행 계획", 9, MUTE, False)]])
    text(slide, Inches(11.8), Inches(7.02), Inches(1.0), Inches(0.35),
         [[(str(n), 9, MUTE, False)]], align=PP_ALIGN.RIGHT)

def bg(slide, color):
    box(slide, 0, 0, SW, SH, fill=color)

def table(slide, l, t, w, rows, col_w, header_fill=INK, header_color=PAPER,
          font=10.5, first_bold=False, red_rows=None, green_cells=None):
    red_rows = red_rows or set()
    nrows, ncols = len(rows), len(rows[0])
    h = Inches(0.5 + 0.42 * (nrows - 1))
    gtbl = slide.shapes.add_table(nrows, ncols, l, t, w, h).table
    gtbl.first_row = False; gtbl.horz_banding = False
    for ci, cw in enumerate(col_w):
        gtbl.columns[ci].width = cw
    for ri, row in enumerate(rows):
        gtbl.rows[ri].height = Inches(0.5 if ri == 0 else 0.42)
        for ci, val in enumerate(row):
            cell = gtbl.cell(ri, ci)
            cell.margin_left = Inches(0.1); cell.margin_right = Inches(0.06)
            cell.margin_top = Inches(0.03); cell.margin_bottom = Inches(0.03)
            cell.vertical_anchor = MSO_ANCHOR.MIDDLE
            if ri == 0:
                cell.fill.solid(); cell.fill.fore_color.rgb = header_fill
            elif ri % 2 == 0:
                cell.fill.solid(); cell.fill.fore_color.rgb = SOFT
            else:
                cell.fill.solid(); cell.fill.fore_color.rgb = PAPER
            p = cell.text_frame.paragraphs[0]
            p.alignment = PP_ALIGN.CENTER if ci > 0 else PP_ALIGN.LEFT
            r = p.add_run(); r.text = str(val)
            if ri == 0:
                _set(r, font, header_color, True)
            else:
                col = INK
                if ri in red_rows: col = RED
                _set(r, font, col, first_bold and ci == 0)
    return gtbl

# ========== 1. 표지 ==========
s = prs.slides.add_slide(BLANK); bg(s, INK)
box(s, Inches(0.9), Inches(2.5), Inches(0.18), Inches(1.7), fill=GREEN)
text(s, Inches(1.3), Inches(2.35), Inches(11), Inches(2.2),
     [[("CdBd 기능 안내판", 46, PAPER, True)],
      [("실행 계획", 46, GREEN, True)]], sp_after=4, line_sp=1.0)
text(s, Inches(1.32), Inches(4.55), Inches(10.5), Inches(0.8),
     [[("어떤 기능이 어느 파일에 있는지 — 정확히 아는 것을 목표로", 16, RGBColor(0xC7,0xCF,0xDA), False)]])
text(s, Inches(1.32), Inches(6.5), Inches(11), Inches(0.5),
     [[("2026-08-11", 11, MUTE, False), ("    ·    후속 문서: 「CdBd 문서 체계 진단 및 개편 제안」", 11, MUTE, False)]])

# ========== 2. 한 장 요약 ==========
s = prs.slides.add_slide(BLANK); bg(s, PAPER)
header(s, "요약", "한 장 요약")
items = [
    ("진단은 끝났습니다.", "기능 96개 중 Claude가 스스로 찾는 건 7개(7.3%)뿐."),
    ("이번 목표는 스킬이 아니라 '안내판'.", "무슨 기능이 → 어느 파일 어느 섹션에 있는지 확정하는 것."),
    ("먼저 '96개'부터 다시 셉니다.", "makevu·마케팅·Figma 드로잉을 걷어내면 진짜 CdBd 기능은 20여 개."),
    ("제품 영역별로 분류합니다.", "에디터 · 어드민 · 내 페이지 · 페이지별(통계·데이터). Figma 작업은 제외."),
    ("스킬·플러그인은 다음 단계.", "안내판이 정확해진 뒤, 고빈도 기능만 얇게 승격."),
]
y = 1.75
for head, body in items:
    box(s, Inches(0.6), Inches(y+0.03), Inches(0.12), Inches(0.72), fill=GREEN)
    text(s, Inches(0.9), Inches(y), Inches(11.6), Inches(0.95),
         [[(head+"  ", 15, INK, True), (body, 13, MUTE, False)]], line_sp=1.05)
    y += 1.02
footer(s, 2)

# ========== 3. 96은 서로 다른 것을 센 숫자 ==========
s = prs.slides.add_slide(BLANK); bg(s, PAPER)
header(s, "재정의 · 1", "'96개'는 서로 다른 것을 한데 센 숫자")
text(s, Inches(0.9), Inches(1.7), Inches(11.6), Inches(3.5),
     [[("• ", 15, GREEN, True), ("96 = 5개 저장소의 마크다운을 전수 조사한 결과입니다 (진단서 부록 C).", 15, INK, False)],
      [("• ", 15, GREEN, True), ("그래서 그 안에는 성격이 전혀 다른 것들이 '기능 1개'로 섞여 있습니다 —", 15, INK, False)],
      [("     ", 13, INK, False), ("다른 제품(makevu) · 마케팅 이미지 · Figma 드로잉 · 메모리/운영 작업까지.", 13, MUTE, False)],
      [("• ", 15, GREEN, True), ("우리가 원하는 건 'CdBd 페이지에서 실제 일어나는 일' 뿐입니다.", 15, INK, False)],
      [("• ", 15, GREEN, True), ("그 기준으로 좁히면 숫자가 크게 줄고, 대신 '무엇이 어디 있는지'가 선명해집니다.", 15, INK, False)]],
     sp_after=14)
box(s, Inches(0.9), Inches(5.35), Inches(11.5), Inches(1.1), fill=SOFT, line=LINE)
text(s, Inches(1.2), Inches(5.55), Inches(11), Inches(0.8),
     [[("핵심 질문:  ", 14, INK, True),
       ("\"96개\"가 아니라, \"CdBd 페이지 기능이 정확히 무엇 무엇인가\" 부터 합의합니다.", 14, INK, False)]],
     anchor=MSO_ANCHOR.MIDDLE)
footer(s, 3)

# ========== 4. 걷어내기 표 ==========
s = prs.slides.add_slide(BLANK); bg(s, PAPER)
header(s, "재정의 · 2", "걷어내면 — CdBd 페이지 기능은 약 20여 개")
rows = [
    ["항목", "개수", "이유"],
    ["총계 (5개 저장소 전수)", "96", "부록 C 전수 조사"],
    ["− makevu-qrstp", "−20", "다른 제품 (QR 스탬프) — CdBd 아님"],
    ["− 마케팅 콜래터럴", "−26", "블로그·매거진 (cdbd.in 블로그용, 페이지 밖)"],
    ["− Figma 드로잉·기법", "−16", "룩북·템플릿·화보 '제작' — 제외 지정"],
    ["− 메타·운영", "−8", "메모리·세션 컨텍스트·마이그레이션"],
    ["− 외부 범용 스킬", "−2", "impeccable (CdBd 무관)"],
    ["= CdBd 기능", "≈ 24", "이 중 순수 '페이지 작업'은 ~11개"],
]
table(s, Inches(0.9), Inches(1.75), Inches(11.5), rows,
      [Inches(3.6), Inches(1.6), Inches(6.3)], first_bold=True)
text(s, Inches(0.9), Inches(5.7), Inches(11.5), Inches(0.9),
     [[("→ ", 14, GREEN, True),
       ("'제품 디자인 시스템(카드·컴포넌트)'까지 포함하면 ~24, 순수 플랫폼 작업만 보면 ~11. 아래 분류로 정리합니다.", 13.5, MUTE, False)]])
footer(s, 4)

# ========== 5. 새 분류 기준 (핵심) ==========
s = prs.slides.add_slide(BLANK); bg(s, PAPER)
header(s, "분류 기준 · 핵심", "제품 영역별 대분류  (Figma 작업은 제외)")
cats = [
    ("① 에디터", "카드 배치·자동화, 카드 타입, 화면 구성", GREEN),
    ("② 어드민", "템플릿·상세페이지 등록, 운영 설정", GREEN),
    ("③ 내 페이지", "콘텐츠 등록, URL(슬러그)·게시, 이미지 라이브러리, OG", GREEN),
    ("④ 페이지별 (통계·데이터)", "방문·통계·데이터 조회  — 현재 문서 공백, 확인 필요", RED),
    ("⑤ (지원) 디자인 시스템·토큰", "색·폰트·아이콘·카드 스펙  — 조회·적용", MUTE),
]
y = 1.75
for name, desc, accent in cats:
    box(s, Inches(0.9), Inches(y), Inches(11.5), Inches(0.86), fill=SOFT, line=LINE)
    box(s, Inches(0.9), Inches(y), Inches(0.12), Inches(0.86), fill=accent)
    text(s, Inches(1.2), Inches(y), Inches(3.6), Inches(0.86),
         [[(name, 15, INK, True)]], anchor=MSO_ANCHOR.MIDDLE)
    text(s, Inches(4.7), Inches(y), Inches(7.5), Inches(0.86),
         [[(desc, 12.5, MUTE, False)]], anchor=MSO_ANCHOR.MIDDLE)
    y += 0.96
text(s, Inches(0.9), Inches(6.75), Inches(11.6), Inches(0.5),
     [[("제외:  ", 12, RED, True),
       ("Figma 드로잉(시안·초안·템플릿 제작) · 마케팅 · 메모리/운영 · makevu", 12, MUTE, False)]])
footer(s, 5)

# ========== 6. 왜 제품 영역별 ==========
s = prs.slides.add_slide(BLANK); bg(s, PAPER)
header(s, "분류 기준 · 근거", "왜 '저장소별'이 아니라 '제품 영역별'인가")
pts = [
    ("팀원은 제품으로 생각합니다.", "\"에디터에서~\", \"어드민에서~\", \"내 페이지 통계~\" — 저장소 이름으로 찾지 않습니다."),
    ("같은 기능이 여러 저장소에 흩어져 있습니다.", "예: '에디터' 관련 문서가 templates 80 · design-system 34 · design-service 19곳."),
    ("영역으로 묶으면 '빈 칸'이 보입니다.", "어느 영역에 문서가 없는지(=공백 기능) 한눈에 드러납니다."),
]
y = 1.9
for head, body in pts:
    box(s, Inches(0.6), Inches(y+0.03), Inches(0.12), Inches(0.9), fill=GREEN)
    text(s, Inches(0.9), Inches(y), Inches(11.6), Inches(1.1),
         [[(head, 16, INK, True)], [(body, 13, MUTE, False)]], sp_after=3, line_sp=1.05)
    y += 1.35
footer(s, 6)

# ========== 7. 커버리지 실측 ==========
s = prs.slides.add_slide(BLANK); bg(s, PAPER)
header(s, "현황 · 실측", "현재 문서는 각 영역을 얼마나 다루나")
rows = [
    ["영역 / 키워드", "design-system", "templates", "design-service", "진단"],
    ["에디터", "34", "80", "19", "풍부"],
    ["어드민", "0", "27", "1", "templates 집중 · 나머지 공백"],
    ["게시·슬러그(URL)", "8", "13", "15", "design-service 집중"],
    ["Supabase(데이터 연동)", "0", "3", "12", "design-service"],
    ["통계", "17", "9", "0", "얇음 · 성격 확인 필요"],
]
table(s, Inches(0.7), Inches(1.75), Inches(11.9), rows,
      [Inches(3.3), Inches(2.2), Inches(1.9), Inches(2.2), Inches(2.3)],
      font=11, first_bold=True, red_rows={5})
text(s, Inches(0.7), Inches(5.55), Inches(11.9), Inches(1.0),
     [[("숫자 = 해당 단어가 등장하는 .md 파일 수 (grep 실측).  ", 11, MUTE, False)],
      [("→ ", 14, GREEN, True),
       ("에디터·URL은 문서가 있고, 어드민·통계·데이터는 얇습니다. 안내판은 '무엇이 없는지'까지 드러냅니다.", 13, INK, False)]],
     sp_after=6)
footer(s, 7)

# ========== 8. 안내판의 형태 ==========
s = prs.slides.add_slide(BLANK); bg(s, PAPER)
header(s, "설계 · 1", "안내판의 형태 — 저장소마다 살아있는 index")
box(s, Inches(0.9), Inches(1.75), Inches(11.5), Inches(2.0), fill=INK)
text(s, Inches(1.2), Inches(1.95), Inches(11), Inches(1.7),
     [[("각 저장소/", 14, GREEN, True)],
      [("├─ CLAUDE.md         ", 13, PAPER, False), ("← 맨 위에 \"작업 전 _기능 안내판.md 읽어라\" 1줄 추가", 12, RGBColor(0x9F,0xF3,0xC7), False)],
      [("└─ _기능 안내판.md    ", 13, PAPER, False), ("← 신규: 기능 → 파일 매핑 표", 12, RGBColor(0x9F,0xF3,0xC7), False)]],
     line_sp=1.25)
text(s, Inches(0.9), Inches(4.0), Inches(11.5), Inches(0.4),
     [[("안내판 한 행의 형식:", 13, INK, True)]])
rows = [
    ["기능", "이렇게 말하면", "정본 파일·섹션 (검증된 경로)", "스킬화"],
    ["CdBd 콘텐츠 등록", "\"룩북 등록해줘\"", "룩북/1. 제작 프로세스/4-CdBd 콘텐츠.md §게시", "후보"],
]
table(s, Inches(0.9), Inches(4.45), Inches(11.5), rows,
      [Inches(2.6), Inches(2.6), Inches(5.1), Inches(1.2)], font=11)
footer(s, 8)

# ========== 9. 왜 CLAUDE.md가 가리켜야 ==========
s = prs.slides.add_slide(BLANK); bg(s, PAPER)
header(s, "설계 · 2", "왜 CLAUDE.md가 안내판을 가리켜야 하나")
pts = [
    "Claude에게 위키링크는 '클릭'이 아니라 그냥 글자입니다 — 스스로 열지 않습니다.",
    "볼트(저장소) 간 링크는 작동하지 않습니다 — 안내판은 각 저장소 안에 self-contained.",
    "CLAUDE.md는 폴더를 열 때 자동으로 읽는 유일한 파일입니다 — 여기서 가리켜야 읽힙니다.",
    "예전 HTML 계획서는 검색에서 빠져 아무도 다시 못 읽어 채택률 0%였습니다 — 반복하지 않습니다.",
]
y = 1.95
for p in pts:
    box(s, Inches(0.6), Inches(y+0.05), Inches(0.12), Inches(0.6), fill=GREEN)
    text(s, Inches(0.9), Inches(y), Inches(11.6), Inches(0.9),
         [[(p, 15, INK, False)]], line_sp=1.1)
    y += 1.05
footer(s, 9)

# ========== 10. 실행 순서 6단계 ==========
s = prs.slides.add_slide(BLANK); bg(s, PAPER)
header(s, "실행", "실행 순서 — 6단계")
rows = [
    ["단계", "할 일", "산출물", "소요"],
    ["1. 정의 확정", "대분류(에디터/어드민/내 페이지/통계·데이터) 승인", "분류 기준 1장", "오늘"],
    ["2. 분류표 초안", "CdBd 기능 24개를 영역별로 배치 (전 저장소)", "분류표 초안", "0.5일"],
    ["3. 파일럿 1곳", "정확한 파일·섹션까지 감사 + 경로 실재 검증", "_기능 안내판.md ×1", "0.5일"],
    ["4. 배선", "파일럿 CLAUDE.md → 안내판 가리키기", "1줄 추가", "5분"],
    ["5. 검증", "\"○○ 만들어줘\" → 올바른 파일 여는지 실제 테스트", "통과 확인", "10분"],
    ["6. 확산 & 스킬", "나머지 저장소 복제 · 고빈도만 얇은 스킬로 승격", "안내판 3개+", "이후"],
]
table(s, Inches(0.7), Inches(1.75), Inches(11.9), rows,
      [Inches(2.3), Inches(5.6), Inches(2.8), Inches(1.2)], font=11, first_bold=True)
text(s, Inches(0.7), Inches(5.85), Inches(11.9), Inches(0.7),
     [[("핵심: ", 13, GREEN, True),
       ("1곳(3~5단계)을 끝까지 돌려 '안내판 → 올바른 파일 오픈'이 실제 작동하는 걸 본 뒤 확산합니다.", 13, INK, False)]])
footer(s, 10)

# ========== 11. 파일럿 & 성공 기준 ==========
s = prs.slides.add_slide(BLANK); bg(s, PAPER)
header(s, "실행 · 파일럿", "파일럿과 '성공'의 정의")
box(s, Inches(0.9), Inches(1.8), Inches(5.5), Inches(4.4), fill=SOFT, line=LINE)
text(s, Inches(1.2), Inches(2.05), Inches(5.0), Inches(0.5),
     [[("파일럿 추천", 15, INK, True)]])
text(s, Inches(1.2), Inches(2.65), Inches(5.0), Inches(3.3),
     [[("cdbd-design-service", 16, GREEN, True)],
      [("• 내 페이지·콘텐츠·URL 기능이 가장 밀집", 13, INK, False)],
      [("• 게시·Supabase 문서가 이미 존재", 13, INK, False)],
      [("• 진단서가 지적한 '표 경로 9개 오류'도", 13, INK, False)],
      [("   같이 정리 → 효과가 가장 잘 보임", 13, INK, False)]], sp_after=8, line_sp=1.1)
box(s, Inches(6.7), Inches(1.8), Inches(5.7), Inches(4.4), fill=INK)
text(s, Inches(7.0), Inches(2.05), Inches(5.2), Inches(0.5),
     [[("'성공'의 정의", 15, GREEN, True)]])
text(s, Inches(7.0), Inches(2.65), Inches(5.2), Inches(3.3),
     [[("사람이 아니라 Claude가", 16, PAPER, True)],
      [("안내판만 보고 올바른 파일을", 16, PAPER, True)],
      [("여는 것.", 16, PAPER, True)],
      [("", 8, PAPER, False)],
      [("통과 전까지는 '문서가 있다'가 아니라", 12.5, RGBColor(0xC7,0xCF,0xDA), False)],
      [("'작동한다'로 판단합니다.", 12.5, RGBColor(0xC7,0xCF,0xDA), False)]], sp_after=6, line_sp=1.1)
footer(s, 11)

# ========== 12. 다음 액션 ==========
s = prs.slides.add_slide(BLANK); bg(s, INK)
box(s, Inches(0.9), Inches(0.8), Inches(0.16), Inches(0.9), fill=GREEN)
text(s, Inches(1.25), Inches(0.75), Inches(11), Inches(1.0),
     [[("지금 결정할 것 · 다음 액션", 30, PAPER, True)]])
qs = [
    ("① 대분류 확정", "에디터 · 어드민 · 내 페이지 · 페이지별(통계·데이터) · (지원)디자인시스템 — 이대로 갈지"),
    ("② 파일럿 저장소", "cdbd-design-service 추천 — 다른 곳으로 할지"),
    ("③ 확정되면", "2단계(분류표 초안)부터 바로 작성 → 파일럿 안내판 제작"),
]
y = 2.2
for head, body in qs:
    box(s, Inches(0.9), Inches(y), Inches(11.5), Inches(1.15), fill=RGBColor(0x24,0x30,0x42))
    box(s, Inches(0.9), Inches(y), Inches(0.12), Inches(1.15), fill=GREEN)
    text(s, Inches(1.25), Inches(y+0.15), Inches(11), Inches(0.9),
         [[(head, 17, GREEN, True)], [(body, 13.5, RGBColor(0xD5,0xDC,0xE5), False)]], sp_after=3, line_sp=1.05)
    y += 1.32
text(s, Inches(0.95), Inches(6.75), Inches(11), Inches(0.4),
     [[("정본 문서: _기능 안내판 실행 계획.md  ·  이 발표: _기능 안내판 실행 계획.pptx", 11, MUTE, False)]])

prs.save("_기능 안내판 실행 계획.pptx")
print("saved:", len(prs.slides.__iter__.__self__._sldIdLst), "slides")
