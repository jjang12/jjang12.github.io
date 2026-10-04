"""네이버 블로그 글을 모아 assets/posts.json 을 만든다.

- posts:   RSS 기준 블로그별 최신 글(썸네일·카테고리 포함)
- related: 도구별 관련 글. 블로그 전체 글 제목에서 TOOLS 의 단어로 고른다.
           관련 글이 없는 도구는 빈 목록이고, 사이트에서는 '최신 글'만 보여 준다.

GitHub Actions(.github/workflows/posts.yml)가 하루 몇 번 실행한다. 로컬에서도
`python3 .github/scripts/build_posts.py` 로 돌릴 수 있다(표준 라이브러리만 사용).
"""
import html
import json
import re
import sys
import time
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta, timezone
from email.utils import parsedate_to_datetime
from pathlib import Path

BLOGS = ['kkultiplab', 'jisik_plus', 'aicoinlab']
PER_BLOG = 30
RELATED_MAX = 6
OUT = Path(__file__).resolve().parents[2] / 'assets' / 'posts.json'
KST = timezone(timedelta(hours=9))
UA = {'User-Agent': 'Mozilla/5.0 (jjangtool posts builder)'}

# 도구별 관련 글 단어: inc 중 하나라도 제목에 있으면 관련 글, exc 가 있으면 제외.
# 대소문자를 구분한다(예: 'PDF' 는 '스캔들'의 '스캔'처럼 엉뚱한 글에 걸리지 않게 일부러 좁게 잡음).
TOOLS = {
    '/hanbang/': {'inc': ['끝말잇기', '한방단어', '한방 단어', '두음법칙', '두음 법칙']},
    '/wordchain/': {'inc': ['끝말잇기', '한방단어', '한방 단어', '두음법칙', '두음 법칙']},
    '/symbols/': {'inc': ['특수문자', '특수기호', '특수 문자', '이모티콘 입력']},
    '/count/': {'inc': ['글자수', '글자 수', '자기소개서', '자소서', '이력서']},
    '/typo/': {'inc': ['한영', '타자', '키보드', '단축키']},
    '/image/': {'inc': ['사진 편집', '이미지 변환', '이미지 압축', '사진 용량', '배경 제거']},
    '/heic/': {'inc': ['HEIC', '아이폰 사진', '사진 용량']},
    '/img2pdf/': {'inc': ['PDF']},
    '/pdf-merge/': {'inc': ['PDF']},
    '/qr/': {'inc': ['QR']},
    '/age/': {'inc': ['만 나이', '만나이', '나이 계산', '삼재', '띠별']},
    '/dday/': {'inc': ['달력', '공휴일', '연휴', 'D-day', '디데이', '기념일']},
    '/salary/': {'inc': ['연봉', '월급', '실수령', '연말정산', '4대보험', '최저임금', '근로소득']},
    '/severance/': {'inc': ['퇴직금', '퇴직소득세', '퇴직연금', 'IRP', '평균임금']},
    '/loan/': {'inc': ['대출', '주택담보', '원리금', '금리 인하', 'DSR', 'LTV', '보금자리론', '디딤돌'], 'exc': ['도서관', '전자책', '책 대출']},
    '/savings/': {'inc': ['적금', '예금', 'CMA', '파킹통장', '저축은행', '비과세', '이자'], 'exc': ['대출', '이자카야']},
    '/bmi/': {'inc': ['BMI', '비만', '다이어트', '체중', '몸무게', '체지방', '뱃살', '마운자로', '위고비'], 'exc': ['소형견', '강아지', '반려', '배우', '역할', '드라마']},
    '/hourly/': {'inc': ['최저임금', '시급', '주휴수당', '알바', '아르바이트']},
    '/unit/': {'inc': ['인치 센치', '인치 cm', '단위 변환', '단위변환', '화씨', '섭씨']},  # 「13인치」「20파운드」처럼 지나가는 말은 빼려고 좁게
    '/power/': {'inc': ['전기요금', '전기세', '누진', '한전', '에어컨 전기', '전기 요금']},
    '/lunar/': {'inc': ['음력', '양력', '설날', '추석 날짜', '윤달'], 'exc': ['선물']},
    '/money/': {'inc': ['축의금', '계약서', '영수증', '착오송금'], 'exc': ['현금영수증']},
    '/pyeong/': {'inc': ['아파트', '평수', '전용면적', '청약', '분양', '공시지가', '전세'], 'exc': ['공모주', '신주인수권', '유상증자']},
    '/liquidation/': {'inc': ['비트코인', '코인', '선물 거래', '펀딩비', '레버리지', '청산', '거래소'], 'exc': ['선물세트', '추석선물', '선물 추천']},
}


def get(url, referer=None):
    h = dict(UA)
    if referer:
        h['Referer'] = referer
    with urllib.request.urlopen(urllib.request.Request(url, headers=h), timeout=20) as r:
        return r.read()


def summary(text, n=110):
    t = re.sub(r'\s+', ' ', html.unescape(re.sub(r'<[^>]+>', ' ', text or ''))).strip()
    t = html.unescape(t)  # og:description 은 두 번 이스케이프돼 있음(&amp;quot;)
    return t if len(t) <= n else t[:n].rstrip() + '…'


def thumb(url):
    return url.split('?')[0] + '?type=w300' if url else ''


def fetch_rss(blog_id):
    ch = ET.fromstring(get(f'https://rss.blog.naver.com/{blog_id}.xml')).find('channel')
    info = {'title': ch.findtext('title', '').strip(), 'desc': ch.findtext('description', '').strip()}
    posts = []
    for it in ch.findall('item')[:PER_BLOG]:
        m = re.search(r'blog\.naver\.com/[^/]+/(\d+)', it.findtext('link', ''))
        if not m:
            continue
        img = re.search(r'<img[^>]+src="([^"]+)"', it.findtext('description', '') or '')
        posts.append({
            'b': blog_id,
            't': it.findtext('title', '').strip(),
            'u': f'https://blog.naver.com/{blog_id}/{m.group(1)}',
            'd': parsedate_to_datetime(it.findtext('pubDate')).strftime('%Y-%m-%d'),
            'c': (it.findtext('category') or '').strip(),
            'img': thumb(img.group(1)) if img else '',
            's': summary(it.findtext('description', '')),
        })
    return info, posts


def parse_date(s):
    m = re.match(r'(\d{4})\.\s*(\d{1,2})\.\s*(\d{1,2})', s)
    if m:
        return f'{int(m[1]):04d}-{int(m[2]):02d}-{int(m[3]):02d}'
    return datetime.now(KST).strftime('%Y-%m-%d')  # '3시간 전' 처럼 상대 표기는 오늘 글


def fetch_titles(blog_id):
    out, page = [], 1
    while True:
        url = ('https://blog.naver.com/PostTitleListAsync.naver?blogId=' + blog_id +
               f'&viewdate=&currentPage={page}&categoryNo=0&parentCategoryNo=&countPerPage=30')
        d = json.loads(get(url, f'https://blog.naver.com/{blog_id}').decode().replace("\\'", "'"))
        for p in d.get('postList', []):
            if p.get('isPostNotOpen') != '0':
                continue
            out.append({
                'b': blog_id,
                't': html.unescape(urllib.parse.unquote_plus(p['title'])).strip(),
                'u': f"https://blog.naver.com/{blog_id}/{p['logNo']}",
                'd': parse_date(p.get('addDate', '')),
            })
        if not d.get('postList') or page * 30 >= int(d.get('totalCount', 0)):
            return out
        page += 1
        time.sleep(0.3)


def og_meta(u):
    """글 페이지의 대표 이미지·요약. 실패하면 빈 값."""
    blog_id, no = u.rstrip('/').split('/')[-2:]
    try:
        page = get(f'https://blog.naver.com/PostView.naver?blogId={blog_id}&logNo={no}').decode('utf-8', 'ignore')
    except Exception:
        return {'img': '', 's': ''}
    img = re.search(r'<meta property="og:image" content="([^"]+)"', page)
    desc = re.search(r'<meta property="og:description" content="([^"]*)"', page)
    # 대표 이미지가 없는 글은 네이버 기본 아이콘(ssl.pstatic.net/static/blog/icon)이 나오므로 비워 둔다
    return {'img': thumb(html.unescape(img.group(1))) if img and 'blogthumb' in img.group(1) else '',
            's': summary(desc.group(1)) if desc else ''}


def main():
    old = json.loads(OUT.read_text()) if OUT.exists() else {}
    blogs, posts, titles = {}, [], []
    for b in BLOGS:
        try:
            info, ps = fetch_rss(b)
            blogs[b] = info
            posts += ps
        except Exception as e:  # 한 블로그가 실패해도 나머지는 갱신
            print(f'{b} RSS: {e}', file=sys.stderr)
            if b in old.get('blogs', {}):
                blogs[b] = old['blogs'][b]
                posts += [p for p in old.get('posts', []) if p['b'] == b]
        try:
            titles += fetch_titles(b)
        except Exception as e:
            print(f'{b} 글 목록: {e}', file=sys.stderr)
    if not posts:
        sys.exit('글을 하나도 가져오지 못해 기존 파일을 유지합니다.')
    posts.sort(key=lambda p: p['d'], reverse=True)

    # 썸네일·요약 캐시: 이번 RSS + 이전 파일의 관련 글(요약이 있는 것만 — 없으면 다시 읽음)
    meta = {p['u']: {'img': p['img'], 's': p['s']} for p in posts}
    for lst in old.get('related', {}).values():
        for p in lst:
            if 's' in p:
                meta.setdefault(p['u'], {'img': p.get('img', ''), 's': p['s']})

    related = {}
    if titles:
        for path, rule in TOOLS.items():
            hits = []
            for p in titles:
                if any(w in p['t'] for w in rule.get('exc', [])):
                    continue
                score = sum(w in p['t'] for w in rule['inc'])
                if score:
                    hits.append((score, p))
            hits.sort(key=lambda x: (x[0], x[1]['d']), reverse=True)
            seen, picked = set(), []
            for _, p in hits:  # 같은 제목으로 두 번 올린 글은 하나만
                if p['t'] not in seen and len(picked) < RELATED_MAX:
                    seen.add(p['t'])
                    picked.append(dict(p))
            related[path] = picked
        for lst in related.values():
            for p in lst:
                if p['u'] not in meta:
                    meta[p['u']] = og_meta(p['u'])
                    time.sleep(0.3)
                p.update(meta[p['u']])
    else:  # 글 목록을 못 가져오면 이전 관련 글 유지
        related = old.get('related', {})

    if old.get('blogs') == blogs and old.get('posts') == posts and old.get('related') == related:
        print('변경 없음')
        return
    data = {'updated': datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%MZ'),
            'blogs': blogs, 'posts': posts, 'related': related}
    OUT.write_text(json.dumps(data, ensure_ascii=False, separators=(',', ':')))
    print(f'최신 글 {len(posts)}개, 관련 글 {sum(map(len, related.values()))}개 저장 → {OUT}')


if __name__ == '__main__':
    main()
