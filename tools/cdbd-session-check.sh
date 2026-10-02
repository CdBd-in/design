#!/usr/bin/env bash
# CdBd 팀 — 세션 시작 점검 (Claude Code SessionStart 훅 · tools/cdbd-setup.sh가 등록)
# 네트워크 없이 1초 안에 끝난다. 문제가 없으면 아무것도 출력하지 않는다.
# 문제가 있으면 한 줄만 출력한다 → 세션 컨텍스트에 실려 Claude가 사용자에게 알려 줄 수 있다.

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CFG="${CDBD_CONFIG_DIR:-$HOME/.config/cdbd}"
CLAUDE_DIR="${CLAUDE_CONFIG_DIR:-$HOME/.claude}"
DAYS=3
now=$(date +%s); issues=()

oldest=0; oldname=""
for r in . cdbd-design-system cdbd-marketing cdbd-design-service cdbd-templates makevu-qrstp; do
  g="$ROOT/$r/.git"
  [ -d "$g" ] || { issues+=("저장소 없음: $r"); continue; }
  f="$g/FETCH_HEAD"; [ -f "$f" ] || f="$g/HEAD"
  t=$(stat -f %m "$f" 2>/dev/null || stat -c %Y "$f" 2>/dev/null || echo "$now")
  age=$(( (now - t) / 86400 ))
  [ "$age" -gt "$oldest" ] && { oldest=$age; oldname=$([ "$r" = . ] && echo design || echo "$r"); }
done
[ "$oldest" -gt "$DAYS" ] && issues+=("${oldname} 등 ${oldest}일째 안 받음 → bash ~/Documents/GitHub/design/tools/cdbd-sync.sh")

[ -f "$CFG/cdbd.env" ] || issues+=("~/.config/cdbd/cdbd.env 없음(자동 재로그인 불가)")
[ -f "$CFG/credentials.json" ] || [ -f "$CFG/cdbd.env" ] || issues+=("CdBd 인증 정보 없음")
[ -e "$CLAUDE_DIR/skills/cdbd-card-automation/card-driver.js" ] || issues+=("cdbd-card-automation 스킬 링크 깨짐 → tools/cdbd-setup.sh")

if [ ${#issues[@]} -gt 0 ]; then
  msg=$(printf '%s · ' "${issues[@]}"); msg=${msg% · }
  echo "⚠️ CdBd 셋업 점검: $msg (상세: bash ~/Documents/GitHub/design/tools/cdbd-doctor.sh)"
fi
exit 0
