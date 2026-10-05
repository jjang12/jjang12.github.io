"""짱툴 연도별 표 페이지: 달력(holidays/<연도>/), 띠·나이표(age/<연도>/), 연도별 최저임금(hourly/minimum-wage/).

    python3 .github/scripts/build_yearly.py                         # 오늘(KST) 기준
    DDAY_TODAY=2027-01-01 python3 .github/scripts/build_yearly.py   # 다른 날 기준으로 확인

올해와 내년 페이지를 만든다(지난 연도 페이지는 지우지 않고 그대로 둔다). 새해가 되면 다음 해 페이지가 자동으로 생긴다.
dday.yml 이 매일 build_dday.py 와 함께 돌린다. 공휴일·음력 표는 build_dday.py 의 것을 같이 쓴다.
음력 날짜는 assets/vendor/korean-lunar-calendar.min.js 를 node 로 돌려 구한다(GitHub Actions 우분투에 node 있음).
최저임금은 MIN_WAGE 에 손으로 넣는다 — 매년 8월 5일까지 고시되면 다음 해 값을 추가할 것.
"""
import json
import math
import re
import shutil
import subprocess
import sys
import tempfile
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import build_dday as dd   # noqa: E402

ROOT = dd.ROOT
esc = dd.esc
WEEK = dd.WEEK
KST = timezone(timedelta(hours=9))

# 시간급 최저임금(원), 고용노동부 고시
MIN_WAGE = {2010: 4110, 2011: 4320, 2012: 4580, 2013: 4860, 2014: 5210, 2015: 5580, 2016: 6030, 2017: 6470, 2018: 7530,
            2019: 8350, 2020: 8590, 2021: 8720, 2022: 9160, 2023: 9620, 2024: 9860, 2025: 10030, 2026: 10320, 2027: 10700}

STEM = '갑을병정무기경신임계'
STEM_H = '甲乙丙丁戊己庚辛壬癸'
BRANCH = '자축인묘진사오미신유술해'
BRANCH_H = '子丑寅卯辰巳午未申酉戌亥'
ANIMAL = ['쥐', '소', '호랑이', '토끼', '용', '뱀', '말', '양', '원숭이', '닭', '개', '돼지']
COLOR = ['푸른', '푸른', '붉은', '붉은', '노란', '노란', '흰', '흰', '검은', '검은']

TERM_NAMES = ['춘분', '청명', '곡우', '입하', '소만', '망종', '하지', '소서', '대서', '입추', '처서', '백로',
              '추분', '한로', '상강', '입동', '소설', '대설', '동지', '소한', '대한', '입춘', '우수', '경칩']
TERM_FIX = {'2026-춘분': '03-20', '2026-백로': '09-07'}   # 계산 시각이 자정 근처인 것 — 천문연구원 발표로 확인(춘분 23:46, 백로 23:41)


def ganji(y):
    s, b = (y - 4) % 10, (y - 4) % 12
    return dict(name=STEM[s] + BRANCH[b], hanja=STEM_H[s] + BRANCH_H[b], animal=ANIMAL[b], color=COLOR[s])


# ── 24절기: 태양 황경(저정밀 공식, 오차 수 분~12분) ──
def _lon(j):
    t = (j + 69 / 86400 - 2451545.0) / 36525
    l0 = 280.46646 + 36000.76983 * t + 0.0003032 * t * t
    m = math.radians(357.52911 + 35999.05029 * t - 0.0001537 * t * t)
    c = (1.914602 - 0.004817 * t - 0.000014 * t * t) * math.sin(m) + (0.019993 - 0.000101 * t) * math.sin(2 * m) + 0.000289 * math.sin(3 * m)
    return (l0 + c - 0.00569 - 0.00478 * math.sin(math.radians(125.04 - 1934.136 * t))) % 360


def solar_terms(y):
    out = []
    for i, name in enumerate(TERM_NAMES):
        deg = i * 15
        t = datetime(y, 3, 20, tzinfo=timezone.utc) + timedelta(days=i * 15.22)
        if deg >= 285:
            t = datetime(y, 1, 5, tzinfo=timezone.utc) + timedelta(days=(deg - 285) / 15 * 15.0)
        for _ in range(60):
            diff = ((deg - _lon(t.timestamp() / 86400 + 2440587.5) + 180) % 360) - 180
            t += timedelta(days=diff / 0.98564736)
            if abs(diff) < 1e-7:
                break
        k = t.astimezone(KST)
        mins = k.hour * 60 + k.minute
        if f'{y}-{name}' in TERM_FIX:
            day = dd.d(y, TERM_FIX[f'{y}-{name}'])
        else:
            day = k.date()
            if mins < 25 or mins > 1415:
                print(f'주의: {y} {name} 계산 시각 {k:%m-%d %H:%M} — 자정 근처, 천문연구원 발표로 확인해 TERM_FIX 에 넣을 것')
        out.append((day, name))
    return sorted(out)


# ── 음력 (node + korean-lunar-calendar) ──
_LUNAR_CACHE = {}


def lunar_year(y):
    if y in _LUNAR_CACHE:
        return _LUNAR_CACHE[y]
    lib = ROOT / 'assets' / 'vendor' / 'korean-lunar-calendar.min.js'
    with tempfile.TemporaryDirectory() as tmp:
        cjs = Path(tmp) / 'klc.cjs'
        shutil.copy(lib, cjs)
        js = (f"let C=require({json.dumps(str(cjs))});C=C.default||C;const c=new C(),o={{}};"
              f"for(let t=Date.UTC({y},0,1);t<Date.UTC({y + 1},0,1);t+=864e5){{const d=new Date(t);"
              "c.setSolarDate(d.getUTCFullYear(),d.getUTCMonth()+1,d.getUTCDate());const l=c.getLunarCalendar();"
              "o[d.toISOString().slice(0,10)]=[l.month,l.day,l.intercalation?1:0];}console.log(JSON.stringify(o));")
        res = json.loads(subprocess.run(['node', '-e', js], capture_output=True, text=True, check=True).stdout)
    _LUNAR_CACHE[y] = {date.fromisoformat(k): v for k, v in res.items()}
    return _LUNAR_CACHE[y]


# ── 공통 ──
def shell(url, title, desc, kw, h1, lead, body, built):
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
<!-- 이 파일은 .github/scripts/build_yearly.py 가 만든다 — 직접 고치지 말 것 -->
<!-- seo:head -->
<!-- /seo:head -->
</head>
<body data-blog="kkultiplab" data-built="{built}">
<main>
<h1>{esc(h1)}</h1>
<p class="lead">{esc(lead)}</p>
{body}
</main>
<!-- seo:nav -->
<!-- /seo:nav -->
<script src="/assets/site.js"></script>
</body>
</html>
'''


def faq_html(items):
    return '<section class="faq"><h2>자주 묻는 질문</h2>' + ''.join(
        f'<details><summary>{esc(q)}</summary><p>{esc(a)}</p></details>' for q, a in items) + '</section>'


def stats_html(cells):
    return '<div class="dd-stats">' + ''.join(f'<div><b>{a}</b><span>{b}</span></div>' for a, b in cells) + '</div>'


def year_links(base, years, cur, fmt_name):
    return '<ul class="dd-links">' + ''.join(
        f'<li><a href="{base}{y}/"{" aria-current=page" if y == cur else ""}><span>{fmt_name(y)}</span><b>{"보는 중" if y == cur else "보기"}</b></a></li>'
        for y in years) + '</ul>'


def write(path, html_text):
    """build_seo.py 가 채운 head/nav 블록은 그대로 둔다."""
    old = path.read_text(encoding='utf-8') if path.exists() else ''
    new = dd.keep_seo(html_text, old)
    if new != old:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(new, encoding='utf-8')
        return 1
    return 0


# ── 달력 ──
def runs_in(y):
    out, s = [], None
    t = date(y, 1, 1) - timedelta(3)
    while t <= date(y, 12, 31) + timedelta(3):
        if dd.off(t):
            s = s or t
        elif s:
            out.append((s, t - timedelta(1)))
            s = None
        t += timedelta(1)
    return [(a, b) for a, b in out if (b - a).days >= 2 and (a.year == y or b.year == y) and any(x in dd.HOL for x in (a + timedelta(i) for i in range((b - a).days + 1)))]


def run_names(a, b):
    """연휴에 든 공휴일 이름(대체공휴일은 원래 공휴일 이름으로), 날짜 순."""
    out = []
    for i in range((b - a).days + 1):
        n = dd.HOL.get(a + timedelta(i), '')
        for part in n.split(' · '):
            part = re.sub(r'^대체공휴일 \((.*)\)$', r'\1', part).replace(' 연휴', '')
            if part and part not in out:
                out.append(part)
    return out


def bridges(y):
    """평일 하루(연차)로 앞뒤 쉬는 날이 이어지는 경우."""
    out = []
    t = date(y, 1, 1)
    while t.year == y:
        if not dd.off(t) and dd.off(t - timedelta(1)) and dd.off(t + timedelta(1)):
            a, b = dd.run_of(t - timedelta(1))[0], dd.run_of(t + timedelta(1))[1]
            out.append((t, a, b))
        t += timedelta(1)
    return out


def calendar_page(y, today):
    hol = {k: v for k, v in dd.HOL.items() if k.year == y}
    terms = solar_terms(y)
    tmap = {d_: n for d_, n in terms}
    lun = lunar_year(y)
    g = ganji(y)
    weekday_hol = [k for k in hol if k.weekday() < 5]
    subs = sorted(k for k, v in hol.items() if v.startswith('대체'))
    offdays = sum(dd.off(date(y, 1, 1) + timedelta(i)) for i in range((date(y + 1, 1, 1) - date(y, 1, 1)).days))
    long_runs = runs_in(y)
    best = max(long_runs, key=lambda r: (r[1] - r[0]).days) if long_runs else None
    br = bridges(y)

    months = []
    for m in range(1, 13):
        first = date(y, m, 1)
        nxt = date(y + (m == 12), m % 12 + 1, 1)
        cells = ['<td></td>'] * ((first.weekday() + 1) % 7)   # 일요일 시작
        t = first
        while t < nxt:
            lm, ld_, leap = lun[t]
            cls = ['h' if t in hol or t.weekday() == 6 else 's' if t.weekday() == 5 else '']
            if t == today:
                cls.append('today')
            label = (hol.get(t) or tmap.get(t) or '').split(' (')[0]
            lun_txt = f'{"윤" if leap else ""}{lm}.{ld_}'
            cells.append(f'<td class="{" ".join(c for c in cls if c)}"><b>{t.day}</b><small class="lu">{lun_txt}</small>'
                         + (f'<small class="ev{" t" if t not in hol else ""}">{esc(label)}</small>' if label else '') + '</td>')
            t += timedelta(1)
        cells += ['<td></td>'] * (-len(cells) % 7)
        rows = ''.join('<tr>' + ''.join(cells[i:i + 7]) + '</tr>' for i in range(0, len(cells), 7))
        months.append(f'<section class="cal-m"><h3>{m}월</h3><table class="cal"><thead><tr>' +
                      ''.join(f'<th>{w}</th>' for w in '일월화수목금토') + f'</tr></thead><tbody>{rows}</tbody></table></section>')

    hol_rows = ''.join(f'<tr><td>{dd.fmt(k, False)}</td><td>{esc(v)}</td></tr>' for k, v in sorted(hol.items()))
    run_rows = ''.join(f'<tr><td>{dd.fmt(a, a.year != y)} ~ {dd.fmt(b, b.year != y)}</td><td>{(b - a).days + 1}일</td>'
                       f'<td>{esc(" · ".join(run_names(a, b)))}</td></tr>'
                       for a, b in long_runs)
    br_html = ''.join(f'<li>{dd.fmt(t, False)} 연차 → {dd.fmt(a, a.year != y)} ~ {dd.fmt(b, b.year != y)} <b>{(b - a).days + 1}일</b> 쉼</li>' for t, a, b in br)
    term_rows = ''.join(f'<tr><td>{n}</td><td>{dd.fmt(d_, False)}</td></tr>' for d_, n in terms)

    body = (
        f'<div class="panel dd-hero"><p class="dd-label">{y}년 · {g["name"]}년({g["hanja"]}年)</p>'
        f'<div class="dd-num">{len(hol)}일</div><p class="dd-date">{y}년 공휴일 (대체공휴일 {len(subs)}일 포함)</p>'
        f'<p class="note">주말까지 더하면 1년에 {offdays}일 쉽니다</p>'
        f'<p class="no-print" style="margin:14px 0 0"><button type="button" class="btn" onclick="print()">달력 인쇄하기</button></p></div>'
        + stats_html([(f'{len(hol)}일', '공휴일'), (f'{len(weekday_hol)}일', '평일에 쉬는 공휴일'), (f'{len(subs)}일', '대체공휴일'),
                      (f'{(best[1] - best[0]).days + 1}일' if best else '-', '가장 긴 연휴')])
        + '<p class="note">빨간 날짜는 일요일·공휴일, 날짜 밑 작은 숫자는 음력(월.일)입니다. 초록 글씨는 24절기입니다.</p>'
        + f'<h2>{y}년 달력</h2><div class="cal-grid">' + ''.join(months) + '</div>'
        + f'<h2>{y}년 공휴일 목록</h2><div class="tbl-wrap"><table class="list"><thead><tr><th>날짜</th><th>공휴일</th></tr></thead><tbody>{hol_rows}</tbody></table></div>'
        + (f'<p>{y}년 대체공휴일은 ' + ', '.join(f'<b>{dd.fmt(k, False)}</b>({esc(hol[k][7:-1])})' for k in subs) + '입니다.</p>' if subs else '')
        + f'<h2>{y}년 연휴</h2><div class="tbl-wrap"><table class="list"><thead><tr><th>기간</th><th>일수</th><th>공휴일</th></tr></thead><tbody>{run_rows}</tbody></table></div>'
        + (f'<h3>연차 쓰기 좋은 날</h3><ul>{br_html}</ul>' if br else '')
        + f'<h2>{y}년 24절기</h2><div class="tbl-wrap"><table class="list"><thead><tr><th>절기</th><th>날짜</th></tr></thead><tbody>{term_rows}</tbody></table></div>'
        + '<p class="note">절기 날짜는 태양 위치로 계산했습니다. 시각이 자정 가까운 해는 한국천문연구원 발표와 하루 차이가 날 수 있습니다.</p>'
        + faq_html([
            (f'{y}년 공휴일은 모두 며칠인가요?', f'대체공휴일을 포함해 {len(hol)}일이고, 이 가운데 평일에 쉬는 날은 {len(weekday_hol)}일입니다.'),
            (f'{y}년 대체공휴일은 언제인가요?', ', '.join(f'{dd.fmt(k, False)}({hol[k][7:-1]})' for k in subs) + '입니다.' if subs else f'{y}년에는 대체공휴일이 없습니다.'),
            (f'{y}년 가장 긴 연휴는 언제인가요?', f'{dd.fmt(best[0], best[0].year != y)}부터 {dd.fmt(best[1], best[1].year != y)}까지 {(best[1] - best[0]).days + 1}일입니다.' if best else '사흘 이상 이어지는 연휴가 없습니다.'),
            (f'{y}년은 무슨 띠인가요?', f'{y}년은 {g["name"]}년({g["hanja"]}年), {g["color"]} {g["animal"]}의 해입니다.'),
        ])
        + '<h2>다른 연도 달력</h2>' + year_links('/holidays/', CAL_YEARS, y, lambda v: f'{v}년 달력')
        + f'<p class="note">다음 공휴일까지 남은 날은 <a href="/holidays/">공휴일 달력</a>, {y}년 띠별 나이는 <a href="/age/{y}/">{y}년 나이표</a>, '
          '음력 생일은 <a href="/lunar/">음력 양력 변환기</a>에서 확인하세요.</p>'
    )
    return shell(f'https://jjangtool.com/holidays/{y}/',
                 f'{y}년 달력 - 공휴일·대체공휴일·음력·24절기 표시, 인쇄용 달력',
                 f'{y}년 달력에 공휴일 {len(hol)}일과 대체공휴일, 음력 날짜, 24절기를 표시했습니다. {y}년 연휴와 연차 쓰기 좋은 날, 인쇄용 달력까지 한 번에 확인하세요.',
                 f'{y}년 달력, {y} 달력, {y}년 공휴일, {y} 대체공휴일, {y} 음력 달력, {y} 연휴, 인쇄용 달력',
                 f'{y}년 달력 (공휴일·음력·24절기)',
                 f'{y}년 공휴일과 대체공휴일, 음력 날짜, 24절기를 한 번에 보는 달력입니다. 인쇄 버튼으로 바로 출력할 수 있습니다.',
                 body, today)


# ── 띠·나이표 ──
def grade(y, b):
    k = y - b - 6
    if k <= 0:
        return '미취학'
    if k <= 6:
        return f'초등학교 {k}학년'
    if k <= 9:
        return f'중학교 {k - 6}학년'
    if k <= 12:
        return f'고등학교 {k - 9}학년'
    return ''


def note_of(y, b):
    if y - b == 19:
        return '1월 1일부터 술·담배 구입 가능 · 생일부터 만 19세 성년'
    if y - b == 65:
        return '생일부터 만 65세 — 기초연금·경로우대'
    return ''


def age_page(y, today):
    g = ganji(y)
    seol = dd.d(y, dd.LUNAR[y][0]) if y in dd.LUNAR else None
    ipchun = dd.d(y, dd.TERMS[y][0]) if y in dd.TERMS else None
    births = list(range(y, y - 101, -1))
    by_animal = {}
    for b in births:
        by_animal.setdefault((b - 4) % 12, []).append(b)
    cur_b = (y - 4) % 12
    order = [(cur_b + i) % 12 for i in range(12)]
    animal_rows = ''.join(
        f'<tr><td>{ANIMAL[i]}띠</td><td>' + ', '.join('올해 출생' if b == y else f'{b}년생 <small>만 {y - b - 1}~{y - b}세</small>' for b in by_animal[i][:9]) + '</td></tr>'
        for i in order)
    rows = ''.join(
        f'<tr><td>{b}년</td><td>{ganji(b)["name"]} · {ganji(b)["animal"]}띠</td><td>{y - b}세</td>'
        f'<td>{"0세" if b == y else f"{y - b - 1}세 → {y - b}세"}</td><td>{grade(y, b) or esc(note_of(y, b))}</td></tr>'
        for b in births)
    seol_txt = f'설날({dd.fmt(seol, False)})' if seol else '설날'
    ip_txt = f'입춘({dd.fmt(ipchun, False)})' if ipchun else '입춘'
    body = (
        f'<div class="panel dd-hero"><p class="dd-label">{y}년은</p><div class="dd-num" style="font-size:48px">{g["name"]}년</div>'
        f'<p class="dd-date">{g["hanja"]}年 · {g["color"]} {g["animal"]}의 해</p>'
        f'<p class="note">{y}년에 태어난 아이는 {g["animal"]}띠입니다</p></div>'
        f'<p>띠는 보통 음력 새해인 {seol_txt}부터 바뀐다고 봅니다. 사주·명리에서는 {ip_txt}을 기준으로 삼아서, '
        f'1월~2월 초에 태어났다면 전년도 띠({ganji(y - 1)["animal"]}띠)일 수 있습니다.</p>'
        + f'<h2>{y}년 띠별 나이</h2><div class="tbl-wrap"><table class="list ages"><thead><tr><th>띠</th><th>출생연도 (만 나이: 생일 전~후)</th></tr></thead><tbody>{animal_rows}</tbody></table></div>'
        + f'<h2>{y}년 출생연도별 나이표</h2><div class="tbl-wrap"><table class="list"><thead><tr><th>출생연도</th><th>간지·띠</th><th>연 나이</th><th>만 나이 (생일 전→후)</th><th>학년·참고</th></tr></thead><tbody>{rows}</tbody></table></div>'
        + '<p class="note">만 나이는 생일이 지나기 전과 지난 뒤로 나눠 적었습니다. 연 나이는 올해 연도에서 출생연도를 뺀 값으로, 병역·청소년보호법(술·담배)에서 씁니다. '
          '학년은 만 6세가 된 다음 해 3월 입학 기준입니다.</p>'
        + faq_html([
            (f'{y}년은 무슨 띠인가요?', f'{y}년은 {g["name"]}년({g["hanja"]}年)으로 {g["color"]} {g["animal"]}띠의 해입니다.'),
            ('띠는 1월 1일부터 바뀌나요?', f'아니요. 보통 설날부터, 사주에서는 입춘부터 바뀐다고 봅니다. {y}년 1월 1일~{seol_txt} 전에 태어났다면 {ganji(y - 1)["animal"]}띠로 보기도 합니다.'),
            (f'{y}년에 초등학교에 들어가는 아이는 몇 년생인가요?', f'{y - 7}년생입니다. 중학교 입학은 {y - 13}년생, 고등학교 입학은 {y - 16}년생입니다.'),
            ('만 나이는 어떻게 계산하나요?', '올해 연도에서 출생연도를 빼고, 올해 생일이 아직 안 지났으면 1을 더 뺍니다. 정확한 날짜로 계산하려면 만 나이 계산기를 쓰세요.'),
        ])
        + '<h2>다른 연도 나이표</h2>' + year_links('/age/', AGE_YEARS, y, lambda v: f'{v}년 나이표 ({ganji(v)["name"]}년 {ganji(v)["animal"]}띠)')
        + f'<p class="note">생년월일로 정확한 만 나이를 구하려면 <a href="/age/">만 나이 계산기</a>, {y}년 공휴일은 <a href="/holidays/{y}/">{y}년 달력</a>에서 확인하세요.</p>'
    )
    return shell(f'https://jjangtool.com/age/{y}/',
                 f'{y}년 나이표 - {y}년 띠({g["name"]}년 {g["color"]} {g["animal"]}띠), 띠별 나이, 출생연도별 만 나이',
                 f'{y}년은 {g["name"]}년 {g["color"]} {g["animal"]}띠의 해입니다. {y}년 띠별 나이와 출생연도별 만 나이·연 나이, 초중고 학년을 한 표로 정리했습니다.',
                 f'{y}년 나이표, {y}년 띠, {y} 띠별 나이, {g["name"]}년, {g["animal"]}띠 나이, 출생연도별 나이, 만 나이표',
                 f'{y}년 띠·나이표 ({g["name"]}년 {g["animal"]}띠)',
                 f'{y}년 기준 출생연도별 만 나이·연 나이와 띠, 초중고 학년을 한눈에 보는 표입니다.',
                 body, today)


# ── 연도별 최저임금 ──
def wage_page(today):
    years = sorted(MIN_WAGE)
    now_y = max(y for y in years if y <= today.year)
    nxt = today.year + 1 if today.year + 1 in MIN_WAGE else None
    latest = max(years)
    w = MIN_WAGE[now_y]
    month = w * 209
    hero_next = ''
    if nxt:
        left = (date(nxt, 1, 1) - today).days
        hero_next = (f'<p class="note" style="margin-top:12px">{nxt}년 1월 1일부터 <b>{MIN_WAGE[nxt]:,}원</b> '
                     f'(<span data-dd="{date(nxt, 1, 1)}">{dd.ddtxt(left)}</span>, {MIN_WAGE[nxt] - w:,}원 인상)</p>')
    rows = ''
    for y in reversed(years):
        prev = MIN_WAGE.get(y - 1)
        up = f'{MIN_WAGE[y] - prev:,}원 ({(MIN_WAGE[y] / prev - 1) * 100:.1f}%)' if prev else '-'
        rows += f'<tr{" class=past" if y < now_y else ""}><td>{y}년</td><td>{MIN_WAGE[y]:,}원</td><td>{up}</td><td>{MIN_WAGE[y] * 209:,}원</td></tr>'

    def kv(y):
        v = MIN_WAGE[y]
        return (f'<h2>{y}년 최저임금 환산표</h2><div class="tbl-wrap"><table class="kv">'
                f'<tr><th>시급</th><td>{v:,}원</td></tr><tr><th>일급 (8시간)</th><td>{v * 8:,}원</td></tr>'
                f'<tr><th>주급 (40시간 + 주휴 8시간)</th><td>{v * 48:,}원</td></tr>'
                f'<tr><th>월급 (209시간)</th><td>{v * 209:,}원</td></tr><tr><th>연봉 (월급 × 12)</th><td>{v * 209 * 12:,}원</td></tr>'
                f'<tr><th>수습 3개월 (90%)</th><td>시급 {math.ceil(v * 0.9):,}원 · 월 {math.ceil(v * 0.9) * 209:,}원</td></tr></table></div>')
    body = (
        f'<div class="panel dd-hero"><p class="dd-label">{now_y}년 최저시급</p><div class="dd-num">{w:,}원</div>'
        f'<p class="dd-date">월 환산 {month:,}원 (209시간)</p><p class="note"><span data-today>{dd.fmt(today)}</span> 기준</p>{hero_next}</div>'
        + kv(now_y) + (kv(nxt) if nxt else '')
        + f'<h2>연도별 최저임금 ({years[0]}~{latest})</h2><div class="tbl-wrap"><table class="list"><thead><tr><th>연도</th><th>시급</th><th>인상</th><th>월 환산(209시간)</th></tr></thead><tbody>{rows}</tbody></table></div>'
        + f'<p class="note">{years[0]}년 {MIN_WAGE[years[0]]:,}원에서 {latest}년 {MIN_WAGE[latest]:,}원으로 {latest - years[0]}년 동안 {MIN_WAGE[latest] / MIN_WAGE[years[0]]:.1f}배가 됐습니다.</p>'
        + '<h2>계산 기준</h2><div class="note"><p>월 환산액은 주 40시간 일하고 주휴수당(8시간)을 받는 경우의 한 달 209시간((40+8)시간 × 4.345주)으로 계산합니다.</p>'
          '<p>1년 이상 근로계약을 맺은 수습 근로자는 처음 3개월 동안 최저임금의 90%까지 줄 수 있습니다. 단순노무직은 수습이어도 100%입니다.</p>'
          '<p>최저임금위원회가 매년 7월 무렵 다음 해 최저임금을 의결하고, 고용노동부가 8월 5일까지 고시합니다. 1월 1일부터 적용됩니다.</p></div>'
        + faq_html([
            (f'{latest}년 최저시급은 얼마인가요?', f'시간당 {MIN_WAGE[latest]:,}원이고, 월 환산액(209시간)은 {MIN_WAGE[latest] * 209:,}원입니다.'),
            (f'{now_y}년 최저임금 월급은 얼마인가요?', f'주 40시간 기준 {month:,}원입니다(주휴수당 포함, 세전).'),
            ('최저임금에 주휴수당이 들어가나요?', '시급에는 주휴수당이 들어 있지 않습니다. 주 15시간 이상 일하면 주휴수당을 따로 받고, 월 환산액 209시간에는 주휴시간이 들어 있습니다.'),
            ('수습 기간에는 최저임금을 덜 받나요?', '1년 이상 계약한 경우 처음 3개월은 90%까지 줄 수 있습니다. 단순노무직은 해당하지 않습니다.'),
        ])
        + '<p class="note">내 시급으로 주휴수당·월급을 계산하려면 <a href="/hourly/">시급 · 주휴수당 계산기</a>, 세금을 뺀 실수령액은 '
          '<a href="/salary/">연봉 실수령액 계산기</a>를 쓰세요. 실업급여 하한액도 최저임금으로 정해집니다(<a href="/unemployment/">실업급여 계산기</a>).</p>'
    )
    title = f'{latest} 최저시급 {MIN_WAGE[latest]:,}원 - 연도별 최저임금, 월급 환산액' + (f' ({now_y}년 {w:,}원)' if now_y != latest else '')
    return shell('https://jjangtool.com/hourly/minimum-wage/', title,
                 f'{latest}년 최저임금은 시간당 {MIN_WAGE[latest]:,}원, 월 {MIN_WAGE[latest] * 209:,}원입니다. {years[0]}년부터 연도별 최저시급과 인상률, 일급·주급·월급·연봉 환산액을 정리했습니다.',
                 f'최저시급, 최저임금, {latest} 최저시급, {latest} 최저임금, {now_y} 최저임금, 연도별 최저임금, 최저임금 월급',
                 '최저시급 · 연도별 최저임금',
                 f'{latest}년까지 확정된 최저임금과 일급·주급·월급 환산액, 연도별 인상률을 정리했습니다.',
                 body, today)


def hub_block(path, marker, html_block):
    s = path.read_text(encoding='utf-8')
    block = f'<!-- {marker} -->\n{html_block}\n<!-- /{marker} -->'
    if f'<!-- {marker} -->' in s:
        s2 = re.sub(rf'<!-- {marker} -->.*?<!-- /{marker} -->', lambda _: block, s, flags=re.S)
    elif '<section class="faq">' in s:
        s2 = s.replace('<section class="faq">', block + '\n<section class="faq">', 1)
    else:
        s2 = s.replace('</main>', block + '\n</main>', 1)
    if s2 != s:
        path.write_text(s2, encoding='utf-8')
        return 1
    return 0


def main():
    global CAL_YEARS, AGE_YEARS
    today = dd.today_kst()
    first = 2026
    CAL_YEARS = [y for y in range(first, today.year + 2) if y in dd.LUNAR]
    AGE_YEARS = list(range(first, today.year + 2))
    n = 0
    for y in CAL_YEARS:
        n += write(ROOT / 'holidays' / str(y) / 'index.html', calendar_page(y, today))
    for y in AGE_YEARS:
        n += write(ROOT / 'age' / str(y) / 'index.html', age_page(y, today))
    n += write(ROOT / 'hourly' / 'minimum-wage' / 'index.html', wage_page(today))
    n += hub_block(ROOT / 'holidays' / 'index.html', 'yearly:list', '<h2>연도별 달력</h2>\n' + year_links('/holidays/', CAL_YEARS, None, lambda v: f'{v}년 달력 (공휴일·음력)'))
    n += hub_block(ROOT / 'age' / 'index.html', 'yearly:list', '<h2>연도별 띠·나이표</h2>\n' + year_links('/age/', AGE_YEARS, None, lambda v: f'{v}년 나이표 ({ganji(v)["name"]}년 {ganji(v)["animal"]}띠)'))
    n += hub_block(ROOT / 'hourly' / 'index.html', 'yearly:list',
                   f'<h2>연도별 최저임금</h2>\n<p><a href="/hourly/minimum-wage/">{max(MIN_WAGE)}년 최저시급 {MIN_WAGE[max(MIN_WAGE)]:,}원과 연도별 최저임금·월급 환산표 보기</a></p>')
    print(f'{today} 기준 연도별 페이지 — 달력 {CAL_YEARS}, 나이표 {AGE_YEARS}, 최저임금 · 바뀐 파일 {n}개')


CAL_YEARS, AGE_YEARS = [], []

if __name__ == '__main__':
    main()
