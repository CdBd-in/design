/* CdBd 기능 안내판 — 실행 계획 (CDBD 브랜드 덱, pptxgenjs)
   node _build_plan_ppt.js */
const SKILL = "/Users/mustard/.claude/skills/cdbd-ppt-generator";
const D = require(SKILL + "/scripts/cdbd_deck.js");
const { C, F, T, RIGHT } = D;
const M = T.M;
const p = D.newPres();

const STAT = { "있음": C.ACCENT, "부분": C.MUTED, "없음": C.FOOT };
const dot = { "있음": "●", "부분": "◐", "없음": "○" };

function hrow(cols) {
  return cols.map(t => ({ text: t, options: { fill: { color: C.INK }, color: "FFFFFF", fontFace: F.semi, fontSize: 12.5, valign: "middle" } }));
}
function brow(cells, i, statusIdx) {
  const fill = i % 2 ? C.WHITE : C.PARCH;
  return cells.map((t, ci) => {
    const base = { fill: { color: fill }, valign: "middle" };
    if (statusIdx != null && ci === statusIdx)
      return { text: dot[t] + "  " + t, options: Object.assign(base, { color: STAT[t], fontFace: F.semi, fontSize: 12.5 }) };
    const strong = ci === 0;
    return { text: t, options: Object.assign(base, { color: strong ? C.INK : C.BODY, fontFace: strong ? F.semi : F.reg, fontSize: strong ? 12 : 11.5 }) };
  });
}
function drawTable(s, y, header, rows, colW, statusIdx, rowH) {
  s.addTable([hrow(header), ...rows.map((r, i) => brow(r, i, statusIdx))],
    { x: M, y, w: RIGHT - M, colW, border: { type: "solid", pt: 0.5, color: C.HAIR }, rowH: rowH || 0.5, valign: "middle", margin: [3, 8, 3, 8] });
}

/* 1. 표지 */
D.cover(p, {
  title: "CdBd 기능\n안내판 · 실행 계획",
  sub: "어느 팀원이 Claude에게 CdBd 기능을 시켜도,\n다 알고 제대로 동작하게",
  contact: "후속 문서: CdBd 문서 체계 진단 및 개편 제안   ·   2026-08-11",
});

/* 2. 목차 */
let s = D.content(p, { eyebrow: "CONTENTS", chapter: "목차", title: "목차", page: "02" });
const toc = [
  ["01", "목표와 문제", "지금 무엇이 안 되나"],
  ["02", "분류 기준 — 에디터·어드민·홈페이지", "뼈대를 새로 세운다"],
  ["03", "분류표 초안", "기능별 볼트 문서 유무"],
  ["04", "문서 채우기 — 화면 캡처가 필요한 기능", "무엇을 어떻게 채우나"],
  ["05", "안내판 설계와 원리", "무슨 파일에 어떻게"],
  ["06", "실행 순서", "한 곳을 끝까지 → 확산"],
  ["07", "예시 — cdbd-design-service", "과정과 예상 결과"],
  ["08", "다음 액션", "지금 결정할 것"],
];
let ty = 2.2;
toc.forEach(([n, t, d]) => {
  s.addText(n, { x: M, y: ty, w: 0.9, h: 0.48, valign: "middle", fontFace: F.bold, bold: true, fontSize: 14, color: C.ACCENT, margin: 0 });
  s.addText(t, { x: M + 1.0, y: ty, w: 7.6, h: 0.48, valign: "middle", fontFace: F.semi, fontSize: 15.5, color: C.INK, margin: 0 });
  s.addText(d, { x: M + 8.4, y: ty, w: 3.2, h: 0.48, valign: "middle", align: "right", fontFace: F.reg, fontSize: 11.5, color: C.MUTED, margin: 0 });
  s.addShape(p.ShapeType.line, { x: M, y: ty + 0.54, w: RIGHT - M, h: 0, line: { color: C.HAIR, width: 0.75 } });
  ty += 0.56;
});

/* 3. 목표와 문제 */
s = D.content(p, { eyebrow: "왜 하는가", chapter: "01  목표와 문제", title: "기능을 다 알고, 다 되게",
  lead: "안내판은 목표가 아니라 방법입니다. 필요하면 스킬·플러그인까지 함께 씁니다.", page: "03" });
D.threeCol(p, s, [
  { label: "목표", title: "누가 시켜도 된다", body: "어느 팀원의 Claude든 CdBd 기능을 알고 제대로 실행한다 — 사람이 문서 위치를 외우지 않아도." },
  { label: "지금 문제", title: "스스로 못 찾는다", body: "기능은 문서에 흩어져 있고, Claude에게 위키링크는 클릭이 아니라 글자일 뿐. 폴더를 열어도 무엇이 있는지 모른다." },
  { label: "방법", title: "안내판을 둔다", body: "무슨 기능이 → 어느 파일 어느 섹션에 있는지 표로 두고, CLAUDE.md가 그걸 먼저 읽게 연결한다." },
]);

/* 4. 분류 기준 (뼈대) — 제품 표면 3곳 */
s = D.content(p, { eyebrow: "분류 기준", chapter: "02  뼈대를 새로 세운다", title: "제품 표면 3곳으로 나눈다",
  lead: "가이드 센터(cdbd.mintlify.app)는 빠짐을 막는 참고용. 뼈대는 팀이 실제 시키는 일 기준으로.", page: "04" });
D.threeCol(p, s, [
  { label: "①", title: "에디터", body: "페이지를 만드는 곳. 카드 · 페이지 구성 · 이미지 · 게시(URL/OG) · 데이터 연결." },
  { label: "②", title: "어드민", body: "템플릿 · 운영 관리. 템플릿 등록 · 상세페이지 · 운영 설정." },
  { label: "③", title: "홈페이지 (계정)", body: "cdbd.in 대시보드. 홈 · 내 페이지 · 통계 · 공유 · 권한 · 버전 · 계정 · 요금." },
], { y: 2.7, h: 2.7 });
s.addShape(p.ShapeType.roundRect, { x: M, y: 5.6, w: RIGHT - M, h: 0.95, fill: { color: C.PARCH }, line: { color: C.HAIR, width: 1 }, rectRadius: 0.1 });
s.addText([
  { text: "＊ 실행 도구는 ‘기능’이 아닙니다.  ", options: { fontFace: F.semi, fontSize: 12.5, color: C.INK } },
  { text: "Supabase 자동화 · 이미지 라이브러리 헬퍼 · 브라우저 세션 등은 그 기능을 ‘실행하는 팀 도구’ → 안내판엔 ‘도구·규칙’으로 따로 표기.", options: { fontFace: F.reg, fontSize: 12, color: C.BODY } },
], { x: M + 0.3, y: 5.72, w: RIGHT - M - 0.6, h: 0.72, valign: "middle", lineSpacingMultiple: 1.3, margin: 0 });

/* 5. 분류표 ① 에디터 */
s = D.content(p, { eyebrow: "분류표 초안", chapter: "03  기능별 볼트 문서 유무", title: "에디터",
  lead: "각 ‘있음’ 행은 다음 단계에서 정확한 파일·섹션까지 채웁니다.", page: "05" });
drawTable(s, 2.5, ["영역", "기능", "볼트 문서"], [
  ["카드 15종", "프로필·텍스트·이미지·갤러리·버튼·Q&A·위치·SNS·구분선·2단·유튜브·예약", "있음"],
  ["카드 15종", "상품 · 코드 · 메뉴", "부분"],
  ["구성·꾸미기", "페이지 테마 · 카드 디자인 · 페이지 관리·설정 · 원페이지", "있음"],
  ["게시", "URL 생성·게시 · OG · 슬러그", "있음"],
  ["이미지", "이미지 라이브러리 (자산 관리)", "있음"],
  ["데이터", "데이터 연결 (개인화 병합)", "없음"],
], [1.9, 7.05, 2.68], 2, 0.6);

/* 6. 분류표 ② 어드민·홈페이지·시작 */
s = D.content(p, { eyebrow: "분류표 초안", chapter: "03  기능별 볼트 문서 유무", title: "어드민 · 홈페이지",
  lead: "‘없음’ = 제품엔 있으나 팀 볼트엔 문서가 없는 기능. 앞으로 채울 목록.", page: "06" });
drawTable(s, 2.45, ["영역", "기능", "볼트 문서"], [
  ["어드민", "템플릿 등록 · 상세페이지", "부분"],
  ["어드민", "운영 설정 세부", "없음"],
  ["홈페이지", "페이지 비밀번호", "부분"],
  ["홈페이지", "페이지 통계 · URL 통계", "없음"],
  ["홈페이지", "홈·내 페이지·공유 복제·버전 기록·권한·계정·내 주소·요금", "없음"],
  ["시작하기", "템플릿 페이지 생성", "부분"],
  ["시작하기", "회원가입", "없음"],
], [1.9, 7.05, 2.68], 2, 0.5);

/* 7. ◐ 부분 상세 */
s = D.content(p, { eyebrow: "분류표 초안", chapter: "03  ◐ 부분 — 구체적으로", title: "‘부분만 있음’은 무엇이 있고 없나",
  lead: "◐ 표시한 기능의 있는 부분과 채울 부분.", page: "07" });
drawTable(s, 2.5, ["기능 (◐ 부분)", "볼트에 있는 부분", "채울 부분"], [
  ["상품·코드·메뉴 카드", "카드 기능 목록(1-6-2)에 정의됨", "전용 제작·사용 가이드"],
  ["페이지 비밀번호", "게시 모달에 ‘페이지 비밀번호’ 언급", "설정 절차 문서"],
  ["템플릿 등록·상세페이지", "상세페이지 문서(1-7) 있음", "어드민 등록 단계"],
  ["템플릿 페이지 생성", "템플릿 워크플로우에 언급", "신규 생성 단계별 문서"],
], [3.0, 4.5, 4.13], null, 0.62);

/* 8. 문서 채우기 — 화면 캡처가 필요한 기능 */
s = D.content(p, { eyebrow: "문서 채우기", chapter: "04  무엇을 어떻게 채우나", title: "화면 캡처가 필요한 기능",
  lead: "로그인 뒤에서만 보이는 UI 흐름이라 텍스트로 유추 불가 → 화면 캡처가 정확한 문서화에 도움.", page: "08" });
const pw8 = (RIGHT - M - 0.4) / 2;
s.addShape(p.ShapeType.roundRect, { x: M, y: 2.5, w: pw8, h: 2.55, fill: { color: C.ATINT }, line: { type: "none" }, rectRadius: 0.12 });
s.addText("화면 캡처 권장 (○ 없음 대부분)", { x: M + 0.3, y: 2.66, w: pw8 - 0.6, h: 0.35, fontFace: F.semi, fontSize: 13.5, color: C.ACCENT, margin: 0 });
s.addText("· 페이지 통계 · URL 통계 (방문·클릭·응답·예약·구독)\n· 데이터 연결(개인화) — 고객 데이터 병합\n· 버전 기록 · 공유 복제\n· 내 페이지 관리 · 어드민 운영 설정\n· 계정 · 내 주소 · 요금(결제) · 권한",
  { x: M + 0.3, y: 3.08, w: pw8 - 0.6, h: 1.85, valign: "top", fontFace: F.reg, fontSize: 12.5, color: C.BODY, lineSpacingMultiple: 1.45, margin: 0 });
s.addShape(p.ShapeType.roundRect, { x: M + pw8 + 0.4, y: 2.5, w: pw8, h: 2.55, fill: { color: C.PARCH }, line: { color: C.HAIR, width: 1 }, rectRadius: 0.12 });
s.addText("영상 불필요 (이미 문서·코드로 있음)", { x: M + pw8 + 0.7, y: 2.66, w: pw8 - 0.6, h: 0.35, fontFace: F.semi, fontSize: 13.5, color: C.MUTED, margin: 0 });
s.addText("· 게시 자동화 (Supabase)\n· 카드 디자인·제작 스펙\n· 이미지 라이브러리 헬퍼\n· URL·OG·슬러그 규칙",
  { x: M + pw8 + 0.7, y: 3.08, w: pw8 - 0.6, h: 1.85, valign: "top", fontFace: F.reg, fontSize: 12.5, color: C.BODY, lineSpacingMultiple: 1.45, margin: 0 });
s.addShape(p.ShapeType.roundRect, { x: M, y: 5.3, w: RIGHT - M, h: 1.1, fill: { color: C.TILE }, line: { type: "none" }, rectRadius: 0.1 });
s.addText([
  { text: "형식 안내  ", options: { fontFace: F.semi, fontSize: 12.5, color: C.ON_DARK_ACCENT } },
  { text: "나는 영상 파일을 직접 재생하지 못하고, 화면 캡처·GIF(이미지)는 읽습니다. → ‘단계별 스크린샷 + 한 줄 설명’이 가장 정확합니다. 녹화하시면 핵심 화면을 캡처로 뽑아 주세요.", options: { fontFace: F.reg, fontSize: 12, color: "FFFFFF" } },
], { x: M + 0.3, y: 5.42, w: RIGHT - M - 0.6, h: 0.86, valign: "middle", lineSpacingMultiple: 1.35, margin: 0 });

/* 9. 안내판 설계와 원리 */
s = D.content(p, { eyebrow: "설계", chapter: "05  안내판 설계와 원리", title: "저장소마다 살아있는 index",
  lead: "각 저장소에 CLAUDE.md + _기능 안내판.md 를 둡니다.", page: "09" });
s.addShape(p.ShapeType.roundRect, { x: M, y: 2.4, w: RIGHT - M, h: 1.4, fill: { color: C.TILE }, line: { type: "none" }, rectRadius: 0.12 });
s.addText([
  { text: "각 저장소/\n", options: { color: C.ON_DARK_ACCENT, fontFace: F.semi } },
  { text: "├─ CLAUDE.md         ", options: { color: "FFFFFF", fontFace: F.reg } },
  { text: "← 맨 위에 \"작업 전 _기능 안내판.md 읽어라\" 1줄\n", options: { color: C.WMUTE, fontFace: F.reg } },
  { text: "└─ _기능 안내판.md    ", options: { color: "FFFFFF", fontFace: F.reg } },
  { text: "← 이 저장소의 기능 → 파일 지도", options: { color: C.WMUTE, fontFace: F.reg } },
], { x: M + 0.35, y: 2.56, w: RIGHT - M - 0.7, h: 1.1, valign: "middle", fontSize: 12.5, lineSpacingMultiple: 1.35, margin: 0 });
[
  "Claude에게 위키링크는 ‘클릭’이 아니라 그냥 글자 — 스스로 열지 않는다.",
  "CLAUDE.md는 폴더 열 때 자동으로 읽는 유일한 파일 → 여기서 가리켜야 읽힌다.",
  "그 볼트에서 일하면 Claude가 파일을 바로 찾는다. (볼트 간 링크는 작동 안 함 → 저장소 안에 self-contained)",
].forEach((t, i) => {
  const y = 4.1 + i * 0.5;
  s.addShape(p.ShapeType.roundRect, { x: M, y: y + 0.04, w: 0.12, h: 0.28, fill: { color: C.ACCENT }, line: { type: "none" }, rectRadius: 0.02 });
  s.addText(t, { x: M + 0.3, y, w: RIGHT - M - 0.3, h: 0.4, valign: "middle", fontFace: F.reg, fontSize: 12.5, color: C.BODY, margin: 0 });
});
s.addShape(p.ShapeType.roundRect, { x: M, y: 5.75, w: RIGHT - M, h: 0.85, fill: { color: C.ATINT }, line: { type: "none" }, rectRadius: 0.1 });
s.addText([
  { text: "‘아무 볼트에서나’ 되게 하려면?  ", options: { fontFace: F.semi, fontSize: 12.5, color: C.ACCENT } },
  { text: "각 저장소 안내판은 그 볼트에서 작동. 어느 볼트·맨 바깥에서 켜도 되게 하려면 → 플러그인 배포(진단서 D안, 이후 단계).", options: { fontFace: F.reg, fontSize: 12, color: C.BODY } },
], { x: M + 0.3, y: 5.85, w: RIGHT - M - 0.6, h: 0.65, valign: "middle", lineSpacingMultiple: 1.3, margin: 0 });

/* 10. 실행 순서 */
s = D.content(p, { eyebrow: "실행", chapter: "06  실행 순서", title: "한 곳을 끝까지 → 확산",
  lead: "‘연결’ = CLAUDE.md에 안내판을 읽으라고 한 줄 적어 두 파일을 잇는 것.", page: "10" });
const steps = [
  ["1  정의 확정", "대분류(에디터·어드민·홈페이지) 합의 — 무엇을 셀지 먼저", "오늘"],
  ["2  분류표 초안", "기능 ↔ 볼트 유무 대조 (앞 03장 형태)", "0.5일"],
  ["3  안내판 1곳", "저장소 1개만 골라 기능→정확한 파일·섹션 확정 + 경로 검증", "0.5일"],
  ["4  연결", "그 저장소 CLAUDE.md에 ‘안내판 먼저 읽어라’ 1줄", "5분"],
  ["5  검증", "\"○○ 해줘\" → Claude가 안내판 보고 올바른 파일 여는지 테스트", "10분"],
  ["6  확산 & 스킬", "작동 확인되면 나머지 저장소 복제 · 고빈도만 얇은 스킬", "이후"],
];
const head10 = ["단계", "무엇을 · 왜", "소요"].map(t => ({ text: t, options: { fill: { color: C.INK }, color: "FFFFFF", fontFace: F.semi, fontSize: 12.5, valign: "middle" } }));
const body10 = steps.map((r, i) => {
  const fill = i % 2 ? C.WHITE : C.PARCH;
  return [
    { text: r[0], options: { fill: { color: fill }, color: C.ACCENT, fontFace: F.semi, fontSize: 12.5 } },
    { text: r[1], options: { fill: { color: fill }, color: C.BODY, fontFace: F.reg, fontSize: 12 } },
    { text: r[2], options: { fill: { color: fill }, color: C.MUTED, fontFace: F.med, fontSize: 12, align: "center" } },
  ];
});
s.addTable([head10, ...body10], { x: M, y: 2.55, w: RIGHT - M, colW: [2.35, 7.68, 1.6], border: { type: "solid", pt: 0.5, color: C.HAIR }, rowH: 0.52, valign: "middle", margin: [3, 8, 3, 8] });

/* 11. 예시 · 과정 */
s = D.content(p, { eyebrow: "예시 · 과정", chapter: "07  cdbd-design-service", title: "끝까지 하면 — 과정",
  lead: "저장소 1곳(추천: cdbd-design-service)을 예로.", page: "11" });
const proc = [
  ["기능 추출", "가이드 + 볼트 대조 → 이 저장소가 실제로 다루는 CdBd 기능만 추림 (콘텐츠 등록·URL 게시·이미지 라이브러리·카드 매핑·누끼 크롭)"],
  ["파일·섹션 확정", "각 기능 → 정확한 파일·섹션 + 경로 실재 검증 (진단서가 지적한 ‘표 경로 9개 오류’ 정정)"],
  ["안내판 작성", "_기능 안내판.md 표로 정리 (기능 | 이렇게 말하면 | 파일·섹션 | 스킬화)"],
  ["연결", "CLAUDE.md 맨 위에 ‘_기능 안내판.md 먼저 읽어라’ 1줄"],
  ["검증", "\"이 룩북 CdBd에 올려줘\" → Claude가 스스로 §등록 워크플로우 열고 7단계 수행"],
];
let py = 2.5;
proc.forEach(([t, d], i) => {
  s.addShape(p.ShapeType.roundRect, { x: M, y: py, w: RIGHT - M, h: 0.78, fill: { color: C.CARD }, line: { color: C.HAIR, width: 1 }, rectRadius: 0.1 });
  s.addShape(p.ShapeType.roundRect, { x: M + 0.14, y: py + 0.19, w: 0.4, h: 0.4, fill: { color: C.ACCENT }, line: { type: "none" }, rectRadius: 0.2 });
  s.addText(String(i + 1), { x: M + 0.14, y: py + 0.19, w: 0.4, h: 0.4, align: "center", valign: "middle", fontFace: F.bold, bold: true, fontSize: 13, color: "FFFFFF", margin: 0 });
  s.addText(t, { x: M + 0.75, y: py, w: 2.2, h: 0.78, valign: "middle", fontFace: F.semi, fontSize: 13, color: C.INK, margin: 0 });
  s.addText(d, { x: M + 3.0, y: py, w: RIGHT - M - 3.2, h: 0.78, valign: "middle", fontFace: F.reg, fontSize: 11.5, color: C.BODY, lineSpacingMultiple: 1.2, margin: 0 });
  py += 0.86;
});

/* 12. 예시 · 결과 */
s = D.content(p, { eyebrow: "예시 · 결과", chapter: "07  cdbd-design-service", title: "예상 결과",
  lead: "\"CdBd에 올려줘\" 한마디로 달라지는 것.", page: "12" });
const pw = (RIGHT - M - 0.4) / 2;
s.addShape(p.ShapeType.roundRect, { x: M, y: 2.5, w: pw, h: 2.35, fill: { color: C.PARCH }, line: { color: C.HAIR, width: 1 }, rectRadius: 0.12 });
s.addText("지금 (안내판 없음)", { x: M + 0.3, y: 2.68, w: pw - 0.6, h: 0.35, fontFace: F.semi, fontSize: 14, color: C.MUTED, margin: 0 });
s.addText("· 어느 문서를 볼지 모름\n· 표 경로가 옛 파일명이라 헤맴\n· 사람이 매번 문서를 지정\n· 팀원마다 결과가 달라짐",
  { x: M + 0.3, y: 3.15, w: pw - 0.6, h: 1.6, valign: "top", fontFace: F.reg, fontSize: 13, color: C.BODY, lineSpacingMultiple: 1.5, margin: 0 });
s.addShape(p.ShapeType.roundRect, { x: M + pw + 0.4, y: 2.5, w: pw, h: 2.35, fill: { color: C.ACCENT }, line: { type: "none" }, rectRadius: 0.12 });
s.addText("안내판 적용 후", { x: M + pw + 0.7, y: 2.68, w: pw - 0.6, h: 0.35, fontFace: F.semi, fontSize: 14, color: "FFFFFF", margin: 0 });
s.addText("· 안내판에서 바로 §등록 워크플로우로 진입\n· 폴더 확인 → 멀티페이지 → 카드 매핑 → URL·OG → 검증 → 게시 자동 흐름\n· 누가 시켜도 같은 결과",
  { x: M + pw + 0.7, y: 3.15, w: pw - 0.6, h: 1.6, valign: "top", fontFace: F.reg, fontSize: 13, color: "FFFFFF", lineSpacingMultiple: 1.5, margin: 0 });
s.addText("부수 결과", { x: M, y: 5.05, w: 10, h: 0.32, fontFace: F.semi, fontSize: 13, color: C.INK, margin: 0 });
s.addText("· 진단서가 지적한 ‘핵심 문서 표 경로 9개 오류’ 정정   · ‘통계·개인화·버전기록 = 볼트에 없음’이 명시돼 다음 작업 목록이 생김\n· 소요 반나절 · 산출물 = _기능 안내판.md 1개 + CLAUDE.md 1줄 → 통하면 나머지 저장소로 복제",
  { x: M, y: 5.4, w: RIGHT - M, h: 1.0, valign: "top", fontFace: F.reg, fontSize: 12, color: C.BODY, lineSpacingMultiple: 1.45, margin: 0 });

/* 13. 다음 액션 */
s = D.content(p, { eyebrow: "다음 액션", chapter: "08  지금 결정할 것", title: "지금 결정할 것", page: "13" });
const acts = [
  ["① 대분류 확정", "에디터 · 어드민 · 홈페이지(계정) — 실행 도구는 ‘도구’로 별도. 이대로 갈지"],
  ["② 첫 저장소", "cdbd-design-service 추천 — 다른 곳으로 할지"],
  ["③ 확정되면", "2단계(분류표 초안) → 3단계(안내판 제작)로 바로 진행"],
];
let ay = 2.7;
acts.forEach(([t, d]) => {
  s.addShape(p.ShapeType.roundRect, { x: M, y: ay, w: RIGHT - M, h: 1.05, fill: { color: C.CARD }, line: { color: C.HAIR, width: 1 }, rectRadius: 0.12 });
  s.addShape(p.ShapeType.roundRect, { x: M, y: ay, w: 0.12, h: 1.05, fill: { color: C.ACCENT }, line: { type: "none" }, rectRadius: 0.02 });
  s.addText(t, { x: M + 0.35, y: ay + 0.16, w: 4.5, h: 0.4, fontFace: F.bold, bold: true, fontSize: 16, color: C.ACCENT, margin: 0 });
  s.addText(d, { x: M + 0.35, y: ay + 0.56, w: RIGHT - M - 0.7, h: 0.4, fontFace: F.reg, fontSize: 13, color: C.BODY, margin: 0 });
  ay += 1.2;
});

p.writeFile({ fileName: "/Users/mustard/Documents/GitHub/design/_기능 안내판 실행 계획.pptx" }).then(f => console.log("saved", f));
