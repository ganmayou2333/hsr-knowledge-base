// 零依赖标题+路径搜索（无障碍版，W-4.6-65）
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
  const items = window.TITLES.map(t=>({t, hay: norm(t.title)+' '+norm(t.path)}));
  let liNodes = [];
  let cur = -1; // 当前高亮项在 liNodes 中的索引

  function clear(){
    res.innerHTML = '';
    liNodes = [];
    cur = -1;
    box.setAttribute('aria-expanded','false');
    box.removeAttribute('aria-activedescendant');
    if(meta) meta.textContent = '';
  }
  function render(q){
    clear();
    const nq = norm(q).trim();
    if(!nq) return;
    const matched = items.filter(it=> it.hay.includes(nq));
    const hits = matched.slice(0,50);
    hits.forEach((h,i)=>{
      const li = document.createElement('li');
      li.id = 'res-'+i;
      li.setAttribute('role','option');
      li.setAttribute('aria-selected','false');
      const cat = h.t.category ? ' <span class="stat">'+h.t.category+'</span>' : '';
      li.innerHTML = `<a href="pages/${h.t.path}">${h.t.title}</a>${cat}`;
      liNodes.push(li);
      res.appendChild(li);
    });
    if(matched.length === 0){
      // 空态：给出可操作提示（不只是「无结果」）
      res.innerHTML = `<li class="stat">没有匹配「${esc(q)}」。试试：类别名（如 物品）、实体名（如 真珠）、或英文名（如 Pearl）。</li>`;
    } else if(matched.length > 50){
      // 结果计数
      if(meta) meta.textContent = '共 ' + matched.length + ' 条，显示前 50 条';
      const li = document.createElement('li');
      li.className = 'stat';
      li.textContent = '还有 '+(matched.length-50)+' 条，请缩小关键词';
      res.appendChild(li);
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
  box.addEventListener('input', ()=>{ render(box.value); });
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
      box.focus(); // 焦点留在输入框
    }
  });
  box.addEventListener('blur', ()=>{ box.setAttribute('aria-expanded','false'); });
});
