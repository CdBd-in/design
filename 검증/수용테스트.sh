#!/usr/bin/env bash
# 팀원 수용 테스트 — 문항마다 새 claude -p 세션을 해당 볼트에서 켜고(읽기 전용), 볼트 밖 채점표로 자동 채점한다.
# 사용법: bash "검증/수용테스트.sh" [--key <채점표.md>] [--only Q01,Q07] [--jobs 5] [--out <결과 폴더>]
# 문항 = 「검증/팀원 수용 테스트.md」 표 · 채점 기준 = 볼트 밖 채점표 「### Qnn」 절
set -euo pipefail
HUB="$(cd "$(dirname "$0")/.." && pwd)"
KEY=""; ONLY=""; JOBS=5; OUT=""
while [ $# -gt 0 ]; do
  case "$1" in
    --key) KEY="$2"; shift 2;;
    --only) ONLY="$2"; shift 2;;
    --jobs) JOBS="$2"; shift 2;;
    --out) OUT="$2"; shift 2;;
    *) echo "알 수 없는 옵션: $1"; exit 2;;
  esac
done
[ -z "$OUT" ] && OUT="$HOME/Desktop/cdbd-수용테스트-결과/$(date +%Y%m%d-%H%M)"
case "$OUT" in "$HUB"*) echo "❌ 결과를 볼트 안에 저장하지 않는다: $OUT"; exit 2;; esac
mkdir -p "$OUT"
command -v claude >/dev/null || { echo "❌ claude CLI 없음"; exit 1; }

HUB="$HUB" KEY="$KEY" ONLY="$ONLY" JOBS="$JOBS" OUT="$OUT" python3 - <<'PY'
import os, re, json, subprocess, concurrent.futures as cf, datetime
HUB, KEY, ONLY, JOBS, OUT = (os.environ[k] for k in ("HUB","KEY","ONLY","JOBS","OUT"))
VAULTS = {"전체": ["design","cdbd-marketing","cdbd-templates"], "T": ["cdbd-templates"], "SV": ["cdbd-design-service"],
          "DS": ["cdbd-design-system"], "MK": ["cdbd-marketing"], "허브": ["design"]}
doc = open(os.path.join(HUB, "검증/팀원 수용 테스트.md"), encoding="utf-8").read()
qs = [r for r in (l.split("|") for l in doc.splitlines() if re.match(r"^\| Q\d\d ", l))]
qs = [(c[1].strip(), c[2].strip(), c[3].strip()) for c in qs]
if ONLY: qs = [q for q in qs if q[0] in ONLY.split(",")]
key = open(KEY, encoding="utf-8").read() if KEY else ""
def crit(qid):
    m = re.search(rf"^### {qid}\n(.*?)(?=^### |\Z)", key, re.S | re.M)
    return m.group(1).strip() if m else ""
tasks = [(qid, v, text) for qid, vk, text in qs for v in VAULTS[vk]]
print(f"▶ {len(tasks)}회 실행 (문항 {len(qs)}개) · 동시 {JOBS} · 결과 {OUT}")

def run(t):
    qid, v, text = t
    cwd = HUB if v == "design" else os.path.join(HUB, v)
    if not os.path.isdir(cwd): return dict(qid=qid, vault=v, error=f"볼트 없음: {cwd}")
    p = subprocess.run(["claude", "-p", text, "--max-turns", "15", "--allowedTools", "Read,Grep,Glob",
                        "--output-format", "json"], cwd=cwd, stdin=subprocess.DEVNULL,
                       capture_output=True, text=True, timeout=900)
    try: j = json.loads(p.stdout)
    except Exception: return dict(qid=qid, vault=v, error=(p.stdout + p.stderr)[-500:])
    r = dict(qid=qid, vault=v, question=text, answer=j.get("result", ""), turns=j.get("num_turns"),
             subtype=j.get("subtype"))
    r["tools_used"] = max((r["turns"] or 1) - 1, 0)
    c = crit(qid)
    if c:
        prompt = ("너는 채점자다. 아래 [채점 기준]으로 [답변]을 채점하라. 기준의 「통과」를 전부 충족하고 「불합격」에 하나도 해당하지 않아야 PASS다. "
                  "가점 항목은 없어도 PASS다. 「도구 사용 0회」 조건이 있으면 [도구 사용 횟수]로 판단한다.\n"
                  "첫 줄에 PASS 또는 FAIL만, 둘째 줄부터 한두 문장으로 이유.\n\n"
                  f"[질문] {text}\n[도구 사용 횟수] {r['tools_used']}\n[채점 기준]\n{c}\n\n[답변]\n{r['answer']}")
        g = subprocess.run(["claude", "-p", prompt, "--max-turns", "1"], cwd=OUT,
                           stdin=subprocess.DEVNULL, capture_output=True, text=True, timeout=300)
        out = g.stdout.strip()
        r["verdict"] = "PASS" if out.startswith("PASS") else ("FAIL" if out.startswith("FAIL") else "?")
        r["reason"] = out.split("\n", 1)[1].strip() if "\n" in out else out
    return r

res = []
with cf.ThreadPoolExecutor(int(JOBS)) as ex:
    for r in ex.map(run, tasks):
        res.append(r)
        print(f"  {r['qid']} @{r['vault']:<20} {r.get('verdict','·'):<5} 도구 {r.get('tools_used','-')}  {r.get('error','')[:80]}")
json.dump(res, open(os.path.join(OUT, "results.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
with open(os.path.join(OUT, "결과.md"), "w", encoding="utf-8") as f:
    n = sum(1 for r in res if r.get("verdict") == "PASS"); tot = len(res)
    f.write(f"# 수용 테스트 결과 — {datetime.datetime.now():%Y-%m-%d %H:%M}\n\n**{n}/{tot} 통과**\n\n| ID | 볼트 | 판정 | 도구 | 이유 |\n|---|---|---|---:|---|\n")
    for r in res:
        f.write(f"| {r['qid']} | {r['vault']} | {r.get('verdict', r.get('error','?')[:40])} | {r.get('tools_used','')} | {r.get('reason','').replace(chr(10),' ').replace('|','/')[:200]} |\n")
    f.write("\n---\n\n")
    for r in res:
        f.write(f"## {r['qid']} @ {r['vault']} — {r.get('verdict','')}\n\n**질문** {r.get('question','')}\n\n{r.get('answer', r.get('error',''))}\n\n")
print(f"\n✅ {sum(1 for r in res if r.get('verdict')=='PASS')}/{len(res)} 통과 · {os.path.join(OUT,'결과.md')}")
PY
