#!/usr/bin/env python3
"""경로 가이드 STEP 4 검증 — 마지막 세션에서 Claude가 실제로 연 파일을 대화 기록에서 추출.

사용법:  python3 "_경로가이드-검증.py" [저장소명]     기본값 cdbd-templates
"""
import json, os, sys, glob, time

repo = sys.argv[1] if len(sys.argv) > 1 else "cdbd-templates"
d = os.path.expanduser(f"~/.claude/projects/-Users-mustard-Documents-GitHub-design-{repo}")
files = sorted(glob.glob(d + "/*.jsonl"), key=os.path.getmtime, reverse=True)
if not files:
    sys.exit(f"❌ 대화 기록 없음: {d}")
f = files[0]
print(f"📄 세션: {os.path.basename(f)}  ({time.strftime('%Y-%m-%d %H:%M', time.localtime(os.path.getmtime(f)))})\n")

asks, opened = [], []
for line in open(f, encoding="utf-8"):
    try: o = json.loads(line)
    except Exception: continue
    m = o.get("message") or {}
    c = m.get("content")
    if m.get("role") == "user" and isinstance(c, str) and not c.startswith("<"):
        asks.append(c.strip().replace("\n", " ")[:70])
    if not isinstance(c, list): continue
    for b in c:
        if not isinstance(b, dict): continue
        if b.get("type") == "text" and m.get("role") == "user":
            t = b.get("text", "").strip()
            if t and not t.startswith("<"): asks.append(t.replace("\n", " ")[:70])
        if b.get("type") == "tool_use":
            i = b.get("input") or {}
            v = i.get("file_path") or i.get("pattern") or i.get("command") or ""
            opened.append((b.get("name"), str(v)))

print("🗣  사용자가 시킨 말")
for a in asks[:6]: print(f"   · {a}")

print("\n📂 Claude가 연/찾은 것")
for n, v in opened[:20]: print(f"   {n:6} {v[:100]}")
if not opened: print("   (없음 — 툴 호출 0건)")

blob = " ".join(v for _, v in opened)
def hit(*keys): return any(k in blob for k in keys)

print("\n" + "─" * 52)
print("판정")
checks = [
    ("① 1-7 상세페이지 라우팅", hit("1-7. 템플릿 상세", "1-7.")),
    ("② 1-6-2 카드 라우팅",      hit("1-6-2", "카드 기능")),
    ("③ 카드 자동화 스킬",       hit("cdbd-card-automation")),
]
for label, ok in checks:
    print(f"  {'✅' if ok else '⬜'} {label}")
if hit("_기능별 경로 가이드"):
    print("  ⚠️  경로 가이드를 '직접 찾아 읽었음' → @import 자동 로드가 안 됐을 가능성")
else:
    print("  ℹ️  경로 가이드를 따로 안 읽음 (= @import로 이미 로드됐거나, 아예 참조 안 함)")
print("─" * 52)
print("※ 툴 호출 0건인데 답이 그럴듯하면 = CLAUDE.md 기억으로 답한 것 → 가짜 통과 의심")
