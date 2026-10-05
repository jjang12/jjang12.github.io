"""짱툴 D-day 페이지: dday/<slug>/index.html 과 날짜 계산기(/dday/)의 「주요 D-day」 목록을 만든다.

    python3 .github/scripts/build_dday.py                         # 오늘(KST) 기준
    DDAY_TODAY=2026-11-20 python3 .github/scripts/build_dday.py   # 다른 날 기준으로 확인

매일 0시(KST)에 GitHub Actions(dday.yml)가 돌려 남은 날 수·주말 수·진행률을 HTML 본문에 새로 써 넣는다
(검색 로봇은 자바스크립트로 그린 숫자를 잘 못 읽어서). 그다음 build_seo.py 가 head·사이트맵·RSS 를 맞춘다.
보는 사람의 날짜가 만든 날과 다르면 site.js 가 [data-dd] 숫자만 고쳐 보여 준다.

설·추석·부처님오신날(음력)은 korean-lunar-calendar(한국천문연구원 기준), 절기는 태양 황경 계산으로 미리 구해 표로 넣었다
(2025~2035, 절기 시각이 자정 30분 안쪽인 해는 없음). 2035년이 오기 전에 표를 늘릴 것.
"""
import html
import os
import re
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
WEEK = '월화수목금토일'   # date.weekday() 순서

# 음력 공휴일 양력 날짜: (설날, 부처님오신날, 추석)
LUNAR = {
    2025: ('01-29', '05-05', '10-06'), 2026: ('02-17', '05-24', '09-25'), 2027: ('02-07', '05-13', '09-15'),
    2028: ('01-27', '05-02', '10-03'), 2029: ('02-13', '05-20', '09-22'), 2030: ('02-03', '05-09', '09-12'),
    2031: ('01-23', '05-28', '10-01'), 2032: ('02-11', '05-16', '09-19'), 2033: ('01-31', '05-06', '09-08'),
    2034: ('02-19', '05-25', '09-27'), 2035: ('02-08', '05-15', '09-16'),
}
# 절기(한국 시각 날짜): (입춘, 하지, 입추, 동지)
TERMS = {
    2025: ('02-03', '06-21', '08-07', '12-22'), 2026: ('02-04', '06-21', '08-07', '12-22'), 2027: ('02-04', '06-21', '08-08', '12-22'),
    2028: ('02-04', '06-21', '08-07', '12-21'), 2029: ('02-03', '06-21', '08-07', '12-21'), 2030: ('02-04', '06-21', '08-07', '12-22'),
    2031: ('02-04', '06-21', '08-08', '12-22'), 2032: ('02-04', '06-21', '08-07', '12-21'), 2033: ('02-03', '06-21', '08-07', '12-21'),
    2034: ('02-04', '06-21', '08-07', '12-22'), 2035: ('02-04', '06-21', '08-08', '12-22'),
}
DONGJI_LUNAR_DAY = {2026: 14, 2027: 25, 2028: 6, 2029: 17, 2030: 28, 2031: 9, 2032: 19, 2033: 30, 2034: 12, 2035: 23}
# 수능: 학년도 → 시행일 (다음 학년도는 교육부 발표 뒤 추가)
SUNEUNG = {2023: '2022-11-17', 2024: '2023-11-16', 2025: '2024-11-14', 2026: '2025-11-13', 2027: '2026-11-19'}
SUNEUNG_SCORE = {2027: '2026-12-11'}
ELECTIONS = {'2028-04-12': '제23대 국회의원 선거'}
EXTRA_HOLIDAYS = {'2026-06-03': '전국동시지방선거', '2028-04-12': '국회의원 선거'}
YEARS = range(min(LUNAR), max(LUNAR) + 1)


def d(y, md):
    return date(y, *map(int, md.split('-')))


def iso(s):
    return date.fromisoformat(s)


def fmt(t, year=True):
    return f"{f'{t.year}년 ' if year else ''}{t.month}월 {t.day}일({WEEK[t.weekday()]})"


def ddtxt(n):
    return 'D-day' if n == 0 else f'D-{n:,}' if n > 0 else f'D+{-n:,}'


esc = html.escape


# ── 공휴일 (holidays/index.html 의 규칙과 같게) ──
def holidays(y):
    if y not in LUNAR:
        return {}
    m = {}

    def add(t, name):
        m[t] = m[t] + ' · ' + name if t in m else name
    rules = []
    for mo, da, name, sub in [(1, 1, '신정', 0), (3, 1, '3·1절', 1), (5, 5, '어린이날', 1), (6, 6, '현충일', 0), (7, 17, '제헌절', 1 if y >= 2026 else -1),
                              (8, 15, '광복절', 1), (10, 3, '개천절', 1), (10, 9, '한글날', 1), (12, 25, '성탄절', 1)]:
        if sub < 0:
            continue
        add(date(y, mo, da), name)
        if sub:
            rules.append(([date(y, mo, da)], name, 'weekend'))
    seol, budda, chu = (d(y, x) for x in LUNAR[y])
    one = timedelta(1)
    sd, cd = [seol - one, seol, seol + one], [chu - one, chu, chu + one]
    for i, t in enumerate(sd):
        add(t, '설날' if i == 1 else '설날 연휴')
    for i, t in enumerate(cd):
        add(t, '추석' if i == 1 else '추석 연휴')
    add(budda, '부처님오신날')
    rules += [(sd, '설날', 'sunday'), (cd, '추석', 'sunday'), ([budda], '부처님오신날', 'weekend')]
    for k, name in EXTRA_HOLIDAYS.items():
        if k.startswith(str(y)):
            add(iso(k), name)
    base = dict(m)
    for days, name, rule in rules:
        need = any((rule == 'weekend' and t.weekday() >= 5) or (rule == 'sunday' and t.weekday() == 6) or ' · ' in base[t] for t in days)
        if not need:
            continue
        t = days[-1] + one
        while t.weekday() >= 5 or t in m:
            t += one
        m[t] = f'대체공휴일 ({name})'
    return m


HOL = {}
for _y in YEARS:
    HOL.update(holidays(_y))


def off(t):
    return t.weekday() >= 5 or t in HOL


def run_of(t):
    """t 를 포함해 이어지는 쉬는 날(주말·공휴일) 묶음."""
    a = b = t
    while off(a - timedelta(1)):
        a -= timedelta(1)
    while off(b + timedelta(1)):
        b += timedelta(1)
    return a, b


# ── 이벤트별 날짜 ──
def fixed(mo, da):
    return lambda: [(date(y, mo, da), str(y)) for y in YEARS]


def lunar_idx(i):
    return lambda: [(d(y, LUNAR[y][i]), str(y)) for y in YEARS]


def term_idx(i):
    return lambda: [(d(y, TERMS[y][i]), str(y)) for y in YEARS]


def black_friday():
    out = []
    for y in YEARS:
        t = date(y, 11, 1)
        t += timedelta((3 - t.weekday()) % 7)        # 11월 첫 목요일
        out.append((t + timedelta(22), str(y)))      # 넷째 목요일 다음 날
    return out


def gyeong(t):   # 천간이 庚 인 날 (2023~2025 복날로 맞춤)
    return (t.toordinal() + 4) % 10 == 6


def bok(y):
    haji, ipchu = d(y, TERMS[y][1]), d(y, TERMS[y][2])
    g = [haji + timedelta(i) for i in range(60) if gyeong(haji + timedelta(i))]
    mal = next(ipchu + timedelta(i) for i in range(10) if gyeong(ipchu + timedelta(i)))
    return g[2], g[3], mal


def boknal():
    out = []
    for y in YEARS:
        for t, nm in zip(bok(y), ('초복', '중복', '말복')):
            out.append((t, f'{y} {nm}'))
    return out


# ── 이벤트별 추가 내용 ──
def x_suneung(c):
    n = int(c['label'][:4])
    score = SUNEUNG_SCORE.get(n)
    rows = [('입실 완료', '08:10'), ('1교시 국어', '08:40 ~ 10:00 (80분)'), ('2교시 수학', '10:30 ~ 12:10 (100분)'), ('점심시간', '12:10 ~ 13:00'),
            ('3교시 영어', '13:10 ~ 14:20 (70분)'), ('4교시 한국사·탐구', '14:50 ~ 16:37'), ('5교시 제2외국어/한문', '17:05 ~ 17:45 (40분)')]
    out = f'<h2>{n}학년도 수능 시간표</h2><div class="tbl-wrap"><table class="kv">' + ''.join(f'<tr><th>{a}</th><td>{b}</td></tr>' for a, b in rows) + '</table></div>'
    out += '<p class="note">최근 수능과 같은 시간표입니다. 시험 당일 세부 안내는 수험표와 교육청 공지를 확인하세요.</p>'
    if score:
        out += f'<p>성적 통지일은 <b>{fmt(iso(score))}</b>이고, 수능 날부터 {(iso(score) - c["target"]).days}일 뒤입니다.</p>'
    if c['dd'] < 0:
        out += f'<p><b>{n + 1}학년도 수능 날짜는 아직 발표 전입니다.</b> 발표되면 이 페이지에 바로 반영합니다.</p>'
    return out


def x_holiday(name):
    def f(c):
        t = c['target']
        a, b = run_of(t)
        days = [a + timedelta(i) for i in range((b - a).days + 1)]
        rows = ''.join(f'<tr><td>{fmt(x, False)}</td><td>{esc(HOL.get(x, "주말"))}</td></tr>' for x in days)
        sub = [x for x in days if HOL.get(x, '').startswith('대체')]
        out = f'<h2>{t.year} {name} 연휴</h2><p>{fmt(a)}부터 {fmt(b)}까지 <b>{len(days)}일</b> 쉽니다' + \
              (f'(대체공휴일 {fmt(sub[0], False)} 포함).' if sub else '.') + '</p>'
        out += f'<div class="tbl-wrap"><table class="list"><thead><tr><th>날짜</th><th>구분</th></tr></thead><tbody>{rows}</tbody></table></div>'
        # 연차 하루로 다른 쉬는 날과 이어지면 알려 준다
        for edge in (a - timedelta(1), b + timedelta(1)):
            if off(edge):
                continue
            nb = edge - timedelta(1) if edge < a else edge + timedelta(1)
            if off(nb):
                aa, bb = (run_of(nb)[0], b) if edge < a else (a, run_of(nb)[1])
                out += f'<p class="note">연차 하루({fmt(edge, False)})를 쓰면 {fmt(aa, False)}부터 {fmt(bb, False)}까지 {(bb - aa).days + 1}일 쉴 수 있습니다.</p>'
        return out
    return f


def x_dongji(c):
    t = c['target']
    ld = DONGJI_LUNAR_DAY.get(t.year)
    if not ld:
        return ''
    kind = '애동지' if ld <= 10 else '중동지' if ld <= 20 else '노동지'
    food = '팥죽 대신 팥시루떡을 먹는 해' if kind == '애동지' else '팥죽을 먹는 해'
    return f'<h2>{t.year}년 동지는 {kind}</h2><p>{t.year}년 동지는 음력 11월 {ld}일입니다. 음력 11월 10일 안쪽이면 애동지, 20일 안쪽이면 중동지, 그 뒤면 노동지라고 부르며, 올해는 {food}입니다.</p>'


def x_bok(c):
    y = c['target'].year
    out = '<h2>연도별 초복·중복·말복</h2><div class="tbl-wrap"><table class="list"><thead><tr><th>연도</th><th>초복</th><th>중복</th><th>말복</th></tr></thead><tbody>'
    for yy in (y - 1, y, y + 1):
        if yy in TERMS:
            cho, jung, mal = bok(yy)
            out += f'<tr><td>{yy}</td><td>{fmt(cho, False)}</td><td>{fmt(jung, False)}</td><td>{fmt(mal, False)}{" · 월복" if (mal - jung).days == 20 else ""}</td></tr>'
    return out + '</tbody></table></div><p class="note">월복: 중복과 말복 사이가 20일로 벌어지는 해입니다.</p>'


def x_blackfriday(c):
    t = c['target']
    return (f'<p>{t.year}년 사이버먼데이는 <b>{fmt(t + timedelta(3))}</b>입니다. 미국 쇼핑몰 할인은 미국 시간 기준이라 한국 시간으로는 '
            '반나절쯤 늦게 시작합니다.</p><p>해외 직구 전에는 <a href="/customs/">관세 계산기</a>로 면세 한도와 관부가세를, '
            '<a href="/exchange/">환율 계산기</a>로 원화 금액을 미리 확인해 두면 좋습니다.</p>')


def x_election(c):
    t = c['target']
    pre = t - timedelta(5)
    return (f'<p>사전투표는 선거일 5일 전부터 이틀 동안인 <b>{fmt(pre, False)}~{fmt(pre + timedelta(1), False)}</b>, '
            '오전 6시부터 오후 6시까지입니다. 선거일 당일 투표 시간도 오전 6시~오후 6시입니다.</p>')


# ── 이벤트 목록 ──
# title/h1/lead/desc 의 {y} 는 다가오는 날의 연도, {label} 은 표의 이름(수능은 학년도)
EVENTS = [
    dict(slug='suneung', name='수능', dates=lambda: [(iso(v), f'{k}학년도') for k, v in SUNEUNG.items()],
         title='{label} 수능 D-day - 수능까지 남은 날, 수능 날짜·시간표', h1='{label} 수능 D-day',
         lead='수능까지 남은 날을 매일 새로 계산하고, 시험 시간표와 성적 통지일을 정리했습니다.',
         desc='{label} 수능은 {date}입니다. 수능까지 남은 날, 남은 주말·평일 수, 수능 시간표와 성적 통지일을 매일 갱신해 보여 줍니다.',
         kw='수능 디데이, 수능 D-day, 수능 날짜, {label} 수능, 수능까지 남은 날, 수능 시간표', extra=x_suneung,
         about=['대학수학능력시험(수능)은 매년 11월 셋째 주 목요일 전후에 치러지고, 교육부가 시행일을 미리 발표합니다.',
                '수능 날에는 관공서·기업 출근 시간이 늦춰지고, 듣기 평가 시간에는 비행기 이착륙도 멈춥니다.'],
         faq=lambda c: [('수능은 언제인가요?', f'{c["label"]} 수능은 {fmt(c["target"])}입니다.'),
                        ('수능 시험은 몇 시에 시작하나요?', '오전 8시 10분까지 입실하고, 1교시 국어가 8시 40분에 시작합니다. 제2외국어/한문을 보면 오후 5시 45분에 끝납니다.'),
                        ('수능 D-day 는 오늘을 포함해서 세나요?', '오늘은 빼고 수능 당일까지 남은 날 수입니다. 수능 당일이 D-day 입니다.')]),
    dict(slug='seollal', name='설날', dates=lunar_idx(0),
         title='{y} 설날 D-day - 설날까지 남은 날, {y} 설 연휴 기간', h1='{y} 설날 D-day',
         lead='설날까지 남은 날과 설 연휴 기간, 대체공휴일, 연차 쓰기 좋은 날을 정리했습니다.',
         desc='{y} 설날은 {date}입니다. 설날까지 남은 날과 설 연휴 기간, 대체공휴일, 연차 하루로 더 길게 쉬는 방법을 매일 갱신해 보여 줍니다.',
         kw='설날 디데이, 설날 D-day, {y} 설날, 설 연휴, {y} 설 연휴, 설날까지 남은 날', extra=x_holiday('설'),
         about=['설날은 음력 1월 1일이고, 앞뒤 하루씩 더해 사흘이 공휴일입니다.',
                '설 연휴가 일요일이나 다른 공휴일과 겹치면 연휴 다음 첫 평일이 대체공휴일이 됩니다(토요일과 겹치는 것은 해당하지 않음).'],
         faq=lambda c: [(f'{c["target"].year} 설날은 언제인가요?', f'{fmt(c["target"])}입니다. 음력 1월 1일입니다.'),
                        ('설 연휴에 대체공휴일이 생기나요?', '설 연휴 사흘 가운데 하루가 일요일이나 다른 공휴일과 겹치면 연휴 다음 평일 하루가 대체공휴일이 됩니다.')]),
    dict(slug='chuseok', name='추석', dates=lunar_idx(2),
         title='{y} 추석 D-day - 추석까지 남은 날, {y} 추석 연휴 기간', h1='{y} 추석 D-day',
         lead='추석까지 남은 날과 추석 연휴 기간, 대체공휴일, 연차 쓰기 좋은 날을 정리했습니다.',
         desc='{y} 추석은 {date}입니다. 추석까지 남은 날과 추석 연휴 기간, 대체공휴일, 연차 하루로 더 길게 쉬는 방법을 매일 갱신해 보여 줍니다.',
         kw='추석 디데이, 추석 D-day, {y} 추석, 추석 연휴, {y} 추석 연휴, 추석까지 남은 날', extra=x_holiday('추석'),
         about=['추석은 음력 8월 15일이고, 앞뒤 하루씩 더해 사흘이 공휴일입니다.',
                '추석 연휴가 일요일이나 개천절 같은 다른 공휴일과 겹치면 연휴 다음 첫 평일이 대체공휴일이 됩니다.'],
         faq=lambda c: [(f'{c["target"].year} 추석은 언제인가요?', f'{fmt(c["target"])}입니다. 음력 8월 15일입니다.'),
                        ('추석 연휴에 대체공휴일이 생기나요?', '추석 연휴 사흘 가운데 하루가 일요일이나 다른 공휴일과 겹치면 연휴 다음 평일 하루가 대체공휴일이 됩니다.')]),
    dict(slug='christmas', name='크리스마스', dates=fixed(12, 25),
         title='크리스마스 D-day {y} - 크리스마스까지 남은 날', h1='{y} 크리스마스 D-day',
         lead='크리스마스까지 남은 날과 요일, 남은 주말 수를 매일 새로 계산합니다.',
         desc='{y} 크리스마스는 {date}입니다. 크리스마스까지 남은 날과 남은 주말 수, 크리스마스이브 요일을 매일 갱신해 보여 줍니다.',
         kw='크리스마스 디데이, 크리스마스 D-day, 크리스마스까지 남은 날, {y} 크리스마스, 크리스마스 요일',
         extra=lambda c: f'<p>크리스마스이브(12월 24일)는 <b>{WEEK[(c["target"] - timedelta(1)).weekday()]}요일</b>입니다.</p>',
         about=['성탄절(12월 25일)은 법정 공휴일이고, 2023년부터 토·일요일과 겹치면 대체공휴일이 생깁니다.'],
         faq=lambda c: [(f'{c["target"].year} 크리스마스는 무슨 요일인가요?', f'{fmt(c["target"])}입니다.'),
                        ('크리스마스가 주말이면 대체공휴일이 있나요?', '네. 성탄절이 토요일이나 일요일이면 다음 월요일이 대체공휴일입니다.')]),
    dict(slug='newyear', name='새해', dates=fixed(1, 1),
         title='새해 D-day {y} - {y}년 새해까지 남은 날', h1='{y} 새해 D-day',
         lead='새해 첫날까지 남은 날과 올해 남은 주말·평일 수를 매일 새로 계산합니다.',
         desc='{y}년 새해 첫날은 {date}입니다. 새해까지 남은 날과 올해 남은 주말·평일 수를 매일 갱신해 보여 줍니다.',
         kw='새해 디데이, 새해 D-day, 새해까지 남은 날, {y} 새해, 올해 남은 날', extra=None,
         about=['1월 1일(신정)은 공휴일이지만 대체공휴일은 적용되지 않습니다.'],
         faq=lambda c: [('올해는 며칠 남았나요?', f'오늘을 포함해 새해 전날까지 {c["dd"]}일 남았습니다.'),
                        ('신정이 주말이면 대체공휴일이 있나요?', '아니요. 1월 1일은 대체공휴일 대상이 아닙니다.')]),
    dict(slug='halloween', name='할로윈', dates=fixed(10, 31),
         title='할로윈 D-day {y} - 할로윈데이까지 남은 날, 날짜·요일', h1='{y} 할로윈 D-day',
         lead='할로윈데이까지 남은 날과 요일, 남은 주말 수를 매일 새로 계산합니다.',
         desc='{y} 할로윈데이는 {date}입니다. 할로윈까지 남은 날과 요일, 남은 주말 수를 매일 갱신해 보여 줍니다.',
         kw='할로윈 디데이, 할로윈데이, 할로윈 날짜, {y} 할로윈, 할로윈까지 남은 날', extra=None,
         about=['할로윈은 매년 10월 31일이고, 켈트족의 가을 축제에서 시작된 서양 풍습입니다. 한국에서는 공휴일이 아닙니다.'],
         faq=lambda c: [(f'{c["target"].year} 할로윈은 무슨 요일인가요?', f'{fmt(c["target"])}입니다.'),
                        ('할로윈은 공휴일인가요?', '아니요. 한국에서는 공휴일이 아닙니다.')]),
    dict(slug='pepero', name='빼빼로데이', dates=fixed(11, 11),
         title='빼빼로데이 D-day {y} - 빼빼로데이까지 남은 날, 날짜·요일', h1='{y} 빼빼로데이 D-day',
         lead='빼빼로데이까지 남은 날과 요일을 매일 새로 계산합니다.',
         desc='{y} 빼빼로데이는 {date}입니다. 빼빼로데이까지 남은 날과 요일, 남은 주말 수를 매일 갱신해 보여 줍니다.',
         kw='빼빼로데이 디데이, 빼빼로데이 날짜, {y} 빼빼로데이, 빼빼로데이까지 남은 날', extra=None,
         about=['빼빼로데이는 매년 11월 11일입니다. 같은 날은 농업인의 날이기도 해서 가래떡데이라고도 부릅니다.'],
         faq=lambda c: [(f'{c["target"].year} 빼빼로데이는 무슨 요일인가요?', f'{fmt(c["target"])}입니다.'),
                        ('11월 11일은 다른 기념일도 있나요?', '농업인의 날이라 가래떡을 나누는 가래떡데이로도 알려져 있습니다.')]),
    dict(slug='valentine', name='발렌타인데이', dates=fixed(2, 14),
         title='발렌타인데이 D-day {y} - 발렌타인데이까지 남은 날, 날짜·요일', h1='{y} 발렌타인데이 D-day',
         lead='발렌타인데이까지 남은 날과 요일을 매일 새로 계산합니다.',
         desc='{y} 발렌타인데이는 {date}입니다. 발렌타인데이까지 남은 날과 요일, 화이트데이 날짜를 매일 갱신해 보여 줍니다.',
         kw='발렌타인데이 디데이, 발렌타인데이 날짜, {y} 발렌타인데이, 발렌타인데이까지 남은 날', extra=None,
         about=['발렌타인데이는 매년 2월 14일입니다. 한 달 뒤 3월 14일이 화이트데이, 4월 14일이 블랙데이입니다.'],
         faq=lambda c: [(f'{c["target"].year} 발렌타인데이는 무슨 요일인가요?', f'{fmt(c["target"])}입니다.'),
                        ('화이트데이는 언제인가요?', f'발렌타인데이 한 달 뒤인 {c["target"].year}년 3월 14일({WEEK[date(c["target"].year, 3, 14).weekday()]})입니다.')]),
    dict(slug='whiteday', name='화이트데이', dates=fixed(3, 14),
         title='화이트데이 D-day {y} - 화이트데이까지 남은 날, 날짜·요일', h1='{y} 화이트데이 D-day',
         lead='화이트데이까지 남은 날과 요일을 매일 새로 계산합니다.',
         desc='{y} 화이트데이는 {date}입니다. 화이트데이까지 남은 날과 요일, 남은 주말 수를 매일 갱신해 보여 줍니다.',
         kw='화이트데이 디데이, 화이트데이 날짜, {y} 화이트데이, 화이트데이까지 남은 날', extra=None,
         about=['화이트데이는 매년 3월 14일로, 발렌타인데이 한 달 뒤입니다. 일본에서 시작된 기념일입니다.'],
         faq=lambda c: [(f'{c["target"].year} 화이트데이는 무슨 요일인가요?', f'{fmt(c["target"])}입니다.'),
                        ('블랙데이는 언제인가요?', '화이트데이 한 달 뒤인 4월 14일입니다.')]),
    dict(slug='blackfriday', name='블랙프라이데이', dates=black_friday,
         title='블랙프라이데이 {y} 날짜 - 블프까지 남은 날, 사이버먼데이', h1='{y} 블랙프라이데이 D-day',
         lead='블랙프라이데이까지 남은 날과 사이버먼데이 날짜, 직구 전에 확인할 것을 정리했습니다.',
         desc='{y} 블랙프라이데이는 {date}입니다. 블프까지 남은 날과 사이버먼데이 날짜, 직구 관세·환율 확인 방법을 매일 갱신해 보여 줍니다.',
         kw='블랙프라이데이, 블랙프라이데이 날짜, {y} 블랙프라이데이, 블프 디데이, 사이버먼데이', extra=x_blackfriday,
         about=['블랙프라이데이는 미국 추수감사절(11월 넷째 목요일) 다음 날인 금요일로, 미국에서 가장 큰 할인 행사가 열립니다.'],
         faq=lambda c: [(f'{c["target"].year} 블랙프라이데이는 언제인가요?', f'{fmt(c["target"])}입니다.'),
                        ('직구 면세 한도는 얼마인가요?', '목록통관 물품은 150달러, 미국에서 오는 물품은 200달러까지 관세·부가세가 면제됩니다(일반 통관은 150달러).')]),
    dict(slug='dongji', name='동지', dates=term_idx(3),
         title='{y} 동지 날짜 - 동지까지 남은 날, 애동지·팥죽', h1='{y} 동지 D-day',
         lead='동지까지 남은 날과 올해가 애동지·중동지·노동지 가운데 어느 해인지 정리했습니다.',
         desc='{y} 동지는 {date}입니다. 동지까지 남은 날과 애동지·중동지·노동지 구분, 팥죽 먹는 해인지 매일 갱신해 보여 줍니다.',
         kw='동지, 동지 날짜, {y} 동지, 동짓날, 애동지, 동지 팥죽', extra=x_dongji,
         about=['동지는 24절기 가운데 22번째로, 1년 중 밤이 가장 긴 날입니다. 팥죽을 쑤어 먹으며 나쁜 기운을 쫓는 풍습이 있습니다.'],
         faq=lambda c: [(f'{c["target"].year} 동지는 언제인가요?', f'{fmt(c["target"])}입니다.'),
                        ('애동지에는 왜 팥죽을 안 먹나요?', '동지가 음력 11월 초순에 들면 아이들에게 좋지 않다고 해서 팥죽 대신 팥시루떡을 먹는 풍습이 있습니다.')]),
    dict(slug='ipchun', name='입춘', dates=term_idx(0),
         title='{y} 입춘 날짜 - 입춘까지 남은 날, 입춘대길 뜻', h1='{y} 입춘 D-day',
         lead='입춘까지 남은 날과 입춘첩(입춘대길) 붙이는 풍습을 정리했습니다.',
         desc='{y} 입춘은 {date}입니다. 입춘까지 남은 날과 입춘대길·건양다경 뜻, 입춘첩 붙이는 때를 매일 갱신해 보여 줍니다.',
         kw='입춘, 입춘 날짜, {y} 입춘, 입춘대길, 입춘첩', extra=None,
         about=['입춘은 24절기의 첫째로 봄이 시작된다는 날입니다.',
                '대문에 「입춘대길 건양다경」(봄이 오니 크게 길하고, 경사가 많기를)이라고 쓴 입춘첩을 붙이는 풍습이 있습니다.'],
         faq=lambda c: [(f'{c["target"].year} 입춘은 언제인가요?', f'{fmt(c["target"])}입니다.'),
                        ('입춘대길 건양다경은 무슨 뜻인가요?', '봄이 시작되니 크게 길하고, 따뜻한 기운이 도니 경사스러운 일이 많기를 바란다는 뜻입니다.')]),
    dict(slug='boknal', name='복날', dates=boknal,
         title='{y} 복날 날짜 - 초복·중복·말복까지 남은 날', h1='{y} 복날 D-day (초복·중복·말복)',
         lead='다가오는 복날까지 남은 날과 초복·중복·말복 날짜를 정리했습니다.',
         desc='{label}은 {date}입니다. 초복·중복·말복 날짜와 다음 복날까지 남은 날, 복날 정하는 방법을 매일 갱신해 보여 줍니다.',
         kw='복날, 초복, 중복, 말복, {y} 복날, 초복 날짜, 말복 날짜', extra=x_bok, table=False,
         about=['초복은 하지 뒤 셋째 경일(庚日), 중복은 넷째 경일, 말복은 입추 뒤 첫 경일입니다. 경일은 10일마다 돌아와서 해마다 날짜가 달라집니다.'],
         faq=lambda c: [('다음 복날은 언제인가요?', f'{c["label"]}로 {fmt(c["target"])}입니다.'),
                        ('월복이 뭔가요?', '중복과 말복 사이가 10일이 아니라 20일로 벌어지는 해를 월복이라고 합니다.')]),
    dict(slug='childrens-day', name='어린이날', dates=fixed(5, 5),
         title='어린이날 D-day {y} - 어린이날까지 남은 날, 대체공휴일', h1='{y} 어린이날 D-day',
         lead='어린이날까지 남은 날과 요일, 대체공휴일 여부를 매일 새로 계산합니다.',
         desc='{y} 어린이날은 {date}입니다. 어린이날까지 남은 날과 대체공휴일 여부, 5월 연휴를 매일 갱신해 보여 줍니다.',
         kw='어린이날 디데이, 어린이날, {y} 어린이날, 어린이날 대체공휴일', extra=x_holiday('어린이날'),
         about=['어린이날(5월 5일)은 공휴일이고, 토·일요일이나 다른 공휴일과 겹치면 다음 평일이 대체공휴일입니다.'],
         faq=lambda c: [(f'{c["target"].year} 어린이날은 무슨 요일인가요?', f'{fmt(c["target"])}입니다.'),
                        ('어린이날 대체공휴일은 언제 생기나요?', '어린이날이 토요일·일요일이거나 부처님오신날 같은 다른 공휴일과 겹치면 다음 평일이 대체공휴일입니다.')]),
    dict(slug='parents-day', name='어버이날', dates=fixed(5, 8),
         title='어버이날 D-day {y} - 어버이날까지 남은 날, 날짜·요일', h1='{y} 어버이날 D-day',
         lead='어버이날까지 남은 날과 요일을 매일 새로 계산합니다.',
         desc='{y} 어버이날은 {date}입니다. 어버이날까지 남은 날과 요일, 남은 주말 수를 매일 갱신해 보여 줍니다.',
         kw='어버이날 디데이, 어버이날, {y} 어버이날, 어버이날 공휴일', extra=None,
         about=['어버이날(5월 8일)은 법정 기념일이지만 공휴일은 아닙니다.'],
         faq=lambda c: [(f'{c["target"].year} 어버이날은 무슨 요일인가요?', f'{fmt(c["target"])}입니다.'),
                        ('어버이날은 쉬는 날인가요?', '아니요. 법정 기념일이지만 공휴일은 아닙니다.')]),
    dict(slug='teachers-day', name='스승의날', dates=fixed(5, 15),
         title='스승의날 D-day {y} - 스승의날까지 남은 날, 날짜·요일', h1='{y} 스승의날 D-day',
         lead='스승의날까지 남은 날과 요일을 매일 새로 계산합니다.',
         desc='{y} 스승의날은 {date}입니다. 스승의날까지 남은 날과 요일, 남은 주말 수를 매일 갱신해 보여 줍니다.',
         kw='스승의날 디데이, 스승의날, {y} 스승의날, 스승의날 날짜', extra=None,
         about=['스승의날(5월 15일)은 세종대왕 탄신일에서 날짜를 따온 법정 기념일이고, 공휴일은 아닙니다.'],
         faq=lambda c: [(f'{c["target"].year} 스승의날은 무슨 요일인가요?', f'{fmt(c["target"])}입니다.'),
                        ('스승의날은 왜 5월 15일인가요?', '세종대왕 탄신일을 스승의날로 정했습니다.')]),
    dict(slug='election', name='총선', dates=lambda: [(iso(k), v) for k, v in ELECTIONS.items()],
         title='{y} 총선 D-day - {label} 날짜, 사전투표 기간', h1='{y} 총선 D-day ({label})',
         lead='국회의원 선거까지 남은 날과 사전투표 기간, 투표 시간을 정리했습니다.',
         desc='{label}는 {date}입니다. 총선까지 남은 날과 사전투표 기간, 투표 시간을 매일 갱신해 보여 줍니다.',
         kw='총선, 총선 디데이, {y} 총선, 국회의원 선거, 총선 날짜, 사전투표', extra=x_election,
         about=['국회의원 선거일은 공휴일입니다. 국회의원 임기는 4년이라 총선도 4년마다 4월에 치러집니다.'],
         faq=lambda c: [('다음 총선은 언제인가요?', f'{c["label"]}로 {fmt(c["target"])}입니다.'),
                        ('선거일은 쉬는 날인가요?', '네. 선거일은 공휴일입니다.')]),
]


def today_kst():
    if os.environ.get('DDAY_TODAY'):
        return iso(os.environ['DDAY_TODAY'])
    return datetime.now(timezone(timedelta(hours=9))).date()


def context(ev, today):
    ds = sorted(ev['dates']())
    nxt = [x for x in ds if x[0] >= today]
    t, label = nxt[0] if nxt else ds[-1]
    prev = [x for x in ds if x[0] < t]
    return dict(target=t, label=label, dd=(t - today).days, prev=prev[-1] if prev else None, rows=ds, today=today)


def stats(today, t):
    if t <= today:
        return ''
    days = [today + timedelta(i) for i in range((t - today).days)]
    wk = sum(x.weekday() >= 5 for x in days)
    hol = sum(x.weekday() < 5 and x in HOL for x in days)
    n = len(days)
    cells = [(f'{n:,}일', '남은 날'), (f'{n // 7}주 {n % 7}일', '주 단위'), (f'{wk}일', '남은 주말(토·일)'), (f'{n - wk - hol}일', '남은 평일(공휴일 제외)')]
    return '<div class="dd-stats">' + ''.join(f'<div><b>{a}</b><span>{b}</span></div>' for a, b in cells) + '</div>' + \
        '<p class="note">오늘을 넣고 당일은 빼서 셉니다.' + (f' 사이에 평일 공휴일이 {hol}일 있습니다.' if hol else '') + '</p>'


def links(ctxs, skip=None):
    items = sorted((c['dd'] < 0, c['target'], ev) for ev, c in ctxs if ev['slug'] != skip)
    return '<ul class="dd-links">' + ''.join(
        f'<li><a href="/dday/{ev["slug"]}/"><span>{ev["name"]} <small>{fmt(t, False)}</small></span><b data-dd="{t}">{ddtxt((t - ctxs[0][1]["today"]).days)}</b></a></li>'
        for _, t, ev in items) + '</ul>'


def page(ev, c, ctxs):
    t, dd = c['target'], c['dd']
    fill = lambda s: s.format(y=t.year, label=c['label'], date=fmt(t))   # noqa: E731
    title, desc, h1 = fill(ev['title']), fill(ev['desc']), fill(ev['h1'])
    url = f'https://jjangtool.com/dday/{ev["slug"]}/'
    bar = ''
    if c['prev'] and dd > 0:
        p0 = c['prev'][0]
        pct = (c['today'] - p0).days / (t - p0).days * 100
        bar = f'<div class="dd-bar"><i style="width:{pct:.1f}%"></i></div><p class="note">지난 {ev["name"]}({fmt(p0)})부터 {pct:.0f}% 지났습니다</p>'
    lab = c['label'] if any(k in c['label'] for k in ('복', '선거')) else f'{c["label"]} {ev["name"]}'
    hero = (f'<div class="panel dd-hero"><p class="dd-label">{esc(lab)}</p>'
            f'<div class="dd-num" data-dd="{t}">{ddtxt(dd)}</div><p class="dd-date">{fmt(t)}</p>'
            f'<p class="note"><span data-today>{fmt(c["today"])}</span> 기준 · 매일 자동 갱신</p>{bar}</div>')
    rows = ''.join(f'<tr{" class=past" if x < c["today"] else ""}><td>{esc(lb)}</td><td>{fmt(x, False)}</td>'
                   f'<td data-dd="{x}">{"지남" if x < c["today"] else ddtxt((x - c["today"]).days)}</td></tr>'
                   for x, lb in c['rows'] if abs(x.year - t.year) <= 2)
    table = (f'<h2>연도별 {ev["name"]} 날짜</h2><div class="tbl-wrap"><table class="list"><thead><tr><th>구분</th><th>날짜</th><th>남은 날</th></tr></thead>'
             f'<tbody>{rows}</tbody></table></div>')
    about = f'<h2>{ev["name"]} 알아보기</h2>' + ''.join(f'<p>{esc(p)}</p>' for p in ev['about'])
    faq = '<section class="faq"><h2>자주 묻는 질문</h2>' + ''.join(
        f'<details><summary>{esc(q)}</summary><p>{esc(a)}</p></details>' for q, a in ev['faq'](c)) + '</section>'
    more = (f'<h2>다른 D-day</h2>{links(ctxs, ev["slug"])}<p class="note">다른 날짜까지 남은 날은 <a href="/dday/">날짜 계산기</a>로, '
            '올해 쉬는 날은 <a href="/holidays/">공휴일 달력</a>으로 확인하세요.</p>')
    body = hero + stats(c['today'], t) + (ev['extra'](c) if ev['extra'] else '') + (table if ev.get('table', True) else '') + about + faq + more
    a = lambda s: esc(s, quote=True)   # noqa: E731
    return f'''<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{esc(title)}</title>
<meta name="description" content="{a(desc)}">
<meta name="keywords" content="{a(fill(ev["kw"]))}">
<meta property="og:title" content="{a(title)}">
<meta property="og:description" content="{a(desc)}">
<meta property="og:type" content="website">
<meta property="og:url" content="{url}">
<link rel="canonical" href="{url}">
<link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/static/pretendard.min.css">
<link rel="stylesheet" href="/assets/site.css">
<!-- 이 파일은 .github/scripts/build_dday.py 가 매일 만든다 — 직접 고치지 말 것 -->
<!-- seo:head -->
<!-- /seo:head -->
</head>
<body data-blog="kkultiplab" data-built="{c["today"]}">
<main>
<h1>{esc(h1)}</h1>
<p class="lead">{esc(ev["lead"])}</p>
{body}
</main>
<!-- seo:nav -->
<!-- /seo:nav -->
<script src="/assets/site.js"></script>
</body>
</html>
'''


def keep_seo(new, old):
    """build_seo.py 가 채운 head/nav 블록은 그대로 둔다(날짜만 바뀐 날 불필요한 변경을 줄임)."""
    for tag in ('head', 'nav'):
        m = re.search(rf'<!-- seo:{tag} -->.*?<!-- /seo:{tag} -->', old, re.S)
        if m:
            new = re.sub(rf'<!-- seo:{tag} -->.*?<!-- /seo:{tag} -->', lambda _: m.group(0), new, flags=re.S)
    return new


def main():
    today = today_kst()
    ctxs = [(ev, context(ev, today)) for ev in EVENTS]
    changed = 0
    for ev, c in ctxs:
        f = ROOT / 'dday' / ev['slug'] / 'index.html'
        f.parent.mkdir(exist_ok=True)
        old = f.read_text(encoding='utf-8') if f.exists() else ''
        new = keep_seo(page(ev, c, ctxs), old)
        if new != old:
            f.write_text(new, encoding='utf-8')
            changed += 1
    # 날짜 계산기 페이지의 「주요 D-day」 목록
    hub = ROOT / 'dday' / 'index.html'
    s = hub.read_text(encoding='utf-8')
    block = f'<!-- dday:list -->\n<h2>주요 D-day</h2>\n{links(ctxs)}\n<!-- /dday:list -->'
    if '<!-- dday:list -->' in s:
        s2 = re.sub(r'<!-- dday:list -->.*?<!-- /dday:list -->', lambda _: block, s, flags=re.S)
    else:
        s2 = s.replace('<section class="faq">', block + '\n<section class="faq">', 1)
    s2 = re.sub(r'<body([^>]*?)( data-built="[^"]*")?>', lambda m: f'<body{m.group(1)} data-built="{today}">', s2, count=1)
    if s2 != s:
        hub.write_text(s2, encoding='utf-8')
        changed += 1
    print(f'{today} 기준 D-day 페이지 {len(EVENTS)}개 · 바뀐 파일 {changed}개')


if __name__ == '__main__':
    main()
