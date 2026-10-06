/* 특수문자 페이지 공통 (build_symbols.py 가 만든 symbols/ 페이지): 누르면 복사 + 모음 칸, 최근·즐겨찾기, 탭 */
(() => {
  const KEY_RECENT = 'jt-sym-recent', KEY_FAV = 'jt-sym-fav', MAX_RECENT = 40;
  const load = k => { try { return JSON.parse(localStorage.getItem(k)) || []; } catch { return []; } };
  const save = (k, v) => { try { localStorage.setItem(k, JSON.stringify(v)); } catch {} };
  const esc = s => String(s).replace(/[&<>"]/g, c => ({'&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;'}[c]));
  let recent = load(KEY_RECENT), fav = load(KEY_FAV), favMode = false;
  const box = $('box'), myBox = $('myBox');

  const row = (title, list, kind) => list.length
    ? `<h3>${title} <small>${list.length}개</small></h3><div class="syms wide my-${kind}">${list.map(c => `<button type="button"${fav.includes(c) ? ' class="fav"' : ''}>${esc(c)}</button>`).join('')}</div>` : '';
  function renderMy(){
    if (!myBox) return;
    $('favRow').innerHTML = row('즐겨찾기', fav, 'fav');
    $('recentRow').innerHTML = row('최근 복사', recent, 'recent');
    myBox.hidden = !fav.length && !recent.length;
    document.querySelectorAll('main .syms:not(.my-fav):not(.my-recent) button').forEach(b => b.classList.toggle('fav', fav.includes(b.textContent)));
  }

  document.querySelector('main').addEventListener('click', async e => {
    const b = e.target.closest('.syms button'); if (!b) return;
    const c = b.textContent;
    if (favMode) {
      fav = fav.includes(c) ? fav.filter(x => x !== c) : [c, ...fav];
      save(KEY_FAV, fav); renderMy();
      toast(fav.includes(c) ? `즐겨찾기에 넣었습니다: ${c}` : `즐겨찾기에서 뺐습니다: ${c}`);
      return;
    }
    if (box) box.value += c;
    recent = [c, ...recent.filter(x => x !== c)].slice(0, MAX_RECENT);
    save(KEY_RECENT, recent);
    const ok = await copyText(c);
    toast(ok ? `복사했습니다: ${c}` : '복사하지 못했습니다. 모음 칸에서 직접 복사하세요.');
    renderMy();
  });

  if ($('copyAll')) $('copyAll').onclick = async () => {
    const v = box.value; if (!v) return toast('모음 칸이 비어 있습니다.');
    toast(await copyText(v) ? `${Array.from(v).length}자를 복사했습니다.` : '복사하지 못했습니다.');
  };
  if ($('clear')) $('clear').onclick = () => { box.value = ''; box.focus(); };
  if ($('favMode')) $('favMode').onclick = e => {
    favMode = !favMode;
    e.currentTarget.setAttribute('aria-pressed', favMode);
    e.currentTarget.textContent = favMode ? '★ 고르는 중 (다시 누르면 끝)' : '☆ 즐겨찾기 고르기';
    document.body.classList.toggle('sym-fav-mode', favMode);
    toast(favMode ? '누르는 문자가 즐겨찾기에 들어갑니다.' : '즐겨찾기 고르기를 마쳤습니다.');
  };

  /* 탭(전체 모음 페이지) — 주소 #e-face 처럼 다른 탭 안의 앵커로 오면 그 탭을 연다 */
  const tabs = document.querySelectorAll('.sym-tabs button');
  const show = k => {
    tabs.forEach(t => t.setAttribute('aria-pressed', t.dataset.tab === k));
    document.querySelectorAll('.sym-panel').forEach(p => p.hidden = p.dataset.panel !== k);
  };
  tabs.forEach(t => t.onclick = () => show(t.dataset.tab));
  const fromHash = () => {
    const el = location.hash && document.getElementById(decodeURIComponent(location.hash.slice(1)));
    const p = el && el.closest('.sym-panel');
    if (p) { show(p.dataset.panel); el.scrollIntoView(); }
  };
  window.addEventListener('hashchange', fromHash);
  fromHash();
  renderMy();
})();
