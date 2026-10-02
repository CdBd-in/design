#!/usr/bin/env bash
# CdBd 팀 — 허브 + 하위 저장소 5개를 한 번에 받기 (fast-forward만 · 안전한 것만 한다)
#
#   bash ~/Documents/GitHub/design/tools/cdbd-sync.sh
#
# - 미커밋 변경이 있는 저장소는 건너뛴다 (내 작업을 덮지 않는다)
# - 내 커밋이 원격에 없는(ahead) 저장소는 받기만 시도하고 「push 필요」를 알린다
# - 갈라진(ahead+behind) 저장소는 건너뛴다 → 직접 확인 (git log origin/main..main)

set -uo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
REPOS=(. cdbd-design-system cdbd-marketing cdbd-design-service cdbd-templates makevu-qrstp)
bad=0

echo "CdBd sync — $ROOT"
for r in "${REPOS[@]}"; do
  d="$ROOT/$r"; name=$([ "$r" = . ] && echo "design(허브)" || echo "$r")
  if [ ! -d "$d/.git" ]; then echo "  ❌ $name — 저장소 없음 (tools/cdbd-setup.sh 실행)"; bad=1; continue; fi
  if ! git -C "$d" fetch -q 2>/dev/null; then echo "  ❌ $name — fetch 실패 (네트워크·SSH 키 확인)"; bad=1; continue; fi
  up=$(git -C "$d" rev-parse --abbrev-ref --symbolic-full-name '@{u}' 2>/dev/null) || { echo "  ⚠️  $name — 추적 브랜치 없음"; bad=1; continue; }
  read -r ahead behind < <(git -C "$d" rev-list --left-right --count "HEAD...$up")
  dirty=$(git -C "$d" status --porcelain | wc -l | tr -d ' ')
  if [ "$behind" -eq 0 ]; then
    msg="최신"; [ "$ahead" -gt 0 ] && { msg="최신 · ⚠️ push 안 한 커밋 $ahead개"; bad=1; }
    [ "$dirty" -gt 0 ] && msg="$msg · 미커밋 $dirty건"
    echo "  ✅ $name — $msg"; continue
  fi
  if [ "$dirty" -gt 0 ]; then echo "  ⚠️  $name — 받을 커밋 $behind개 있지만 미커밋 $dirty건이 있어 건너뜀"; bad=1; continue; fi
  if [ "$ahead" -gt 0 ]; then echo "  ⚠️  $name — 갈라짐(내 커밋 $ahead · 원격 $behind) → 건너뜀 · 직접 확인: git -C \"$d\" log $up..HEAD"; bad=1; continue; fi
  if git -C "$d" pull -q --ff-only 2>/dev/null; then echo "  🔧 $name — $behind개 받음"
  else echo "  ❌ $name — pull 실패"; bad=1; fi
done
date +%s > "$ROOT/.git/cdbd-last-sync" 2>/dev/null || true
[ $bad -eq 0 ] && echo "완료 — 전부 최신" || echo "완료 — ⚠️ 표시된 저장소를 확인하세요"
exit $bad
