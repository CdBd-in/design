"""CdBd 「이미지 라이브러리」 헬퍼.

⚠️ 자동화로 카드/페이지에 이미지를 넣을 때는 반드시 이 헬퍼를 경유한다.
raw storage POST만 하면 사용자 cdbd.in 「이미지 추가하기 → 내 이미지」 모달에 안 보여
이름 변경·삭제·재사용 관리가 불가능해진다.

3-call 시퀀스 (문서 「이미지 라이브러리」 검증 시퀀스):
    1) Storage POST  /storage/v1/object/user_image/{uid}/{ts}_{rand12}.{ext}
    2) Sign URL POST /storage/v1/object/sign/... {"expiresIn": 946080000}
    3) image_modal PATCH  {"images": [new, ...existing], "is_saving": false}
"""

import json
import os
import random
import string
import sys
import urllib.request
import urllib.error
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from auth import get_credentials, rest  # noqa: E402

EXPIRES_IN = 946080000  # ~30년 (cdbd.in UI 발급값과 동일)

# mixed-case — UI 업로드와 동일 외관 (lowercase-only는 구 자동화 시그니처)
_RAND12_ALPHA = string.ascii_letters + string.digits
_ID_ALPHA = string.ascii_letters + string.digits + '_-'

_MIME = {'png': 'image/png', 'jpeg': 'image/jpeg', 'webp': 'image/webp', 'gif': 'image/gif'}


def _rand(n, alpha=_RAND12_ALPHA):
    return ''.join(random.choice(alpha) for _ in range(n))


def short_id():
    """갤러리 카드 images[].id — 21자 no-dash nanoid."""
    return _rand(21, string.ascii_letters + string.digits)


def modal_id_style():
    """image_modal.images[].id — nanoid 8-4-4-4-12 형태."""
    return '-'.join(_rand(n, _ID_ALPHA) for n in (8, 4, 4, 4, 12))


def _ext_of(path):
    ext = os.path.splitext(path)[1].lstrip('.').lower()
    return 'jpeg' if ext in ('jpg', 'jpeg') else ext


def _resolution(path):
    try:
        from PIL import Image
        with Image.open(path) as im:
            return '%d*%d' % im.size
    except Exception:
        return None


def _get_modal(creds):
    rows = rest('image_modal?select=id,images&user_id=eq.%s' % creds['user_id'], creds=creds)
    if rows:
        return rows[0]['id'], (rows[0].get('images') or [])
    created = rest(
        'image_modal', method='POST',
        body={'user_id': creds['user_id'], 'images': [], 'is_saving': False},
        prefer='return=representation', creds=creds,
    )
    return created[0]['id'], []


def list_library(name_filter=None):
    creds = get_credentials()
    _, images = _get_modal(creds)
    out = [i for i in images if not i.get('is_deleted')]
    if name_filter:
        out = [i for i in out if name_filter.lower() in (i.get('name') or '').lower()]
    return out


def find_in_library(name):
    for i in list_library():
        if i.get('name') == name:
            return i
    return None


def upload_to_library(file_path, name=None):
    """신규 업로드 + 라이브러리 등록. 반환: image_modal entry dict (url 포함)."""
    creds = get_credentials()
    uid = creds['user_id']
    ext = _ext_of(file_path)
    if ext not in _MIME:
        raise ValueError('지원하지 않는 확장자: %s' % ext)
    name = name or os.path.splitext(os.path.basename(file_path))[0]

    with open(file_path, 'rb') as f:
        raw = f.read()

    ts = datetime.now().strftime('%Y%m%d%H%M%S')
    storage_ext = 'png' if ext == 'png' else ('jpeg' if ext == 'jpeg' else ext)
    obj_path = '%s/%s_%s.%s' % (uid, ts, _rand(12), storage_ext)

    # 1) storage POST
    req = urllib.request.Request(
        creds['supabase_url'] + '/storage/v1/object/user_image/' + obj_path,
        data=raw, method='POST',
        headers={
            'apikey': creds['anon_key'],
            'Authorization': 'Bearer ' + creds['access_token'],
            'Content-Type': _MIME[ext],
            'x-upsert': 'false',
        },
    )
    urllib.request.urlopen(req)

    # 2) sign URL
    req = urllib.request.Request(
        creds['supabase_url'] + '/storage/v1/object/sign/user_image/' + obj_path,
        data=json.dumps({'expiresIn': EXPIRES_IN}).encode(), method='POST',
        headers={
            'apikey': creds['anon_key'],
            'Authorization': 'Bearer ' + creds['access_token'],
            'Content-Type': 'application/json',
        },
    )
    signed = json.load(urllib.request.urlopen(req))['signedURL']
    full_url = creds['supabase_url'] + '/storage/v1' + signed

    entry = {
        'id': modal_id_style(),
        'url': full_url,
        'name': name,
        'path': obj_path,
        'size': str(len(raw)),
        'type': ext,
        'pexels': None,
        'user_id': uid,
        'folder_id': None,
        'created_at': datetime.now(timezone.utc).isoformat(timespec='milliseconds').replace('+00:00', 'Z'),
        'deleted_at': None,
        'is_deleted': False,
        'resolution': _resolution(file_path),
        'is_bookmarked': False,
    }

    # 3) image_modal PATCH (prepend)
    modal_id, images = _get_modal(creds)
    rest('image_modal?id=eq.%s' % modal_id, method='PATCH',
         body={'images': [entry] + images, 'is_saving': False},
         prefer='return=minimal', creds=creds)
    return entry


def upload_if_missing(file_path, name=None, strict=True):
    """같은 name이 이미 라이브러리에 있으면 그 entry 재사용 (룩북 재작업용).

    ⚠️ 라이브러리는 사용자 전체 자산이 섞여 있어 'store-logo' 같은 범용 이름은
    다른 브랜드 작업물과 충돌한다. strict=True(기본)이면 해상도까지 일치할 때만
    재사용하고, 이름만 같고 해상도가 다르면 새로 업로드한다.
    ➡️ 룩북 작업 시 name은 항상 브랜드/페이지로 스코프를 준다 (예: 'N21-09-store-logo').
    """
    name = name or os.path.splitext(os.path.basename(file_path))[0]
    found = find_in_library(name)
    if found:
        if not strict or found.get('resolution') == _resolution(file_path):
            return found
        raise ValueError(
            "라이브러리에 name='%s' 항목이 이미 있으나 해상도가 다릅니다 "
            "(기존 %s / 새 %s). 다른 작업물과 충돌 가능 — 브랜드·페이지로 "
            "스코프를 준 이름을 사용하세요 (예: 'N21-09-%s')."
            % (name, found.get('resolution'), _resolution(file_path), name)
        )
    return upload_to_library(file_path, name=name)


def delete_from_library(id_or_name):
    """라이브러리 entry + 스토리지 오브젝트 동시 제거."""
    creds = get_credentials()
    modal_id, images = _get_modal(creds)
    target = None
    for i in images:
        if i.get('id') == id_or_name or i.get('name') == id_or_name:
            target = i
            break
    if not target:
        return False
    rest('image_modal?id=eq.%s' % modal_id, method='PATCH',
         body={'images': [i for i in images if i is not target], 'is_saving': False},
         prefer='return=minimal', creds=creds)
    try:
        req = urllib.request.Request(
            creds['supabase_url'] + '/storage/v1/object/user_image/' + target['path'],
            method='DELETE',
            headers={'apikey': creds['anon_key'],
                     'Authorization': 'Bearer ' + creds['access_token']},
        )
        urllib.request.urlopen(req)
    except urllib.error.HTTPError:
        pass
    return True


if __name__ == '__main__':
    imgs = list_library()
    print('이미지 라이브러리: %d장' % len(imgs))
    for i in imgs[:15]:
        print('  %-28s %-10s %s' % (i.get('name'), i.get('resolution'), i.get('created_at')))
