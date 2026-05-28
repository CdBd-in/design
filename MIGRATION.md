# CdBd 디자인 볼트 전환 가이드 (기존 사용자용)

> 이 문서는 **이전에 `git-sync-sh` 단일 볼트로 작업하던 팀원**이
> 새로운 구조(허브 `design` + 카테고리 5개 독립 저장소, SSH 인증)로
> 안전하게 갈아타기 위한 안내입니다.
>
> **새로 합류한 팀원은 이 문서가 아니라 `ONBOARDING.md`를 보세요.**

---

## 변경 요약

| 항목 | 옛 구조 | 새 구조 |
|---|---|---|
| **저장소 수** | 1개 (`git-sync-sh`) | 6개 (허브 `design` + 카테고리 5개) |
| **인증 방식** | PAT (HTTPS) | SSH 키 |
| **저장소 이름** | `git-sync-sh` | `cdbd-design-system`(이 폴더가 옛것의 후속), `cdbd-marketing`, `cdbd-design-service`, `cdbd-templates`, `makevu-qrstp` |
| **옵시디언 볼트** | 1개 | 6개 (카테고리 5개 + 허브 1개) |

> 💡 옛 `git-sync-sh`의 모든 커밋 히스토리는 **`cdbd-design-system`에 그대로 보존**되어 있습니다. 작업물은 한 줄도 사라지지 않았습니다.

---

## 작업 시간 안내

- SSH가 처음인 경우: **약 30~40분**
- SSH 키를 이미 다른 용도로 쓰고 있는 경우: **약 15~20분**

한 번에 마치는 것을 추천합니다.

> ⚠️ **시작 전 필수:** 마지막 동기화 이후 작업한 파일이 안 올라간 상태일 수 있습니다.
> Step 0에서 옛 볼트의 푸시 상태부터 확인합니다.

---

## Step 0. 옛 볼트 안전 확인 (가장 중요)

새 구조로 넘어가기 전에 옛 볼트의 **미푸시 변경이 없는지 반드시 확인**합니다.
빠뜨리면 새 구조에 옮길 때 데이터가 사라질 수 있습니다.

### 0-1. 옵시디언에서 마지막 동기화

옵시디언에서 옛 `git-sync-sh` 볼트를 열고:

1. `⌘+P` → **`Obsidian Git: Commit-and-sync`** 실행
2. 토스트 알림에서 결과 확인:
   - `Pushed n commits` → 정상. 남아 있던 변경이 푸시됨
   - `No changes to commit` → 이미 동기화 상태
   - 에러 → **여기서 멈추고 담당자에게 문의** (절대 다음 단계로 넘어가지 마세요)

### 0-2. 터미널에서 더블 체크

옛 볼트가 있던 폴더로 이동해 상태를 점검합니다 (경로는 본인 환경에 맞게):

```bash
cd ~/Documents/GitHub/git-sync-sh
git status
git fetch origin
git log origin/main..HEAD --oneline
```

**기대 결과:**
- `git status` → `working tree clean`
- 마지막 명령 → **출력 없음** (푸시 안 된 커밋 없음)

> ⚠️ 둘 중 하나라도 다른 결과가 나오면 멈추세요.
> - `working tree clean`이 아니면: 미저장 변경 있음 → 옵시디언에서 저장하고 동기화
> - `git log ...`에 줄이 출력되면: 미푸시 커밋 있음 → `git push origin main`

### 0-3. 전체 폴더 백업

만약을 대비해 옛 볼트 폴더를 통째로 백업합니다 (오늘 날짜로):

```bash
cp -R ~/Documents/GitHub/git-sync-sh ~/Desktop/git-sync-sh-backup-$(date +%Y%m%d)
ls ~/Desktop/git-sync-sh-backup-*
```

**기대 결과:** 데스크탑에 `git-sync-sh-backup-YYYYMMDD` 폴더가 생기고, 원본 내용이 그대로 보임.

> 💡 이 백업은 새 환경이 안정적으로 동작하는 게 확인되면(약 1~2주 후) 삭제하세요.

### 0-4. 옵시디언 완전 종료

전환 작업 중 obsidian-git 자동 sync가 끼어들면 폴더가 망가질 수 있습니다.
**옵시디언을 `⌘+Q`로 완전히 종료**한 뒤 작업 내내 꺼둡니다.

---

## Step 1. SSH 키 준비

> 💡 **SSH 키를 이미 다른 용도로 쓰고 있다면 1-2로 바로 가서 GitHub 등록 여부만 확인하세요.** 새로 만들 필요 없습니다.

### 1-1. SSH 키가 있는지 확인

```bash
ls -la ~/.ssh/
```

**3가지 시나리오:**

| 시나리오 | 출력 | 처리 |
|---|---|---|
| **A. 폴더 자체가 없음** | `No such file or directory` | 1-2 (신규 생성)로 진행 |
| **B. 폴더 있는데 `id_*` 파일 없음** | `known_hosts`만 있음 | 1-2 (신규 생성)로 진행 |
| **C. `id_ed25519` 또는 `id_rsa` 있음** | 키 파일이 보임 | 1-3 (기존 키 재사용)으로 진행 |

### 1-2. SSH 키 신규 생성

이메일 자리에는 본인 기기 식별용 라벨을 넣습니다 (예: `MacBook-홍길동-2026-05-21`):

```bash
ssh-keygen -t ed25519 -C "MacBook-홍길동-2026-05-21" -f ~/.ssh/id_ed25519
```

두 번의 프롬프트에서 **패스프레이즈를 설정**합니다. 짧고 복잡한 것보다 **여러 단어를 띄어서 조합**한 문장이 안전합니다 (예: `푸른하늘 노란새 빨간자전거 2026`). 패스프레이즈를 **1Password 같은 곳에 안전하게 저장**해 두세요.

이어서 macOS 자동 등록 설정:

```bash
eval "$(ssh-agent -s)"
ssh-add --apple-use-keychain ~/.ssh/id_ed25519
```

마지막으로 재부팅 후에도 동작하도록 config 작성:

```bash
cat > ~/.ssh/config << 'EOF'
Host github.com
  AddKeysToAgent yes
  UseKeychain yes
  IdentityFile ~/.ssh/id_ed25519
EOF

chmod 600 ~/.ssh/config
```

→ **Step 2로 진행**

### 1-3. 기존 SSH 키 재사용 (시나리오 C인 경우)

기존 키가 깃허브에 이미 등록돼 있는지 확인:

```bash
ssh -T git@github.com
```

- **`Hi <사용자명>! You've successfully authenticated...`** → 등록돼 있음. **Step 3으로 바로 진행** (Step 2 건너뜀)
- **`Permission denied (publickey)`** → 키는 있지만 깃허브에 등록 안 돼 있음. **Step 2로 진행**

> ⚠️ 사용자명이 `CdBd-in`이 아니라 본인 개인 계정이면, 깃허브에서 공용 계정으로 별도 등록 필요. Step 2로 진행하세요.

---

## Step 2. 깃허브에 공개키 등록

**Step 1.** 공개키를 클립보드에 복사:

```bash
pbcopy < ~/.ssh/id_ed25519.pub
```

> 💡 공개키(`.pub`)는 노출돼도 안전합니다. 개인키는 절대 외부에 보내지 마세요.

**Step 2.** 브라우저에서 **CdBd 공용 계정**으로 깃허브 로그인 후:

```
https://github.com/settings/keys
```

**Step 3.** 우측 `New SSH key` 클릭 → 입력:
- **Title**: `MacBook-홍길동` 같이 본인 기기 식별 라벨
- **Key type**: `Authentication Key` (기본값)
- **Key**: `⌘+V`로 붙여넣기

**Step 4.** `Add SSH key` → 비밀번호 또는 2FA 확인.

**Step 5.** 검증:

```bash
ssh -T git@github.com
```

처음 실행 시 `Are you sure you want to continue connecting?` → **`yes`** 입력.

다음이 보이면 성공:
```
Hi CdBd-in! You've successfully authenticated, but GitHub does not provide shell access.
```

---

## Step 3. 새 구조로 저장소 받기

옛 `git-sync-sh` 폴더는 **건드리지 않고 그대로 두고**, 새 구조를 별도 위치에 받습니다. 옛 폴더는 Step 6에서 마지막에 정리합니다.

### 3-1. 작업 폴더 만들기

옛 `git-sync-sh`가 있던 위치 옆에 `design`이라는 새 작업 폴더를 만듭니다.

예: 옛 폴더가 `~/Documents/GitHub/git-sync-sh`라면, 새 폴더는 `~/Documents/GitHub/design`:

```bash
cd ~/Documents/GitHub
```

### 3-2. 허브 저장소부터 받기

```bash
git clone git@github.com:CdBd-in/design.git
cd design
```

### 3-3. 카테고리 저장소 5개 받기

```bash
git clone git@github.com:CdBd-in/cdbd-design-system.git
git clone git@github.com:CdBd-in/cdbd-marketing.git
git clone git@github.com:CdBd-in/cdbd-design-service.git
git clone git@github.com:CdBd-in/cdbd-templates.git
git clone git@github.com:CdBd-in/makevu-qrstp.git
```

**기대 결과:** 비밀번호도 토큰도 묻지 않고 6번 모두 통과되면 정상. SSH가 자동 인증해주고 있는 것입니다.

### 3-4. 받은 결과 확인

```bash
ls
```

다음 폴더들이 보여야 합니다: `cdbd-design-system`, `cdbd-marketing`, `cdbd-design-service`, `cdbd-templates`, `makevu-qrstp` + 허브 파일 (`ONBOARDING.md`, `README.md`).

`cdbd-design-system` 폴더 안의 내용이 옛 `git-sync-sh`와 사실상 동일한지 한 번 봐두시면 안심됩니다:

```bash
ls cdbd-design-system
```

---

## Step 4. 옵시디언 볼트 6개 등록

### 4-1. 옛 볼트 등록 제거

옵시디언 실행 → 좌측 하단 볼트 아이콘 → **`Manage vaults`**.

목록에서 옛 경로(`.../git-sync-sh`) 호버 시 나타나는 **`-`** 또는 **`x`** 버튼으로 등록 해제.

> 💡 이건 옵시디언이 그 폴더를 잊어버리게 하는 것일 뿐, 실제 폴더는 안 지워집니다.

### 4-2. 새 볼트 6개 열기

같은 `Manage vaults`에서 **`Open folder as vault`**로 다음 6개를 차례로 등록합니다.
카테고리 5개를 먼저, 허브를 마지막에:

1. `~/Documents/GitHub/design/cdbd-design-system`
2. `~/Documents/GitHub/design/cdbd-marketing`
3. `~/Documents/GitHub/design/cdbd-design-service`
4. `~/Documents/GitHub/design/cdbd-templates`
5. `~/Documents/GitHub/design/makevu-qrstp`
6. `~/Documents/GitHub/design` (허브, 마지막)

> 🔑 **`cdbd-design-system` 처음 열기:** Trust author 다이얼로그가 뜸 → **`Trust author and enable plugins`** 선택.
> 이 볼트는 옛 `git-sync-sh`의 후속이라 obsidian-git이 이미 설치돼 있습니다.

### 4-3. obsidian-git 검증 (`cdbd-design-system` 먼저)

`cdbd-design-system` 볼트 활성화 상태에서:

1. `⌘+P` → **`Obsidian Git: Pull`** 실행
2. **기대 결과:** `Everything is up to date` 또는 변경사항 풀, 에러 없음

> ⚠️ **만약 에러가 나면 멈추세요:**
> - `Permission denied (publickey)` → Step 2가 제대로 안 됨. `ssh -T git@github.com`으로 인증 재확인
> - 그 외 → 담당자에게 문의

### 4-4. 나머지 5개 볼트에 obsidian-git 설치

`design`, `cdbd-marketing`, `cdbd-design-service`, `cdbd-templates`, `makevu-qrstp` 각각에서 진행합니다.

> 💡 **이미 설치돼 있는 볼트는 건너뛰세요.**
> 다른 기기에서 먼저 셋업해 푸시한 상태라면 obsidian-git이 **이미 설치·활성화돼 있을 수 있습니다.** 좌측 사이드바에 `Obsidian Git` 항목이 보이면 설치된 것입니다. 이 경우 아래 1~2단계(설치)는 건너뛰고, **3단계(설정 확인)와 4단계(검증)만** 진행하세요.

1. `⌘+,` → **`커뮤니티 플러그인`** → (처음 여는 볼트면) **`커뮤니티 플러그인 켜기`**
2. **`찾아보기`** → **`obsidian git`** 검색 → **`Obsidian Git`** (작성자: **Vinzent03**) 설치 → 활성화
3. 좌측 사이드바 `Obsidian Git` 설정이 다음과 같이 돼 있는지 확인 (다르면 아래 값으로 맞춤):
   - **Auto pull interval (minutes)**: `10`
   - **Auto commit-and-sync interval (minutes)**: `10`
   - **Pull on startup**: ON
4. 검증: `⌘+P` → `Obsidian Git: Commit-and-sync` → `No changes to commit` 확인

---

## Step 5. 옛 PAT 정리

옛 구조에서는 PAT(개인 액세스 토큰)로 인증했지만, 이제 SSH로 전환됐으므로 옛 토큰은 더 이상 필요 없습니다. 보안을 위해 폐기합니다.

### 5-1. 옛 토큰 확인

브라우저에서 **CdBd 공용 계정**으로:

```
https://github.com/settings/tokens
```

**`Tokens (classic)`** 탭에서 다음과 같은 옛 토큰을 찾습니다:
- Note가 `Obsidian`, `obsidian-git`, `vault sync` 같은 키워드인 것
- 특히 **만료일 없음(`This token has no expiration date`)** + **`repo` 권한**인 것 → 즉시 폐기 대상

### 5-2. 키체인의 옛 자격증명 제거

옛 PAT가 macOS 키체인에 저장돼 있을 수 있습니다. 새 환경은 SSH로만 동작하므로 옛 자격증명을 빼냅니다:

```bash
git credential-osxkeychain erase <<EOF
protocol=https
host=github.com
EOF
```

> 명령 4줄을 한 번에 복사·붙여넣고 Enter 치면 됩니다. 출력 없이 조용히 처리됩니다.

### 5-3. 옛 PAT 폐기

깃허브 토큰 페이지에서 해당 옛 토큰 옆 **`Delete`** 클릭 → **`I understand, delete this token`** 으로 확인.

> ⚠️ **`Obsidian BRAT` 토큰은 건드리지 마세요.** Claudian이나 베타 플러그인 설치에 별도로 쓰이는 토큰이라 그대로 두는 게 안전합니다.

### 5-4. 폐기 후 재검증

옵시디언에서 `cdbd-design-system` 볼트 → `⌘+P` → `Obsidian Git: Pull` 한 번 더 실행.

**기대 결과:** 에러 없이 통과. 이게 통과되면 SSH로만 모든 동기화가 이루어지고 있는 것이 확정 검증된 상태입니다.

---

## Step 6. 옛 볼트 폴더 정리

새 환경이 정상 동작하는 게 확인됐으니, 옛 `git-sync-sh` 폴더와 `git-sync-sh-backup-*` 백업의 정리 계획을 세웁니다.

### 권장 정리 시점

| 폴더 | 처리 |
|---|---|
| **`git-sync-sh`** (원본) | **즉시 삭제 가능**. 모든 데이터는 `cdbd-design-system`에 그대로 있고 깃허브에도 백업돼 있음 |
| **`git-sync-sh-backup-YYYYMMDD`** (Step 0-3에서 만든 백업) | **1~2주 후 삭제 권장**. 새 환경에서 작업을 며칠 해보고 문제 없는 게 확실해진 뒤 |

### 옛 원본 폴더 삭제 (선택)

```bash
rm -rf ~/Documents/GitHub/git-sync-sh
```

> ⚠️ `rm -rf`는 휴지통을 거치지 않고 즉시 영구 삭제합니다. **명령 실행 전 한 번 더 경로 확인하세요.**
>
> 불안하면 휴지통을 거치는 방법으로:
> ```bash
> mv ~/Documents/GitHub/git-sync-sh ~/.Trash/git-sync-sh-old
> ```

### 백업 폴더 삭제 (1~2주 후)

```bash
rm -rf ~/Desktop/git-sync-sh-backup-*
```

---

## 완료 체크리스트

- [ ] Step 0: 옛 볼트 미푸시 변경 없음 + 백업 완료
- [ ] Step 1~2: SSH 키 생성·등록, `ssh -T git@github.com`로 `Hi CdBd-in!` 확인
- [ ] Step 3: 6개 저장소 모두 SSH로 클론 (비밀번호/토큰 묻지 않음)
- [ ] Step 4: 옵시디언에 6개 볼트 모두 등록, obsidian-git 동작 확인
- [ ] Step 5: 옛 PAT 폐기 후에도 동기화 정상 동작
- [ ] Step 6: 옛 원본 폴더 정리 (백업은 1~2주 후)

전부 체크되면 전환 완료입니다.

---

## 자주 발생하는 문제

**Q. Step 3에서 클론 시 비밀번호를 묻습니다.**
A. SSH가 아니라 HTTPS로 클론하려고 한 것입니다. URL이 `https://...`로 시작하면 그렇습니다. **`git@github.com:CdBd-in/...` 형태**가 맞는지 확인하세요.

**Q. Step 4에서 `Permission denied (publickey)` 에러가 뜹니다.**
A. SSH 키가 등록은 됐지만 ssh-agent에 안 잡혀 있을 수 있습니다. 다음 명령으로 등록:
```bash
ssh-add --apple-use-keychain ~/.ssh/id_ed25519
```

**Q. 옛 `git-sync-sh` 폴더에 미푸시 변경이 있는 걸 뒤늦게 발견했어요.**
A. 옛 폴더에서 `git push origin main`을 실행해 깃허브의 `cdbd-design-system`에 푸시합니다 (저장소 이름 변경은 자동 리다이렉트됨). 그다음 새 환경의 `cdbd-design-system` 볼트에서 `Obsidian Git: Pull`로 받아옵니다.

**Q. 옛 볼트의 `.obsidian/` 설정(테마, 플러그인 등)을 새 볼트들에 옮기고 싶어요.**
A. `cdbd-design-system`은 옛 `git-sync-sh`의 `.obsidian/`을 그대로 물려받았으니 신경 쓸 필요 없습니다. **나머지 5개 볼트**(`cdbd-marketing` 등)는 각자 별도로 설정해야 합니다. 한 번 설정해두면 obsidian-git이 동기화하므로 다른 기기에도 적용됩니다.

**Q. 다른 기기(예: 회사 데스크탑)에서도 전환해야 합니다.**
A. 그 기기에서 이 문서를 처음부터 다시 따라 하면 됩니다. **SSH 키는 기기마다 새로 만들어야** 하고(같은 키 공유 비권장), 깃허브에는 두 키를 모두 등록하면 됩니다.

---

## 도움 요청

- 전환 중 막히는 부분: 팀 담당자 (`help@cdbd.in`)
- 옛 볼트에 데이터가 남아 있는 것 같다: **옛 폴더 삭제하지 말고** 담당자에게 문의

---

*이 문서는 단일 `git-sync-sh` 볼트에서 허브 + 카테고리 5개 독립 저장소 + SSH 인증 구조로의 전환을 다룹니다. 신규 합류 팀원은 `ONBOARDING.md`를 참고하세요.*
