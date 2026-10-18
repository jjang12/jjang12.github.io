"""짱툴 뉴스픽: assets/news.json 으로 /news/(인기 뉴스 TOP 20)와 분야별 /news/<분야>/ 정적 페이지를 만든다.

news.json 은 맥(blog-pipeline 「뉴스픽」 수집)이 만든다 — 뉴스픽 파트너스 로그인이 필요해서 GitHub Actions 에서는 못 받는다.
블로그 글 갱신(posts.yml, 4시간)과 같은 주기로 맥이 news.json 을 쓰고 이 스크립트를 돌린 뒤 push 한다.

    python3 .github/scripts/build_news.py

- 자바스크립트 없이 읽히는 정적 목록(검색 로봇용) + canonical·og·구조화 정보(CollectionPage·BreadcrumbList).
- 기사 링크는 뉴스픽 파트너스 제휴 링크라 rel="nofollow sponsored noopener" 를 붙이고, 페이지에 제휴 안내를 적는다.
- 메뉴(좌측 「짱툴 뉴스픽」)와 오른쪽 인기 뉴스·도구 페이지 아래 추천 뉴스는 assets/site.js 가 같은 news.json 으로 그린다.
- 사이트맵은 build_seo.py 가 news/ 아래 페이지를 같이 넣는다.
"""
import html
import json
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BASE = 'https://jjangtool.com'
SITE_NAME = '짱툴'
MENU = '짱툴 뉴스픽'

# 분야 소개 문구(페이지마다 다르게 — 같은 문장만 반복되면 검색엔진이 비슷한 페이지로 본다)
INTRO = {
    '': ('지금 인기 뉴스 TOP 20 - 실시간 많이 보는 뉴스',
         '지금 사람들이 가장 많이 보고 있는 뉴스 20개를 모았습니다. 유머·연예·사회·생활 소식을 한곳에서 확인하세요.',
         '지난 1시간 동안 반응이 가장 많았던 기사 순서입니다. 몇 시간마다 새로 바뀝니다.'),
    'humor': ('유머·이슈 인기 뉴스 - 요즘 화제인 웃긴 이야기',
              '요즘 커뮤니티와 SNS에서 화제인 유머·이슈 글을 인기순으로 모았습니다.',
              '가볍게 웃고 넘기기 좋은 화제의 글을 인기순으로 보여 드립니다.'),
    'story': ('스토리 인기 뉴스 - 사연·썰·웹툰 모음',
              '많이 읽힌 사연, 썰, 짧은 웹툰 이야기를 인기순으로 모았습니다.',
              '끝까지 읽게 되는 사연과 짧은 이야기들을 인기순으로 보여 드립니다.'),
    'entertain': ('연예가 화제 인기 뉴스 - 오늘의 연예 소식',
                  '오늘 가장 많이 본 연예계 소식과 스타 근황을 인기순으로 모았습니다.',
                  '스타 근황, 결혼·열애 소식, 화제의 발언을 인기순으로 보여 드립니다.'),
    'tv': ('TV 연예 인기 뉴스 - 드라마·예능 화제',
           '방송 중인 드라마와 예능 프로그램 관련 화제 기사를 인기순으로 모았습니다.',
           '드라마 줄거리 화제, 예능 출연 소식, 시청률 이야기를 인기순으로 보여 드립니다.'),
    'kmusic': ('K-뮤직 인기 뉴스 - 아이돌·가요 소식',
               '아이돌 컴백, 음원 차트, 가수 소식 등 K-뮤직 기사를 인기순으로 모았습니다.',
               '컴백·공연·차트 소식을 인기순으로 보여 드립니다.'),
    'world-star': ('해외 연예 인기 뉴스 - 할리우드·해외 스타 소식',
                   '해외 스타와 할리우드 소식 중 많이 본 기사를 인기순으로 모았습니다.',
                   '해외 셀럽 근황과 화제 소식을 인기순으로 보여 드립니다.'),
    'society': ('사회 인기 뉴스 - 오늘 많이 본 사회 소식',
                '오늘 많이 본 사회 뉴스를 인기순으로 모았습니다. 날씨·생활과 맞닿은 소식도 함께 확인하세요.',
                '생활과 가까운 사회 소식을 인기순으로 보여 드립니다.'),
    'incident': ('사건사고 인기 뉴스 - 오늘의 사건·사고 소식',
                 '오늘 많이 본 사건·사고 뉴스를 인기순으로 모았습니다.',
                 '지금 주목받는 사건·사고 소식을 인기순으로 보여 드립니다.'),
    'life': ('생활픽 인기 뉴스 - 건강·꿀팁·생활 정보',
             '건강, 생활 꿀팁, 알아 두면 좋은 정보 기사를 인기순으로 모았습니다.',
             '일상에 바로 쓸 수 있는 건강·생활 정보를 인기순으로 보여 드립니다.'),
}


def esc(s) -> str:
    return html.escape(str(s or ''), quote=True)


def fmt_date(d: str) -> str:
    try:
        return datetime.strptime(d[:16], '%Y-%m-%d %H:%M').strftime('%m.%d %H:%M')
    except ValueError:
        return d[:10]


def card(n: dict) -> str:
    img = f'<img src="{esc(n["img"])}" alt="" loading="lazy" referrerpolicy="no-referrer" onerror="this.remove()">' if n.get('img') else ''
    tag = f'<em class="post-tag news-tag">{esc(n["c"])}</em>' if n.get('c') else ''
    return (f'<li><a class="post" href="{esc(n["u"])}" target="_blank" rel="nofollow sponsored noopener">'
            f'<span class="post-body"><b>{esc(n["t"])}</b><small>{tag}{esc(n.get("src"))} · {fmt_date(n.get("d", ""))}</small></span>'
            f'<span class="thumb">{img}</span></a></li>')


def page(slug: str, name: str, items: list, cats: list, updated: str) -> str:
    title, desc, sub = INTRO.get(slug, (f'{name} 인기 뉴스', f'{name} 분야 인기 뉴스를 모았습니다.', ''))
    path = f'/news/{slug}/' if slug else '/news/'
    url = BASE + path
    h1 = '지금 인기 뉴스 TOP 20' if not slug else f'{name} 인기 뉴스'
    crumbs = [(SITE_NAME, BASE + '/'), (MENU, BASE + '/news/')] + ([(h1, url)] if slug else [])
    ld = {'@context': 'https://schema.org', '@graph': [
        {'@type': 'CollectionPage', 'name': h1, 'url': url, 'description': desc, 'inLanguage': 'ko-KR', 'dateModified': updated,
         'isPartOf': {'@type': 'WebSite', 'name': SITE_NAME, 'url': BASE + '/'}},
        {'@type': 'BreadcrumbList', 'itemListElement': [
            {'@type': 'ListItem', 'position': i + 1, 'name': n, 'item': u} for i, (n, u) in enumerate(crumbs)]}]}
    ld_s = json.dumps(ld, ensure_ascii=False, separators=(',', ':')).replace('</', '<\\/')
    cur = ' aria-current="page"'
    chips = ''.join(f'<a href="/news/{c["slug"]}/"{cur if c["slug"] == slug else ""}>{esc(c["name"])}</a>' for c in cats)
    chips = f'<a href="/news/"{cur if not slug else ""}>🔥 인기 TOP 20</a>' + chips
    upd = updated[:16].replace('T', ' ')
    body = ''.join(card(n) for n in items) if items else '<li class="news-empty">지금은 보여 드릴 기사가 없습니다. 잠시 뒤 다시 확인해 주세요.</li>'
    return f"""<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{esc(title)} | {SITE_NAME}</title>
<meta name="description" content="{esc(desc)}">
<meta name="robots" content="index,follow,max-image-preview:large">
<meta property="og:title" content="{esc(title)}">
<meta property="og:description" content="{esc(desc)}">
<meta property="og:type" content="website">
<meta property="og:url" content="{url}">
<meta property="og:site_name" content="{SITE_NAME}">
<meta property="og:locale" content="ko_KR">
<meta property="og:image" content="{BASE}/assets/og/home.jpg">
<link rel="canonical" href="{url}">
<link rel="icon" href="/favicon.ico" sizes="48x48">
<link rel="icon" href="/assets/img/favicon.svg" type="image/svg+xml">
<link rel="apple-touch-icon" href="/assets/img/apple-touch-icon.png">
<meta name="theme-color" content="#3157E0">
<link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/static/pretendard.min.css">
<link rel="stylesheet" href="/assets/site.css">
<script type="application/ld+json">{ld_s}</script>
</head>
<body data-news="{esc(slug or 'top')}">
<main>
<p class="crumb news-crumb"><a href="/">전체 도구</a> › <a href="/news/">{MENU}</a>{f' › <span>{esc(name)}</span>' if slug else ''}</p>
<h1>{esc(h1)}</h1>
<p class="lead">{esc(desc)}</p>
<nav class="chips news-chips" aria-label="뉴스 분야">{chips}</nav>
<p class="note news-upd">{esc(sub)} 마지막 갱신 {esc(upd)}</p>
<ol class="post-list news-list">{body}</ol>
<p class="note news-disc">기사 링크는 뉴스픽 파트너스 제휴 링크로, 새 창에서 원문을 볼 수 있는 뉴스픽 페이지로 이동합니다. 링크를 통한 방문에 따라 짱툴 운영자(라이프큐브)가 일정 수익을 받을 수 있습니다. 기사의 저작권은 각 언론사·제공처에 있습니다.</p>
</main>
<script src="/assets/site.js"></script>
</body>
</html>
"""


def main():
    src = ROOT / 'assets' / 'news.json'
    if not src.exists():
        print('assets/news.json 없음 — 건너뜀')
        return
    d = json.loads(src.read_text(encoding='utf-8'))
    cats = d.get('cats') or []
    out = {Path('news/index.html'): page('', MENU, d.get('top') or [], cats, d.get('updated', ''))}
    for c in cats:
        out[Path(f'news/{c["slug"]}/index.html')] = page(c['slug'], c['name'], c.get('items') or [], cats, d.get('updated', ''))
    changed = 0
    for rel, text in out.items():
        f = ROOT / rel
        f.parent.mkdir(parents=True, exist_ok=True)
        if not f.exists() or f.read_text(encoding='utf-8') != text:
            f.write_text(text, encoding='utf-8')
            changed += 1
    print(f'뉴스 페이지 {len(out)}개 중 {changed}개 바뀜')


if __name__ == '__main__':
    main()
