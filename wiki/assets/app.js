// 零依赖标题+路径搜索（升级版）
document.addEventListener('DOMContentLoaded', ()=>{
  const box = document.getElementById('search');
  const res = document.getElementById('results');
  const statEl = document.getElementById('stat');
  if(!box || !res || !window.TITLES) return;
  // 统计行：自动读取，不再写死
  if(statEl) statEl.textContent = '崩坏：星穹铁道 4.6 静态知识库 · 页面 ' + window.TITLES.length;

  // 归一化：小写 + 全角空格(\u3000)当普通空格
  const norm = s => String(s).toLowerCase().replace(/\u3000/g,' ');
  const items = window.TITLES.map(t=>({t, hay: norm(t.title)+' '+norm(t.path)}));
  let liNodes = [];
  let cur = -1; // 当前高亮项在 liNodes 中的索引

  function clear(){
    res.innerHTML = '';
    liNodes = [];
    cur = -1;
  }
  function render(q){
    clear();
    const nq = norm(q).trim();
    if(!nq) return;
    const matched = items.filter(it=> it.hay.includes(nq));
    const hits = matched.slice(0,50);
    hits.forEach(h=>{
      const li = document.createElement('li');
      const cat = h.t.category ? ' <span class="stat">'+h.t.category+'</span>' : '';
      li.innerHTML = `<a href="pages/${h.t.path}">${h.t.title}</a>${cat}`;
      liNodes.push(li);
      res.appendChild(li);
    });
    if(matched.length > 50){
      const li = document.createElement('li');
      li.className = 'stat';
      li.textContent = '还有 '+(matched.length-50)+' 条，请缩小关键词';
      res.appendChild(li);
    }
    if(!hits.length) res.innerHTML = '<li class="stat">无匹配</li>';
  }
  // 键盘移动高亮
  function move(d){
    if(!liNodes.length) return;
    if(cur >= 0) liNodes[cur].classList.remove('hl');
    cur = (cur + d + liNodes.length) % liNodes.length;
    liNodes[cur].classList.add('hl');
    const a = liNodes[cur].querySelector('a');
    if(a) a.focus();
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
      box.focus();
    }
  });
});
