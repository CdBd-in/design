#!/usr/bin/env bash
# CdBd 팀 — 새 기기 Claude 셋업 (몇 번 다시 실행해도 안전하다)
#
#   bash ~/Documents/GitHub/design/tools/cdbd-setup.sh
#
# 하는 일
#   1. 하위 저장소 5개 확인 — 없으면 clone (SSH 키가 GitHub에 등록돼 있어야 함 · ONBOARDING §3)
#   2. gstack(헤드리스 브라우저) 확인 — 없으면 설치 안내 후 중단
#   3. 전역 스킬 링크   ~/.claude/skills/cdbd-card-automation → design/cdbd-templates/.claude/skills/cdbd-card-automation
#   4. 인증 헬퍼 링크   ~/.config/cdbd/auth.py · image_library.py → design/tools/cdbd/
#   5. ~/.config/cdbd/cdbd.env — 없으면 견본을 복사하고 채우라고 안내 (비밀값은 출력하지 않는다)
#   6. ~/.claude/CLAUDE.md 에 전역 안내 @import 한 줄 (이미 있으면 건너뜀)
#   7. 세션 시작 점검 훅 등록 (tools/cdbd-session-check.sh가 있을 때만)
#   8. 인증 점검 (cdbd.env가 채워져 있을 때만)
#
# 기존 파일을 링크로 바꿀 때는 지우지 않고 「이름.bak-날짜」로 옮겨 둔다.
# 환경변수: CLAUDE_CONFIG_DIR(기본 ~/.claude) · CDBD_CONFIG_DIR(기본 ~/.config/cdbd)

set -uo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"   # design/
CLAUDE_DIR="${CLAUDE_CONFIG_DIR:-$HOME/.claude}"
CFG="${CDBD_CONFIG_DIR:-$HOME/.config/cdbd}"
GH="git@github.com:CdBd-in"
REPOS=(cdbd-design-system cdbd-marketing cdbd-design-service cdbd-templates makevu-qrstp)
STAMP="$(date +%Y%m%d-%H%M%S)"
N_OK=0; N_FIX=0; N_WARN=0

ok()   { echo "  ✅ $*"; N_OK=$((N_OK+1)); }
fix()  { echo "  🔧 $*"; N_FIX=$((N_FIX+1)); }
warn() { echo "  ⚠️  $*"; N_WARN=$((N_WARN+1)); }
die()  { echo "  ❌ $*"; echo; echo "중단 — 위 문제를 해결하고 다시 실행하세요 (다시 실행해도 안전합니다)."; exit 1; }

# 링크 걸기: 이미 맞으면 그대로 · 다른 곳을 가리키는 링크면 교체 · 실제 파일/폴더면 .bak-날짜로 옮기고 링크
link_safe() {
  local src="$1" dst="$2" label="$3"
  [ -e "$src" ] || { warn "$label — 원본이 없습니다: $src"; return; }
  mkdir -p "$(dirname "$dst")"
  if [ -L "$dst" ]; then
    if [ "$(readlink "$dst")" = "$src" ]; then ok "$label"; return; fi
    rm "$dst"; ln -s "$src" "$dst"; fix "$label — 링크 대상을 바로잡음"; return
  fi
  if [ -e "$dst" ]; then
    mv "$dst" "$dst.bak-$STAMP"; ln -s "$src" "$dst"; fix "$label — 기존 사본을 $(basename "$dst").bak-$STAMP 로 옮기고 링크"; return
  fi
  ln -s "$src" "$dst"; fix "$label — 링크 생성"
}

echo "CdBd 셋업 — design = $ROOT"
echo

echo "1. 하위 저장소"
for r in "${REPOS[@]}"; do
  if [ -d "$ROOT/$r/.git" ]; then ok "$r"
  else
    echo "  ⏳ $r 없음 → clone"
    if git clone -q "$GH/$r.git" "$ROOT/$r"; then fix "$r — clone 완료"
    else die "$r clone 실패 — SSH 키 등록을 확인하세요 (ONBOARDING §3-2 · ssh -T git@github.com)"; fi
  fi
done

echo "2. gstack (헤드리스 브라우저)"
if [ -x "$CLAUDE_DIR/skills/gstack/browse/dist/browse" ]; then ok "gstack browse"
else die "gstack이 없습니다 — $CLAUDE_DIR/skills/gstack 설치 후 다시 실행하세요 (ONBOARDING §3-6 Step 3)"; fi

echo "3. 전역 스킬"
link_safe "$ROOT/cdbd-templates/.claude/skills/cdbd-card-automation" "$CLAUDE_DIR/skills/cdbd-card-automation" "cdbd-card-automation"

echo "4. 인증 헬퍼"
mkdir -p "$CFG"; chmod 700 "$CFG"
for f in auth.py image_library.py; do link_safe "$ROOT/tools/cdbd/$f" "$CFG/$f" "$f"; done

echo "5. cdbd.env"
ENVF="$CFG/cdbd.env"
if [ ! -f "$ENVF" ]; then
  cp "$ROOT/tools/cdbd/cdbd.env.example" "$ENVF"; chmod 600 "$ENVF"
  warn "cdbd.env 견본을 만들었습니다 → $ENVF 를 채우세요 (공용 계정 · 다른 기기의 cdbd.env를 옮겨 와도 됨)"
else
  chmod 600 "$ENVF"
  missing=()
  for k in CDBD_EMAIL CDBD_PASSWORD CDBD_SUPABASE_URL CDBD_SUPABASE_ANON_KEY; do
    grep -Eq "^$k=.+" "$ENVF" || missing+=("$k")
  done
  if [ ${#missing[@]} -eq 0 ]; then ok "cdbd.env — 키 4개 채워짐"
  else warn "cdbd.env — 비어 있는 키: ${missing[*]}"; fi
fi

echo "6. 전역 CLAUDE.md"
GLOBAL_SRC="$ROOT/tools/cdbd/global-CLAUDE.md"
case "$GLOBAL_SRC" in "$HOME"/*) IMP="~/${GLOBAL_SRC#"$HOME"/}";; *) IMP="$GLOBAL_SRC";; esac
IMP_LINE="@${IMP// /\\ }"          # 공백은 백슬래시 이스케이프 (따옴표·꺾쇠는 로드 안 됨 · 2026-09-29 실측)
GCM="$CLAUDE_DIR/CLAUDE.md"
if [ -f "$GCM" ] && grep -qxF "$IMP_LINE" "$GCM"; then ok "~/.claude/CLAUDE.md @import"
else
  mkdir -p "$CLAUDE_DIR"
  { [ -s "$GCM" ] && echo; echo "# CdBd 팀 전역 안내 (tools/cdbd-setup.sh가 추가)"; echo "$IMP_LINE"; } >> "$GCM"
  fix "~/.claude/CLAUDE.md 에 @import 추가"
fi

echo "7. 세션 시작 점검 훅"
HOOK="$ROOT/tools/cdbd-session-check.sh"
if [ -f "$HOOK" ]; then
  r=$(python3 - "$CLAUDE_DIR/settings.json" "bash \"$HOOK\"" <<'PY'
import json, os, sys
path, cmd = sys.argv[1], sys.argv[2]
d = json.load(open(path)) if os.path.exists(path) else {}
ss = d.setdefault('hooks', {}).setdefault('SessionStart', [])
if any(h.get('command') == cmd for g in ss for h in g.get('hooks', [])):
    print('exists')
else:
    ss.append({'hooks': [{'type': 'command', 'command': cmd}]})
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = path + '.tmp'
    json.dump(d, open(tmp, 'w'), indent=2, ensure_ascii=False)
    os.replace(tmp, path)
    print('added')
PY
)
  [ "$r" = "exists" ] && ok "SessionStart 훅" || fix "SessionStart 훅 등록"
else
  echo "  ·  건너뜀 — cdbd-session-check.sh 가 아직 없습니다 (체크리스트 15번)"
fi

echo "8. 인증 점검"
if grep -Eq '^CDBD_EMAIL=.+' "$ENVF" && grep -Eq '^CDBD_PASSWORD=.+' "$ENVF"; then
  if out=$(python3 "$CFG/auth.py" 2>&1); then ok "get_credentials() — $(echo "$out" | grep '인증 방식' | sed 's/ *: */: /')"
  else warn "get_credentials() 실패 — $(echo "$out" | tail -1)"; fi
else
  echo "  ·  건너뜀 — cdbd.env 를 채운 뒤 다시 실행하세요"
fi

echo
echo "완료 — ✅ $N_OK · 🔧 고침 $N_FIX · ⚠️ 확인 필요 $N_WARN"
[ "$N_WARN" -eq 0 ] || echo "⚠️ 항목을 해결한 뒤 다시 실행하면 됩니다."
echo "다음: 폴더 신뢰 승인(볼트마다 claude 한 번 실행 → 「Yes, proceed」) — ONBOARDING §3-6 Step 6"
