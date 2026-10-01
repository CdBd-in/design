---
title: 세션 컨텍스트 — MBP에서 인수인계 A~F 완주 + 카드 드라이버 실측 + fixedPosition 정정
date: 2026-10-01
project: design
type: context
tags: [문서체계, 기능별경로가이드, 검증, 카드자동화, 팀공유]
related:
  - "[[2026-09-29 g1 세션 — 경로 가이드 실제 로드·확산 4·4·수용 테스트 + 맥북 프로 인수인계]]"
  - "[[2026-09-27 팀 공유 방식 확정 + 남은 작업 계획]]"
  - "[[원본 영상 목록]]"
---

# 2026-10-01 MBP 세션 — 그리고 다른 맥에서 이어받는 법

> 💻 **MBP** = `hyeonimeoseutadeuui-MacBookPro`(이 노트를 쓴 기기) · **g1** = `g1-Mac.local`
> 9/29 노트의 「🚩 MBP에서 시작하면」 **A~F를 전부 끝냈다.** 이제 남은 일은 **기기 무관** → 9/27 계획 **5번부터.**

---

## 🚩 다른 맥에서 시작하면 — 이 순서대로

### 0. 받아오기 (5분)
```bash
cd ~/Documents/GitHub/design && git pull
for r in cdbd-templates cdbd-design-system cdbd-design-service; do (cd $r && git fetch && git status -sb | head -1); done
```
- 🔑 **`cdbd-templates`는 pull 전에 `git status -sb`부터 볼 것.** 9/29 노트에 「g1의 `cdbd-templates`는 원격과 갈라져 있다」고 적혀 있었다.
  - `behind`만 있으면 → `git pull --ff-only`
  - `ahead`도 있으면 → **그 커밋이 이미 원격에 들어갔는지 먼저 확인**: `git cherry origin/main` (`-`면 이미 반영 · `+`면 아직 없음). 원격엔 g1 브랜치 `g1-0916-gate-fixes` 4커밋이 **이미 병합돼 있다**(그래서 원격 브랜치는 지웠다). 로컬에 같은 브랜치가 남아 있으면 `git branch -d g1-0916-gate-fixes`.
  - 충돌이 나면 **이 맥에서 고른 결론**(아래 「합치기 결정」)을 기준으로 푼다.
- `cdbd-design-system` · `cdbd-design-service`는 `git pull --ff-only`로 충분할 것(MBP 쪽 미푸시 커밋은 오늘 전부 올렸다).

### 1. 첫 실행이면 — 폴더 신뢰 승인 (5분)
새 기기·처음 여는 폴더는 **신뢰 승인 전까지 `.claude/settings.json` 허용 목록이 무시된다**(`claude -p` 실행 시 경고가 뜬다).
```bash
cd ~/Documents/GitHub/design && claude            # → 「1. Yes, proceed」 → /exit
# 같은 걸 cdbd-templates · cdbd-design-service · cdbd-design-system · cdbd-marketing · makevu-qrstp 에서
```

### 2. 채점표 — 드라이브에서 받기
- 정본 = 드라이브 `CdBd 기능 녹화 원본/` 최상위 **`구간별 테스트 채점표.md`** (구간 4~10 + 수용 테스트 Q01~Q15 · 2026-10-01 병합본)
- 🔒 **볼트 안에 두지 않는다.** 받아서 `~/Desktop/` 같은 볼트 밖에.
- 수용 테스트: `bash 검증/수용테스트.sh --key "<채점표 경로>"`

### 3. 그다음 → [[2026-09-27 팀 공유 방식 확정 + 남은 작업 계획]] **5번(감사 잔여)부터**

---

## ✅ 2026-10-01 MBP에서 끝난 것 — 다시 하지 말 것

| 단계 | 결과 | 커밋 |
|---|---|---|
| **A** 받아오기 | `cdbd-design-service` ff · `cdbd-design-system`은 **MBP 10커밋(판정 67~135) ↔ 원격 8커밋(9/29 가이드·3갈래) 갈라져 있었음** → 충돌 없이 병합 · push | DS `1dede1c` |
| **B** `cdbd-templates` 세 갈래 합치기 | ① MBP 미커밋 +24줄(§4-1-B 판정 125~135) 커밋 → ② `origin/main` 병합(**충돌 3곳** — 노트 예상 「CLAUDE.md만」과 달랐다) → ③ `g1-0916-gate-fixes` 병합(충돌 2곳) · 원격 브랜치 삭제 | T `28432bb` `8a33de3` `1f62672` |
| **C** 되묻기 3갈래 | 가이드 「문서가 없습니다, 어드민 로그인」 멈춤 문구 삭제 → `[SV]` §2 · 허브 사전으로 · ②③ 줄 추가 · `CLAUDE.md` 7줄 백스톱 정리 · **`claude -p` 로드 확인 OK** | T `a16a9d1` |
| **D** 스킬 이중 사본 | `.agents/skills` → `../.claude/skills` **심볼릭 링크** · `diff -rq` 무출력 · `pinnedIds` 존재 | T `eb07118` |
| **E** 채점표 병합 | g1판(구간 4 + 수용 Q01~Q15) + MBP판(구간 5~10) — **겹치는 구간 없음** → `구간별 테스트 채점표.md` · 볼트 인용 13곳 새 이름으로 · 👤 드라이브 업로드 완료 | 허브 `e4304c3` 외 자동 백업 |
| **F** 수용 테스트 | **15/15 PASS** · Q07·Q08 도구 0회 · 「어드민 로그인」 문구 사라짐 · 결과 `~/Desktop/cdbd-수용테스트-결과/20261001-1051/`(MBP) | — |
| 신뢰 승인 | MBP 6폴더 전부 `hasTrustDialogAccepted: true` | — |
| **카드 드라이버 실측** | 테스트 페이지 **editor 6530**(원페이지 · 텍스트/이미지/버튼) — 아래 표 | T `ad95dd0` |

### B 합치기 결정 — 다른 맥에서 충돌이 나면 이 기준으로

| 충돌 | 고른 것 | 이유 |
|---|---|---|
| `card-driver.js` `_sortableCtx` | **9/21 MBP 방식**(items가 블록 id와 가장 많이 겹치는 컨텍스트) | 9/08 g1 방식(`items.length === boardRows().length`)은 **고정 카드가 있으면 항상 실패** — 고정 카드는 sortable에서 빠진다(10/01 재확인: rows 3 / sortable 2) |
| 경로 가이드 카드 표 | g1 실측(9/08~9/16) 기본 + MBP 판정 113(구분선 굵기 0 · 코드 `http://` 무경고) | — |
| 경로 가이드 **상품** 행 | **둘 다 틀려서 새로 씀** — 미연동 [연동하기] = 페이지 이동(판정 106) · 연동 후 [스마트스토어 상품 추가하기] = 모달·그리드(판정 137) | 허브 사전 §3 상품 행과 일치 |
| 「버전 히스토리」/「버전 기록」 | ~~「버전 기록」~~ → 🔁 **「버전 히스토리」**(2026-10-01 g1 정정) | 제품 명칭은 「버전 히스토리」(판정 116 · 사전 7곳). 「원격·허브 표기」라는 근거는 틀렸다 — 사전엔 「버전 기록」이 0건 |

### 카드 드라이버 실측 (editor 6530 · 크레딧 0)

| 확인 | 결과 |
|---|---|
| `cardOrder()` | ✅ sortable 컨텍스트가 **5개**인데 카드 3개를 정확히 집음 |
| 상단 고정 → `pinnedIds()` · `pinVerify()` | ✅ `"top"` |
| 🎯 **고정 카드가 있는 채로** `reorderCard(0,1)` → `(1,0)` | ✅ 이동·원복 |
| 고정 해제(`openPin` → `confirmSwal`) | ✅ `pinVerify` = `false` |
| `dumpState()` | ✅ `total 3 / captured 3` |
| 리로드 후 | ✅ 테스트 전 상태 그대로 |
| ⏳ **멀티페이지** | **미검증** — 6530이 원페이지라 결함 A4(멀티에서 `dumpState` 붕괴) 수리는 아직 실측 안 됨 |

## 🔑 오늘 배운 것

1. 🔴 **`block.fixedPosition`은 있다** — 고정하면 `"top"`/`"bottom"`, 해제하면 `null`, 한 번도 고정 안 한 카드엔 키 자체가 없다. **9/08 g1 실측이 맞았고 9/21 「존재하지 않는다(핀 전/후 키 동일)」는 오판**(핀 카드 없는 문서에서 본 것으로 보임). B에서 9/21 쪽을 골랐다가 실측으로 뒤집었다 → 드라이버 `pinVerify()`가 이제 `"top"`/`"bottom"`/`false`/`null` 반환 · `SKILL.md` · 허브 `구간 1.md` A2 정정.
   → **두 기기 서술이 부딪히면 「나중 날짜」가 아니라 실측으로 가린다.**
2. **인수인계 노트의 명령도 낡는다** — 「`--ff-only`로 받기」「CLAUDE.md만 바뀌어 충돌 없음」 둘 다 실제와 달랐다. 실행 전에 `git status -sb` · `git merge-tree --write-tree`로 **미리 충돌을 본다.**
3. **`.agents/skills`는 Codex 미러였다**(`.Codex/…` · `AGENTS.md` 치환). 흡수할 내용은 없었다. 📌 `cdbd-templates/AGENTS.md`는 9/17 이후 안 고쳐져 `CLAUDE.md`와 266줄 다르다 — **사용자 결정으로 보류.**
4. **헤드리스 로그인** — `goto`로 새 페이지를 열면 세션이 풀린 적이 있다. 로그인 후 **8초 대기 → 페이지 안에서 `location.href='/editor/{id}'`로 이동**하니 유지됐다. 비밀번호는 `~/.config/cdbd/cdbd.env`에서 환경변수로만(출력 금지). 끝나면 `$B stop` — 오늘은 「Server crashed twice」로 안 꺼져 프로세스를 직접 종료했다.
5. **Obsidian 자동 백업이 허브 변경을 먼저 커밋·push한다** — 의미 있는 커밋 메시지를 남기려면 편집 직후 바로 커밋할 것.

## ⏭ 남은 일 (다른 맥 · 기기 무관)

| 순서 | 할 일 |
|---|---|
| 👤 | 드라이브 최상위에서 **옛 `게이트 채점표.md` · g1판 채점표 삭제** → 최상위 = PDF 1 + 채점표 1 (삭제했으면 [[원본 영상 목록]] 285줄 ⏳ 지우기) |
| 5 | 감사 잔여 5건 — 판정 126 경고 · 판정 37 §10 · 카드 「15종」 · 슬러그 규칙 · `구간 1.md:528` + **실제로 실리는 가이드 3개의 옛 판정 잔재** |
| 5+ | 카드 드라이버 **멀티페이지 실측**(A4) — 자기 전용 멀티페이지 테스트 문서 필요 · 게시 ❌ |
| 6 | 인증 헬퍼(`auth.py`·`image_library.py`) 저장소화 + 자동 재로그인 |
| 14~16 | `cdbd-setup.sh` · doctor · sync · `.env.example` · ONBOARDING 「Claude 셋업」 — 🔑 **새 기기 체크리스트에 「폴더 신뢰 승인」 추가** |
| 17~19 | 새 기기 리허설 · 제품팀 결함 전달문 |
| 22~25 | 선호님·명우님 셋업 → 두 분 기기에서 `검증/수용테스트.sh` 통과 → 🎯 목표 |
