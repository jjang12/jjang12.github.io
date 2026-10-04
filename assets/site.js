/* 사이트 공통 설정: 메뉴·배너·블로그 소개는 여기만 고치면 전체 페이지에 반영됩니다.
   새 도구를 추가할 때는 groups 의 알맞은 묶음에 한 줄 넣고, index.html 카드와 sitemap.xml 에도 추가하세요.
   k 는 '관련 블로그 글'을 고를 때 쓰는 단어(글 제목·카테고리에 들어 있으면 우선 노출)입니다. */
const SITE = {
  name: '짱툴',
  groups: [
    {name: '글자·단어', icon: 'type', tone: 'violet', items: [
      {p: '/hanbang/', t: '한방단어', i: 'target', k: ['끝말잇기', '단어', '맞춤법', '한글', '국어']},
      {p: '/wordchain/', t: '끝말잇기 대결', i: 'swords', k: ['끝말잇기', '단어', '게임', '퀴즈', '국어']},
      {p: '/symbols/', t: '특수문자', i: 'omega', k: ['특수문자', '이모지', '키보드', '단축키', '기호']},
      {p: '/count/', t: '글자수 세기', i: 'letter-text', k: ['글자수', '자기소개서', '자소서', '이력서', '취업', '채용']},
      {p: '/typo/', t: '한영 변환', i: 'languages', k: ['키보드', '한영', '타자', '단축키', '윈도우', '맥북']},
    ]},
    {name: '이미지·PDF', icon: 'layers', tone: 'sky', items: [
      {p: '/image/', t: '이미지 변환', i: 'image', k: ['이미지', '사진', '용량', '변환', '편집']},
      {p: '/heic/', t: 'HEIC→JPG', i: 'file-image', k: ['아이폰', 'HEIC', '사진', '갤러리', 'iOS']},
      {p: '/img2pdf/', t: '이미지→PDF', i: 'file-output', k: ['PDF', '스캔', '서류', '문서', '사진']},
      {p: '/pdf-merge/', t: 'PDF 합치기', i: 'files', k: ['PDF', '서류', '문서', '증빙', '계약']},
      {p: '/qr/', t: 'QR 코드', i: 'qr-code', k: ['QR', '큐알', '링크', '카카오', '네이버']},
    ]},
    {name: '날짜', icon: 'calendar', tone: 'amber', items: [
      {p: '/age/', t: '만 나이', i: 'cake', k: ['나이', '만나이', '만 나이', '생일', '출생', '연령']},
      {p: '/dday/', t: 'D-day', i: 'calendar-days', k: ['일정', '날짜', '연휴', '공휴일', '마감', '기념일', '신청']},
    ]},
    {name: '돈·생활', icon: 'coins', tone: 'green', items: [
      {p: '/salary/', t: '연봉 실수령액', i: 'wallet', k: ['연봉', '월급', '실수령', '세금', '연말정산', '4대보험', '소득']},
      {p: '/money/', t: '금액 한글', i: 'banknote', k: ['금액', '계약', '은행', '송금', '대출', '예금']},
      {p: '/pyeong/', t: '평수 변환', i: 'ruler', k: ['아파트', '평수', '부동산', '청약', '전세', '분양']},
      {p: '/liquidation/', t: '청산가·펀딩비', i: 'chart-candlestick', k: ['코인', '비트코인', '선물', '펀딩', '거래소', '레버리지']},
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
};

/* 아이콘: Lucide (ISC License, https://lucide.dev) */
const ICONS = {
  'arrow-up-right': '<path d="M7 7h10v10"/><path d="M7 17 17 7"/>',
  'banknote': '<rect width="20" height="12" x="2" y="6" rx="2"/><circle cx="12" cy="12" r="2"/><path d="M6 12h.01M18 12h.01"/>',
  'cake': '<path d="M20 21v-8a2 2 0 0 0-2-2H6a2 2 0 0 0-2 2v8"/><path d="M4 16s.5-1 2-1 2.5 2 4 2 2.5-2 4-2 2.5 2 4 2 2-1 2-1"/><path d="M2 21h20"/><path d="M7 8v3"/><path d="M12 8v3"/><path d="M17 8v3"/><path d="M7 4h.01"/><path d="M12 4h.01"/><path d="M17 4h.01"/>',
  'calendar-days': '<path d="M8 2v3"/><path d="M16 2v3"/><rect x="3" y="3" width="18" height="18" rx="2"/><path d="M3 9h18"/><path d="M8 13h.01"/><path d="M12 13h.01"/><path d="M16 13h.01"/><path d="M8 17h.01"/><path d="M12 17h.01"/><path d="M16 17h.01"/>',
  'calendar': '<path d="M8 2v3"/><path d="M16 2v3"/><rect x="3" y="3" width="18" height="18" rx="2"/><path d="M3 9h18"/>',
  'chart-candlestick': '<path d="M9 5v4"/><rect width="4" height="6" x="7" y="9" rx="1"/><path d="M9 15v2"/><path d="M17 3v2"/><rect width="4" height="8" x="15" y="5" rx="1"/><path d="M17 13v3"/><path d="M3 3v16a2 2 0 0 0 2 2h16"/>',
  'chevron-right': '<path d="m9 18 6-6-6-6"/>',
  'coins': '<path d="M13.744 17.736a6 6 0 1 1-7.48-7.48"/><path d="M15 6h1v4"/><path d="m6.134 14.768.866-.5 2 3.464"/><circle cx="16" cy="8" r="6"/>',
  'file-image': '<path d="M6 22a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h8a2.4 2.4 0 0 1 1.704.706l3.588 3.588A2.4 2.4 0 0 1 20 8v12a2 2 0 0 1-2 2z"/><path d="M14 2v5a1 1 0 0 0 1 1h5"/><circle cx="10" cy="12" r="2"/><path d="m20 17-1.296-1.296a2.41 2.41 0 0 0-3.408 0L9 22"/>',
  'file-output': '<path d="M4.226 20.925A2 2 0 0 0 6 22h12a2 2 0 0 0 2-2V8a2.4 2.4 0 0 0-.706-1.706l-3.588-3.588A2.4 2.4 0 0 0 14 2H6a2 2 0 0 0-2 2v3.127"/><path d="M14 2v5a1 1 0 0 0 1 1h5"/><path d="m5 11-3 3"/><path d="m5 17-3-3h10"/>',
  'files': '<path d="M15 2h-4a2 2 0 0 0-2 2v11a2 2 0 0 0 2 2h8a2 2 0 0 0 2-2V8"/><path d="M16.706 2.706A2.4 2.4 0 0 0 15 2v5a1 1 0 0 0 1 1h5a2.4 2.4 0 0 0-.706-1.706z"/><path d="M5 7a2 2 0 0 0-2 2v11a2 2 0 0 0 2 2h8a2 2 0 0 0 1.732-1"/>',
  'image': '<rect width="18" height="18" x="3" y="3" rx="2" ry="2"/><circle cx="9" cy="9" r="2"/><path d="m21 15-3.086-3.086a2 2 0 0 0-2.828 0L6 21"/>',
  'languages': '<path d="m5 8 6 6"/><path d="m4 14 6-6 2-3"/><path d="M2 5h12"/><path d="M7 2h1"/><path d="m22 22-5-10-5 10"/><path d="M14 18h6"/>',
  'layers': '<path d="M12.83 2.18a2 2 0 0 0-1.66 0L2.6 6.08a1 1 0 0 0 0 1.83l8.58 3.91a2 2 0 0 0 1.66 0l8.58-3.9a1 1 0 0 0 0-1.83z"/><path d="M2 12a1 1 0 0 0 .58.91l8.6 3.91a2 2 0 0 0 1.65 0l8.58-3.9A1 1 0 0 0 22 12"/><path d="M2 17a1 1 0 0 0 .58.91l8.6 3.91a2 2 0 0 0 1.65 0l8.58-3.9A1 1 0 0 0 22 17"/>',
  'letter-text': '<path d="M15 5h6"/><path d="M15 12h6"/><path d="M3 19h18"/><path d="m3 12 3.553-7.724a.5.5 0 0 1 .894 0L11 12"/><path d="M3.92 10h6.16"/>',
  'menu': '<path d="M4 5h16"/><path d="M4 12h16"/><path d="M4 19h16"/>',
  'omega': '<path d="M3 20h4.5a.5.5 0 0 0 .5-.5v-.282a.52.52 0 0 0-.247-.437 8 8 0 1 1 8.494-.001.52.52 0 0 0-.247.438v.282a.5.5 0 0 0 .5.5H21"/>',
  'qr-code': '<rect width="5" height="5" x="3" y="3" rx="1"/><rect width="5" height="5" x="16" y="3" rx="1"/><rect width="5" height="5" x="3" y="16" rx="1"/><path d="M21 16h-3a2 2 0 0 0-2 2v3"/><path d="M21 21v.01"/><path d="M12 7v3a2 2 0 0 1-2 2H7"/><path d="M3 12h.01"/><path d="M12 3h.01"/><path d="M12 16v.01"/><path d="M16 12h1"/><path d="M21 12v.01"/><path d="M12 21v-1"/>',
  'ruler': '<path d="M21.3 15.3a2.4 2.4 0 0 1 0 3.4l-2.6 2.6a2.4 2.4 0 0 1-3.4 0L2.7 8.7a2.41 2.41 0 0 1 0-3.4l2.6-2.6a2.41 2.41 0 0 1 3.4 0Z"/><path d="m14.5 12.5 2-2"/><path d="m11.5 9.5 2-2"/><path d="m8.5 6.5 2-2"/><path d="m17.5 15.5 2-2"/>',
  'search': '<path d="m21 21-4.34-4.34"/><circle cx="11" cy="11" r="8"/>',
  'shield-check': '<path d="M20 13c0 5-3.5 7.5-7.66 8.95a1 1 0 0 1-.67-.01C7.5 20.5 4 18 4 13V6a1 1 0 0 1 1-1c2 0 4.5-1.2 6.24-2.72a1.17 1.17 0 0 1 1.52 0C14.51 3.81 17 5 19 5a1 1 0 0 1 1 1z"/><path d="m9 12 2 2 4-4"/>',
  'sparkles': '<path d="M11.017 2.814a1 1 0 0 1 1.966 0l1.051 5.558a2 2 0 0 0 1.594 1.594l5.558 1.051a1 1 0 0 1 0 1.966l-5.558 1.051a2 2 0 0 0-1.594 1.594l-1.051 5.558a1 1 0 0 1-1.966 0l-1.051-5.558a2 2 0 0 0-1.594-1.594l-5.558-1.051a1 1 0 0 1 0-1.966l5.558-1.051a2 2 0 0 0 1.594-1.594z"/><path d="M20 2v4"/><path d="M22 4h-4"/><circle cx="4" cy="20" r="2"/>',
  'swords': '<path d="m13 19 6-6"/><path d="M14.5 17.5 3.586 6.586A2 2 0 013 5.172V3h2.172a2 2 0 011.414.586L17.5 14.5"/><path d="m14.828 6.172 2.586-2.586A2 2 0 0118.828 3H21v2.172a2 2 0 01-.586 1.414l-2.586 2.586"/><path d="m16 16 4 4"/><path d="m19 21 2-2"/><path d="m5 14 4 4"/><path d="m5 21-2-2"/><path d="M7.5 16.5 4 20"/>',
  'target': '<circle cx="12" cy="12" r="10"/><circle cx="12" cy="12" r="6"/><circle cx="12" cy="12" r="2"/>',
  'type': '<path d="M12 4v16"/><path d="M4 7V5a1 1 0 0 1 1-1h14a1 1 0 0 1 1 1v2"/><path d="M9 20h6"/>',
  'wallet': '<path d="M19 7V4a1 1 0 0 0-1-1H5a2 2 0 0 0 0 4h15a1 1 0 0 1 1 1v4h-3a2 2 0 0 0 0 4h3a1 1 0 0 0 1-1v-2a1 1 0 0 0-1-1"/><path d="M3 5v14a2 2 0 0 0 2 2h15a1 1 0 0 0 1-1v-4"/>',
  'x': '<path d="M18 6 6 18"/><path d="m6 6 12 12"/>',
  'zap': '<path d="M15.914 4a1.5 1.5 0 00-2.474-1.561l-9 9A1.5 1.5 0 005.5 14h4.002a.5.5 0 01.471.666L8.086 20a1.5 1.5 0 002.475 1.56l9-9A1.5 1.5 0 0018.5 10h-3.997a.5.5 0 01-.472-.667z"/>',
};
const icon = (name, cls = 'ic') => `<svg class="${cls}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">${ICONS[name] || ''}</svg>`;

(() => {
  const path = location.pathname.replace(/index\.html$/, '');
  const blogKey = document.body.dataset.blog || 'kkultiplab';
  const esc = s => String(s).replace(/[&<>"]/g, c => ({'&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;'}[c]));
  let curGroup = null, curItem = null;
  for (const g of SITE.groups) for (const it of g.items) if (it.p === path) { curGroup = g; curItem = it; }
  const brand = `<a class="brand" href="/"><span class="brand-mark">${icon('zap')}</span>${SITE.name}</a>`;

  /* 모바일 상단 바 */
  const head = document.createElement('header');
  head.className = 'site-head';
  head.innerHTML = `${brand}<button type="button" class="nav-toggle" aria-controls="side-nav" aria-expanded="false" aria-label="메뉴 열기">${icon('menu')}</button>`;

  /* 좌측 메뉴 (모바일에서는 서랍 메뉴) */
  const nav = document.createElement('nav');
  nav.className = 'side-nav'; nav.id = 'side-nav'; nav.setAttribute('aria-label', '도구 메뉴');
  nav.innerHTML = `<div class="side-top">${brand}<button type="button" class="nav-close" aria-label="메뉴 닫기">${icon('x')}</button></div>
    <a class="side-home" href="/"${path === '/' ? ' aria-current="page"' : ''}>${icon('sparkles')}<span>전체 도구</span></a>
    ${SITE.groups.map(g => `<div class="side-group tone-${g.tone}">
      <p class="side-label">${icon(g.icon)}${g.name}</p>
      ${g.items.map(it => `<a href="${it.p}"${it === curItem ? ' aria-current="page"' : ''}>${icon(it.i)}<span>${it.t}</span></a>`).join('')}
    </div>`).join('')}
    <div class="side-blogs"><p class="side-label">운영 블로그</p>${Object.entries(SITE.blogs).map(([k, b]) =>
      `<a href="${b.url}" target="_blank" rel="noopener"><img src="/assets/img/profile-${k}.png" alt="" width="28" height="28"><span>${b.name}</span></a>`).join('')}</div>`;
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
  const cur = nav.querySelector('[aria-current]');
  if (cur && cur.offsetTop > nav.clientHeight - 80) nav.scrollTop = cur.offsetTop - nav.clientHeight / 2;

  const main = document.querySelector('main');

  /* 도구 페이지 머리: 분류 경로와 아이콘 */
  if (curItem) {
    const top = document.createElement('div');
    top.className = `tool-head tone-${curGroup.tone}`;
    top.innerHTML = `<span class="tool-icon">${icon(curItem.i)}</span><p class="crumb"><a href="/">전체 도구</a>${icon('chevron-right')}<span>${curGroup.name}</span></p>`;
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
    rel.innerHTML = `<div class="rel-posts" hidden><h2>이 도구와 함께 보면 좋은 글</h2><div class="post-grid"></div></div>
      ${sib.length ? `<h2>${curGroup.name} 도구 더 보기</h2><div class="chips tone-${curGroup.tone}">${sib.map(it => `<a href="${it.p}">${icon(it.i)}${it.t}</a>`).join('')}</div>` : ''}`;
    main.append(rel);
  }

  /* 블로그 소개 */
  const order = [blogKey, ...Object.keys(SITE.blogs).filter(k => k !== blogKey)];
  const blogs = document.createElement('section');
  blogs.className = 'blogs';
  blogs.setAttribute('aria-labelledby', 'blogs-title');
  blogs.innerHTML = `<div class="blogs-in">
    <p class="eyebrow">짱툴 운영자의 네이버 블로그</p>
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
    <p class="foot-safe">${icon('shield-check')}모든 계산과 변환은 브라우저 안에서만 처리되며, 입력한 내용은 저장되거나 전송되지 않습니다.</p>
    <p class="foot-links">${Object.values(SITE.blogs).map(b => `<a href="${b.url}" target="_blank" rel="noopener">${b.name}</a>`).join('')}</p>`;
  blogs.after(foot);

  /* 블로그 글 불러오기 (assets/posts.json 은 GitHub Actions 가 4시간마다 갱신) */
  const home = document.getElementById('home-posts');
  if (!rel && !bRight && !home) return;
  const card = (p, cls = 'post') => `<a class="${cls}" href="${esc(p.u)}" target="_blank" rel="noopener">
    <span class="thumb">${p.img ? `<img src="${esc(p.img)}" alt="" loading="lazy" referrerpolicy="no-referrer" onerror="this.remove()">` : ''}</span>
    <span class="post-body"><b>${esc(p.t)}</b><small><img src="/assets/img/profile-${p.b}.png" alt="" width="16" height="16">${(SITE.blogs[p.b] || {}).name || ''} · ${p.d.slice(5).replace('-', '.')}</small></span></a>`;
  fetch('/assets/posts.json').then(r => r.ok ? r.json() : Promise.reject(r.status)).then(d => {
    const posts = d.posts || [];
    if (!posts.length) return;
    if (rel) {
      const score = p => curItem.k.reduce((s, w) => s + ((p.t + ' ' + p.c).includes(w) ? 1 : 0), 0);
      const ranked = posts.map(p => [score(p), p]).filter(([s]) => s > 0)
        .sort((a, b) => b[0] - a[0] || b[1].d.localeCompare(a[1].d)).map(x => x[1]);
      const pick = [...ranked, ...posts.filter(p => p.b === blogKey && !ranked.includes(p))].slice(0, 4);
      const box = rel.querySelector('.rel-posts');
      box.querySelector('.post-grid').innerHTML = pick.map(p => card(p)).join('');
      box.hidden = false;
    }
    if (bRight) {
      const latest = order.flatMap(k => posts.filter(p => p.b === k).slice(0, 2));
      bRight.innerHTML = `<p class="rail-title">블로그 최신 글</p>${latest.map(p => card(p, 'post mini')).join('')}`;
    }
    if (home) {
      home.innerHTML = Object.keys(SITE.blogs).flatMap(k => posts.filter(p => p.b === k).slice(0, 2)).map(p => card(p)).join('');
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
