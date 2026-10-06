/* 사이트 공통 설정: 메뉴·배너·블로그 소개는 여기만 고치면 전체 페이지에 반영됩니다.
   새 도구를 추가할 때는 groups 의 알맞은 묶음에 한 줄 넣고, index.html 카드와 sitemap.xml 에도 추가하세요.
   도구별 '관련 블로그 글'을 고르는 단어는 .github/scripts/build_posts.py 의 TOOLS 에 있습니다. */
const SITE = {
  name: '짱툴',
  groups: [
    {name: '글자·단어', icon: 'type', tone: 'violet', items: [
      {p: '/hanbang/', t: '한방단어', i: 'target'},
      {p: '/wordchain/', t: '끝말잇기 대결', i: 'swords'},
      {p: '/symbols/', t: '특수문자', i: 'omega'},
      {p: '/count/', t: '글자수 세기', i: 'letter-text'},
      {p: '/typo/', t: '한영 변환', i: 'languages'},
      {p: '/romanize/', t: '여권 영문 이름', i: 'book-user'},
      {p: '/fonts/', t: '인스타 글씨체', i: 'case-sensitive'},
      {p: '/tts/', t: '글자 음성 변환(TTS)', i: 'volume-2'},
    ]},
    {name: '이미지·PDF', icon: 'layers', tone: 'sky', items: [
      {p: '/image/', t: '이미지 변환', i: 'image'},
      {p: '/heic/', t: 'HEIC→JPG', i: 'file-image'},
      {p: '/img2pdf/', t: '이미지→PDF', i: 'file-output'},
      {p: '/pdf-merge/', t: 'PDF 합치기', i: 'files'},
      {p: '/pdf2img/', t: 'PDF→JPG', i: 'images'},
      {p: '/qr/', t: 'QR 코드', i: 'qr-code'},
      {p: '/barcode/', t: '바코드 생성기', i: 'barcode'},
    ]},
    {name: '날짜·시간', icon: 'calendar', tone: 'amber', items: [
      {p: '/age/', t: '만 나이', i: 'cake'},
      {p: '/dday/', t: '날짜·D-day', i: 'calendar-days'},
      {p: '/lunar/', t: '음력 양력 변환', i: 'moon'},
      {p: '/holidays/', t: '공휴일 달력', i: 'calendar-heart'},
      {p: '/timer/', t: '타이머·스톱워치', i: 'timer'},
      {p: '/time-calc/', t: '시간 계산기', i: 'clock-plus'},
    ]},
    {name: '월급·세금', icon: 'receipt', tone: 'green', items: [
      {p: '/salary/', t: '연봉 실수령액', i: 'wallet'},
      {p: '/severance/', t: '퇴직금', i: 'briefcase'},
      {p: '/hourly/', t: '시급·주휴수당', i: 'clock'},
      {p: '/unemployment/', t: '실업급여', i: 'hand-coins'},
      {p: '/vat/', t: '부가세', i: 'calculator'},
    ]},
    {name: '대출·금융', icon: 'landmark', tone: 'teal', items: [
      {p: '/loan/', t: '대출 이자', i: 'percent'},
      {p: '/savings/', t: '예금·적금 이자', i: 'piggy-bank'},
      {p: '/dsr/', t: 'DSR·LTV 대출 한도', i: 'gauge'},
      {p: '/exchange/', t: '환율 계산기', i: 'circle-dollar-sign'},
      {p: '/customs/', t: '관세(해외직구)', i: 'plane'},
      {p: '/money/', t: '금액 한글', i: 'banknote'},
      {p: '/liquidation/', t: '청산가·펀딩비', i: 'chart-candlestick'},
    ]},
    {name: '생활', icon: 'house', tone: 'rose', items: [
      {p: '/bmi/', t: 'BMI·비만도', i: 'heart-pulse'},
      {p: '/ovulation/', t: '배란일', i: 'baby'},
      {p: '/pyeong/', t: '평수 변환', i: 'ruler'},
      {p: '/brokerage/', t: '중개보수(복비)', i: 'handshake'},
      {p: '/unit/', t: '단위 변환', i: 'arrow-left-right'},
      {p: '/power/', t: '전기요금', i: 'plug-zap'},
      {p: '/parcel/', t: '택배 조회', i: 'package'},
      {p: '/discount/', t: '할인율·퍼센트', i: 'tag'},
      {p: '/gpa/', t: '학점 계산기', i: 'graduation-cap'},
      {p: '/zipcode/', t: '우편번호·영문주소', i: 'mailbox'},
      {p: '/myip/', t: '내 아이피 확인', i: 'globe'},
    ]},
    {name: '랜덤·게임', icon: 'dices', tone: 'orange', items: [
      {p: '/ladder/', t: '사다리게임', i: 'shuffle'},
      {p: '/lots/', t: '제비뽑기', i: 'ticket'},
      {p: '/lotto/', t: '로또 번호·당첨번호', i: 'clover'},
    ]},
  ],
  blogs: {
    kkultiplab: {url: 'https://blog.naver.com/kkultiplab', name: '생활의 꿀팁정보', tags: ['생활·건강', '정부지원', '여행·축제'],
      desc: '건강, 생활, 정부 지원 제도처럼 일상에 바로 쓰는 정보를 직접 확인해서 정리합니다.'},
    jisik_plus: {url: 'https://blog.naver.com/jisik_plus', name: '짱투의 지식플러스', tags: ['IT기기', '앱·AI', '신차 정보'],
      desc: '스마트폰·PC 활용법, 유용한 앱과 AI, 새로 나온 기기와 자동차 정보를 쉽게 풀어 씁니다.'},
    aicoinlab: {url: 'https://blog.naver.com/aicoinlab', name: '머니버그의 존버노트', tags: ['금리·예적금', '코인', '재테크'],
      desc: '코인·주식·부동산에 직접 투자하며 공부한 시장 이야기와 금리·재테크 정보를 기록합니다.'},
  },
  /* 배너 HTML. 비워 두면('') 그 위치에는 배너가 나오지 않습니다.
     'POSTS' 는 블로그 최신 글 목록(넓은 화면 오른쪽)입니다.
     쿠팡 파트너스 코드를 넣을 때는 아래 coupang 을 true 로 바꾸면 고지 문구가 함께 표시됩니다. */
  banners: {
    top: '',
    right: 'POSTS',
  },
  coupang: false,
  contact: ['kchi1114', 'naver.com'],  // 문의하기 메일 (아이디, 도메인)
};

/* 아이콘: Lucide (ISC License, https://lucide.dev) */
const ICONS = {
  'arrow-left-right': '<path d="M8 3 4 7l4 4"/><path d="M4 7h16"/><path d="m16 21 4-4-4-4"/><path d="M20 17H4"/>',
  'arrow-up-right': '<path d="M7 7h10v10"/><path d="M7 17 17 7"/>',
  'baby': '<path d="M10 16c.5.3 1.2.5 2 .5s1.5-.2 2-.5"/><path d="M15 12h.01"/><path d="M19.38 6.813A9 9 0 0 1 20.8 10.2a2 2 0 0 1 0 3.6 9 9 0 0 1-17.6 0 2 2 0 0 1 0-3.6A9 9 0 0 1 12 3c2 0 3.5 1.1 3.5 2.5s-.9 2.5-2 2.5c-.8 0-1.5-.4-1.5-1"/><path d="M9 12h.01"/>',
  'banknote': '<rect width="20" height="12" x="2" y="6" rx="2"/><circle cx="12" cy="12" r="2"/><path d="M6 12h.01M18 12h.01"/>',
  'barcode': '<path d="M3 5v14"/><path d="M8 5v14"/><path d="M12 5v14"/><path d="M17 5v14"/><path d="M21 5v14"/>',
  'book-user': '<path d="M15 13a3 3 0 1 0-6 0"/><path d="M4 19.5v-15A2.5 2.5 0 0 1 6.5 2H19a1 1 0 0 1 1 1v18a1 1 0 0 1-1 1H6.5a1 1 0 0 1 0-5H20"/><circle cx="12" cy="8" r="2"/>',
  'briefcase': '<path d="M16 20V4a2 2 0 0 0-2-2h-4a2 2 0 0 0-2 2v16"/><rect width="20" height="14" x="2" y="6" rx="2"/>',
  'cake': '<path d="M20 21v-8a2 2 0 0 0-2-2H6a2 2 0 0 0-2 2v8"/><path d="M4 16s.5-1 2-1 2.5 2 4 2 2.5-2 4-2 2.5 2 4 2 2-1 2-1"/><path d="M2 21h20"/><path d="M7 8v3"/><path d="M12 8v3"/><path d="M17 8v3"/><path d="M7 4h.01"/><path d="M12 4h.01"/><path d="M17 4h.01"/>',
  'calculator': '<rect width="16" height="20" x="4" y="2" rx="2"/><line x1="8" x2="16" y1="6" y2="6"/><line x1="16" x2="16" y1="14" y2="18"/><path d="M16 10h.01"/><path d="M12 10h.01"/><path d="M8 10h.01"/><path d="M12 14h.01"/><path d="M8 14h.01"/><path d="M12 18h.01"/><path d="M8 18h.01"/>',
  'calendar': '<path d="M8 2v3"/><path d="M16 2v3"/><rect x="3" y="3" width="18" height="18" rx="2"/><path d="M3 9h18"/>',
  'calendar-days': '<path d="M8 2v3"/><path d="M16 2v3"/><rect x="3" y="3" width="18" height="18" rx="2"/><path d="M3 9h18"/><path d="M8 13h.01"/><path d="M12 13h.01"/><path d="M16 13h.01"/><path d="M8 17h.01"/><path d="M12 17h.01"/><path d="M16 17h.01"/>',
  'calendar-heart': '<path d="M12.127 21H5a2 2 0 01-2-2V5a2 2 0 012-2h14a2 2 0 012 2v5.125"/><path d="M14.62 17.8A2.25 2.25 0 1118 14.836a2.25 2.25 0 113.38 2.966l-2.626 2.856a.998.998 0 01-1.507 0z"/><path d="M16 2v3"/><path d="M3 9h18"/><path d="M8 2v3"/>',
  'case-sensitive': '<path d="m2 16 4.039-9.69a.5.5 0 0 1 .923 0L11 16"/><path d="M22 9v7"/><path d="M3.304 13h6.392"/><circle cx="18.5" cy="12.5" r="3.5"/>',
  'chart-candlestick': '<path d="M9 5v4"/><rect width="4" height="6" x="7" y="9" rx="1"/><path d="M9 15v2"/><path d="M17 3v2"/><rect width="4" height="8" x="15" y="5" rx="1"/><path d="M17 13v3"/><path d="M3 3v16a2 2 0 0 0 2 2h16"/>',
  'chevron-down': '<path d="m6 9 6 6 6-6"/>',
  'chevron-right': '<path d="m9 18 6-6-6-6"/>',
  'circle-dollar-sign': '<circle cx="12" cy="12" r="10"/><path d="M16 8h-6a2 2 0 1 0 0 4h4a2 2 0 1 1 0 4H8"/><path d="M12 18V6"/>',
  'clock': '<circle cx="12" cy="12" r="10"/><path d="M12 6v6l4 2"/>',
  'clock-plus': '<path d="M12 6v6l3.644 1.822"/><path d="M16 19h6"/><path d="M19 16v6"/><path d="M21.92 13.267a10 10 0 1 0-8.653 8.653"/>',
  'clover': '<path d="M16.17 7.83 2 22"/><path d="M4.02 12a2.827 2.827 0 1 1 3.81-4.17A2.827 2.827 0 1 1 12 4.02a2.827 2.827 0 1 1 4.17 3.81A2.827 2.827 0 1 1 19.98 12a2.827 2.827 0 1 1-3.81 4.17A2.827 2.827 0 1 1 12 19.98a2.827 2.827 0 1 1-4.17-3.81A1 1 0 1 1 4 12"/><path d="m7.83 7.83 8.34 8.34"/>',
  'coins': '<path d="M13.744 17.736a6 6 0 1 1-7.48-7.48"/><path d="M15 6h1v4"/><path d="m6.134 14.768.866-.5 2 3.464"/><circle cx="16" cy="8" r="6"/>',
  'dices': '<rect width="12" height="12" x="2" y="10" rx="2" ry="2"/><path d="m17.92 14 3.5-3.5a2.24 2.24 0 0 0 0-3l-5-4.92a2.24 2.24 0 0 0-3 0L10 6"/><path d="M6 18h.01"/><path d="M10 14h.01"/><path d="M15 6h.01"/><path d="M18 9h.01"/>',
  'file-image': '<path d="M6 22a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h8a2.4 2.4 0 0 1 1.704.706l3.588 3.588A2.4 2.4 0 0 1 20 8v12a2 2 0 0 1-2 2z"/><path d="M14 2v5a1 1 0 0 0 1 1h5"/><circle cx="10" cy="12" r="2"/><path d="m20 17-1.296-1.296a2.41 2.41 0 0 0-3.408 0L9 22"/>',
  'file-output': '<path d="M4.226 20.925A2 2 0 0 0 6 22h12a2 2 0 0 0 2-2V8a2.4 2.4 0 0 0-.706-1.706l-3.588-3.588A2.4 2.4 0 0 0 14 2H6a2 2 0 0 0-2 2v3.127"/><path d="M14 2v5a1 1 0 0 0 1 1h5"/><path d="m5 11-3 3"/><path d="m5 17-3-3h10"/>',
  'files': '<path d="M15 2h-4a2 2 0 0 0-2 2v11a2 2 0 0 0 2 2h8a2 2 0 0 0 2-2V8"/><path d="M16.706 2.706A2.4 2.4 0 0 0 15 2v5a1 1 0 0 0 1 1h5a2.4 2.4 0 0 0-.706-1.706z"/><path d="M5 7a2 2 0 0 0-2 2v11a2 2 0 0 0 2 2h8a2 2 0 0 0 1.732-1"/>',
  'gauge': '<path d="m12 14 4-4"/><path d="M3.34 19a10 10 0 1 1 17.32 0"/>',
  'globe': '<circle cx="12" cy="12" r="10"/><path d="M12 2a14.5 14.5 0 0 0 0 20 14.5 14.5 0 0 0 0-20"/><path d="M2 12h20"/>',
  'graduation-cap': '<path d="M21.42 10.922a1 1 0 0 0-.019-1.838L12.83 5.18a2 2 0 0 0-1.66 0L2.6 9.08a1 1 0 0 0 0 1.832l8.57 3.908a2 2 0 0 0 1.66 0z"/><path d="M22 10v6"/><path d="M6 12.5V16a6 3 0 0 0 12 0v-3.5"/>',
  'hand-coins': '<path d="M11 15h2a2 2 0 1 0 0-4h-3c-.6 0-1.1.2-1.4.6L3 17"/><path d="m7 21 1.6-1.4c.3-.4.8-.6 1.4-.6h4c1.1 0 2.1-.4 2.8-1.2l4.6-4.4a2 2 0 0 0-2.75-2.91l-4.2 3.9"/><path d="m2 16 6 6"/><circle cx="16" cy="9" r="2.9"/><circle cx="6" cy="5" r="3"/>',
  'handshake': '<path d="m11 17 2 2a1 1 0 1 0 3-3"/><path d="m14 14 2.5 2.5a1 1 0 1 0 3-3l-3.88-3.88a3 3 0 0 0-4.24 0l-.88.88a1 1 0 1 1-3-3l2.81-2.81a5.79 5.79 0 0 1 7.06-.87l.47.28a2 2 0 0 0 1.42.25L21 4"/><path d="m21 3 1 11h-2"/><path d="M3 3 2 14l6.5 6.5a1 1 0 1 0 3-3"/><path d="M3 4h8"/>',
  'heart-pulse': '<path d="M2 9.5a5.5 5.5 0 0 1 9.591-3.676.56.56 0 0 0 .818 0A5.49 5.49 0 0 1 22 9.5c0 2.29-1.5 4-3 5.5l-5.492 5.313a2 2 0 0 1-3 .019L5 15c-1.5-1.5-3-3.2-3-5.5"/><path d="M3.22 13H9.5l.5-1 2 4.5 2-7 1.5 3.5h5.27"/>',
  'house': '<path d="M15 21v-8a1 1 0 0 0-1-1h-4a1 1 0 0 0-1 1v8"/><path d="M3 10a2 2 0 0 1 .709-1.528l7-6a2 2 0 0 1 2.582 0l7 6A2 2 0 0 1 21 10v9a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/>',
  'id-card': '<path d="M13 19a4 4 0 00-8 0"/><path d="M16 10h2"/><path d="M16 14h2"/><circle cx="9" cy="12" r="3"/><rect x="2" y="5" width="20" height="14" rx="2"/>',
  'image': '<rect width="18" height="18" x="3" y="3" rx="2" ry="2"/><circle cx="9" cy="9" r="2"/><path d="m21 15-3.086-3.086a2 2 0 0 0-2.828 0L6 21"/>',
  'images': '<path d="m22 11-1.296-1.296a2.4 2.4 0 0 0-3.408 0L11 16"/><path d="M4 8a2 2 0 0 0-2 2v10a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2"/><circle cx="13" cy="7" r="1" fill="currentColor"/><rect x="8" y="2" width="14" height="14" rx="2"/>',
  'landmark': '<path d="M10 18v-7"/><path d="M11.119 2.205a2 2 0 0 1 1.762 0l7.84 3.846A.5.5 0 0 1 20.5 7h-17a.5.5 0 0 1-.22-.949z"/><path d="M14 18v-7"/><path d="M18 18v-7"/><path d="M3 22h18"/><path d="M6 18v-7"/>',
  'languages': '<path d="m5 8 6 6"/><path d="m4 14 6-6 2-3"/><path d="M2 5h12"/><path d="M7 2h1"/><path d="m22 22-5-10-5 10"/><path d="M14 18h6"/>',
  'layers': '<path d="M12.83 2.18a2 2 0 0 0-1.66 0L2.6 6.08a1 1 0 0 0 0 1.83l8.58 3.91a2 2 0 0 0 1.66 0l8.58-3.9a1 1 0 0 0 0-1.83z"/><path d="M2 12a1 1 0 0 0 .58.91l8.6 3.91a2 2 0 0 0 1.65 0l8.58-3.9A1 1 0 0 0 22 12"/><path d="M2 17a1 1 0 0 0 .58.91l8.6 3.91a2 2 0 0 0 1.65 0l8.58-3.9A1 1 0 0 0 22 17"/>',
  'letter-text': '<path d="M15 5h6"/><path d="M15 12h6"/><path d="M3 19h18"/><path d="m3 12 3.553-7.724a.5.5 0 0 1 .894 0L11 12"/><path d="M3.92 10h6.16"/>',
  'mail': '<path d="m22 7-8.991 5.727a2 2 0 0 1-2.009 0L2 7"/><rect x="2" y="4" width="20" height="16" rx="2"/>',
  'mailbox': '<path d="M22 17a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V9.5C2 7 4 5 6.5 5H18c2.2 0 4 1.8 4 4v8Z"/><polyline points="15,9 18,9 18,11"/><path d="M6.5 5C9 5 11 7 11 9.5V17a2 2 0 0 1-2 2"/><line x1="6" x2="7" y1="10" y2="10"/>',
  'menu': '<path d="M4 5h16"/><path d="M4 12h16"/><path d="M4 19h16"/>',
  'moon': '<path d="M20.985 12.486a9 9 0 1 1-9.473-9.472c.405-.022.617.46.402.803a6 6 0 0 0 8.268 8.268c.344-.215.825-.004.803.401"/>',
  'omega': '<path d="M3 20h4.5a.5.5 0 0 0 .5-.5v-.282a.52.52 0 0 0-.247-.437 8 8 0 1 1 8.494-.001.52.52 0 0 0-.247.438v.282a.5.5 0 0 0 .5.5H21"/>',
  'package': '<path d="M11 21.73a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73z"/><path d="M12 22V12"/><polyline points="3.29 7 12 12 20.71 7"/><path d="m7.5 4.27 9 5.15"/>',
  'percent': '<line x1="19" x2="5" y1="5" y2="19"/><circle cx="6.5" cy="6.5" r="2.5"/><circle cx="17.5" cy="17.5" r="2.5"/>',
  'piggy-bank': '<path d="M11 17h3v2a1 1 0 0 0 1 1h2a1 1 0 0 0 1-1v-3a3.16 3.16 0 0 0 2-2h1a1 1 0 0 0 1-1v-2a1 1 0 0 0-1-1h-1a5 5 0 0 0-2-4V3a4 4 0 0 0-3.2 1.6l-.3.4H11a6 6 0 0 0-6 6v1a5 5 0 0 0 2 4v3a1 1 0 0 0 1 1h2a1 1 0 0 0 1-1z"/><path d="M16 10h.01"/><path d="M2 8v1a2 2 0 0 0 2 2h1"/>',
  'plane': '<path d="M17.8 19.2 16 11l3.5-3.5C21 6 21.5 4 21 3c-1-.5-3 0-4.5 1.5L13 8 4.8 6.2c-.5-.1-.9.1-1.1.5l-.3.5c-.2.5-.1 1 .3 1.3L9 12l-2 3H4l-1 1 3 2 2 3 1-1v-3l3-2 3.5 5.3c.3.4.8.5 1.3.3l.5-.2c.4-.3.6-.7.5-1.2z"/>',
  'plug-zap': '<path d="M6.3 20.3a2.4 2.4 0 0 0 3.4 0L12 18l-6-6-2.3 2.3a2.4 2.4 0 0 0 0 3.4Z"/><path d="m2 22 3-3"/><path d="M7.5 13.5 10 11"/><path d="M10.5 16.5 13 14"/><path d="m18 3-4 4h6l-4 4"/>',
  'qr-code': '<rect width="5" height="5" x="3" y="3" rx="1"/><rect width="5" height="5" x="16" y="3" rx="1"/><rect width="5" height="5" x="3" y="16" rx="1"/><path d="M21 16h-3a2 2 0 0 0-2 2v3"/><path d="M21 21v.01"/><path d="M12 7v3a2 2 0 0 1-2 2H7"/><path d="M3 12h.01"/><path d="M12 3h.01"/><path d="M12 16v.01"/><path d="M16 12h1"/><path d="M21 12v.01"/><path d="M12 21v-1"/>',
  'receipt': '<path d="M12 17V7"/><path d="M16 8h-6a2 2 0 0 0 0 4h4a2 2 0 0 1 0 4H8"/><path d="M4 3a1 1 0 0 1 1-1 1.3 1.3 0 0 1 .7.2l.933.6a1.3 1.3 0 0 0 1.4 0l.934-.6a1.3 1.3 0 0 1 1.4 0l.933.6a1.3 1.3 0 0 0 1.4 0l.933-.6a1.3 1.3 0 0 1 1.4 0l.934.6a1.3 1.3 0 0 0 1.4 0l.933-.6A1.3 1.3 0 0 1 19 2a1 1 0 0 1 1 1v18a1 1 0 0 1-1 1 1.3 1.3 0 0 1-.7-.2l-.933-.6a1.3 1.3 0 0 0-1.4 0l-.934.6a1.3 1.3 0 0 1-1.4 0l-.933-.6a1.3 1.3 0 0 0-1.4 0l-.933.6a1.3 1.3 0 0 1-1.4 0l-.934-.6a1.3 1.3 0 0 0-1.4 0l-.933.6a1.3 1.3 0 0 1-.7.2 1 1 0 0 1-1-1z"/>',
  'ruler': '<path d="M21.3 15.3a2.4 2.4 0 0 1 0 3.4l-2.6 2.6a2.4 2.4 0 0 1-3.4 0L2.7 8.7a2.41 2.41 0 0 1 0-3.4l2.6-2.6a2.41 2.41 0 0 1 3.4 0Z"/><path d="m14.5 12.5 2-2"/><path d="m11.5 9.5 2-2"/><path d="m8.5 6.5 2-2"/><path d="m17.5 15.5 2-2"/>',
  'scale': '<path d="M12 3v18"/><path d="m19 8 3 8a5 5 0 0 1-6 0zV7"/><path d="M3 7h1a17 17 0 0 0 8-2 17 17 0 0 0 8 2h1"/><path d="m5 8 3 8a5 5 0 0 1-6 0zV7"/><path d="M7 21h10"/>',
  'search': '<path d="m21 21-4.34-4.34"/><circle cx="11" cy="11" r="8"/>',
  'shield-check': '<path d="M20 13c0 5-3.5 7.5-7.66 8.95a1 1 0 0 1-.67-.01C7.5 20.5 4 18 4 13V6a1 1 0 0 1 1-1c2 0 4.5-1.2 6.24-2.72a1.17 1.17 0 0 1 1.52 0C14.51 3.81 17 5 19 5a1 1 0 0 1 1 1z"/><path d="m9 12 2 2 4-4"/>',
  'shuffle': '<path d="m18 14 4 4-4 4"/><path d="m18 2 4 4-4 4"/><path d="M2 18h1.973a4 4 0 0 0 3.3-1.7l5.454-8.6a4 4 0 0 1 3.3-1.7H22"/><path d="M2 6h1.972a4 4 0 0 1 3.6 2.2"/><path d="M22 18h-6.041a4 4 0 0 1-3.3-1.8l-.359-.45"/>',
  'sparkles': '<path d="M11.017 2.814a1 1 0 0 1 1.966 0l1.051 5.558a2 2 0 0 0 1.594 1.594l5.558 1.051a1 1 0 0 1 0 1.966l-5.558 1.051a2 2 0 0 0-1.594 1.594l-1.051 5.558a1 1 0 0 1-1.966 0l-1.051-5.558a2 2 0 0 0-1.594-1.594l-5.558-1.051a1 1 0 0 1 0-1.966l5.558-1.051a2 2 0 0 0 1.594-1.594z"/><path d="M20 2v4"/><path d="M22 4h-4"/><circle cx="4" cy="20" r="2"/>',
  'swords': '<path d="m13 19 6-6"/><path d="M14.5 17.5 3.586 6.586A2 2 0 013 5.172V3h2.172a2 2 0 011.414.586L17.5 14.5"/><path d="m14.828 6.172 2.586-2.586A2 2 0 0118.828 3H21v2.172a2 2 0 01-.586 1.414l-2.586 2.586"/><path d="m16 16 4 4"/><path d="m19 21 2-2"/><path d="m5 14 4 4"/><path d="m5 21-2-2"/><path d="M7.5 16.5 4 20"/>',
  'tag': '<path d="M12.586 2.586A2 2 0 0 0 11.172 2H4a2 2 0 0 0-2 2v7.172a2 2 0 0 0 .586 1.414l8.704 8.704a2.426 2.426 0 0 0 3.42 0l6.58-6.58a2.426 2.426 0 0 0 0-3.42z"/><circle cx="7.5" cy="7.5" r=".5" fill="currentColor"/>',
  'target': '<circle cx="12" cy="12" r="10"/><circle cx="12" cy="12" r="6"/><circle cx="12" cy="12" r="2"/>',
  'ticket': '<path d="M2 9a3 3 0 0 1 0 6v2a2 2 0 0 0 2 2h16a2 2 0 0 0 2-2v-2a3 3 0 0 1 0-6V7a2 2 0 0 0-2-2H4a2 2 0 0 0-2 2Z"/><path d="M13 5v2"/><path d="M13 17v2"/><path d="M13 11v2"/>',
  'timer': '<line x1="10" x2="14" y1="2" y2="2"/><line x1="12" x2="15" y1="14" y2="11"/><circle cx="12" cy="14" r="8"/>',
  'truck': '<path d="M14 18V6a2 2 0 0 0-2-2H4a2 2 0 0 0-2 2v11a1 1 0 0 0 1 1h2"/><path d="M15 18H9"/><path d="M19 18h2a1 1 0 0 0 1-1v-3.65a1 1 0 0 0-.22-.624l-3.48-4.35A1 1 0 0 0 17.52 8H14"/><circle cx="17" cy="18" r="2"/><circle cx="7" cy="18" r="2"/>',
  'type': '<path d="M12 4v16"/><path d="M4 7V5a1 1 0 0 1 1-1h14a1 1 0 0 1 1 1v2"/><path d="M9 20h6"/>',
  'volume-2': '<path d="M11 4.702a.705.705 0 0 0-1.203-.498L6.413 7.587A1.4 1.4 0 0 1 5.416 8H3a1 1 0 0 0-1 1v6a1 1 0 0 0 1 1h2.416a1.4 1.4 0 0 1 .997.413l3.383 3.384A.705.705 0 0 0 11 19.298z"/><path d="M16 9a5 5 0 0 1 0 6"/><path d="M19.364 18.364a9 9 0 0 0 0-12.728"/>',
  'wallet': '<path d="M19 7V4a1 1 0 0 0-1-1H5a2 2 0 0 0 0 4h15a1 1 0 0 1 1 1v4h-3a2 2 0 0 0 0 4h3a1 1 0 0 0 1-1v-2a1 1 0 0 0-1-1"/><path d="M3 5v14a2 2 0 0 0 2 2h15a1 1 0 0 0 1-1v-4"/>',
  'x': '<path d="M18 6 6 18"/><path d="m6 6 12 12"/>',
  'zap': '<path d="M15.914 4a1.5 1.5 0 00-2.474-1.561l-9 9A1.5 1.5 0 005.5 14h4.002a.5.5 0 01.471.666L8.086 20a1.5 1.5 0 002.475 1.56l9-9A1.5 1.5 0 0018.5 10h-3.997a.5.5 0 01-.472-.667z"/>',
};
const icon = (name, cls = 'ic') => `<svg class="${cls}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">${ICONS[name] || ''}</svg>`;

(() => {
  document.getElementById('static-nav')?.remove();   // 검색 로봇용 정적 도구 링크(build_seo.py) — 화면에서는 좌측 메뉴가 대신한다
  const path = location.pathname.replace(/index\.html$/, '');
  const blogKey = document.body.dataset.blog || 'kkultiplab';
  const esc = s => String(s).replace(/[&<>"]/g, c => ({'&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;'}[c]));
  let curGroup = null, curItem = null;
  for (const g of SITE.groups) for (const it of g.items) if (it.p === path) { curGroup = g; curItem = it; }
  /* 도구 아래 하위 페이지(예: /dday/suneung/)는 부모 도구로 본다 */
  if (!curItem) for (const g of SITE.groups) for (const it of g.items) if (path.startsWith(it.p)) { curGroup = g; curItem = it; }
  const brand = `<a class="brand" href="/"><span class="brand-mark">${icon('zap')}</span>${SITE.name}<span class="brand-domain">jjangtool.com</span></a>`;

  /* 모바일 상단 바 */
  const head = document.createElement('header');
  head.className = 'site-head';
  head.innerHTML = `${brand}<button type="button" class="nav-toggle" aria-controls="side-nav" aria-expanded="false" aria-label="메뉴 열기">${icon('menu')}</button>`;

  /* 좌측 메뉴 (모바일에서는 서랍 메뉴) */
  const nav = document.createElement('nav');
  nav.className = 'side-nav'; nav.id = 'side-nav'; nav.setAttribute('aria-label', '도구 메뉴');
  nav.innerHTML = `<div class="side-top">${brand}<button type="button" class="nav-close" aria-label="메뉴 닫기">${icon('x')}</button></div>
    <div class="side-find">${icon('search')}<input type="search" placeholder="도구 검색" aria-label="도구 검색" autocomplete="off"></div>
    <a class="side-home" href="/"${path === '/' ? ' aria-current="page"' : ''}>${icon('sparkles')}<span>전체 도구</span></a>
    ${SITE.groups.map((g, gi) => `<div class="side-group tone-${g.tone}">
      <button type="button" class="side-label" aria-expanded="false" aria-controls="sg${gi}">${icon(g.icon)}<span>${g.name}</span><small>${g.items.length}</small>${icon('chevron-down', 'ic chev')}</button>
      <div class="side-items" id="sg${gi}">${g.items.map(it => `<a href="${it.p}"${it === curItem ? ' aria-current="page"' : ''}>${icon(it.i)}<span>${it.t}</span></a>`).join('')}</div>
    </div>`).join('')}
    <div class="side-blogs"><p class="side-label">추천 블로그</p>${Object.entries(SITE.blogs).map(([k, b]) =>
      `<a href="${b.url}" target="_blank" rel="noopener"><img src="/assets/img/profile-${k}.png" alt="" width="28" height="28"><span>${b.name}</span></a>`).join('')}</div>
    <div class="side-contact"><p class="side-label">문의하기</p><a href="mailto:${SITE.contact.join('@')}?subject=${encodeURIComponent('[짱툴] 문의')}">${icon('mail')}<span>${SITE.contact.join('@')}</span></a>
      <p class="side-note">도구 오류 제보·기능 제안·제휴 문의</p></div>`;
  const dim = document.createElement('div');
  dim.className = 'nav-dim';
  document.body.prepend(head, nav, dim);

  const toggle = head.querySelector('.nav-toggle');
  const setOpen = open => {
    document.documentElement.classList.toggle('nav-open', open);
    toggle.setAttribute('aria-expanded', open);
    if (open) nav.querySelector('.nav-close').focus(); else if (nav.contains(document.activeElement)) toggle.focus();
  };
  toggle.onclick = () => setOpen(true);
  nav.querySelector('.nav-close').onclick = () => setOpen(false);
  dim.onclick = () => setOpen(false);
  document.addEventListener('keydown', e => { if (e.key === 'Escape' && document.documentElement.classList.contains('nav-open')) setOpen(false); });
  /* 묶음 접기·펼치기: 지금 페이지의 묶음은 항상 펼치고, 나머지는 사용자가 펼쳐 둔 것만 기억(이 브라우저에만) */
  const groupsEl = [...nav.querySelectorAll('.side-group')];
  let opened = [];
  try { opened = JSON.parse(localStorage.getItem('jt-open') || '[]'); } catch {}
  const setGroup = (el, open) => { el.classList.toggle('open', open); el.querySelector('.side-label').setAttribute('aria-expanded', open); };
  groupsEl.forEach((el, gi) => {
    const g = SITE.groups[gi];
    setGroup(el, path === '/' || g === curGroup || opened.includes(g.name));
    el.querySelector('.side-label').onclick = () => {
      const open = !el.classList.contains('open');
      setGroup(el, open);
      opened = opened.filter(n => n !== g.name); if (open) opened.push(g.name);
      try { localStorage.setItem('jt-open', JSON.stringify(opened)); } catch {}
    };
  });
  /* 메뉴 검색: 맞는 도구만 남기고 그 묶음을 펼침. 비우면 원래대로 */
  const findIn = nav.querySelector('.side-find input');
  const before = new Map();
  findIn.addEventListener('input', () => {
    const q = findIn.value.trim().toLowerCase().replace(/\s+/g, '');
    groupsEl.forEach((el, gi) => {
      if (!before.has(el)) before.set(el, el.classList.contains('open'));
      let n = 0;
      el.querySelectorAll('.side-items a').forEach(a => {
        const hit = !q || (a.textContent + SITE.groups[gi].name).toLowerCase().replace(/\s+/g, '').includes(q);
        a.hidden = !hit; if (hit) n++;
      });
      el.hidden = q && !n;
      if (q) setGroup(el, n > 0); else { setGroup(el, before.get(el)); before.delete(el); }
    });
  });
  findIn.addEventListener('keydown', e => { if (e.key === 'Enter') { const a = nav.querySelector('.side-items a:not([hidden])'); if (a) location.href = a.href; } });

  const cur = nav.querySelector('[aria-current]');
  if (cur && cur.offsetTop > nav.clientHeight - 80) nav.scrollTop = cur.offsetTop - nav.clientHeight / 2;

  const main = document.querySelector('main');

  /* 도구 페이지 머리: 분류 경로와 아이콘 */
  if (curItem) {
    const top = document.createElement('div');
    top.className = `tool-head tone-${curGroup.tone}`;
    top.innerHTML = `<span class="tool-icon">${icon(curItem.i)}</span><p class="crumb"><a href="/">전체 도구</a>${icon('chevron-right')}<span>${curGroup.name}</span>${path !== curItem.p ? `${icon('chevron-right')}<a href="${curItem.p}">${curItem.t}</a>` : ''}</p>`;
    main.querySelector('h1').before(top);
  }

  /* 배너 */
  const disclosure = SITE.coupang ? '<div class="bn-disclosure">이 배너는 쿠팡 파트너스 활동의 일환으로, 이에 따른 일정액의 수수료를 제공받습니다.</div>' : '';
  const make = (pos, html) => {
    if (!html) return null;
    const d = document.createElement('aside');
    d.className = `bn bn-${pos}`;
    d.setAttribute('aria-label', html === 'POSTS' ? '블로그 최신 글' : '배너');
    if (html !== 'POSTS') d.innerHTML = html + disclosure;
    return d;
  };
  const bTop = make('top', SITE.banners.top); if (bTop) main.before(bTop);
  const bRight = make('right', SITE.banners.right); if (bRight) document.body.append(bRight);

  /* 관련 블로그 글 + 같은 묶음 도구 (도구 페이지) */
  let rel = null;
  if (curItem) {
    rel = document.createElement('section');
    rel.className = 'rel';
    const sib = curGroup.items.filter(it => it !== curItem);
    rel.innerHTML = `<div class="rel-posts" hidden><h2 class="rel-h">${icon('target')}이 도구와 관련된 글</h2><p class="rel-sub">도구 주제와 직접 연결된 추천 블로그 글입니다.</p><div class="post-list"></div></div>
      <div class="new-posts" hidden><h2 class="new-h">${icon('sparkles')}추천 블로그 최신 글</h2><p class="rel-sub"></p><div class="post-list"></div></div>
      ${sib.length ? `<h2>${curGroup.name} 도구 더 보기</h2><div class="chips tone-${curGroup.tone}">${sib.map(it => `<a href="${it.p}">${icon(it.i)}${it.t}</a>`).join('')}</div>` : ''}`;
    main.append(rel);
  }

  /* 블로그 소개 */
  const order = [blogKey, ...Object.keys(SITE.blogs).filter(k => k !== blogKey)];
  const blogs = document.createElement('section');
  blogs.className = 'blogs';
  blogs.setAttribute('aria-labelledby', 'blogs-title');
  blogs.innerHTML = `<div class="blogs-in">
    <p class="eyebrow">짱툴 추천 블로그</p>
    <h2 id="blogs-title">도구만큼 쓸모 있는 정보, 블로그에서 이어집니다</h2>
    <div class="blog-cards">${order.map(k => { const b = SITE.blogs[k], on = k === blogKey && curItem; return `
      <a class="blog-card${on ? ' is-rel' : ''}" href="${b.url}" target="_blank" rel="noopener">
        ${on ? '<span class="badge">이 도구 관련</span>' : ''}
        <img class="avatar" src="/assets/img/profile-${k}.png" alt="${b.name} 프로필" width="72" height="72" loading="lazy">
        <b>${b.name}</b>
        <span class="desc">${b.desc}</span>
        <span class="tags">${b.tags.map(t => `<i>${t}</i>`).join('')}</span>
        <span class="go">블로그 보러 가기${icon('arrow-up-right')}</span>
      </a>`; }).join('')}</div></div>`;
  main.after(blogs);

  const foot = document.createElement('footer');
  foot.className = 'site-foot';
  foot.innerHTML = `<p class="foot-brand">${brand}<span>설치·가입 없이 바로 쓰는 무료 생활 도구</span></p>
    <p class="foot-safe">${icon('shield-check')}${esc(document.body.dataset.ext || '모든 계산과 변환은 브라우저 안에서만 처리되며, 입력한 내용은 저장되거나 전송되지 않습니다.')}</p>
    <p class="foot-copy">© ${new Date().getFullYear()} 짱툴닷컴(jjangtool.com) · 문의 ${SITE.contact.join('@')}</p>
    <p class="foot-links">${Object.values(SITE.blogs).map(b => `<a href="${b.url}" target="_blank" rel="noopener">${b.name}</a>`).join('')}</p>`;
  blogs.after(foot);

  /* D-day 숫자: 페이지를 만든 날(data-built)과 오늘이 다르면 다시 센다 */
  const built = document.body.dataset.built;
  if (built) {
    const n = new Date(), t = Date.UTC(n.getFullYear(), n.getMonth(), n.getDate());
    if (t !== Date.parse(built)) {
      document.querySelectorAll('[data-dd]').forEach(e => {
        const d = Math.round((Date.parse(e.dataset.dd) - t) / 864e5);
        e.textContent = d === 0 ? 'D-day' : d > 0 ? `D-${d.toLocaleString()}` : e.closest('table') ? '지남' : `D+${(-d).toLocaleString()}`;
      });
      const s = document.querySelector('[data-today]');
      if (s) s.textContent = `${n.getFullYear()}년 ${n.getMonth() + 1}월 ${n.getDate()}일(${'일월화수목금토'[n.getDay()]})`;
    }
  }

  /* 블로그 글 불러오기 (assets/posts.json 은 GitHub Actions 가 4시간마다 갱신) */
  const home = document.getElementById('home-posts');
  if (!rel && !bRight && !home) return;
  /* 글 한 줄: 제목·요약·블로그(왼쪽) + 작은 썸네일(오른쪽). mini(우측 영역)는 썸네일이 왼쪽, 요약 없음 */
  const card = (p, cls = 'post', tag = '') => `<a class="${cls}" href="${esc(p.u)}" target="_blank" rel="noopener">
    <span class="post-body"><b>${esc(p.t)}</b>${p.s && !cls.includes('mini') ? `<span class="ex">${esc(p.s)}</span>` : ''}
      <small>${tag ? `<em class="post-tag">${tag}</em>` : ''}<img src="/assets/img/profile-${p.b}.png" alt="" width="16" height="16">${(SITE.blogs[p.b] || {}).name || ''} · ${p.d.slice(5).replace('-', '.')}</small></span>
    <span class="thumb">${p.img ? `<img src="${esc(p.img)}" alt="" loading="lazy" referrerpolicy="no-referrer" onerror="this.remove()">` : ''}</span></a>`;
  fetch('/assets/posts.json').then(r => r.ok ? r.json() : Promise.reject(r.status)).then(d => {
    const posts = d.posts || [];
    if (!posts.length) return;
    if (rel) {
      const related = ((d.related || {})[curItem.p] || []).slice(0, 4);
      if (related.length) {
        const box = rel.querySelector('.rel-posts');
        box.querySelector('.post-list').innerHTML = related.map(p => card(p, 'post is-rel', '관련 글')).join('');
        box.hidden = false;
      }
      if (related.length < 4) {
        const urls = new Set(related.map(p => p.u));
        const fill = posts.filter(p => p.b === blogKey && !urls.has(p.u)).slice(0, Math.max(2, 4 - related.length));
        const box = rel.querySelector('.new-posts');
        box.querySelector('.rel-sub').textContent = related.length
          ? '관련 글 외에 함께 둘러보기 좋은 최근 글입니다.'
          : '이 도구와 직접 관련된 글은 아직 없어서, 추천 블로그의 최근 글을 보여 드립니다.';
        box.querySelector('.post-list').innerHTML = fill.map(p => card(p)).join('');
        box.hidden = false;
      }
    }
    if (bRight) {
      const latest = order.flatMap(k => posts.filter(p => p.b === k).slice(0, 4));
      bRight.innerHTML = `<p class="rail-title">블로그 최신 글</p>${latest.map(p => card(p, 'post mini')).join('')}`;
    }
    if (home) {
      home.innerHTML = Object.keys(SITE.blogs).flatMap(k => posts.filter(p => p.b === k).slice(0, 4)).map(p => card(p)).join('');
      home.closest('section').hidden = false;
    }
  }).catch(() => {});
})();

/* data-icon 속성이 있는 요소에 아이콘 넣기 (index.html 카드 등) */
document.querySelectorAll('[data-icon]').forEach(el => el.insertAdjacentHTML('afterbegin', icon(el.dataset.icon)));

/* 공통 함수 */
const fmt = n => Math.round(n).toLocaleString('ko-KR');
const floor10 = n => Math.floor(n / 10) * 10;
const $ = id => document.getElementById(id);
const fmtBytes = n => n < 1024 ? n + ' B' : n < 1048576 ? (n / 1024).toFixed(1) + ' KB' : (n / 1048576).toFixed(2) + ' MB';
function toast(msg){
  let t = document.querySelector('.toast');
  if (!t){ t = document.createElement('div'); t.className = 'toast'; t.setAttribute('role', 'status'); document.body.append(t); }
  t.textContent = msg; t.classList.add('on');
  clearTimeout(toast._t); toast._t = setTimeout(() => t.classList.remove('on'), 1400);
}
async function copyText(s){
  try { await navigator.clipboard.writeText(s); return true; }
  catch { const ta = document.createElement('textarea'); ta.value = s; ta.style.position = 'fixed'; ta.style.opacity = '0';
    document.body.append(ta); ta.select(); const ok = document.execCommand('copy'); ta.remove(); return ok; }
}
function saveBlob(blob, name){
  const a = document.createElement('a'); a.href = URL.createObjectURL(blob); a.download = name;
  document.body.append(a); a.click(); a.remove(); setTimeout(() => URL.revokeObjectURL(a.href), 4000);
}
/* 파일 선택·끌어다 놓기 공통 처리 */
function bindDrop(label, onFiles){
  const input = label.querySelector('input');
  input.addEventListener('change', () => { onFiles([...input.files]); input.value = ''; });
  label.addEventListener('dragover', e => { e.preventDefault(); label.classList.add('over'); });
  label.addEventListener('dragleave', () => label.classList.remove('over'));
  label.addEventListener('drop', e => { e.preventDefault(); label.classList.remove('over'); onFiles([...e.dataTransfer.files]); });
}
const baseName = n => n.replace(/\.[^.]+$/, '');
/* 조사: 받침 유무에 따라 은/는, 으로/로 */
const lastJong = w => { const c = w.charCodeAt(w.length - 1) - 0xAC00; return c >= 0 && c < 11172 ? c % 28 : 0; };
const eun = w => lastJong(w) ? '은' : '는';
const euro = w => { const j = lastJong(w); return j && j !== 8 ? '으로' : '로'; };
