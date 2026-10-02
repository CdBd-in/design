"""CdBd 자동화 인증 헬퍼 — 정본은 design/tools/cdbd/auth.py (~/.config/cdbd/auth.py는 이 파일로의 링크).

사용 패턴 (기존과 동일):
    import sys, os
    sys.path.insert(0, os.path.expanduser('~/.config/cdbd'))
    from auth import get_credentials, rest
    creds = get_credentials()

비밀은 저장소가 아니라 ~/.config/cdbd/ 에만 둔다 (CDBD_CONFIG_DIR로 바꿀 수 있음):
    credentials.json (mode 600 · 자동 생성/갱신 — 🔴 기기끼리 복사 금지: refresh token이 회전형이라 서로를 무효화)
        supabase_url, supabase_anon_key, refresh_token, user_id, (email), (figma_pat)
    cdbd.env (mode 600 · 기기끼리 옮겨도 됨 — 공용 계정 정보)
        CDBD_EMAIL, CDBD_PASSWORD               ← 자동 재로그인용
        CDBD_SUPABASE_URL, CDBD_SUPABASE_ANON_KEY ← credentials.json이 없을 때 첫 발급용
        FIGMA_PAT (선택)                          ← Figma REST 스크립트용 · 각자 발급(90일)

동작:
    1) credentials.json의 refresh_token으로 새 access_token 발급(회전된 refresh_token 저장)
    2) refresh가 거부되면(만료·무효) 또는 credentials.json이 없으면
       → cdbd.env의 계정으로 password grant 재로그인 → 새 refresh_token 저장 (2026-10-02 신설)
    3) 갱신은 파일 잠금(.auth.lock) 안에서 한다 — 두 프로세스가 동시에 refresh하면 한쪽 토큰이 죽기 때문

점검:  python3 ~/.config/cdbd/auth.py           (비밀값은 출력하지 않는다)
셸용:  eval "$(python3 ~/.config/cdbd/auth.py --env)"
       → $CDBD_ACCESS_TOKEN · $CDBD_USER_ID · $CDBD_SUPABASE_URL · $CDBD_SUPABASE_ANON · $CDBD_FIGMA_PAT
"""

import fcntl
import json
import os
import urllib.error
import urllib.request

CONFIG_DIR = os.path.expanduser(os.environ.get('CDBD_CONFIG_DIR', '~/.config/cdbd'))
CRED_PATH = os.path.join(CONFIG_DIR, 'credentials.json')
ENV_PATH = os.path.join(CONFIG_DIR, 'cdbd.env')
LOCK_PATH = os.path.join(CONFIG_DIR, '.auth.lock')

_cache = {}
last_auth_method = None  # 'refresh' | 'password' — 점검·테스트용


# ── 파일 ────────────────────────────────────────────────────────────────
def _load():
    if not os.path.exists(CRED_PATH):
        return {}
    with open(CRED_PATH) as f:
        return json.load(f)


def _save(data):
    os.makedirs(CONFIG_DIR, exist_ok=True)
    tmp = CRED_PATH + '.tmp'
    fd = os.open(tmp, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    with os.fdopen(fd, 'w') as f:
        json.dump(data, f, indent=1)
    os.replace(tmp, CRED_PATH)  # 원자적 교체 — 쓰다 죽어도 반쪽 파일이 남지 않는다
    os.chmod(CRED_PATH, 0o600)


def _env():
    """cdbd.env(KEY=VALUE) 위에 실제 환경변수를 덮어 반환."""
    out = {}
    if os.path.exists(ENV_PATH):
        with open(ENV_PATH) as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#') or '=' not in line:
                    continue
                k, v = line.split('=', 1)
                out[k.strip()] = v.strip().strip('"').strip("'")
    for k in ('CDBD_EMAIL', 'CDBD_PASSWORD', 'CDBD_SUPABASE_URL', 'CDBD_SUPABASE_ANON_KEY', 'FIGMA_PAT'):
        if os.environ.get(k):
            out[k] = os.environ[k]
    return out


# ── Supabase 토큰 발급 ──────────────────────────────────────────────────
class _AuthRejected(Exception):
    pass


def _token(url, anon, grant, body):
    req = urllib.request.Request(
        url + '/auth/v1/token?grant_type=' + grant,
        data=json.dumps(body).encode(),
        headers={'apikey': anon, 'Content-Type': 'application/json'},
        method='POST',
    )
    try:
        return json.load(urllib.request.urlopen(req, timeout=30))
    except urllib.error.HTTPError as e:
        detail = e.read().decode(errors='replace')[:200]
        if e.code in (400, 401, 403):
            raise _AuthRejected('%s %s' % (e.code, detail))
        raise RuntimeError('Supabase 인증 서버 오류 (%s): %s' % (e.code, detail))


def _password_login(cred, env):
    email, pw = env.get('CDBD_EMAIL'), env.get('CDBD_PASSWORD')
    if not (email and pw):
        raise RuntimeError(
            '자동 재로그인 불가 — %s 에 CDBD_EMAIL · CDBD_PASSWORD 가 없습니다.\n'
            '  공용 계정 정보를 넣은 뒤 다시 실행하세요 (credentials.json을 다른 기기에서 복사하지 말 것).' % ENV_PATH
        )
    try:
        res = _token(cred['supabase_url'], cred['supabase_anon_key'], 'password',
                     {'email': email, 'password': pw})
    except _AuthRejected as e:
        raise RuntimeError('재로그인 거부 — cdbd.env의 이메일/비밀번호를 확인하세요. (%s)' % e)
    cred['refresh_token'] = res['refresh_token']
    user = res.get('user') or {}
    if user.get('id'):
        cred['user_id'] = user['id']
    if user.get('email'):
        cred['email'] = user['email']
    return res['access_token']


def _issue_token():
    """잠금 안에서: 파일을 다시 읽고(다른 프로세스가 방금 회전했을 수 있음) refresh → 실패 시 재로그인."""
    global last_auth_method
    os.makedirs(CONFIG_DIR, exist_ok=True)
    with open(LOCK_PATH, 'w') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        try:
            cred = _load()
            env = _env()
            cred['supabase_url'] = cred.get('supabase_url') or env.get('CDBD_SUPABASE_URL')
            cred['supabase_anon_key'] = cred.get('supabase_anon_key') or env.get('CDBD_SUPABASE_ANON_KEY')
            if not (cred['supabase_url'] and cred['supabase_anon_key']):
                raise RuntimeError(
                    'Supabase 접속정보 없음 — credentials.json도 없고 %s 에 '
                    'CDBD_SUPABASE_URL · CDBD_SUPABASE_ANON_KEY 도 없습니다.' % ENV_PATH
                )
            if not cred.get('refresh_token') and cred.get('supabase_refresh_token'):
                cred['refresh_token'] = cred.pop('supabase_refresh_token')  # 옛 이선호판 키 이름 호환
            token = None
            if cred.get('refresh_token'):
                try:
                    res = _token(cred['supabase_url'], cred['supabase_anon_key'], 'refresh_token',
                                 {'refresh_token': cred['refresh_token']})
                    cred['refresh_token'] = res['refresh_token']
                    token = res['access_token']
                    last_auth_method = 'refresh'
                except _AuthRejected:
                    token = None  # 만료·무효 → 아래에서 재로그인
            if token is None:
                token = _password_login(cred, env)
                last_auth_method = 'password'
            if not cred.get('user_id'):
                raise RuntimeError('user_id를 알 수 없습니다 (재로그인 응답에 user가 없음).')
            _save(cred)
            return cred, token
        finally:
            fcntl.flock(lock, fcntl.LOCK_UN)


# ── 공개 API (기존과 동일) ──────────────────────────────────────────────
def get_credentials(force_refresh=False):
    """figma_pat + 최신 access_token + user_id + supabase 접속정보를 한 번에 반환."""
    if _cache and not force_refresh:
        return _cache
    cred, token = _issue_token()
    _cache.clear()
    _cache.update({
        'supabase_url': cred['supabase_url'],
        'anon_key': cred['supabase_anon_key'],
        'access_token': token,
        'user_id': cred['user_id'],
        'figma_pat': cred.get('figma_pat') or _env().get('FIGMA_PAT'),  # credentials.json 우선 · 없으면 cdbd.env
    })
    return _cache


def rest_headers(creds=None, content_json=True, prefer=None):
    c = creds or get_credentials()
    h = {'apikey': c['anon_key'], 'Authorization': 'Bearer ' + c['access_token']}
    if content_json:
        h['Content-Type'] = 'application/json'
    if prefer:
        h['Prefer'] = prefer
    return h


def rest(path, method='GET', body=None, prefer=None, creds=None):
    """Supabase REST 호출. path 예: 'editor?select=pages&id=eq.5798'"""
    c = creds or get_credentials()
    url = c['supabase_url'] + '/rest/v1/' + path
    data = json.dumps(body, ensure_ascii=False).encode() if body is not None else None
    req = urllib.request.Request(
        url, data=data, headers=rest_headers(c, prefer=prefer), method=method
    )
    res = urllib.request.urlopen(req)
    raw = res.read()
    if not raw:
        return None
    return json.loads(raw)


if __name__ == '__main__':
    import shlex
    import sys
    c = get_credentials()
    if '--env' in sys.argv:
        for k, v in (('CDBD_ACCESS_TOKEN', c['access_token']), ('CDBD_USER_ID', c['user_id']),
                     ('CDBD_SUPABASE_URL', c['supabase_url']), ('CDBD_SUPABASE_ANON', c['anon_key']),
                     ('CDBD_FIGMA_PAT', c['figma_pat'] or '')):
            print('export %s=%s' % (k, shlex.quote(v)))
        sys.exit(0)
    env = _env()
    print('config dir   :', CONFIG_DIR)
    print('인증 방식    :', last_auth_method, '(password = 자동 재로그인으로 복구됨)')
    print('supabase_url :', c['supabase_url'])
    print('user_id      : %s…' % c['user_id'][:8])
    print('access_token : %d chars (OK)' % len(c['access_token']))
    print('figma_pat    :', 'set' if c['figma_pat'] else '미설정')
    print('cdbd.env     : 재로그인 %s · 첫 발급 %s' % (
        'OK' if env.get('CDBD_EMAIL') and env.get('CDBD_PASSWORD') else '❌ 계정 없음',
        'OK' if env.get('CDBD_SUPABASE_URL') and env.get('CDBD_SUPABASE_ANON_KEY') else '— (credentials.json 있으면 불필요)',
    ))
