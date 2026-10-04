"""짱툴 SEO 일괄 적용: 페이지마다 head 의 공유·구조화 정보, 자바스크립트 없이 읽히는 도구 링크, 사이트맵을 맞춘다.

    python3 .github/scripts/build_seo.py            # 정보·링크·사이트맵만
    python3 .github/scripts/build_seo.py --images   # + 공유 이미지(assets/og/*.png)·파비콘 (맥 크롬 필요, 없는 것만 만듦)
    python3 .github/scripts/build_seo.py --images --force-images   # 이미지 전부 다시

메뉴(도구 목록·묶음)는 assets/site.js 의 SITE.groups 를 그대로 읽는다 — 새 도구는 거기 넣고 이 스크립트를 돌리면 된다.
페이지 안의 `<!-- seo:head -->…<!-- /seo:head -->`, `<!-- seo:nav -->…<!-- /seo:nav -->` 사이만 바꾼다(없으면 넣음).
자주 묻는 질문은 `<section class="faq">` 안의 <details><summary>질문</summary><p>답</p></details> 를 읽어 FAQPage 로 넣는다.
"""
import html
import json
import re
import shutil
import subprocess
import sys
import tempfile
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BASE = 'https://jjang12.github.io'
SITE_NAME = '짱툴'
CHROME = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'


def read_site():
    js = (ROOT / 'assets' / 'site.js').read_text(encoding='utf-8')
    groups = []
    for m in re.finditer(r"\{name: '([^']+)', icon: '([^']+)', tone: '([^']+)', items: \[(.*?)\]\}", js, re.S):
        items = [{'p': p, 't': t, 'i': i} for p, t, i in re.findall(r"\{p: '([^']+)', t: '([^']+)', i: '([^']+)'\}", m.group(4))]
        groups.append({'name': m.group(1), 'icon': m.group(2), 'tone': m.group(3), 'items': items})
    icons = dict(re.findall(r"^  '([a-z0-9-]+)': '(.*)',$", js, re.M))
    return groups, icons


def page_info(path: Path):
    s = path.read_text(encoding='utf-8')
    get = lambda pat: html.unescape(re.search(pat, s, re.S).group(1)).strip() if re.search(pat, s, re.S) else ''   # noqa: E731
    return s, {'title': get(r'<title>(.*?)</title>'), 'desc': get(r'<meta name="description" content="([^"]*)"'),
               'h1': re.sub(r'<[^>]+>', '', get(r'<h1[^>]*>(.*?)</h1>'))}


def faq_of(s: str):
    sec = re.search(r'<section class="faq"[^>]*>(.*?)</section>', s, re.S)
    if not sec:
        return []
    out = []
    for q, a in re.findall(r'<details>\s*<summary>(.*?)</summary>(.*?)</details>', sec.group(1), re.S):
        clean = lambda x: re.sub(r'\s+', ' ', html.unescape(re.sub(r'<[^>]+>', ' ', x))).strip()   # noqa: E731
        out.append((clean(q), clean(a)))
    return out


def replace_block(s: str, tag: str, content: str, before: str) -> str:
    start, end = f'<!-- seo:{tag} -->', f'<!-- /seo:{tag} -->'
    block = f'{start}\n{content}\n{end}'
    if start in s:
        return re.sub(re.escape(start) + r'.*?' + re.escape(end), lambda _: block, s, flags=re.S)
    i = s.index(before)
    return s[:i] + block + '\n' + s[i:]


def head_block(url, info, og, crumbs, faq, is_home, category):
    title = html.escape(info['title'], quote=True)
    lines = [
        '<link rel="icon" href="/favicon.ico" sizes="48x48">',
        '<link rel="icon" href="/assets/img/favicon.svg" type="image/svg+xml">',
        '<link rel="apple-touch-icon" href="/assets/img/apple-touch-icon.png">',
        '<meta name="theme-color" content="#3157E0">',
        f'<meta property="og:site_name" content="{SITE_NAME}">',
        '<meta property="og:locale" content="ko_KR">',
        f'<meta property="og:image" content="{BASE}{og}">',
        '<meta property="og:image:width" content="1200">',
        '<meta property="og:image:height" content="630">',
        '<meta name="twitter:card" content="summary_large_image">',
        f'<meta name="twitter:title" content="{title}">',
        f'<meta name="twitter:image" content="{BASE}{og}">',
    ]
    graph = []
    if is_home:
        graph.append({'@type': 'WebSite', 'name': SITE_NAME, 'url': BASE + '/', 'inLanguage': 'ko-KR', 'description': info['desc']})
    else:
        graph.append({'@type': 'WebApplication', 'name': info['h1'], 'url': url, 'description': info['desc'], 'inLanguage': 'ko-KR',
                      'applicationCategory': category, 'operatingSystem': '모든 기기 (웹 브라우저)',
                      'offers': {'@type': 'Offer', 'price': '0', 'priceCurrency': 'KRW'},
                      'isPartOf': {'@type': 'WebSite', 'name': SITE_NAME, 'url': BASE + '/'}})
        graph.append({'@type': 'BreadcrumbList', 'itemListElement': [
            {'@type': 'ListItem', 'position': i + 1, 'name': n, **({'item': u} if u else {})} for i, (n, u) in enumerate(crumbs)]})
    if faq:
        graph.append({'@type': 'FAQPage', 'mainEntity': [{'@type': 'Question', 'name': q, 'acceptedAnswer': {'@type': 'Answer', 'text': a}} for q, a in faq]})
    ld = json.dumps({'@context': 'https://schema.org', '@graph': graph}, ensure_ascii=False, separators=(',', ':')).replace('</', '<\\/')
    lines.append(f'<script type="application/ld+json">{ld}</script>')
    return '\n'.join(lines)


def nav_block(groups, names, current):
    """자바스크립트 없이도 읽히는 전체 도구 링크(검색 로봇용). site.js 가 화면에서는 지우고 좌측 메뉴로 대신한다."""
    parts = ['<nav class="static-nav" id="static-nav" aria-label="짱툴 전체 도구">', f'<p><a href="/">{SITE_NAME} 전체 도구</a></p>']
    for g in groups:
        cur = ' aria-current="page"'
        links = ''.join(f'<li><a href="{it["p"]}"{cur if it["p"] == current else ""}>{html.escape(names.get(it["p"], it["t"]))}</a></li>' for it in g['items'])
        parts.append(f'<h2>{html.escape(g["name"])}</h2><ul>{links}</ul>')
    parts.append('</nav>')
    return ''.join(parts)


CATEGORY = {'글자·단어': 'UtilitiesApplication', '이미지·PDF': 'MultimediaApplication', '날짜·시간': 'UtilitiesApplication',
            '월급·세금': 'FinanceApplication', '대출·금융': 'FinanceApplication', '생활': 'LifestyleApplication'}

OG_HTML = """<!doctype html><html><head><meta charset="utf-8">
<link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/static/pretendard.min.css">
<style>html,body{{margin:0;width:1200px;height:630px;overflow:hidden}}
body{{font-family:Pretendard,sans-serif;background:radial-gradient(120% 140% at 100% 0%,{tone}55 0%,transparent 55%),radial-gradient(120% 120% at 0% 100%,#3157E040 0%,transparent 60%),#0F1424;color:#fff;
display:flex;flex-direction:column;justify-content:center;padding:0 90px;box-sizing:border-box}}
.brand{{display:flex;align-items:center;gap:16px;font-size:34px;font-weight:800;opacity:.92}}
.mark{{width:58px;height:58px;border-radius:16px;display:grid;place-items:center;background:linear-gradient(135deg,#5B7CFA,#3157E0 55%,#6A4FD8)}}
.mark svg{{width:34px;height:34px;fill:#fff}}
.row{{display:flex;align-items:center;gap:44px;margin-top:46px}}
.ic{{flex:none;width:170px;height:170px;border-radius:44px;display:grid;place-items:center;background:{tone}2E;box-shadow:inset 0 0 0 2px {tone}66}}
.ic svg{{width:96px;height:96px;stroke:{tone};fill:none;stroke-width:2;stroke-linecap:round;stroke-linejoin:round}}
h1{{margin:0;font-size:{size}px;line-height:1.18;letter-spacing:-0.03em;font-weight:800}}
.g{{font-size:30px;font-weight:700;color:{tone};margin-bottom:12px}}
.foot{{position:absolute;left:90px;bottom:56px;font-size:26px;color:#B9C2D6}}</style></head><body>
<div class="brand"><span class="mark"><svg viewBox="0 0 24 24">{zap}</svg></span>{site}</div>
<div class="row"><span class="ic"><svg viewBox="0 0 24 24">{icon}</svg></span><div><div class="g">{group}</div><h1>{title}</h1></div></div>
<div class="foot">무료 · 설치·가입 없이 바로 · jjang12.github.io</div></body></html>"""
TONES = {'violet': '#A894FF', 'sky': '#5BB8EE', 'amber': '#F0A54A', 'green': '#4FCB94', 'teal': '#4CC9C9', 'rose': '#F07A98'}


def chrome_shot(html_text: str, out: Path, w: int, h: int, transparent=False):
    with tempfile.TemporaryDirectory() as d:
        f = Path(d) / 'p.html'
        f.write_text(html_text, encoding='utf-8')
        args = [CHROME, '--headless=new', '--disable-gpu', '--hide-scrollbars', f'--window-size={w},{h}', '--virtual-time-budget=4000',
                f'--screenshot={out}', f'file://{f}']
        if transparent:
            args.insert(2, '--default-background-color=00000000')
        subprocess.run(args, check=True, capture_output=True, timeout=60)


def make_images(groups, icons, names, force=False):
    if not Path(CHROME).exists():
        print('크롬이 없어 이미지는 건너뜀')
        return
    og_dir = ROOT / 'assets' / 'og'
    og_dir.mkdir(parents=True, exist_ok=True)
    zap = icons.get('zap', '')
    jobs = [('home', '무료 생활 도구 모음', '계산기 · 변환기 · 생활 도구', 'sparkles', 'violet')]
    for g in groups:
        for it in g['items']:
            jobs.append((it['p'].strip('/'), names.get(it['p'], it['t']), g['name'], it['i'], g['tone']))
    made = 0
    for slug, title, group, ic, tone in jobs:
        out = og_dir / f'{slug}.jpg'
        if out.exists() and not force:
            continue
        tmp = og_dir / f'_{slug}.png'
        size = 76 if len(title) <= 10 else 64 if len(title) <= 14 else 54
        chrome_shot(OG_HTML.format(tone=TONES.get(tone, '#8AA4FF'), zap=zap, icon=icons.get(ic, ''), site=SITE_NAME,
                                   group=html.escape(group), title=html.escape(title), size=size), tmp, 1200, 630)
        from PIL import Image
        Image.open(tmp).convert('RGB').save(out, 'JPEG', quality=86, optimize=True, progressive=True)   # PNG 는 장당 240KB 라 JPG 로
        tmp.unlink()
        made += 1
    print(f'공유 이미지 {made}개 만듦')
    img = ROOT / 'assets' / 'img'
    svg = ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64"><defs><linearGradient id="g" x1="0" y1="0" x2="1" y2="1">'
           '<stop offset="0" stop-color="#5B7CFA"/><stop offset=".55" stop-color="#3157E0"/><stop offset="1" stop-color="#6A4FD8"/></linearGradient></defs>'
           '<rect width="64" height="64" rx="16" fill="url(#g)"/><g transform="translate(14 14) scale(1.5)" fill="#fff">' + zap + '</g></svg>')
    (img / 'favicon.svg').write_text(svg, encoding='utf-8')
    if force or not (ROOT / 'favicon.ico').exists():
        from PIL import Image   # 맥 기본 python3 에 있음
        big = img / '_icon512.png'
        sized = svg.replace('<svg ', '<svg width="512" height="512" ', 1)
        chrome_shot('<html><body style="margin:0;background:transparent">' + sized + '</body></html>', big, 512, 512, transparent=True)
        im = Image.open(big).convert('RGBA').crop((0, 0, 512, 512))
        im.resize((180, 180), Image.LANCZOS).save(img / 'apple-touch-icon.png')
        im.resize((192, 192), Image.LANCZOS).save(img / 'icon-192.png')
        im.save(ROOT / 'favicon.ico', sizes=[(16, 16), (32, 32), (48, 48)])
        big.unlink()
        print('파비콘 만듦')


def git_date(rel: str) -> str:
    try:
        dirty = subprocess.run(['git', 'status', '--porcelain', '--', rel], cwd=ROOT, capture_output=True, text=True).stdout.strip()
        if dirty:
            return date.today().isoformat()
        d = subprocess.run(['git', 'log', '-1', '--format=%cs', '--', rel], cwd=ROOT, capture_output=True, text=True).stdout.strip()
        return d or date.today().isoformat()
    except OSError:
        return date.today().isoformat()


def main():
    groups, icons = read_site()
    pages = [('/', ROOT / 'index.html', None)]
    for g in groups:
        for it in g['items']:
            pages.append((it['p'], ROOT / it['p'].strip('/') / 'index.html', g))
    names = {}
    for p, f, _ in pages[1:]:
        if f.exists():
            names[p] = page_info(f)[1]['h1'] or p
    if '--images' in sys.argv:
        make_images(groups, icons, names, force='--force-images' in sys.argv)
    changed = 0
    for p, f, g in pages:
        if not f.exists():
            print(f'없음: {f}')
            continue
        s, info = page_info(f)
        s2 = re.sub(r'<link rel="icon" href="data:image/svg\+xml,[^"]*">\n?', '', s)   # 예전 이모지 아이콘
        slug = 'home' if p == '/' else p.strip('/')
        # 구글 경로(BreadcrumbList)는 마지막 칸을 빼고 모두 주소가 있어야 해서, 주소 없는 묶음 이름은 넣지 않는다
        crumbs = [(SITE_NAME, BASE + '/')] + ([(info['h1'], BASE + p)] if g else [])
        s2 = replace_block(s2, 'head', head_block(BASE + p, info, f'/assets/og/{slug}.jpg', crumbs, faq_of(s2), p == '/', CATEGORY.get(g['name'] if g else '', 'UtilitiesApplication')), '</head>')
        s2 = replace_block(s2, 'nav', nav_block(groups, names, p), '<script src="/assets/site.js"></script>')
        if s2 != s:
            f.write_text(s2, encoding='utf-8')
            changed += 1
    urls = ''.join(f'  <url><loc>{BASE}{p}</loc><lastmod>{git_date(str(f.relative_to(ROOT)))}</lastmod></url>\n' for p, f, _ in pages if f.exists())
    sm = f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n{urls}</urlset>\n'
    if (ROOT / 'sitemap.xml').read_text(encoding='utf-8') != sm:
        (ROOT / 'sitemap.xml').write_text(sm, encoding='utf-8')
        print('사이트맵 갱신')
    print(f'페이지 {len(pages)}개 중 {changed}개 바뀜')


if __name__ == '__main__':
    main()
