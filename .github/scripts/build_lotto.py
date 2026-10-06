"""짱툴 로또: 동행복권 회차별 당첨번호를 받아 assets/lotto.json 에 쌓고, lotto/index.html 의 당첨번호 표(정적 HTML)를 새로 쓴다.

    python3 .github/scripts/build_lotto.py

처음엔 1회부터 전부 받고(10회씩 약 125번 요청), 그다음부턴 새 회차만 받는다.
GitHub Actions(lotto.yml)가 토요일 추첨 뒤(21:30 KST)와 일요일 아침에 돌린다.
출처: 동행복권 추첨결과 페이지가 쓰는 /lt645/selectPstLt645InfoNew.do (예전 common.do?method=getLottoNumber 는 2025년 개편으로 막힘).
"""
import html
import json
import re
import ssl
import time
import urllib.request
from collections import Counter
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'assets' / 'lotto.json'
PAGE = ROOT / 'lotto' / 'index.html'
API = 'https://www.dhlottery.co.kr/lt645/selectPstLt645InfoNew.do?srchDir=center&srchLtEpsd={}'
FIRST = date(2002, 12, 7)   # 1회 추첨일
KST = timezone(timedelta(hours=9))
esc = html.escape


def fetch(center):
    req = urllib.request.Request(API.format(center), headers={
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)', 'X-Requested-With': 'XMLHttpRequest',
        'Referer': 'https://www.dhlottery.co.kr/lt645/result', 'Accept': 'application/json'})
    ctx = ssl.create_default_context()
    for i in range(3):
        try:
            with urllib.request.urlopen(req, timeout=20, context=ctx) as r:
                return json.loads(r.read().decode('utf-8'))['data']['list']
        except Exception as e:   # noqa: BLE001
            if i == 2:
                raise
            print(f'  재시도 {center}: {e}')
            time.sleep(2 + i * 3)


def row(x):
    y = x['ltRflYmd']
    return [x['ltEpsd'], f'{y[:4]}-{y[4:6]}-{y[6:]}', x['tm1WnNo'], x['tm2WnNo'], x['tm3WnNo'], x['tm4WnNo'], x['tm5WnNo'], x['tm6WnNo'],
            x['bnsWnNo'], x['rnk1WnNope'], x['rnk1WnAmt'], x.get('rnk2WnNope', 0), x.get('rnk2WnAmt', 0), x.get('rlvtEpsdSumNtslAmt', 0)]


def expected_latest():
    now = datetime.now(KST)
    d = now.date()
    last_sat = d - timedelta((d.weekday() - 5) % 7)
    if last_sat == d and now.hour < 21:   # 토요일 추첨(20:35) 결과는 21시 넘어서
        last_sat -= timedelta(7)
    return (last_sat - FIRST).days // 7 + 1


def update():
    data = json.loads(OUT.read_text(encoding='utf-8')) if OUT.exists() else {'draws': []}
    have = {d[0]: d for d in data['draws']}
    want = expected_latest()
    start = max(have) + 1 if have else 1
    n = start
    while n <= want:
        # center=c 이면 c+4 ~ c-5 회차. 아직 없는 회차를 center 로 주면 빈 목록이라, 최신 회차 근처에선 하나씩 낮춰 본다
        c, got = min(n + 5, want), []
        while c >= n and not got:
            got = fetch(c)
            c -= 1
        if not got:
            break
        for x in got:
            if x.get('ltEpsd') and x.get('tm1WnNo'):
                have[x['ltEpsd']] = row(x)
        n += 10
        time.sleep(0.25)
    draws = [have[k] for k in sorted(have)]
    if draws and draws != data['draws']:
        OUT.write_text(json.dumps({'updated': datetime.now(KST).strftime('%Y-%m-%d %H:%M'), 'draws': draws},
                                  ensure_ascii=False, separators=(',', ':')), encoding='utf-8')
        print(f'로또 {len(draws)}회차 저장 (새로 {len(draws) - len(data["draws"])}회)')
    return draws


def ball(n, cls=''):
    tone = 'y' if n <= 10 else 'b' if n <= 20 else 'r' if n <= 30 else 'g' if n <= 40 else 'n'
    return f'<span class="ball {tone}{cls}">{n}</span>'


def won(v):
    if v >= 1e8:
        eok, man = divmod(round(v / 1e4), 10000)
        return f'{eok:,}억 {man:,}만 원' if man else f'{eok:,}억 원'
    return f'{v:,}원'


def render(draws):
    last = draws[-1]
    n, ymd, nums, bonus = last[0], last[1], last[2:8], last[8]
    recent = draws[-10:][::-1]
    cnt = Counter(x for d in draws for x in d[2:8])
    top = cnt.most_common(10)
    low = sorted(cnt.items(), key=lambda t: (t[1], t[0]))[:6]
    gap = {k: n - max(d[0] for d in draws if k in d[2:8]) for k in range(1, 46)}
    cold = sorted(gap.items(), key=lambda t: -t[1])[:6]
    y, m, dd = ymd.split('-')
    out = (f'<div class="panel lt-latest"><p class="dd-label">제{n:,}회 로또 당첨번호 · {int(y)}년 {int(m)}월 {int(dd)}일 추첨</p>'
           f'<div class="balls big">{"".join(ball(x) for x in nums)}<span class="plus">+</span>{ball(bonus)}</div>'
           f'<p class="note">1등 {last[9]:,}명 · 1인당 <b>{won(last[10])}</b>'
           + (f' · 2등 {last[11]:,}명 · {won(last[12])}' if last[11] else '') + '</p></div>')
    out += ('<h2>최근 10회 당첨번호</h2><div class="tbl-wrap"><table class="list lt-table"><thead><tr><th>회차</th><th>추첨일</th><th>당첨번호</th><th>1등 당첨금</th></tr></thead><tbody>'
            + ''.join(f'<tr><td>{d[0]:,}회</td><td>{d[1][2:].replace("-", ".")}</td><td><span class="balls">{"".join(ball(x) for x in d[2:8])}<span class="plus">+</span>{ball(d[8])}</span></td>'
                      f'<td>{won(d[10])}<small> · {d[9]}명</small></td></tr>' for d in recent)
            + '</tbody></table></div>')
    out += (f'<h2>번호별 통계 (1~{n:,}회)</h2>'
            f'<p>가장 많이 나온 번호: {"".join(ball(k) for k, _ in top)}</p>'
            '<div class="tbl-wrap"><table class="list"><thead><tr><th>번호</th><th>나온 횟수</th><th>비율</th></tr></thead><tbody>'
            + ''.join(f'<tr><td>{ball(k)}</td><td>{v:,}번</td><td>{v / len(draws) * 100:.1f}%</td></tr>' for k, v in top)
            + '</tbody></table></div>'
            f'<p>가장 적게 나온 번호: {" ".join(f"{ball(k)}<small>{v}번</small>" for k, v in low)}</p>'
            f'<p>오래 안 나온 번호: {" ".join(f"{ball(k)}<small>{v}회째</small>" for k, v in cold)}</p>'
            '<p class="note">로또는 회차마다 번호가 새로 뽑혀서 지난 통계가 다음 결과를 바꾸지 않습니다. 재미로만 참고하세요.</p>')
    return out, n, ymd, nums, bonus, last


def write_page(draws):
    s = PAGE.read_text(encoding='utf-8')
    block, n, ymd, nums, bonus, last = render(draws)
    s2 = re.sub(r'<!-- lotto:data -->.*?<!-- /lotto:data -->', lambda _: f'<!-- lotto:data -->\n{block}\n<!-- /lotto:data -->', s, flags=re.S)
    numtxt = ', '.join(map(str, nums))
    title = f'로또 번호 생성기 · {n:,}회 로또 당첨번호 - 자동 번호 뽑기, 당첨 확인, 번호 통계'
    desc = (f'제{n:,}회 로또 당첨번호는 {numtxt} 보너스 {bonus}입니다. 로또 번호 자동 생성(고정수·제외수), 내 번호 당첨 확인, '
            '역대 당첨번호와 번호별 출현 통계를 매주 갱신합니다.')
    s2 = re.sub(r'<title>.*?</title>', f'<title>{esc(title)}</title>', s2, count=1)
    for pat in (r'(<meta name="description" content=")[^"]*', r'(<meta property="og:description" content=")[^"]*'):
        s2 = re.sub(pat, lambda m: m.group(1) + esc(desc, quote=True), s2, count=1)
    s2 = re.sub(r'(<meta property="og:title" content=")[^"]*', lambda m: m.group(1) + esc(title, quote=True), s2, count=1)
    s2 = re.sub(r'<body([^>]*?)( data-built="[^"]*")?>', lambda m: f'<body{m.group(1)} data-built="{ymd}">', s2, count=1)
    # 자주 묻는 질문 중 「이번 회차」 답
    s2 = re.sub(r'(<details data-latest><summary>[^<]*</summary><p>)[^<]*', lambda m: m.group(1) + esc(
        f'제{n:,}회({ymd}) 당첨번호는 {numtxt}, 보너스 번호 {bonus}입니다. 1등은 {last[9]:,}명이 1인당 {won(last[10])}을 받았습니다.'), s2, count=1)
    if s2 != s:
        PAGE.write_text(s2, encoding='utf-8')
        print(f'lotto/index.html 갱신 ({n}회)')


if __name__ == '__main__':
    draws = update()
    if draws:
        write_page(draws)
