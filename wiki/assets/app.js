// 简单标题搜索
document.addEventListener('DOMContentLoaded', ()=>{
  const box = document.getElementById('search');
  const res = document.getElementById('results');
  if(!box || !res || !window.TITLES) return;
  box.addEventListener('input', ()=>{
    const q = box.value.trim().toLowerCase();
    res.innerHTML = '';
    if(!q) return;
    const hits = window.TITLES.filter(t=> t.title.toLowerCase().includes(q) || t.path.toLowerCase().includes(q)).slice(0,30);
    hits.forEach(h=>{
      const li = document.createElement('li');
      li.innerHTML = `<a href="pages/${h.path}">${h.title}</a> <span class="stat">${h.category||''}</span>`;
      res.appendChild(li);
    });
    if(!hits.length) res.innerHTML = '<li class="stat">无匹配</li>';
  });
});
