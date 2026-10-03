// 零依赖标题+路径搜索（无障碍版 W-4.6-65；W-4.6-67：惰性索引 · ?q= 深链/返回恢复 · listbox 语义修正）
document.addEventListener('DOMContentLoaded', ()=>{
  const box = document.getElementById('search');
  const res = document.getElementById('results');
  const pc = document.getElementById('pagecount');
  const meta = document.getElementById('resultmeta');
  if(!box || !res || !window.TITLES) return;

  // 页面总数（数字由 JS 填入，不写死）
  if(pc) pc.textContent = String(window.TITLES.length);

  // 分类条目数：按 category 统计，填入 bento 卡片 .c
  const counts = {};
  window.TITLES.forEach(t=>{ counts[t.category]=(counts[t.category]||0)+1; });
  document.querySelectorAll('.cats .cat').forEach(a=>{
    const c = a.querySelector('.c');
    const key = a.getAttribute('data-cat');
    if(c && key && counts[key]) c.textContent = counts[key] + ' 页';
  });

  // prefers-reduced-motion：为真时不做平滑滚动
  const reduceMotion = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  // 归一化：小写 + 全角空格(\u3000)当普通空格
  const norm = s => String(s).toLowerCase().replace(/\u3000/g,' ');
  const esc = s => String(s).replace(/[&<>"]/g, m=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[m]));

  // 惰性索引：载入只保留 titles.js 的原始数组引用，首次检索时才构建（data/titles.js ≈810 KB）
  let items = null;
  function index(){
    if(!items) items = window.TITLES.map(t=>({t, hay: norm(t.title)+' '+norm(t.path)}));
    return items;
  }

  let liNodes = [];
  let cur = -1; // 当前高亮项在 liNodes 中的索引

  // #resultmeta 承载所有非选项文案（计数 / 截断提示 / 空态）：
  // role="listbox" 的直接子元素只允许 role="option"
  function say(text){ if(meta) meta.textContent = text || ''; }

  function clear(){
    res.innerHTML = '';
    liNodes = [];
    cur = -1;
    box.setAttribute('aria-expanded','false');
    box.removeAttribute('aria-activedescendant');
    say('');
  }
  function render(q){
    clear();
    const nq = norm(q).trim();
    if(!nq) return;
    const matched = index().filter(it=> it.hay.includes(nq));
    const hits = matched.slice(0,50);
    hits.forEach((h,i)=>{
      const li = document.createElement('li');
      li.id = 'res-'+i;
      li.setAttribute('role','option');
      li.setAttribute('aria-selected','false');
      const cat = h.t.category ? ' <span class="stat">'+h.t.category+'</span>' : '';
      const href = 'pages/' + h.t.path.split('/').map(encodeURIComponent).join('/');
      li.innerHTML = `<a href="${href}">${esc(h.t.title)}</a>${cat}`;
      liNodes.push(li);
      res.appendChild(li);
    });
    if(matched.length === 0){
      // 空态：给出可操作提示（不只是「无结果」）
      say('没有匹配「'+q+'」。试试：类别名（如 物品）、实体名（如 真珠）、或英文名（如 Pearl）。');
    } else if(matched.length > 50){
      // 结果计数 + 截断提示（两者都在 #resultmeta，不进 listbox）
      say('共 ' + matched.length + ' 条，显示前 50 条 · 还有 '+(matched.length-50)+' 条，请缩小关键词');
    }
    if(liNodes.length) box.setAttribute('aria-expanded','true');
  }
  // 键盘移动高亮：同步 aria-selected / aria-activedescendant，并保证可见
  function move(d){
    if(!liNodes.length) return;
    if(cur >= 0){
      liNodes[cur].setAttribute('aria-selected','false');
      liNodes[cur].classList.remove('hl');
    }
    cur = (cur + d + liNodes.length) % liNodes.length;
    liNodes[cur].setAttribute('aria-selected','true');
    liNodes[cur].classList.add('hl');
    box.setAttribute('aria-activedescendant', liNodes[cur].id);
    liNodes[cur].scrollIntoView({block:'nearest', behavior: reduceMotion ? 'auto' : 'smooth'});
  }

  // ---- 深链 / 返回恢复：URL 带 ?q=关键词（兼容 #q=） ----
  function readQuery(){
    let q = '';
    try{
      const v = new URLSearchParams(window.location.search).get('q');
      if(v !== null){ q = v; }
      else {
        const h = window.location.hash || '';
        if(h.indexOf('#q=') === 0){
          const raw = h.slice(3);
          try{ q = decodeURIComponent(raw); }catch(e){ q = raw; }
        }
      }
    }catch(e){ q = ''; }
    return q || '';
  }
  function writeQuery(q){
    // 只替换当前历史条目（不新增记录），避免污染浏览器「返回」栈
    try{
      if(!window.history || !window.history.replaceState) return;
      window.history.replaceState(null, '', q ? ('?q=' + encodeURIComponent(q)) : window.location.pathname);
    }catch(e){ /* file:// 下部分浏览器禁止改写 URL：忽略，搜索本身不受影响 */ }
  }

  box.addEventListener('input', ()=>{ render(box.value); writeQuery(box.value); });
  box.addEventListener('keydown', e=>{
    if(e.key === 'ArrowDown'){ e.preventDefault(); move(1); }
    else if(e.key === 'ArrowUp'){ e.preventDefault(); move(-1); }
    else if(e.key === 'Enter'){
      e.preventDefault();
      if(cur >= 0 && liNodes[cur]){
        const a = liNodes[cur].querySelector('a');
        if(a) a.click();
      }
    }
    else if(e.key === 'Escape'){
      e.preventDefault();
      box.value = '';
      clear();
      writeQuery('');
      box.focus(); // 焦点留在输入框
    }
  });
  box.addEventListener('blur', ()=>{ box.setAttribute('aria-expanded','false'); });

  // 载入即读深链（?q= 或 #q=）：填入搜索框并立即渲染结果（不刷新页面）
  const initialQ = readQuery();
  if(initialQ){ box.value = initialQ; render(initialQ); }

  // 浏览器「返回」：从 bfcache 恢复本页时 pageshow 触发，按 URL 的 ?q= 复原搜索词与结果
  window.addEventListener('pageshow', ()=>{
    const q = readQuery();
    if(q !== box.value){ box.value = q; render(q); }
  });
});
