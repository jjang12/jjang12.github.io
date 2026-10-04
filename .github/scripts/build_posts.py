"""네이버 블로그 RSS에서 최근 글을 모아 assets/posts.json 을 만든다.

GitHub Actions(.github/workflows/posts.yml)가 하루 몇 번 실행한다. 로컬에서도
`python3 .github/scripts/build_posts.py` 로 돌릴 수 있다(표준 라이브러리만 사용).
"""
import json
import re
import sys
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from pathlib import Path

BLOGS = ['kkultiplab', 'jisik_plus', 'aicoinlab']
PER_BLOG = 30
OUT = Path(__file__).resolve().parents[2] / 'assets' / 'posts.json'


def fetch(blog_id):
    req = urllib.request.Request(f'https://rss.blog.naver.com/{blog_id}.xml',
                                 headers={'User-Agent': 'Mozilla/5.0 (jjangtool posts builder)'})
    with urllib.request.urlopen(req, timeout=20) as r:
        return ET.fromstring(r.read())


def parse(blog_id, root):
    ch = root.find('channel')
    info = {'title': ch.findtext('title', '').strip(), 'desc': ch.findtext('description', '').strip()}
    posts = []
    for it in ch.findall('item')[:PER_BLOG]:
        link = it.findtext('link', '')
        m = re.search(r'blog\.naver\.com/[^/]+/(\d+)', link)
        if not m:
            continue
        img = re.search(r'<img[^>]+src="([^"]+)"', it.findtext('description', '') or '')
        posts.append({
            'b': blog_id,
            't': it.findtext('title', '').strip(),
            'u': f'https://blog.naver.com/{blog_id}/{m.group(1)}',
            'd': parsedate_to_datetime(it.findtext('pubDate')).strftime('%Y-%m-%d'),
            'c': (it.findtext('category') or '').strip(),
            'img': img.group(1).split('?')[0] + '?type=w300' if img else '',
        })
    return info, posts


def main():
    blogs, posts = {}, []
    for b in BLOGS:
        try:
            info, ps = parse(b, fetch(b))
        except Exception as e:  # 한 블로그가 실패해도 나머지는 갱신
            print(f'{b}: {e}', file=sys.stderr)
            continue
        blogs[b] = info
        posts += ps
    if not posts:
        sys.exit('글을 하나도 가져오지 못해 기존 파일을 유지합니다.')
    # 이전 파일에서 실패한 블로그 글은 그대로 살린다
    if OUT.exists() and len(blogs) < len(BLOGS):
        old = json.loads(OUT.read_text())
        for b in BLOGS:
            if b not in blogs and b in old.get('blogs', {}):
                blogs[b] = old['blogs'][b]
                posts += [p for p in old['posts'] if p['b'] == b]
    posts.sort(key=lambda p: p['d'], reverse=True)
    data = {'updated': datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%MZ'), 'blogs': blogs, 'posts': posts}
    new = json.dumps(data, ensure_ascii=False, separators=(',', ':'))
    if OUT.exists():
        old = json.loads(OUT.read_text())
        if old.get('blogs') == blogs and old.get('posts') == posts:
            print('변경 없음')
            return
    OUT.write_text(new)
    print(f'{len(posts)}개 글 저장 → {OUT}')


if __name__ == '__main__':
    main()
