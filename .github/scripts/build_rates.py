"""환율 계산기(/exchange/)용 assets/rates.json 을 만든다(표준 라이브러리만).

- 현재 환율: ExchangeRate-API 공개 엔드포인트(open.er-api.com, 키 없음, 하루 1번 갱신, 출처 표시 조건)
- 추이(최근 60일): Frankfurter(유럽중앙은행 기준환율, 영업일만) — ECB 에 없는 통화(VND·TWD 등)는 추이 없이 현재값만
값은 모두 「외화 1단위 = 몇 원」. GitHub Actions(.github/workflows/rates.yml)가 하루 한 번 돌린다.
"""
import json
import sys
import urllib.request
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

OUT = Path(__file__).resolve().parents[2] / 'assets' / 'rates.json'
CURRENCIES = ['USD', 'JPY', 'EUR', 'CNY', 'VND', 'THB', 'TWD', 'PHP', 'HKD', 'GBP', 'AUD', 'CAD', 'SGD', 'CHF', 'NZD', 'MYR', 'IDR', 'MXN']
HISTORY = ['USD', 'JPY', 'EUR', 'CNY', 'THB', 'PHP', 'HKD', 'GBP', 'AUD', 'CAD', 'SGD', 'CHF', 'NZD', 'MYR', 'IDR', 'MXN']   # ECB 에 있는 것만
UA = {'User-Agent': 'Mozilla/5.0 (jjangtool rates builder)'}


def get(url):
    with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=20) as r:
        return json.loads(r.read())


def current():
    d = get('https://open.er-api.com/v6/latest/USD')
    if d.get('result') != 'success':
        raise RuntimeError(d.get('error-type') or 'open.er-api 실패')
    r = d['rates']
    krw = r['KRW']
    return {c: round(krw / r[c], 6) for c in CURRENCIES if c in r}, d.get('time_last_update_utc', '')


def history(days=60):
    start = (date.today() - timedelta(days=days)).isoformat()
    # 원화 기준(from=KRW)으로 받으면 0.00074 처럼 작은 값이 잘려 정밀도가 떨어진다 → 유로 기준으로 받아 나눈다
    others = [c for c in HISTORY if c != 'EUR']
    d = get(f'https://api.frankfurter.dev/v1/{start}..?from=EUR&to=KRW,{",".join(others)}')
    out = {c: [] for c in HISTORY}
    for day in sorted(d.get('rates', {})):
        r = d['rates'][day]
        krw = r.get('KRW')
        if not krw:
            continue
        out['EUR'].append([day, round(krw, 4)])
        for c in others:
            if r.get(c):
                out[c].append([day, round(krw / r[c], 4)])
    return out


def main():
    old = json.loads(OUT.read_text()) if OUT.exists() else {}
    data = {'updated': datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%MZ'), 'source': 'ExchangeRate-API · 유럽중앙은행(Frankfurter)'}
    try:
        data['rates'], data['rates_at'] = current()
    except Exception as e:
        print(f'현재 환율 실패: {e}', file=sys.stderr)
        if not old.get('rates'):
            sys.exit('현재 환율을 못 가져와 파일을 만들지 않습니다.')
        data['rates'], data['rates_at'] = old['rates'], old.get('rates_at', '')
    try:
        data['history'] = history()
    except Exception as e:
        print(f'추이 실패: {e}', file=sys.stderr)
        data['history'] = old.get('history', {})
    if old and old.get('rates') == data['rates'] and old.get('history') == data['history']:
        print('변경 없음')
        return
    OUT.write_text(json.dumps(data, ensure_ascii=False, separators=(',', ':')))
    print(f"환율 {len(data['rates'])}개, 추이 {sum(len(v) for v in data['history'].values())}점 → {OUT}")


if __name__ == '__main__':
    main()
