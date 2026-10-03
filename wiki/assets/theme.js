(function(){
  var KEY='hsr-theme';
  var ORDER=['system','light','dark'];
  function read(){ try{ var v=localStorage.getItem(KEY); return (v==='light'||v==='dark'||v==='system')?v:'system'; }catch(e){ return 'system'; } }
  function save(v){ try{ localStorage.setItem(KEY,v); }catch(e){} }
  function apply(v){
    var el=document.documentElement;
    if(v==='system'){ el.removeAttribute('data-theme'); } else { el.setAttribute('data-theme',v); }
  }
  function label(v){ return v==='system' ? '跟随系统' : (v==='dark' ? '暗色' : '亮色'); }
  var state=read(); apply(state);
  function paint(){
    var b=document.getElementById('theme-toggle'); if(!b) return;
    b.textContent=label(state);
    b.setAttribute('aria-label','当前主题：'+label(state)+'（点击切换）');
    b.setAttribute('title','当前主题：'+label(state)+'（依次切换：跟随系统 → 亮色 → 暗色）');
  }
  function toggle(){
    state=ORDER[(ORDER.indexOf(state)+1)%ORDER.length];
    apply(state); save(state); paint();
  }
  document.addEventListener('DOMContentLoaded',function(){
    var b=document.getElementById('theme-toggle');
    if(b) b.addEventListener('click',toggle);
    paint();
  });
})();
