# CdBd 팀 — 전역 안내

> `tools/cdbd-setup.sh`가 `~/.claude/CLAUDE.md`에 `@import` 한 줄로 연결한 파일이다. **어느 폴더에서 세션을 켜도** 실린다.
> 규칙의 정본은 여기가 아니라 **`~/Documents/GitHub/design/CLAUDE.md`**(허브)다 — 여기엔 「어디로 가라」만 둔다(정답 두 벌 방지).

- **CdBd(cdbd.in) 제품 기능 · 페이지 제작 · 에디터 자동화 · 크레딧이 걸린 요청**이면:
  - 지금 세션이 `~/Documents/GitHub/design/` **안**이면 허브 `CLAUDE.md`가 이미 실려 있다 → 그 규칙을 따른다.
  - **밖**이면 작업 전에 `~/Documents/GitHub/design/CLAUDE.md`를 **먼저 Read** 하고 그 규칙(되묻기 3갈래 · 💰 공용 계정 규칙 · 기능별 경로)을 따른다.
- 💰 공용 계정이라 **게시 · URL 생성/연장 · 개별 URL · 주소 변경 · 팀원 초대 · 크레딧 충전**은 실행 전에 금액을 말하고 승인받는다.
- 인증: `~/.config/cdbd/auth.py`(정본 `design/tools/cdbd/`) · 🔴 `~/.config/cdbd/credentials.json`은 기기끼리 **복사하지 않는다**.
- 점검: `bash ~/Documents/GitHub/design/tools/cdbd-doctor.sh` (없으면 아직 셋업 전)
