"""짱툴 끝말잇기 글자별 페이지: hanbang/<글자>/index.html (「기로 시작하는 단어 · 기로 끝나는 단어」)와 한방단어 검색기의 글자 목록.

    python3 .github/scripts/build_words.py

단어 데이터는 끝말잇기 도구가 쓰는 것을 그대로 읽는다 — 사전 데이터가 바뀌었을 때만 다시 돌리면 된다(매일 돌릴 필요 없음).
    wordchain/words.txt   기본 단어(우리말샘 명사·일반어, 전문용어만 있는 단어 제외) 한 줄에 하나
    hanbang/hanbang.json  한방·준한방 단어(words: [단어, 플래그, 뜻번호], 플래그 1=한방(전체) 2=한방(기본) 4·8=준한방)
만드는 글자: 기본 단어가 MIN_WORDS 개 넘게 시작하거나 끝나는 글자 + 한방단어가 HB_MIN 개 넘게 끝나는 글자.
"""
import html
import json
import re
from collections import defaultdict
from pathlib import Path
from urllib.parse import quote

ROOT = Path(__file__).resolve().parents[2]
BASE = 'https://jjangtool.com'
MIN_WORDS = 300
HB_MIN = 3
SHOW = {2: 150, 3: 150, 4: 80}   # 길이별로 보여 줄 개수(4는 4글자 이상)
CHO = 'ㄱㄲㄴㄷㄸㄹㅁㅂㅃㅅㅆㅇㅈㅉㅊㅋㅌㅍㅎ'
esc = html.escape

# 두음법칙 (build_hanbang.py · hanbang/index.html 과 같은 규칙)
N_TO_O, R_TO_O, R_TO_N = {6, 12, 17, 20}, {2, 6, 7, 12, 17, 20}, {0, 1, 8, 11, 13, 18}


def parts(ch):
    c = ord(ch) - 0xAC00
    return (c // 588, (c % 588) // 28, c % 28) if 0 <= c < 11172 else None


def dueum(ch):
    p = parts(ch)
    if not p:
        return None
    cho, jung, jong = p
    if cho == 2 and jung in N_TO_O or cho == 5 and jung in R_TO_O:
        n = 11
    elif cho == 5 and jung in R_TO_N:
        n = 2
    else:
        return None
    return chr(0xAC00 + n * 588 + jung * 28 + jong)


def ro(ch):
    """조사 (으)로: 받침이 있고 ㄹ 받침이 아니면 '으로'."""
    p = parts(ch)
    return '으로' if p and p[2] and p[2] != 8 else '로'


def word_list(words):
    out = ''
    for ln, label in ((2, '2글자'), (3, '3글자'), (4, '4글자 이상')):
        g = [w for w in words if (len(w) == ln if ln < 4 else len(w) >= 4)]
        if not g:
            continue
        shown = g[:SHOW[ln]]
        more = f' <span class="note">(전체 {len(g):,}개 중 {len(shown)}개)</span>' if len(g) > len(shown) else f' <span class="note">{len(g):,}개</span>'
        out += f'<h3>{label}{more}</h3><ul class="words">' + ''.join(f'<li>{esc(w)}</li>' for w in shown) + '</ul>'
    return out


def page(ch, d, related):
    r = ro(ch)
    alt = dueum(ch)
    st, en = d['start'][ch], d['end'][ch]
    st_alt = d['start'].get(alt, []) if alt else []
    hb_end = [w for w, f in d['hb'] if w[-1] == ch]
    hb_start = [w for w, f in d['hb'] if w[0] == ch]
    near_end = [w for w, f in d['near'] if w[-1] == ch]
    can = len(st) + len(st_alt)
    dead = d['start_basic'].get(ch, 0) + (d['start_basic'].get(alt, 0) if alt else 0) == 0   # 기본 단어로 이을 단어 없음
    if dead:
        title = f'{ch}{r} 끝나는 단어 - 끝말잇기 한방단어 {len(hb_end):,}개 ({ch}{r} 끝나는 말)'
        h1 = f'{ch}{r} 끝나는 단어 · 끝말잇기 한방단어'
        desc = f'{ch}{r} 끝나는 단어 {len(en):,}개는 모두 끝말잇기 한방단어입니다. {ch}{r} 시작하는 단어가 없어 상대가 이을 수 없는 필승 단어를 모았습니다. 국립국어원 우리말샘 기준.'
    elif len(st) < 30:
        title = f'{ch}{r} 끝나는 단어 - 끝말잇기 공격 단어 ({ch}{r} 끝나는 말 {len(en) + len(near_end):,}개)'
        h1 = f'{ch}{r} 끝나는 단어 · 끝말잇기 공격 단어'
        desc = (f'{ch}{r} 끝나는 단어를 모았습니다. {ch}{r} 시작하는 단어가 {can}개뿐이라 끝말잇기에서 상대를 막기 좋은 공격 단어입니다. '
                '국립국어원 우리말샘 기준, 두음법칙 반영.')
    else:
        title = f'{ch}{r} 시작하는 단어 · {ch}{r} 끝나는 단어 - 끝말잇기 {ch} 단어 모음'
        h1 = f'{ch}{r} 시작하는 단어 · {ch}{r} 끝나는 단어'
        desc = (f'{ch}{r} 시작하는 단어 {len(st):,}개, {ch}{r} 끝나는 단어 {len(en):,}개를 2글자·3글자·4글자로 나눠 정리했습니다. '
                f'끝말잇기에서 {ch}{r} 이어 갈 단어와 {ch}{r} 시작하는 한방단어도 확인하세요. 국립국어원 우리말샘 기준.')
    cells = [(f'{len(st):,}개', f'{ch}{r} 시작하는 단어'), (f'{len(en):,}개', f'{ch}{r} 끝나는 단어'),
             (f'{len(hb_start):,}개', f'{ch}{r} 시작하는 한방단어'), (f'{len(hb_end):,}개', f'{ch}{r} 끝나는 한방단어'),
             (f'{len(near_end):,}개', f'{ch}{r} 끝나는 준한방 단어')]
    cells = [c for c in cells if c[0] != '0개']
    tip = []
    if dead:
        tip.append(f'<b>{ch}</b>{r} 시작하는 단어가 사전에 없어서(두음법칙 포함), {ch}{r} 끝나는 단어를 말하면 상대가 이을 수 없습니다. 아래 단어가 모두 한방단어입니다.')
    else:
        ways = ([f'{ch}{r} 시작하는 단어 {len(st):,}개'] if st else []) + ([f'두음법칙으로 <b>{alt}</b>{ro(alt)} 시작하는 단어 {len(st_alt):,}개'] if alt and st_alt else [])
        tip.append(f'상대가 <b>{ch}</b>{r} 끝나는 단어를 냈다면 ' + ('와 '.join(ways) + '로 이어 갈 수 있습니다.' if ways else '기본 단어로는 이을 단어가 없고 전문용어로만 이을 수 있습니다.'))
        if hb_start:
            tip.append(f'그중 {ch}{r} 시작하는 한방단어 {len(hb_start):,}개를 쓰면 상대가 이어 가지 못합니다: <b>{esc(", ".join(hb_start[:12]))}</b>' + (' 등' if len(hb_start) > 12 else '') + '.')
        if can <= 30:
            tip.append(f'이어 갈 단어가 {can}개뿐이라 {ch}{r} 끝나는 단어로 공격하면 상대가 막히기 쉽습니다.')
    body = ('<div class="dd-stats">' + ''.join(f'<div><b>{a}</b><span>{b}</span></div>' for a, b in cells) + '</div>'
            f'<div class="panel"><p style="margin:0">{"</p><p style=\"margin:8px 0 0\">".join(tip)}</p></div>')
    if hb_end:
        body += f'<h2>{ch}{r} 끝나는 한방단어</h2><ul class="words">' + ''.join(f'<li>{esc(w)}</li>' for w in hb_end[:300]) + '</ul>'
        if len(hb_end) > 300:
            body += f'<p class="note">전체 {len(hb_end):,}개 중 300개. 나머지는 <a href="/hanbang/">한방단어 검색기</a>에서 볼 수 있습니다.</p>'
    if st:
        body += f'<h2>{ch}{r} 시작하는 단어</h2>' + word_list(st)
    if hb_start:
        body += f'<h2>{ch}{r} 시작하는 한방단어</h2><ul class="words">' + ''.join(f'<li>{esc(w)}</li>' for w in hb_start[:200]) + '</ul>'
    if en:
        body += f'<h2>{ch}{r} 끝나는 단어</h2>' + word_list(en)
    if near_end:
        body += (f'<h2>{ch}{r} 끝나는 준한방 단어</h2><p class="note">상대가 이을 단어가 1~3개뿐인 단어입니다.</p><ul class="words">' +
                 ''.join(f'<li>{esc(w)}</li>' for w in near_end[:100]) + '</ul>')
    faq = [(f'{ch}{r} 시작하는 단어는 몇 개인가요?', f'우리말샘 기본 명사 기준 {len(st):,}개입니다.' + (f' 두음법칙으로 {alt}{ro(alt)} 시작하는 단어 {len(st_alt):,}개도 끝말잇기에 쓸 수 있습니다.' if alt and st_alt else '')),
           (f'{ch}{r} 끝나는 단어는 몇 개인가요?', f'기본 명사 기준 {len(en):,}개이고, 그중 한방단어는 {len(hb_end):,}개입니다.' if not dead else f'기본 명사 {len(en):,}개와 전문용어까지 합친 한방단어 {len(hb_end):,}개가 있습니다.'),
           ('끝말잇기에서 두음법칙을 써도 되나요?', '보통 허용합니다. 예를 들어 「력」으로 끝나면 「역」으로, 「리」로 끝나면 「이」로 시작하는 단어를 이어도 됩니다. 시작 전에 규칙을 정해 두세요.'),
           ('어떤 사전 기준인가요?', '국립국어원 우리말샘의 명사(일반어) 기준입니다. 옛말·방언·북한어·고유명사(지명·인명)는 뺐습니다.')]
    body += '<section class="faq"><h2>자주 묻는 질문</h2>' + ''.join(f'<details><summary>{esc(q)}</summary><p>{esc(a)}</p></details>' for q, a in faq) + '</section>'
    body += ('<h2>다른 글자 단어</h2><ul class="chips">' + ''.join(f'<li><a href="/hanbang/{quote(c)}/">{c}</a></li>' for c in related) + '</ul>'
             '<p class="note">내 단어가 한방인지 검사하려면 <a href="/hanbang/">한방단어 검색기</a>, 컴퓨터와 겨뤄 보려면 '
             '<a href="/wordchain/">끝말잇기 컴퓨터 대결</a>을 쓰세요. 단어 수는 국립국어원 우리말샘 기준입니다.</p>')
    url = f'{BASE}/hanbang/{quote(ch)}/'
    a = lambda s: esc(s, quote=True)   # noqa: E731
    kw = f'{ch}{r} 시작하는 단어, {ch}{r} 끝나는 단어, {ch} 끝말잇기, {ch}{r} 끝나는 한방단어, 끝말잇기 한방단어'
    return f'''<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{esc(title)}</title>
<meta name="description" content="{a(desc)}">
<meta name="keywords" content="{a(kw)}">
<meta property="og:title" content="{a(title)}">
<meta property="og:description" content="{a(desc)}">
<meta property="og:type" content="website">
<meta property="og:url" content="{url}">
<link rel="canonical" href="{url}">
<link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/static/pretendard.min.css">
<link rel="stylesheet" href="/assets/site.css">
<!-- 이 파일은 .github/scripts/build_words.py 가 만든다 — 직접 고치지 말 것 -->
<!-- seo:head -->
<!-- /seo:head -->
</head>
<body data-blog="kkultiplab">
<main>
<h1>{esc(h1)}</h1>
<p class="lead">끝말잇기에 쓸 수 있는 「{ch}」 단어를 모았습니다. 국립국어원 우리말샘 명사 기준이고, 두음법칙까지 반영했습니다.</p>
{body}
</main>
<!-- seo:nav -->
<!-- /seo:nav -->
<script src="/assets/site.js"></script>
</body>
</html>
'''


def load():
    words = [w.strip() for w in (ROOT / 'wordchain' / 'words.txt').read_text(encoding='utf-8').split('\n') if w.strip()]
    start, end = defaultdict(list), defaultdict(list)
    for w in sorted(words, key=lambda x: (len(x), x)):
        start[w[0]].append(w)
        end[w[-1]].append(w)
    hj = json.loads((ROOT / 'hanbang' / 'hanbang.json').read_text(encoding='utf-8'))
    # 한방단어 검색기 기본값(기본 단어)과 같게 판정. 준한방은 전문용어 기준(4)까지 넣는다(늄·륨 같은 글자)
    hb = sorted(((r[0], r[1]) for r in hj['words'] if r[1] & 2), key=lambda x: (len(x[0]), x[0]))
    near = sorted(((r[0], r[1]) for r in hj['words'] if r[1] & 12 and not r[1] & 2), key=lambda x: (not x[1] & 8, len(x[0]), x[0]))
    return dict(start=start, end=end, hb=hb, near=near, start_basic=hj['start_basic'])


def main():
    d = load()
    hb_end = defaultdict(int)
    for w, _ in d['hb']:
        hb_end[w[-1]] += 1
    near_end = defaultdict(int)
    for w, _ in d['near']:
        near_end[w[-1]] += 1
    chars = sorted({c for c, v in d['start'].items() if len(v) >= MIN_WORDS} | {c for c, v in d['end'].items() if len(v) >= MIN_WORDS}
                   | {c for c, n in hb_end.items() if n >= HB_MIN and parts(c)} | {c for c, n in near_end.items() if n >= HB_MIN and parts(c)})
    by_cho = defaultdict(list)
    for c in chars:
        by_cho[parts(c)[0]].append(c)
    out_dir = ROOT / 'hanbang'
    keep = set()
    changed = 0
    for c in chars:
        same = by_cho[parts(c)[0]]
        i = same.index(c)
        related = [x for x in same[max(0, i - 8):i + 9] if x != c][:16]
        f = out_dir / c / 'index.html'
        keep.add(f.parent)
        old = f.read_text(encoding='utf-8') if f.exists() else ''
        new = page(c, d, related)
        for tag in ('head', 'nav'):   # build_seo.py 가 채운 블록은 그대로
            m = re.search(rf'<!-- seo:{tag} -->.*?<!-- /seo:{tag} -->', old, re.S)
            if m:
                new = re.sub(rf'<!-- seo:{tag} -->.*?<!-- /seo:{tag} -->', lambda _: m.group(0), new, flags=re.S)
        if new != old:
            f.parent.mkdir(exist_ok=True)
            f.write_text(new, encoding='utf-8')
            changed += 1
    # 기준이 바뀌어 빠진 글자 폴더는 지운다(이 스크립트가 만든 것만)
    for sub in out_dir.iterdir():
        if sub.is_dir() and sub not in keep and (sub / 'index.html').exists() and 'build_words.py' in (sub / 'index.html').read_text(encoding='utf-8'):
            (sub / 'index.html').unlink()
            sub.rmdir()
    # 한방단어 검색기에 글자 목록
    hub = out_dir / 'index.html'
    s = hub.read_text(encoding='utf-8')
    groups = ''.join(f'<h3>{CHO[k]}</h3><ul class="chips">' + ''.join(f'<li><a href="/hanbang/{quote(c)}/">{c}</a></li>' for c in v) + '</ul>'
                     for k, v in sorted(by_cho.items()))
    block = f'<!-- words:list -->\n<h2>글자별 끝말잇기 단어</h2>\n<p class="note">글자를 누르면 그 글자로 시작하는 단어·끝나는 단어·한방단어를 볼 수 있습니다.</p>\n{groups}\n<!-- /words:list -->'
    if '<!-- words:list -->' in s:
        s2 = re.sub(r'<!-- words:list -->.*?<!-- /words:list -->', lambda _: block, s, flags=re.S)
    elif '<section class="faq">' in s:
        s2 = s.replace('<section class="faq">', block + '\n<section class="faq">', 1)
    else:
        s2 = s.replace('</main>', block + '\n</main>', 1)
    if s2 != s:
        hub.write_text(s2, encoding='utf-8')
        changed += 1
    print(f'글자 {len(chars)}개 · 바뀐 파일 {changed}개')


if __name__ == '__main__':
    main()
