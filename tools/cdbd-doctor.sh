#!/usr/bin/env bash
# CdBd 팀 — 이 기기의 Claude 셋업 상태 점검표 (아무것도 고치지 않는다 · 읽기만)
#
#   bash ~/Documents/GitHub/design/tools/cdbd-doctor.sh
#
# ❌가 있으면 대개 `tools/cdbd-setup.sh` 또는 `tools/cdbd-sync.sh` 한 번으로 해결된다.
# 네트워크를 쓴다(git fetch · Supabase 인증 확인). 헤드리스 브라우저를 잠깐 띄웠다가 끈다.

set -uo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CFG="${CDBD_CONFIG_DIR:-$HOME/.config/cdbd}"
CLAUDE_DIR="${CLAUDE_CONFIG_DIR:-$HOME/.claude}"
VAULTS=(. cdbd-design-system cdbd-marketing cdbd-design-service cdbd-templates makevu-qrstp)
P=0; F=0; W=0
pass() { echo "  ✅ $*"; P=$((P+1)); }
fail() { echo "  ❌ $*"; F=$((F+1)); }
warn() { echo "  ⚠️  $*"; W=$((W+1)); }
vname() { [ "$1" = . ] && echo "design(허브)" || echo "$1"; }

echo "CdBd doctor — $(hostname -s) · design = $ROOT"

echo "1. 저장소 (허브 + 5)"
for r in "${VAULTS[@]}"; do
  d="$ROOT/$r"; n=$(vname "$r")
  [ -d "$d/.git" ] || { fail "$n — 없음 → tools/cdbd-setup.sh"; continue; }
  git -C "$d" fetch -q 2>/dev/null || { warn "$n — fetch 실패(오프라인?)"; continue; }
  up=$(git -C "$d" rev-parse --abbrev-ref '@{u}' 2>/dev/null) || { warn "$n — 추적 브랜치 없음"; continue; }
  read -r a b < <(git -C "$d" rev-list --left-right --count "HEAD...$up")
  dirty=$(git -C "$d" status --porcelain | wc -l | tr -d ' ')
  extra=""; [ "$dirty" -gt 0 ] && extra=" · 미커밋 $dirty건"
  if [ "$a" -eq 0 ] && [ "$b" -eq 0 ]; then pass "$n — 최신$extra"
  elif [ "$a" -eq 0 ]; then fail "$n — $b개 뒤처짐 → tools/cdbd-sync.sh$extra"
  elif [ "$b" -eq 0 ]; then warn "$n — push 안 한 커밋 $a개$extra"
  else fail "$n — 갈라짐(내 $a · 원격 $b) → 직접 확인$extra"; fi
done

echo "2. 링크"
chk_link() { # dst expected label
  if [ -L "$1" ] && [ "$(readlink "$1")" = "$2" ] && [ -e "$1" ]; then pass "$3"
  elif [ -e "$1" ] && [ ! -L "$1" ]; then fail "$3 — 링크가 아니라 옛 사본 → tools/cdbd-setup.sh"
  else fail "$3 — 없음/깨짐 → tools/cdbd-setup.sh"; fi
}
chk_link "$CLAUDE_DIR/skills/cdbd-card-automation" "$ROOT/cdbd-templates/.claude/skills/cdbd-card-automation" "전역 스킬 cdbd-card-automation"
chk_link "$CFG/auth.py" "$ROOT/tools/cdbd/auth.py" "인증 헬퍼 auth.py"
chk_link "$CFG/image_library.py" "$ROOT/tools/cdbd/image_library.py" "인증 헬퍼 image_library.py"
if grep -q 'pinnedIds' "$CLAUDE_DIR/skills/cdbd-card-automation/card-driver.js" 2>/dev/null; then
  pass "카드 드라이버 최신판(pinnedIds 있음)"
else fail "카드 드라이버 옛판 — pinnedIds 없음"; fi

echo "3. 전역 설정"
GCM="$CLAUDE_DIR/CLAUDE.md"
if grep -q 'tools/cdbd/global-CLAUDE.md' "$GCM" 2>/dev/null; then pass "~/.claude/CLAUDE.md 전역 안내 @import"
else fail "~/.claude/CLAUDE.md 전역 안내 없음 → tools/cdbd-setup.sh"; fi
if python3 - "$CLAUDE_DIR/settings.json" "$ROOT/tools/cdbd-session-check.sh" <<'PY' 2>/dev/null
import json, sys
d = json.load(open(sys.argv[1]))
ok = any(sys.argv[2] in h.get('command', '') for g in d.get('hooks', {}).get('SessionStart', []) for h in g.get('hooks', []))
sys.exit(0 if ok else 1)
PY
then pass "SessionStart 점검 훅"; else fail "SessionStart 점검 훅 미등록 → tools/cdbd-setup.sh"; fi
out=$(bash "$ROOT/tools/cdbd-session-check.sh" 2>&1)
[ -z "$out" ] && pass "세션 시작 점검 — 경고 없음" || warn "세션 시작 점검: ${out#⚠️ }"

echo "4. 폴더 신뢰 승인 (승인 전엔 볼트의 .claude/settings.json 허용 목록이 무시된다)"
python3 - "$ROOT" "$HOME/.claude.json" <<'PY'
import json, os, sys
root, path = sys.argv[1], sys.argv[2]
try:
    proj = json.load(open(path)).get('projects', {})
except Exception:
    proj = {}
for v in ['.', 'cdbd-design-system', 'cdbd-marketing', 'cdbd-design-service', 'cdbd-templates', 'makevu-qrstp']:
    p = os.path.normpath(os.path.join(root, v))
    name = 'design(허브)' if v == '.' else v
    if proj.get(p, {}).get('hasTrustDialogAccepted'):
        print('  ✅ ' + name)
    else:
        print('  ❌ %s — 미승인 → cd "%s" && claude → 「Yes, proceed」 → /exit' % (name, p))
PY
n_trust_fail=$(python3 - "$ROOT" "$HOME/.claude.json" <<'PY'
import json, os, sys
root, path = sys.argv[1], sys.argv[2]
try: proj = json.load(open(path)).get('projects', {})
except Exception: proj = {}
print(sum(1 for v in ['.', 'cdbd-design-system', 'cdbd-marketing', 'cdbd-design-service', 'cdbd-templates', 'makevu-qrstp']
          if not proj.get(os.path.normpath(os.path.join(root, v)), {}).get('hasTrustDialogAccepted')))
PY
)
F=$((F + n_trust_fail)); P=$((P + 6 - n_trust_fail))

echo "5. Claudian 「사용자 설정 불러오기」(loadUserSettings — 꺼져 있으면 전역 스킬·전역 안내가 안 읽힌다)"
for r in "${VAULTS[@]}"; do
  n=$(vname "$r"); s="$ROOT/$r/.claudian/claudian-settings.json"
  if [ ! -f "$s" ]; then pass "$n — 기본값(켜짐)"; continue; fi
  v=$(python3 -c "import json,sys;d=json.load(open(sys.argv[1]));print(d.get('providerConfigs',{}).get('claude',{}).get('loadUserSettings',True))" "$s" 2>/dev/null)
  [ "$v" = "True" ] && pass "$n — 켜짐" || fail "$n — 꺼짐 → Claudian 설정에서 켜기"
done

echo "6. 인증·도구"
ENVF="$CFG/cdbd.env"
if [ -f "$ENVF" ]; then
  miss=(); for k in CDBD_EMAIL CDBD_PASSWORD CDBD_SUPABASE_URL CDBD_SUPABASE_ANON_KEY; do grep -Eq "^$k=.+" "$ENVF" || miss+=("$k"); done
  perm=$(stat -f %Lp "$ENVF" 2>/dev/null || stat -c %a "$ENVF")
  if [ ${#miss[@]} -eq 0 ]; then pass "cdbd.env — 키 4개 (권한 $perm)"; else fail "cdbd.env — 빈 키: ${miss[*]}"; fi
  [ "$perm" = 600 ] || warn "cdbd.env 권한이 $perm — chmod 600 권장"
else fail "cdbd.env 없음 → tools/cdbd-setup.sh 후 채우기"; fi
if out=$(python3 "$CFG/auth.py" 2>&1); then pass "get_credentials() — $(echo "$out" | grep '인증 방식' | sed 's/.*: *//; s/ (.*//')"
else fail "get_credentials() 실패 — $(echo "$out" | tail -1)"; fi
B="$CLAUDE_DIR/skills/gstack/browse/dist/browse"
if [ -x "$B" ]; then
  u=$("$B" url 2>/dev/null | tail -1)
  "$B" stop >/dev/null 2>&1; pkill -f 'gstack/browse/src' 2>/dev/null
  [ -n "$u" ] && pass "gstack browse 실행 ($u)" || fail "gstack browse 실행 실패"
else fail "gstack browse 없음 → gstack 설치"; fi

echo
echo "결과 — ✅ $P · ⚠️ $W · ❌ $F"
[ "$F" -eq 0 ] && echo "이 기기는 CdBd 작업 준비가 끝났습니다." || echo "❌ 항목의 → 안내를 따르세요. 대부분 tools/cdbd-setup.sh · tools/cdbd-sync.sh 로 해결됩니다."
exit $([ "$F" -eq 0 ] && echo 0 || echo 1)
