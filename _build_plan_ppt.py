# -*- coding: utf-8 -*-
"""CdBd 기능 안내판 — 실행 계획 PPT 생성 (v2)"""
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE

INK   = RGBColor(0x1B, 0x24, 0x32)
INK2  = RGBColor(0x24, 0x30, 0x42)
PAPER = RGBColor(0xFF, 0xFF, 0xFF)
GREEN = RGBColor(0x3D, 0xF6, 0x9B)
MUTE  = RGBColor(0x6B, 0x74, 0x84)
LINE  = RGBColor(0xE3, 0xE7, 0xEC)
SOFT  = RGBColor(0xF4, 0xF6, 0xF8)
RED   = RGBColor(0xD8, 0x45, 0x45)
CLOUD = RGBColor(0xC7, 0xCF, 0xDA)
FONT  = "Apple SD Gothic Neo"

prs = Presentation()
prs.slide_width  = Inches(13.333); prs.slide_height = Inches(7.5)
BLANK = prs.slide_layouts[6]; SW, SH = prs.slide_width, prs.slide_height

def _set(run, size, color, bold=False):
    run.font.size = Pt(size); run.font.color.rgb = color
    run.font.bold = bold; run.font.name = FONT

def box(slide, l, t, w, h, fill=None, line=None, lw=0.75):
    sp = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, l, t, w, h)
    sp.shadow.inherit = False
    if fill is None: sp.fill.background()
    else: sp.fill.solid(); sp.fill.fore_color.rgb = fill
    if line is None: sp.line.fill.background()
    else: sp.line.color.rgb = line; sp.line.width = Pt(lw)
    return sp

def text(slide, l, t, w, h, runs, align=PP_ALIGN.LEFT, anchor=MSO_ANCHOR.TOP, sp_after=6, line_sp=1.05):
    tb = slide.shapes.add_textbox(l, t, w, h); tf = tb.text_frame
    tf.word_wrap = True; tf.vertical_anchor = anchor
    for i, para in enumerate(runs):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = align; p.space_after = Pt(sp_after); p.space_before = Pt(0); p.line_spacing = line_sp
        for (s, size, color, bold) in para:
            r = p.add_run(); r.text = s; _set(r, size, color, bold)
    return tb

def header(slide, kicker, title, dark=False):
    box(slide, 0, 0, SW, Inches(1.3), fill=(INK if dark else PAPER))
    box(slide, Inches(0.6), Inches(0.4), Inches(0.14), Inches(0.5), fill=GREEN)
    text(slide, Inches(0.9), Inches(0.28), Inches(11.8), Inches(0.9),
         [[(kicker, 12, GREEN, True)], [(title, 25, (PAPER if dark else INK), True)]], sp_after=3)

def footer(slide, n):
    text(slide, Inches(0.6), Inches(7.04), Inches(9), Inches(0.35),
         [[("CdBd 기능 안내판 — 실행 계획", 9, MUTE, False)]])
    text(slide, Inches(12.0), Inches(7.04), Inches(0.8), Inches(0.35),
         [[(str(n), 9, MUTE, False)]], align=PP_ALIGN.RIGHT)

def bg(slide, c): box(slide, 0, 0, SW, SH, fill=c)

def table(slide, l, t, w, rows, col_w, font=10.5, first_bold=False, red_rows=None):
    red_rows = red_rows or set()
    nrows, ncols = len(rows), len(rows[0])
    h = Inches(0.5 + 0.42 * (nrows - 1))
    tb = slide.shapes.add_table(nrows, ncols, l, t, w, h).table
    tb.first_row = False; tb.horz_banding = False
    for ci, cw in enumerate(col_w): tb.columns[ci].width = cw
    for ri, row in enumerate(rows):
        tb.rows[ri].height = Inches(0.5 if ri == 0 else 0.42)
        for ci, val in enumerate(row):
            cell = tb.cell(ri, ci)
            cell.margin_left = Inches(0.1); cell.margin_right = Inches(0.06)
            cell.margin_top = Inches(0.02); cell.margin_bottom = Inches(0.02)
            cell.vertical_anchor = MSO_ANCHOR.MIDDLE
            if ri == 0: cell.fill.solid(); cell.fill.fore_color.rgb = INK
            elif ri % 2 == 0: cell.fill.solid(); cell.fill.fore_color.rgb = SOFT
            else: cell.fill.solid(); cell.fill.fore_color.rgb = PAPER
            p = cell.text_frame.paragraphs[0]
            p.alignment = PP_ALIGN.CENTER if ci > 0 else PP_ALIGN.LEFT
            r = p.add_run(); r.text = str(val)
            _set(r, font, (PAPER if ri == 0 else (RED if ri in red_rows else INK)),
                 True if ri == 0 else (first_bold and ci == 0))
    return tb

# ===== 1. 표지 =====
s = prs.slides.add_slide(BLANK); bg(s, INK)
box(s, Inches(0.9), Inches(2.15), Inches(0.18), Inches(1.05), fill=GREEN)
text(s, Inches(1.3), Inches(2.05), Inches(11), Inches(1.3),
     [[("CdBd 기능 안내판", 46, PAPER, True)]])
text(s, Inches(0.95), Inches(3.05), Inches(0.14), Inches(0.14), [[("", 8, INK, False)]])
text(s, Inches(1.32), Inches(3.35), Inches(11), Inches(1.6),
     [[("목표 — 어느 팀원이 Claude에게 CdBd 기능을 시켜도, 다 알고 제대로 동작한다", 18, GREEN, True)],
      [("", 6, PAPER, False)],
      [("‘안내판’은 그 목표를 이루기 위한 방법입니다. 필요하면 스킬·플러그인까지 함께 씁니다.", 14.5, CLOUD, False)]],
     line_sp=1.1)
text(s, Inches(1.32), Inches(6.55), Inches(11), Inches(0.5),
     [[("실행 계획  ·  2026-08-11  ·  후속 문서: 「CdBd 문서 체계 진단 및 개편 제안」", 11, MUTE, False)]])

# ===== 2. 한 장 요약 =====
s = prs.slides.add_slide(BLANK); bg(s, PAPER); header(s, "요약", "한 장 요약")
items = [
    ("프로젝트 목표는 '기능을 다 알고 다 되게'.", "어느 팀원의 Claude든 CdBd 기능을 알고 실행. 지금은 96개 중 7개만 발견(7.3%)."),
    ("그 방법으로 '안내판'을 만듭니다.", "무슨 기능이 → 어느 파일 어느 섹션에 있는지 매핑."),
    ("스킬·플러그인도 필요하면 적용합니다.", "안내판도 스킬도 목적이 아니라 수단. 상황에 맞게 씁니다."),
    ("먼저 CdBd 기능을 제품 영역별로 분류합니다.", "에디터 · 어드민 · 내 페이지(통계·데이터). Figma 작업은 제외."),
    ("저장소 1곳부터 만들어 '작동'을 확인한 뒤 확산합니다.", "문서를 늘리는 게 아니라 실제로 동작하는지를 기준으로."),
]
y = 1.65
for head, body in items:
    box(s, Inches(0.6), Inches(y+0.03), Inches(0.12), Inches(0.74), fill=GREEN)
    text(s, Inches(0.9), Inches(y), Inches(11.7), Inches(0.95),
         [[(head, 15, INK, True)], [(body, 12.5, MUTE, False)]], sp_after=2, line_sp=1.05)
    y += 1.02
footer(s, 2)

# ===== 3. 제품 영역 대분류 =====
s = prs.slides.add_slide(BLANK); bg(s, PAPER)
header(s, "분류 · 1", "CdBd 기능을 '제품 영역'으로 나눕니다  (Figma 작업 제외)")
cats = [
    ("① 에디터", "cdbd.in/editor — 페이지·카드·이미지 라이브러리·URL/게시", "CdBd 기능의 핵심 · 대부분 여기", GREEN),
    ("② 어드민", "템플릿 등록·상세페이지·운영 설정", "templates 저장소 중심", GREEN),
    ("③ 내 페이지 (대시보드)", "내 페이지 목록 · 페이지별 통계·데이터(방문 등)", "⚠️ 현재 팀 문서 거의 공백 — 확인 필요", RED),
    ("④ (지원) 디자인 시스템·토큰", "색·폰트·아이콘·카드 스펙", "조회·적용 (제작 아님)", MUTE),
]
y = 1.6
for name, desc, note, accent in cats:
    box(s, Inches(0.9), Inches(y), Inches(11.5), Inches(1.06), fill=SOFT, line=LINE)
    box(s, Inches(0.9), Inches(y), Inches(0.12), Inches(1.06), fill=accent)
    text(s, Inches(1.2), Inches(y+0.12), Inches(3.7), Inches(0.85),
         [[(name, 15.5, INK, True)]], anchor=MSO_ANCHOR.MIDDLE)
    text(s, Inches(4.9), Inches(y+0.13), Inches(7.3), Inches(0.85),
         [[(desc, 12.5, INK, False)], [(note, 11, accent if accent==RED else MUTE, accent==RED)]],
         anchor=MSO_ANCHOR.MIDDLE, sp_after=2)
    y += 1.16
text(s, Inches(0.9), Inches(6.85), Inches(11.6), Inches(0.4),
     [[("제외:  ", 11.5, RED, True), ("Figma 드로잉(시안·초안·템플릿 제작) · 마케팅 · 메모리/운영 · makevu(다른 제품)", 11.5, MUTE, False)]])
footer(s, 3)

# ===== 4. 에디터 세부 구조 =====
s = prs.slides.add_slide(BLANK); bg(s, PAPER)
header(s, "분류 · 2", "① 에디터 — 4개 하위 영역")
subs = [
    ("페이지", "멀티페이지 생성(380×580) · 페이지 추가/순서 · 설정(사이즈·넘김효과·테마·스크롤 애니메이션)"),
    ("카드", "기본 13종 + 2단 6종 카드 추가·편집 · 디자인 보드 옵션(배경·테두리·여백) · 링크 연결"),
    ("이미지 라이브러리", "cdbd.in 「이미지 추가하기 → 내 이미지」 자산 관리 — 카드·배경 이미지는 반드시 여기 업로드 경유"),
    ("URL · 게시", "상단 우측 「URL 생성하기」 → 슬러그(페이지 주소) · OG(썸네일·제목·설명) · 비밀번호 · 상단 메뉴 → 게시"),
]
y = 1.55
for i, (name, desc) in enumerate(subs, 1):
    box(s, Inches(0.9), Inches(y), Inches(11.5), Inches(1.02), fill=(INK if i==0 else SOFT), line=LINE)
    box(s, Inches(0.9), Inches(y), Inches(0.5), Inches(1.02), fill=INK)
    text(s, Inches(0.9), Inches(y), Inches(0.5), Inches(1.02), [[(str(i), 18, GREEN, True)]],
         align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
    text(s, Inches(1.65), Inches(y+0.11), Inches(3.0), Inches(0.8),
         [[(name, 15, INK, True)]], anchor=MSO_ANCHOR.MIDDLE)
    text(s, Inches(4.75), Inches(y+0.11), Inches(7.45), Inches(0.8),
         [[(desc, 12, MUTE, False)]], anchor=MSO_ANCHOR.MIDDLE, line_sp=1.05)
    y += 1.12
text(s, Inches(0.9), Inches(6.85), Inches(11.6), Inches(0.4),
     [[("‘CdBd 콘텐츠 등록’은 이 4개를 순서대로 쓰는 전체 워크플로우입니다 (다음 장).", 11.5, INK, True)]])
footer(s, 4)

# ===== 5. 용어 정리 (질문 답변) =====
s = prs.slides.add_slide(BLANK); bg(s, PAPER)
header(s, "분류 · 용어 정리", "헷갈리기 쉬운 4가지 — 정확히 무엇인가")
qa = [
    ("‘CdBd 콘텐츠 등록’ = 빈 페이지 만들기?",
     "아닙니다. 디자인 내보내기 이미지를 에디터에 멀티페이지·카드로 등록하고 URL까지 게시하는 전체 7단계 워크플로우. → 에디터 중심 작업"),
    ("‘URL 게시’는 어디서?",
     "맞습니다, 에디터 기능. 상단 우측 「URL 생성하기」 → 「URL 정보 편집」 모달에서 슬러그·게시."),
    ("‘이미지 라이브러리’는 무슨 기능?",
     "cdbd.in의 내 이미지 자산 보관·관리 공간. 카드·배경 이미지는 반드시 여기 업로드를 경유해야 UI에서 관리(이름변경·삭제·재선택) 가능."),
    ("‘OG’는 어디서?",
     "맞습니다, 에디터 기능. 「URL 정보 편집」 모달에서 등록하는 공유 카드(썸네일·제목·설명). 멀티페이지 전체에 1개."),
]
y = 1.55
for q, a in qa:
    box(s, Inches(0.9), Inches(y), Inches(11.5), Inches(1.18), fill=SOFT, line=LINE)
    text(s, Inches(1.15), Inches(y+0.12), Inches(11.1), Inches(0.4),
         [[("Q.  ", 12.5, RED, True), (q, 13, INK, True)]])
    text(s, Inches(1.15), Inches(y+0.55), Inches(11.1), Inches(0.6),
         [[("A.  ", 12.5, GREEN, True), (a, 12, MUTE, False)]], line_sp=1.05)
    y += 1.28
footer(s, 5)

# ===== 6. 현황 실측 =====
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
table(s, Inches(0.7), Inches(1.6), Inches(11.9), rows,
      [Inches(3.3), Inches(2.2), Inches(1.9), Inches(2.2), Inches(2.3)], font=11, first_bold=True, red_rows={5})
text(s, Inches(0.7), Inches(5.45), Inches(11.9), Inches(1.2),
     [[("숫자 = 해당 단어가 등장하는 .md 파일 수 (grep 실측, 2026-08-11).", 11, MUTE, False)],
      [("→ ", 14, GREEN, True),
       ("에디터·URL은 문서가 있고, 어드민·통계·데이터는 얇습니다.", 13, INK, False)],
      [("→ ", 14, GREEN, True),
       ("영역별로 묶으면 이런 ‘빈 칸(공백 기능)’이 바로 보입니다 — 안내판의 부수 효과.", 13, INK, False)]],
     sp_after=6)
footer(s, 6)

# ===== 7. 왜 제품 영역별 =====
s = prs.slides.add_slide(BLANK); bg(s, PAPER)
header(s, "근거", "왜 ‘저장소별’이 아니라 ‘제품 영역별’인가")
pts = [
    ("팀원은 제품으로 생각합니다.", "\"에디터에서~\", \"어드민에서~\", \"내 페이지 통계~\" — 저장소 이름으로 찾지 않습니다."),
    ("같은 기능이 여러 저장소에 흩어져 있습니다.", "예: ‘에디터’ 문서가 templates 80 · design-system 34 · design-service 19곳."),
    ("영역으로 묶으면 ‘빈 칸’이 보입니다.", "어느 영역에 문서가 없는지(=공백 기능)가 한눈에 드러납니다."),
]
y = 1.85
for head, body in pts:
    box(s, Inches(0.6), Inches(y+0.03), Inches(0.12), Inches(0.9), fill=GREEN)
    text(s, Inches(0.9), Inches(y), Inches(11.6), Inches(1.1),
         [[(head, 16, INK, True)], [(body, 13, MUTE, False)]], sp_after=3, line_sp=1.05)
    y += 1.35
footer(s, 7)

# ===== 8. 안내판의 형태와 원리 =====
s = prs.slides.add_slide(BLANK); bg(s, PAPER)
header(s, "설계", "안내판의 형태와 원리")
box(s, Inches(0.9), Inches(1.55), Inches(11.5), Inches(1.75), fill=INK)
text(s, Inches(1.2), Inches(1.72), Inches(11), Inches(1.5),
     [[("각 저장소/", 13.5, GREEN, True)],
      [("├─ CLAUDE.md         ", 12.5, PAPER, False), ("← 맨 위에 \"작업 전 _기능 안내판.md 읽어라\" 1줄 추가", 11.5, RGBColor(0x9F,0xF3,0xC7), False)],
      [("└─ _기능 안내판.md    ", 12.5, PAPER, False), ("← 신규: 기능 → 파일 매핑 표", 11.5, RGBColor(0x9F,0xF3,0xC7), False)]],
     line_sp=1.22)
rows = [
    ["기능", "이렇게 말하면", "정본 파일·섹션 (검증된 경로)", "스킬화"],
    ["CdBd 콘텐츠 등록", "\"CdBd에 올려줘\"", "룩북/1. 제작 프로세스/4-CdBd 콘텐츠.md §등록 워크플로우", "후보"],
]
table(s, Inches(0.9), Inches(3.5), Inches(11.5), rows,
      [Inches(2.5), Inches(2.4), Inches(5.4), Inches(1.2)], font=11)
text(s, Inches(0.9), Inches(4.75), Inches(11.5), Inches(2.0),
     [[("왜 이 형태여야 하나", 14, INK, True)],
      [("• ", 13, GREEN, True), ("Claude에게 위키링크는 ‘클릭’이 아니라 그냥 글자 — 스스로 열지 않습니다.", 12.5, INK, False)],
      [("• ", 13, GREEN, True), ("볼트(저장소) 간 링크는 작동하지 않습니다 → 안내판은 저장소 안에 self-contained.", 12.5, INK, False)],
      [("• ", 13, GREEN, True), ("CLAUDE.md는 폴더 열 때 자동으로 읽는 유일한 파일 → 여기서 가리켜야 읽힙니다.", 12.5, INK, False)]],
     sp_after=6, line_sp=1.05)
footer(s, 8)

# ===== 9. 실행 순서 =====
s = prs.slides.add_slide(BLANK); bg(s, PAPER)
header(s, "실행", "실행 순서 — 6단계 (한 곳을 끝까지 → 확산)")
rows = [
    ["단계", "무엇을 · 왜", "산출물", "소요"],
    ["1. 정의 확정", "대분류(에디터/어드민/내 페이지) 합의 — 무엇을 셀지 먼저 정함", "분류 기준 1장", "오늘"],
    ["2. 분류표 초안", "CdBd 기능을 영역별로 배치 — 전체 지도를 그림", "분류표 초안", "0.5일"],
    ["3. 파일럿 1곳", "저장소 1개만 골라 기능→정확한 파일·섹션 감사 + 경로 실재 확인", "_기능 안내판.md ×1", "0.5일"],
    ["4. 배선", "그 저장소 CLAUDE.md가 안내판을 가리키게 — Claude가 읽도록", "1줄 추가", "5분"],
    ["5. 검증", "\"○○ 해줘\" → Claude가 안내판 보고 올바른 파일 여는지 실제 테스트", "통과 확인", "10분"],
    ["6. 확산 & 스킬", "작동 확인되면 나머지 저장소 복제 · 고빈도만 얇은 스킬로 승격", "안내판 3개+", "이후"],
]
table(s, Inches(0.6), Inches(1.6), Inches(12.1), rows,
      [Inches(1.85), Inches(6.55), Inches(2.5), Inches(1.2)], font=10.5, first_bold=True)
text(s, Inches(0.6), Inches(5.7), Inches(12.1), Inches(0.9),
     [[("핵심: ", 13, GREEN, True),
       ("3~5단계를 한 저장소에서 끝까지 돌려 ‘안내판 → 올바른 파일 오픈’이 실제 작동하는 걸 확인한 다음에 확산합니다.", 12.5, INK, False)]])
footer(s, 9)

# ===== 10. 파일럿이란 + 성공 정의 =====
s = prs.slides.add_slide(BLANK); bg(s, PAPER)
header(s, "실행 · 파일럿", "‘파일럿 1곳’ = 한 곳을 먼저 끝까지 해본다")
box(s, Inches(0.9), Inches(1.6), Inches(5.5), Inches(4.7), fill=SOFT, line=LINE)
text(s, Inches(1.15), Inches(1.8), Inches(5.05), Inches(4.4),
     [[("파일럿이란", 15, INK, True)],
      [("네 곳(4개 저장소)에 한꺼번에 만들지", 12.5, INK, False)],
      [("않고, 먼저 한 곳만 완성해 봅니다.", 12.5, INK, False)],
      [("", 6, INK, False)],
      [("• 방식이 실제로 통하는지 싸게 검증", 12.5, MUTE, False)],
      [("• 틀린 형식을 4곳에 복사하는 낭비 방지", 12.5, MUTE, False)],
      [("", 6, INK, False)],
      [("추천 = cdbd-design-service", 14, GREEN, True)],
      [("· 콘텐츠·URL·이미지 라이브러리 기능 밀집", 12, INK, False)],
      [("· 진단서가 지적한 ‘표 경로 9개 오류’도", 12, INK, False)],
      [("  같이 정리 → 효과가 가장 잘 보임", 12, INK, False)]],
     sp_after=4, line_sp=1.08)
box(s, Inches(6.7), Inches(1.6), Inches(5.7), Inches(4.7), fill=INK)
text(s, Inches(6.95), Inches(1.8), Inches(5.25), Inches(4.4),
     [[("‘성공’의 정의", 15, GREEN, True)],
      [("", 6, PAPER, False)],
      [("사람이 아니라 Claude가", 17, PAPER, True)],
      [("안내판만 보고 올바른 파일을", 17, PAPER, True)],
      [("여는 것.", 17, PAPER, True)],
      [("", 8, PAPER, False)],
      [("통과 전까지는 ‘문서가 있다’가 아니라", 12.5, CLOUD, False)],
      [("‘작동한다’로 판단합니다.", 12.5, CLOUD, False)],
      [("", 8, PAPER, False)],
      [("→ 통과하면, 같은 형식을 나머지", 12, CLOUD, False)],
      [("   저장소로 확산합니다.", 12, CLOUD, False)]],
     sp_after=3, line_sp=1.1)
footer(s, 10)

# ===== 11. 다음 액션 =====
s = prs.slides.add_slide(BLANK); bg(s, INK)
box(s, Inches(0.9), Inches(0.75), Inches(0.16), Inches(0.85), fill=GREEN)
text(s, Inches(1.25), Inches(0.7), Inches(11), Inches(1.0), [[("지금 결정할 것 · 다음 액션", 29, PAPER, True)]])
qs = [
    ("① 대분류 확정", "에디터 · 어드민 · 내 페이지(통계·데이터) · (지원)디자인시스템 — 이대로 갈지"),
    ("② 파일럿 저장소", "cdbd-design-service 추천 — 다른 곳으로 할지"),
    ("③ 확정되면", "2단계(분류표 초안) → 3단계(파일럿 안내판 제작)로 바로 진행"),
]
y = 2.05
for head, body in qs:
    box(s, Inches(0.9), Inches(y), Inches(11.5), Inches(1.15), fill=INK2)
    box(s, Inches(0.9), Inches(y), Inches(0.12), Inches(1.15), fill=GREEN)
    text(s, Inches(1.25), Inches(y+0.16), Inches(11), Inches(0.9),
         [[(head, 17, GREEN, True)], [(body, 13.5, RGBColor(0xD5,0xDC,0xE5), False)]], sp_after=3, line_sp=1.05)
    y += 1.32
text(s, Inches(0.95), Inches(6.75), Inches(11.5), Inches(0.4),
     [[("정본 문서: _기능 안내판 실행 계획.md  ·  이 발표: _기능 안내판 실행 계획.pptx", 11, MUTE, False)]])

prs.save("_기능 안내판 실행 계획.pptx")
print("saved", len(prs.slides._sldIdLst), "slides")
