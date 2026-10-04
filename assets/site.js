/* 사이트 공통 설정: 메뉴·배너·하단 정보는 여기만 고치면 전체 페이지에 반영됩니다. */
const SITE = {
  name: '짱툴',
  menu: [
    ['/hanbang/', '한방단어'],
    ['/wordchain/', '끝말잇기 대결'],
    ['/symbols/', '특수문자'],
    ['/count/', '글자수 세기'],
    ['/typo/', '한영 변환'],
    ['/money/', '금액 한글'],
    ['/image/', '이미지 변환'],
    ['/heic/', 'HEIC→JPG'],
    ['/img2pdf/', '이미지→PDF'],
    ['/pdf-merge/', 'PDF 합치기'],
    ['/qr/', 'QR 코드'],
    ['/age/', '만 나이'],
    ['/dday/', 'D-day'],
    ['/salary/', '연봉 실수령액'],
    ['/pyeong/', '평수 변환'],
    ['/liquidation/', '청산가·펀딩비'],
  ],
  blogs: {
    kkultiplab: ['https://blog.naver.com/kkultiplab', '꿀팁 블로그'],
    jisik_plus: ['https://blog.naver.com/jisik_plus', 'IT·AI 블로그'],
    aicoinlab: ['https://blog.naver.com/aicoinlab', '경제·코인 블로그'],
  },
  /* 배너 HTML. 비워 두면('') 그 위치에는 배너가 나오지 않습니다.
     'BLOG' 는 페이지별 연결 블로그 홍보 배너입니다.
     쿠팡 파트너스 코드를 넣을 때는 아래 coupang 을 true 로 바꾸면 고지 문구가 함께 표시됩니다. */
  banners: {
    top: '',
    bottom: 'BLOG',
    left: '',
    right: '',
  },
  coupang: false,
};

(() => {
  const path = location.pathname.replace(/index\.html$/, '');
  const blogKey = document.body.dataset.blog || 'kkultiplab';

  const head = document.createElement('header');
  head.className = 'site-head';
  head.innerHTML = `<div class="in"><a class="brand" href="/">${SITE.name}</a><nav class="site-nav" aria-label="도구 메뉴">${
    SITE.menu.map(([h, t]) => `<a href="${h}"${path === h ? ' aria-current="page"' : ''}>${t}</a>`).join('')}</nav></div>`;
  document.body.prepend(head);
  const cur = head.querySelector('[aria-current]');
  if (cur) cur.scrollIntoView({block: 'nearest', inline: 'center'});

  const blogBox = () => {
    const [u, t] = SITE.blogs[blogKey];
    return `<a class="bn-box" href="${u}" target="_blank" rel="noopener"><b>${t}에서 더 보기</b><span>이 도구와 관련된 정리 글을 블로그에 올리고 있습니다.</span></a>`;
  };
  const disclosure = SITE.coupang ? '<div class="bn-disclosure">이 배너는 쿠팡 파트너스 활동의 일환으로, 이에 따른 일정액의 수수료를 제공받습니다.</div>' : '';
  const make = (pos, html) => {
    if (!html) return null;
    const d = document.createElement('aside');
    d.className = `bn bn-${pos}` + (pos === 'left' || pos === 'right' ? ' bn-side' : '');
    d.setAttribute('aria-label', '배너');
    d.innerHTML = html === 'BLOG' ? blogBox() : html + disclosure;
    return d;
  };
  const main = document.querySelector('main');
  const b = SITE.banners;
  const top = make('top', b.top); if (top) main.before(top);
  const bottom = make('bottom', b.bottom); if (bottom) main.after(bottom);
  const left = make('left', b.left); if (left) document.body.append(left);
  const right = make('right', b.right); if (right) document.body.append(right);

  const foot = document.createElement('footer');
  foot.className = 'site-foot';
  foot.innerHTML = `<p>${Object.values(SITE.blogs).map(([u, t]) => `<a href="${u}" target="_blank" rel="noopener">${t}</a>`).join(' | ')}</p>
    <p>모든 계산은 브라우저 안에서만 처리되며, 입력한 내용은 저장되거나 전송되지 않습니다.</p>`;
  document.body.append(foot);
})();

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
