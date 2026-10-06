"""짱툴 특수문자: symbols/index.html(전체 모음)과 symbols/<분류>/index.html(하트·화살표·별·이모티콘·이모지·귀여운 특수문자).

    python3 .github/scripts/build_symbols.py

기호는 유니코드 범위에서 뽑는다(파이썬 unicodedata 로 배정된 글자만). 이모지는 .github/data/emoji.json
(유니코드 emoji-test.txt 에서 15.0 이하·피부색 변형 제외로 뽑은 것), 텍스트 이모티콘·꾸밈 문자는
.github/data/emoticons.txt · decorations.txt. 데이터를 고쳤을 때만 다시 돌리면 된다(매일 아님).
복사·최근·즐겨찾기·탭은 assets/symbols.js.
"""
import html
import json
import re
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / '.github' / 'data'
BASE = 'https://jjangtool.com'
esc = html.escape


def R(a, b, skip=''):
    """a~b 범위에서 배정된 글자(제어·결합 문자 제외)."""
    out = []
    for cp in range(a, b + 1):
        c = chr(cp)
        if c in skip or not unicodedata.name(c, '') or unicodedata.category(c) in ('Cc', 'Cf', 'Mn', 'Me', 'Zs', 'Co', 'Cn'):
            continue
        out.append(c)
    return out


def L(s):
    return [c for c in s.split(' ') if c] if ' ' in s else list(s)


def uniq(xs):
    seen, out = set(), []
    for x in xs:
        if x not in seen:
            seen.add(x)
            out.append(x)
    return out


# ── 기호 분류: (앵커, 이름, 글자들) ──
HEARTS = L('♥ ♡ ❤ ❥ ❣ ❦ ❧ ☙ ღ ❤︎ ❣︎ ♥︎ εїз ʚ♡ɞ ⸜♡⸝ ❤️ 💕 💗 💓 💖 💘 💝 💞 💟 💌 💔 ❤️‍🔥 ❤️‍🩹 🧡 💛 💚 💙 💜 🤎 🖤 🤍 🩷 🩵 🩶 💋 😍 🥰 😘 😻 🫶 🤟')
STARS = L('★ ☆ ✦ ✧ ✩ ✪ ✫ ✬ ✭ ✮ ✯ ✰ ⋆ ✡ ✴ ✵ ✶ ✷ ✸ ✹ ✺ ✻ ✼ ❂ ⁂ ⍟ ✢ ✣ ✤ ✥ ❉ ❊ ❋ ⊹ ⁺ ˚ ✳ ❇ ❈ ⭑ ⭒ ⯪ ⯫ ⭐ 🌟 ✨ 💫 🌠 🌌 ☄️ ✩°｡ ⋆｡˚ ☆彡 ★彡')
CHECKS = L('✓ ✔ ☑ ✅ ✗ ✘ ☒ ❌ ❎ ✕ ✖ ⨯ ☐ □ ■ ▣ ◯ ○ ⭕ ❗ ❕ ❓ ❔ ‼ ⁉ ⚠ ⛔ 🚫 ✋')
FREQ = L('★ ☆ ♥ ♡ ♪ ♬ ※ ○ ● ◎ ◇ ◆ □ ■ △ ▲ ▽ ▼ → ← ↑ ↓ ↔ · • … ‥ 「 」 『 』 【 】 《 》 〈 〉 ㆍ ✓ ✔ ✕ ✖ ① ② ③ ㉠ ㉡ ㉢ ℃ ㎡ ㎏ ± × ÷ ≠ ₩ ™ © ® ☎ ☏ ☞ ♨')
SYMBOL_CATS = [
    ('freq', '자주 쓰는', FREQ),
    ('heart', '하트', [h for h in HEARTS if len(h) <= 3 and not 0x1F000 <= ord(h[0]) <= 0x1FAFF][:28]),
    ('star', '별·반짝이', [s for s in STARS if not 0x1F000 <= ord(s[0]) <= 0x1FAFF and len(s) <= 2]),
    ('check', '체크·엑스', [c for c in CHECKS if not 0x1F000 <= ord(c[0]) <= 0x1FAFF]),
    ('arrow', '화살표', uniq(R(0x2190, 0x21FF) + R(0x27F0, 0x27FF) + R(0x2794, 0x27BF) + R(0x2B00, 0x2B11) + R(0x2B60, 0x2B95))),
    ('shape', '도형', uniq(R(0x25A0, 0x25FF) + R(0x2B12, 0x2B2F) + L('♤ ♠ ♡ ♥ ♧ ♣ ♢ ♦ ⊙ ◉ ⦿ ⬤'))),
    ('punct', '괄호·문장부호', uniq(L('「 」 『 』 【 】 《 》 〈 〉 〔 〕 〖 〗 〘 〙 〚 〛 ｛ ｝ ［ ］ （ ） ‘ ’ “ ” ‚ „ ‹ › « » 〃 ‥ … · ㆍ • ‧ ¡ ¿ § ¶ † ‡ ※ ‰ ‱ ′ ″ ‴ ‵ ‶ ⁂ ⁎ ⁑ ‼ ⁇ ⁈ ⁉ ‐ ‑ ‒ – — ― ‖ ‗ ⁓ 〜 ～ ¦ ¨ ´ ˇ ˘ ˝ ˚ ˙ ¸ ˛ ¯ ˜ 、 。 ・ ･'))),
    ('circle-num', '원·괄호 숫자', uniq(R(0x2460, 0x249B) + R(0x24EA, 0x24FF) + R(0x2776, 0x2793) + R(0x3251, 0x325F) + R(0x32B1, 0x32BF))),
    ('circle-en', '원·괄호 영문', R(0x249C, 0x24E9) + R(0x1F130, 0x1F149) + R(0x1F150, 0x1F169) + R(0x1F170, 0x1F189)),
    ('circle-ko', '원·괄호 한글', R(0x3200, 0x321E) + R(0x3260, 0x327F)),
    ('circle-hanja', '원·괄호 한자', R(0x3220, 0x3243) + R(0x3280, 0x32B0)),
    ('roman', '로마 숫자', R(0x2160, 0x2188)),
    ('sup', '위·아래 첨자·분수', uniq(L('⁰ ¹ ² ³') + R(0x2074, 0x209C) + L('½ ⅓ ⅔ ¼ ¾') + R(0x2150, 0x215F) + L('↉'))),
    ('unit', '단위', uniq(R(0x3380, 0x33DF) + L('℃ ℉ ° ′ ″ Å ℓ № ℡ ™ ® © ℗ ℠ ℮ ㏂ ㏘ ‰'))),
    ('letterlike', '문자 모양 기호', R(0x2100, 0x214F)),
    ('math', '수학', uniq(L('± × ÷ ¬') + R(0x2200, 0x22FF))),
    ('currency', '통화', uniq(L('$ ¢ £ ¤ ¥ ₩') + R(0x20A0, 0x20C0) + L('元 円 圓'))),
    ('greek', '그리스 문자', R(0x0391, 0x03A9) + R(0x03B1, 0x03C9)),
    ('latin', '라틴 문자(악센트)', R(0x00C0, 0x00FF, skip='×÷')),
    ('box', '괘선·블록', R(0x2500, 0x259F)),
    ('hiragana', '히라가나', R(0x3041, 0x3096)),
    ('katakana', '가타카나', R(0x30A1, 0x30FA) + L('ー')),
    ('jamo', '한글 자모', R(0x3131, 0x318E)),
    ('game', '카드·체스·주사위', uniq(R(0x2654, 0x265F) + R(0x2660, 0x2667) + R(0x2680, 0x2685) + L('🂡 🂱 🃁 🃑 🃏'))),
    ('music', '음악', uniq(R(0x2669, 0x266F) + L('𝄞 𝄢 𝄪 𝄫 🎵 🎶'))),
    ('misc', '여러 가지 기호', R(0x2600, 0x26FF)),
    ('dingbat', '딩뱃(장식 기호)', R(0x2700, 0x27BF)),
]


def load_lines(name):
    """## 이름|앵커 아래 한 줄에 하나."""
    cats, cur = [], None
    for ln in (DATA / name).read_text(encoding='utf-8').split('\n'):
        if ln.startswith('## '):
            n, _, slug = ln[3:].partition('|')
            cur = (slug.strip(), n.strip(), [])
            cats.append(cur)
        elif ln.strip() and not ln.startswith('#') and cur:
            cur[2].append(ln.rstrip())
    return cats


EMOJI_GROUPS = {'Smileys & Emotion': ('face', '표정·감정'), 'People & Body': ('people', '사람·손'), 'Animals & Nature': ('nature', '동물·자연'),
                'Food & Drink': ('food', '음식·음료'), 'Travel & Places': ('travel', '여행·장소'), 'Activities': ('activity', '활동·스포츠'),
                'Objects': ('object', '사물'), 'Symbols': ('symbol', '기호'), 'Flags': ('flag', '국기')}


def emoji_cats():
    rows = json.loads((DATA / 'emoji.json').read_text(encoding='utf-8'))
    cats = {}
    for g, sub, e, name in rows:
        slug, ko = EMOJI_GROUPS[g]
        cats.setdefault(slug, (slug, ko, []))[2].append(e)
    return list(cats.values()), rows


# ── HTML 조각 ──
def grid(chars, kind=''):
    cls = 'syms' + (f' {kind}' if kind else '')
    return f'<div class="{cls}">' + ''.join(f'<button type="button">{esc(c)}</button>' for c in chars) + '</div>'


def sections(cats, prefix, kind='', h='h2'):
    nav = '<p class="sym-jump">' + ''.join(f'<a href="#{prefix}-{s}">{esc(n)}</a>' for s, n, _ in cats) + '</p>'
    body = ''.join(f'<{h} id="{prefix}-{s}">{esc(n)} <small>{len(xs):,}개</small></{h}>{grid(xs, kind)}' for s, n, xs in cats if xs)
    return nav + body


COLLECT = ('<div class="collect">'
           '<div class="field"><label for="box">모음 칸</label><input id="box" type="text" placeholder="누른 문자가 여기에 모입니다."></div>'
           '<div class="btns" style="margin-top:0"><button type="button" class="btn" id="copyAll">모음 전체 복사</button>'
           '<button type="button" class="btn sub" id="clear">비우기</button>'
           '<button type="button" class="btn sub" id="favMode" aria-pressed="false">☆ 즐겨찾기 고르기</button></div></div>'
           '<div class="sym-my" id="myBox" hidden><h2>최근·즐겨찾기</h2><div id="favRow"></div><div id="recentRow"></div></div>')

KEYS = [('ㄱ', '문장부호', '! ? , . : ; 、 。 …'), ('ㄴ', '괄호', '( ) [ ] { } 「 」 『 』 【 】 《 》'), ('ㄷ', '수학 기호', '+ − ± × ÷ ≠ ≤ ≥ ∞ ∴ √ ∑'),
        ('ㄹ', '단위', '$ % ₩ ℃ ㎜ ㎝ ㎞ ㎡ ㎏ ㏄'), ('ㅁ', '도형·기호', '★ ☆ ○ ● ◎ ◇ ◆ □ ■ △ ▲ → ← ♥ ♡'),
        ('ㅂ', '괘선', '─ │ ┌ ┐ ┘ └ ├ ┼ ━ ┃'), ('ㅅ', '원·괄호 한글', '㉠ ㉡ ㉢ ㉮ ㉯ ㈀ ㈎'), ('ㅇ', '원·괄호 영문·숫자', 'ⓐ ⓑ ① ② ⒜ ⑴ ⒈'),
        ('ㅈ', '숫자(로마)', '0~9 Ⅰ Ⅱ Ⅲ ⅰ ⅱ'), ('ㅊ', '분수·첨자', '½ ⅓ ¼ ¹ ² ³ ⁿ ₁ ₂'), ('ㅋ', '한글 자모', 'ㄱ ㄲ ㄳ ㄴ … ㅏ ㅐ'),
        ('ㅌ', '옛한글 자모', 'ㅥ ㅦ ㅿ ㆁ ㆆ'), ('ㅍ', '라틴 문자', 'A B C … a b c'), ('ㅎ', '그리스 문자', 'Α Β Γ … α β γ'),
        ('ㄲ', '라틴 특수 문자', 'Æ Ð Ø Þ æ ð ø ß'), ('ㄸ', '히라가나', 'ぁ あ ぃ い …'), ('ㅃ', '가타카나', 'ァ ア ィ イ …'), ('ㅆ', '러시아 문자', 'А Б В … а б в')]


def key_table():
    rows = ''.join(f'<tr><th>{k} + 한자</th><td>{n}</td><td>{esc(ex)}</td></tr>' for k, n, ex in KEYS)
    return ('<h2 id="howto">PC에서 특수문자 입력하는 법</h2><p>윈도우 한글 입력 상태에서 자음 하나를 쓰고 <b>한자</b> 키(오른쪽 Ctrl)를 누르면 특수문자 목록이 뜹니다. '
            'Tab 키로 전체 목록을 펼칠 수 있습니다. 맥은 <b>Control + Command + 스페이스</b>로 이모지·기호 창을 엽니다.</p>'
            f'<div class="tbl-wrap"><table class="list"><thead><tr><th>입력</th><th>나오는 문자</th><th>예시</th></tr></thead><tbody>{rows}</tbody></table></div>'
            '<p class="note">휴대폰은 키보드의 「!#1」 또는 기호 버튼, 이모지 버튼에서 고를 수 있지만 종류가 적어서 이 페이지에서 복사해 붙여 넣는 편이 빠릅니다.</p>')


def faq_html(items):
    return '<section class="faq"><h2>자주 묻는 질문</h2>' + ''.join(
        f'<details><summary>{esc(q)}</summary><p>{esc(a)}</p></details>' for q, a in items) + '</section>'


def shell(url, title, desc, kw, h1, lead, body):
    a = lambda s: esc(s, quote=True)   # noqa: E731
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
<!-- 이 파일은 .github/scripts/build_symbols.py 가 만든다 — 직접 고치지 말 것 -->
<!-- seo:head -->
<!-- /seo:head -->
</head>
<body data-blog="kkultiplab">
<main>
<h1>{esc(h1)}</h1>
<p class="lead">{esc(lead)}</p>
{body}
</main>
<!-- seo:nav -->
<!-- /seo:nav -->
<script src="/assets/site.js"></script>
<script src="/assets/symbols.js"></script>
</body>
</html>
'''


SUBS = [   # (주소, 메뉴 이름)
    ('heart', '하트 특수문자'), ('arrow', '화살표 특수문자'), ('star', '별 특수문자'),
    ('emoticon', '특수문자 이모티콘'), ('emoji', '이모지 모음'), ('cute', '귀여운 특수문자'),
]


def sub_links(cur=None):
    return ('<h2>분류별 특수문자</h2><ul class="dd-links">' + ''.join(
        f'<li><a href="/symbols/{s}/"{" aria-current=page" if s == cur else ""}><span>{n}</span><b>{"보는 중" if s == cur else "보기"}</b></a></li>'
        for s, n in SUBS) + '<li><a href="/symbols/"><span>전체 특수문자 모음</span><b>보기</b></a></li></ul>')


def write(path, text):
    old = path.read_text(encoding='utf-8') if path.exists() else ''
    for tag in ('head', 'nav'):   # build_seo.py 가 채운 블록은 그대로
        m = re.search(rf'<!-- seo:{tag} -->.*?<!-- /seo:{tag} -->', old, re.S)
        if m:
            text = re.sub(rf'<!-- seo:{tag} -->.*?<!-- /seo:{tag} -->', lambda _: m.group(0), text, flags=re.S)
    if text != old:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding='utf-8')
        return 1
    return 0


def main():
    emo = load_lines('emoticons.txt')
    deco = load_lines('decorations.txt')
    ecats, erows = emoji_cats()
    n_sym = sum(len(x) for _, _, x in SYMBOL_CATS)
    n_emo = sum(len(x) for _, _, x in emo)
    n_deco = sum(len(x) for _, _, x in deco)
    n_emoji = len(erows)
    total = n_sym + n_emo + n_deco + n_emoji
    changed = 0

    tabs = [('sym', f'기호 {n_sym:,}'), ('emoji', f'이모지 {n_emoji:,}'), ('emo', f'이모티콘 {n_emo:,}'), ('deco', f'꾸밈 문자 {n_deco:,}')]
    tabbar = '<div class="seg sym-tabs" role="tablist">' + ''.join(
        f'<button type="button" role="tab" data-tab="{k}" aria-pressed="{"true" if i == 0 else "false"}">{n}</button>' for i, (k, n) in enumerate(tabs)) + '</div>'
    body = (COLLECT + tabbar
            + f'<section class="sym-panel" data-panel="sym">{sections(SYMBOL_CATS, "s")}</section>'
            + f'<section class="sym-panel" data-panel="emoji" hidden>{sections(ecats, "e", "emoji")}</section>'
            + f'<section class="sym-panel" data-panel="emo" hidden>{sections(emo, "t", "wide")}</section>'
            + f'<section class="sym-panel" data-panel="deco" hidden>{sections(deco, "d", "wide")}</section>'
            + sub_links() + key_table()
            + faq_html([('특수문자는 어떻게 복사하나요?', '원하는 문자를 누르면 바로 복사되고 위 모음 칸에도 쌓입니다. 여러 개를 고른 뒤 「모음 전체 복사」를 누르면 한 번에 복사됩니다.'),
                        ('자주 쓰는 특수문자를 저장할 수 있나요?', '「☆ 즐겨찾기 고르기」를 켜고 문자를 누르면 즐겨찾기에 들어갑니다. 최근에 복사한 문자도 위쪽에 따로 모여서, 다음에 다시 와도 바로 쓸 수 있습니다(이 기기 브라우저에만 저장).'),
                        ('특수문자가 네모(□)나 물음표로 보여요.', '보는 기기에 그 글자를 그릴 글꼴이 없을 때 그렇습니다. 오래된 휴대폰이나 일부 앱에서는 최신 이모지와 드문 기호가 안 보일 수 있습니다.'),
                        ('PC에서 특수문자 단축키가 있나요?', '윈도우에서는 자음 하나 + 한자 키(예: ㅁ + 한자 → ★☆○●), 맥에서는 Control + Command + 스페이스입니다. 위 표에 자음별로 정리했습니다.'),
                        ('이모지와 이모티콘은 어떻게 다른가요?', '이모지(😀)는 유니코드에 정해진 그림 문자이고, 텍스트 이모티콘((＾▽＾))은 여러 글자를 조합해 표정을 만든 것입니다.')]))
    changed += write(ROOT / 'symbols' / 'index.html', shell(
        f'{BASE}/symbols/',
        f'특수문자 모음 - 하트·화살표·별·이모지·이모티콘 누르면 복사 ({total:,}개)',
        f'하트 ♥, 별 ★, 화살표 →, 원문자 ①㉠, 단위 ㎡, 이모지 😀, 텍스트 이모티콘 (＾▽＾), 인스타 꾸밈 문자 ʚɞ까지 특수문자 {total:,}개를 누르면 바로 복사합니다. PC 특수문자 단축키 표 포함.',
        '특수문자, 특수문자 모음, 특수문자 복사, 특수기호, 하트 특수문자, 화살표 특수문자, 별 특수문자, 특수문자 이모티콘, 이모지, 귀여운 특수문자',
        '특수문자 모음',
        f'기호·이모지·이모티콘·꾸밈 문자 {total:,}개. 누르면 바로 복사되고 위 모음 칸에 쌓여서 여러 개를 한 번에 복사할 수 있습니다.',
        body))

    # ── 분류 페이지 ──
    heart_emoji = [e for g, sub, e, n in erows if sub == 'heart' or 'heart' in n or 'kiss' in n]
    star_emoji = [e for g, sub, e, n in erows if 'star' in n or n in ('sparkles', 'dizzy', 'milky way', 'comet')]
    emo_by = {s: (s, n, xs) for s, n, xs in emo}
    deco_by = {s: (s, n, xs) for s, n, xs in deco}
    pages = {
        'heart': dict(
            title='하트 특수문자 모음 ♥ ♡ ❤ - 누르면 복사 (하트 이모티콘·이모지)',
            desc='하트 특수문자 ♥ ♡ ❤ ❥ ❣ ღ, 하트 이모지 💕💗💖, 하트 텍스트 이모티콘 (♡˙︶˙♡), 하트 꾸밈 문자 ʚ♡ɞ를 누르면 바로 복사합니다.',
            kw='하트 특수문자, 특수문자 하트, 하트 이모티콘, 하트 기호, 하트 이모지, 하트 복사', h1='하트 특수문자 ♥',
            lead='하트 기호와 이모지, 하트 이모티콘, 하트 꾸밈 문자를 모았습니다. 누르면 바로 복사됩니다.',
            cats=[('symbol', '하트 기호', [h for h in HEARTS if not 0x1F000 <= ord(h[0]) <= 0x1FAFF], ''), ('emoji', '하트 이모지', uniq(heart_emoji), 'emoji'),
                  ('emoticon', '하트 이모티콘', emo_by['love'][2], 'wide'),
                  ('deco', '하트 꾸밈 문자', [x for _, _, xs in deco for x in xs if '♡' in x or '♥' in x or 'ɞ' in x], 'wide')],
            faq=[('하트 특수문자는 PC에서 어떻게 입력하나요?', 'ㅁ을 쓰고 한자 키를 누르면 목록에 ♡ ♥가 있습니다. 다른 하트(❤ ❥ ❣ ღ)는 이 페이지에서 복사하는 편이 빠릅니다.'),
                 ('하트가 빨간 그림으로 보이거나 검은 선으로 보여요.', '같은 ❤라도 기기·앱에 따라 글자(검은색) 또는 이모지(빨간색)로 그려집니다. 글자로 쓰고 싶으면 ♥ ♡를 쓰세요.')]),
        'arrow': dict(
            title='화살표 특수문자 모음 → ← ↑ ↓ ➜ - 누르면 복사',
            desc=f'화살표 특수문자 → ← ↑ ↓ ↔ ⇒ ➜ ➤ ⬅ 등 {len(SYMBOL_CATS[4][2]):,}개를 누르면 바로 복사합니다. 굵은 화살표, 이중 화살표, 곡선 화살표까지.',
            kw='화살표 특수문자, 특수문자 화살표, 화살표 기호, 화살표 복사, 화살표 이모티콘', h1='화살표 특수문자 →',
            lead='기본 화살표부터 굵은·이중·곡선 화살표까지 모았습니다. 누르면 바로 복사됩니다.',
            cats=[('basic', '자주 쓰는 화살표', L('→ ← ↑ ↓ ↔ ↕ ↗ ↘ ↙ ↖ ⇒ ⇐ ⇔ ➜ ➔ ➡ ⬅ ⬆ ⬇ ▶ ◀ ▷ ◁ ► ◄ ➤ ➢ ↩ ↪ ⟶ ⟵'), ''),
                  ('all', '화살표 전체', SYMBOL_CATS[4][2], ''),
                  ('emoji', '화살표 이모지', [e for g, sub, e, n in erows if sub == 'arrow'], 'emoji')],
            faq=[('화살표 특수문자는 PC에서 어떻게 입력하나요?', 'ㅁ + 한자 키를 누르면 → ← ↑ ↓ ↔이 나옵니다. ⇒ ⇔는 ㄷ + 한자(수학 기호)에 있습니다.')]),
        'star': dict(
            title='별 특수문자 모음 ★ ☆ ✦ ✧ - 누르면 복사 (반짝이 ✨)',
            desc='별 특수문자 ★ ☆ ✦ ✧ ✩ ✪ ⋆ ✨, 별 이모지 ⭐🌟💫, 반짝이 꾸밈 문자 ⋆｡˚를 누르면 바로 복사합니다.',
            kw='별 특수문자, 특수문자 별, 별 기호, 반짝이 특수문자, 별 이모티콘, 별 복사', h1='별 특수문자 ★',
            lead='별 기호와 반짝이, 별 이모지, 별 꾸밈 문자를 모았습니다. 누르면 바로 복사됩니다.',
            cats=[('symbol', '별 기호', [s for s in STARS if not 0x1F000 <= ord(s[0]) <= 0x1FAFF], ''), ('emoji', '별 이모지', uniq(star_emoji), 'emoji'),
                  ('deco', '별·반짝이 꾸밈 문자', [x for _, _, xs in deco for x in xs if any(c in x for c in '★☆✧✦⋆✩˚')], 'wide')],
            faq=[('별 특수문자는 PC에서 어떻게 입력하나요?', 'ㅁ + 한자 키를 누르면 ★ ☆가 있습니다. ✦ ✧ ✩ 같은 다른 별은 이 페이지에서 복사하세요.')]),
        'emoticon': dict(
            title=f'특수문자 이모티콘 모음 (＾▽＾) - 텍스트 이모티콘 {n_emo:,}개 누르면 복사',
            desc='특수문자로 만든 텍스트 이모티콘을 기쁨·하트·슬픔·화남·놀람·인사·동물·응원 등 감정별로 모았습니다. ¯\\_(ツ)_/¯ ʕ•ᴥ•ʔ (╥﹏╥)를 누르면 바로 복사합니다.',
            kw='특수문자 이모티콘, 텍스트 이모티콘, 이모티콘 특수문자, 귀여운 이모티콘, 카오모지, 문자 이모티콘', h1='특수문자 이모티콘 (＾▽＾)',
            lead='특수문자를 조합한 텍스트 이모티콘을 감정별로 모았습니다. 누르면 바로 복사됩니다.',
            cats=[(s, n, xs, 'wide') for s, n, xs in emo],
            faq=[('텍스트 이모티콘이 깨져 보여요.', '일본어·특수 결합 문자를 쓰는 이모티콘은 기기에 따라 모양이 조금 달라질 수 있습니다. 카카오톡·인스타그램 등 대부분의 앱에서는 그대로 보입니다.')]),
        'emoji': dict(
            title=f'이모지 모음 😀 - 이모지 {n_emoji:,}개 누르면 복사 (표정·하트·동물·음식·국기)',
            desc=f'표정, 사람·손, 동물, 음식, 여행, 활동, 사물, 기호, 국기 이모지 {n_emoji:,}개를 분류별로 모았습니다. 누르면 바로 복사합니다.',
            kw='이모지, 이모지 모음, 이모지 복사, 이모티콘 이모지, 국기 이모지, 하트 이모지', h1='이모지 모음 😀',
            lead=f'유니코드 이모지 {n_emoji:,}개를 분류별로 모았습니다. 누르면 바로 복사됩니다.',
            cats=[(s, n, xs, 'emoji') for s, n, xs in ecats],
            faq=[('이모지가 네모로 보여요.', '최신 이모지는 오래된 기기에서 안 보일 수 있습니다. 이 페이지는 대부분의 기기에서 보이는 이모지 15.0 버전까지만 넣었습니다.'),
                 ('피부색이 다른 이모지는 없나요?', '목록을 간단히 하려고 기본 색만 넣었습니다. 휴대폰 이모지 키보드에서 길게 누르면 피부색을 고를 수 있습니다.')]),
        'cute': dict(
            title='귀여운 특수문자 모음 ʚ♡ɞ - 인스타 꾸밈 문자·구분선·귀여운 이모티콘',
            desc='인스타그램·카톡 프로필 꾸미기에 쓰는 귀여운 특수문자 ʚɞ ꒰꒱ ₊˚⊹ ୨୧, 앞뒤 장식, 구분선, 귀여운 이모티콘을 누르면 바로 복사합니다.',
            kw='귀여운 특수문자, 인스타 특수문자, 꾸밈 문자, 귀여운 이모티콘, 프로필 꾸미기 특수문자, 특수문자 구분선', h1='귀여운 특수문자 ʚ♡ɞ',
            lead='인스타·카톡 프로필 꾸미기에 쓰는 귀여운 특수문자와 구분선, 이모티콘을 모았습니다. 누르면 바로 복사됩니다.',
            cats=[(s, n, xs, 'wide') for s, n, xs in deco] + [(f'emo-{k}', f'귀여운 이모티콘 · {emo_by[k][1]}', emo_by[k][2], 'wide') for k in ('love', 'shy', 'animal')],
            faq=[('인스타그램에 붙여 넣으면 모양이 바뀌어요.', '일부 결합 문자(˚ ࣪ 등)는 앱 글꼴에 따라 위치가 조금 달라집니다. 붙여 넣은 뒤 미리 보기로 확인하세요.')]),
    }
    for slug, p in pages.items():
        cats = p['cats']
        nav = '<p class="sym-jump">' + ''.join(f'<a href="#{slug}-{s}">{esc(n)}</a>' for s, n, xs, _ in cats if xs) + '</p>'
        body = COLLECT + nav + ''.join(f'<h2 id="{slug}-{s}">{esc(n)} <small>{len(xs):,}개</small></h2>{grid(xs, k)}' for s, n, xs, k in cats if xs)
        body += sub_links(slug) + faq_html(p['faq'] + [('특수문자는 어떻게 복사하나요?', '원하는 문자를 누르면 바로 복사되고 위 모음 칸에도 쌓입니다. 여러 개를 고른 뒤 「모음 전체 복사」를 누르면 한 번에 복사됩니다.')])
        body += '<p class="note">PC 특수문자 단축키(자음 + 한자 키)는 <a href="/symbols/#howto">특수문자 모음</a> 페이지에 정리했습니다.</p>'
        changed += write(ROOT / 'symbols' / slug / 'index.html', shell(f'{BASE}/symbols/{slug}/', p['title'], p['desc'], p['kw'], p['h1'], p['lead'], body))
    print(f'특수문자 {total:,}개(기호 {n_sym:,} · 이모지 {n_emoji:,} · 이모티콘 {n_emo:,} · 꾸밈 {n_deco:,}) · 페이지 {1 + len(pages)}개 · 바뀐 파일 {changed}개')


if __name__ == '__main__':
    main()
