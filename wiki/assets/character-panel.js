/* character-panel.js — 角色直达面板的**增量增强**（W-4.6-94）
 *
 * 静态优先：面板、筛选 chips、全部卡片均由 build_wiki.py 静态渲染 → 无 JS 也可直接点击。
 * 本脚本只做静态做不到的事：按 命途×属性×星级 叠加筛选（AND 语义），实时更新计数，一键重置。
 * 纪律：只切换 li.citem 的 hidden，**不重排 DOM**；零依赖 · 不请求网络 · 不改动任何静态内容。
 */
(function () {
  "use strict";

  var root = document.getElementById("character-panel");
  if (!root) return;

  var grid = root.querySelector("ul.cgrid");
  if (!grid) return;

  var items = Array.prototype.slice.call(grid.querySelectorAll("li.citem"));
  if (!items.length) return;

  var chips = Array.prototype.slice.call(root.querySelectorAll("button.chip"));
  var countEl = document.getElementById("cp-count");
  var reset = document.getElementById("cp-reset");

  /* 当前筛选状态：空串 = 该组不约束 */
  var sel = { path: "", element: "", rarity: "" };

  function apply() {
    var shown = 0;
    items.forEach(function (li) {
      var hit = true;
      for (var g in sel) {
        if (sel[g] && li.getAttribute("data-" + g) !== sel[g]) {
          hit = false;
          break;
        }
      }
      li.hidden = !hit;
      if (hit) shown++;
    });
    if (countEl) countEl.textContent = "显示 " + shown + " / " + items.length;
  }

  chips.forEach(function (b) {
    b.addEventListener("click", function () {
      var g = b.getAttribute("data-group");
      var v = b.getAttribute("data-value") || "";
      sel[g] = v;
      chips.forEach(function (x) {
        if (x.getAttribute("data-group") === g) {
          x.setAttribute("aria-pressed", x === b ? "true" : "false");
        }
      });
      apply();
    });
  });

  if (reset) {
    reset.addEventListener("click", function () {
      sel = { path: "", element: "", rarity: "" };
      chips.forEach(function (b) {
        b.setAttribute("aria-pressed",
          (b.getAttribute("data-value") || "") === "" ? "true" : "false");
      });
      apply();
    });
  }

  apply();
})();

/* ===================================================================
 * hero 过场动画（R2，方案 α-2：并入本脚本 —— 零新请求、零竞态、零 HTML 改动）
 * -------------------------------------------------------------------
 * 流程：首次点击某角色卡 → 插入 .hero-overlay 播 840ms 过场 → 跳转详情页。
 * 铁律：
 *   1. e.preventDefault() 只能在 overlay **插入成功之后**调用；
 *      任何异常路径都直接 return，放行浏览器原生跳转（最坏 = 回到没有动画的今天）。
 *   2. 只新增运行时节点（overlay），不改动任何静态内容、不重排网格、不加静态类名。
 *   3. 零依赖、零外链、零新请求；256px 立绘**点播时**才创建 img 元素；
 *      无立绘角色（缺 avatar 图标的那 4 个）直接走 SVG 剪影，连请求都不发，因此不会出现坏图。
 *   4. 每会话每角色只播一次（sessionStorage 键 hsr-hero-v1）；
 *      存储不可用 / prefers-reduced-motion:reduce → 不播、不记账，直接原生跳转。
 *   5. 无障碍：overlay aria-hidden，不移动焦点、不加 role=dialog、内部无 tabindex；
 *      Esc 与点击 overlay 都是「跳过并继续跳转」；键盘 Enter 与鼠标走同一条路径。
 * =================================================================== */
(function () {
  "use strict";

  var panel = document.getElementById("character-panel");
  if (!panel) return;

  var STORE = "hsr-hero-v1";
  var DEFAULT_MS = 840;      /* 与 style.css 的 --hero-total 默认值一致；运行时以 CSS 为准 */
  var nav = false;           /* navigateOnce 幂等标志 */
  var overlay = null;        /* 当前过场层；null = 没有 */
  var pendingHref = "";
  var timers = [];

  function reduceMotion() {
    try {
      if (!window.matchMedia) return false;
      var m = window.matchMedia("(prefers-reduced-motion: reduce)");
      return !!(m && m.matches);
    } catch (e) {
      return false;
    }
  }

  /* 读：返回数组 = 已播过的 id；返回 null = 存储不可用（保守视为「已看过」） */
  function readStore() {
    try {
      var raw = window.sessionStorage.getItem(STORE);
      if (!raw) return [];
      var a = JSON.parse(raw);
      if (!a || typeof a.length !== "number") return null;
      var out = [];
      for (var i = 0; i < a.length; i++) out.push(String(a[i]));
      return out;
    } catch (e) {
      return null;
    }
  }

  function writeStore(id) {
    try {
      var a = readStore();
      if (!a) return;
      if (a.length > 300) a = [];   /* 防脏数据撑爆；94 个角色远达不到 */
      if (a.indexOf(id) < 0) a.push(id);
      window.sessionStorage.setItem(STORE, JSON.stringify(a));
    } catch (e) { /* 隐私模式：静默忽略 */ }
  }

  /* 总时长以 CSS 变量 --hero-total 为唯一真相源 */
  function heroTotal() {
    try {
      var v = window.getComputedStyle(document.documentElement)
        .getPropertyValue("--hero-total");
      var n = parseFloat(String(v));
      if (n && isFinite(n) && n > 0) return n;
    } catch (e) { /* 忽略 */ }
    return DEFAULT_MS;
  }

  /* 首帧（背板 + 擦除）时长 = --hero-total 的 1/7（CSS 里 21 步中的 3 步，默认 120ms）。
     与 CSS 同源：改 --hero-total 一个变量，data-state 的 enter→hero 切换点也跟着缩放，
     不再在 JS 里留一处 120ms 硬编码（P1-2 的另一半）。 */
  function heroEnterMs() {
    return heroTotal() / 7;
  }

  function clearTimers() {
    for (var i = 0; i < timers.length; i++) {
      try { window.clearTimeout(timers[i]); } catch (e) { /* 忽略 */ }
    }
    timers = [];
  }

  function tag(node) {
    return node && node.tagName ? String(node.tagName).toLowerCase() : "";
  }

  /* 从点击目标向上找 <a class="ccard">（不依赖 Element.closest，兼容老浏览器） */
  function cardOf(node) {
    while (node && node !== document) {
      if (tag(node) === "a" && String(node.className || "").indexOf("ccard") >= 0) {
        return node;
      }
      node = node.parentNode;
    }
    return null;
  }

  /* 实体 id = href 末段的 <数字>.html（94/94 可解析；解析失败则不播） */
  function cardId(a) {
    var href = String(a.getAttribute("href") || "");
    var p = href.split("#")[0].split("?")[0];
    var seg = p.substring(p.lastIndexOf("/") + 1);
    var m = /^([0-9]+)\.html$/i.exec(seg);
    return m ? m[1] : "";
  }

  /* pages/ 之前的前缀（角色总索引页实测为 "../../"），用于拼 assets 路径 */
  function upOf(href) {
    var i = String(href).indexOf("pages/");
    return i > 0 ? String(href).substring(0, i) : "";
  }

  function el(name, cls, txt) {
    var n = document.createElement(name);
    if (cls) n.className = cls;
    if (txt != null) n.textContent = txt;
    return n;
  }

  function txtOf(root, sel) {
    if (!root || !root.querySelector) return "";
    var n = root.querySelector(sel);
    return n && n.textContent ? String(n.textContent).replace(/^\s+|\s+$/g, "") : "";
  }

  function attrOf(node, name) {
    return node && node.getAttribute ? String(node.getAttribute(name) || "") : "";
  }

  /* 剪影降级节点：纯 CSS data URI，零请求 */
  function silhouette() {
    return el("span", "hero-art hero-art-sil");
  }

  function buildOverlay(a) {
    var href = attrOf(a, "href");
    var id = cardId(a);
    var up = upOf(href);
    var li = a.parentNode;

    var o = el("div", "hero-overlay");
    o.setAttribute("aria-hidden", "true");
    o.setAttribute("data-state", "enter");

    var stage = el("div", "hero-stage");
    stage.appendChild(el("span", "hero-frame"));
    stage.appendChild(el("span", "hero-spine"));
    stage.appendChild(el("span", "hero-br hero-br-tl"));
    stage.appendChild(el("span", "hero-br hero-br-tr"));
    stage.appendChild(el("span", "hero-br hero-br-bl"));
    stage.appendChild(el("span", "hero-br hero-br-br"));

    /* 主视觉：先放已在缓存里的 avatar（首帧即有形），256px 立绘加载完再叠上去 */
    var wrap = el("div", "hero-art-wrap");
    var icon = a.querySelector ? a.querySelector("img.cicon") : null;
    var iconSrc = icon ? attrOf(icon, "src") : "";
    if (iconSrc && id && up) {
      var base = el("img", "hero-art hero-art-base");
      base.setAttribute("src", iconSrc);
      base.setAttribute("alt", "");
      wrap.appendChild(base);

      var top = el("img", "hero-art hero-art-top");
      top.setAttribute("alt", "");
      top.onload = function () {
        top.className = "hero-art hero-art-top is-ready";
      };
      top.onerror = function () {
        /* 立绘缺失：撤掉这一层，露出下面已缓存的小图，绝不出现坏图图标 */
        if (top.parentNode) top.parentNode.removeChild(top);
      };
      top.setAttribute("src", up + "assets/icons/character/" + id + ".png");
      wrap.appendChild(top);
    } else {
      /* 无 avatar 图标的那 4 个角色：连请求都不发，直接剪影 */
      wrap.appendChild(silhouette());
    }
    stage.appendChild(wrap);

    var name = txtOf(a, ".cname") || attrOf(a, "aria-label");
    if (name) stage.appendChild(el("p", "hero-name", name));

    /* 数据条：优先用 li 上的 data-*，回退到 .csub 按「·」切；解析失败的整行不出现 */
    var elem = attrOf(li, "data-element");
    var path = attrOf(li, "data-path");
    var star = attrOf(li, "data-rarity") || txtOf(a, ".cstar");
    if (!elem || !path) {
      var parts = txtOf(a, ".csub").split("·");
      if (!elem) elem = parts[0] || "";
      if (!path) path = parts[1] || "";
    }
    var rows = [["属性", elem], ["命途", path], ["星级", star]];
    var shown = 0;
    var ul = el("ul", "hero-stats");
    for (var i = 0; i < rows.length; i++) {
      if (!rows[i][1]) continue;
      var line = el("li", "hero-stat");
      line.appendChild(el("span", "hero-k", rows[i][0]));
      line.appendChild(document.createElement("b")).textContent = rows[i][1];
      ul.appendChild(line);
      shown++;
    }
    if (shown) stage.appendChild(ul);

    stage.appendChild(el("p", "hero-hint", "Esc / 点击 跳过"));
    o.appendChild(stage);

    /* 冷光扫过：整层宽度的窄条，由 overlay 的 overflow 裁住 */
    o.appendChild(el("span", "hero-sweep"));
    return o;
  }

  /* 播报节点挂在 body 上而不是 overlay 内：overlay 是 aria-hidden，
     放在里面读屏软件根本收不到（对设计样例的这一处做了修正）。 */
  function announce(text) {
    try {
      var st = el("p", "sr-only");
      st.setAttribute("role", "status");
      st.setAttribute("aria-live", "polite");
      st.textContent = text;
      document.body.appendChild(st);
      timers.push(window.setTimeout(function () {
        if (st.parentNode) st.parentNode.removeChild(st);
      }, 1200));
    } catch (e) { /* 播报不是关键路径 */ }
  }

  function dropOverlay() {
    clearTimers();
    if (overlay && overlay.parentNode) overlay.parentNode.removeChild(overlay);
    overlay = null;
  }

  function navigateOnce(href) {
    if (nav) return;
    nav = true;
    clearTimers();
    if (!href) { dropOverlay(); return; }
    try {
      window.location.assign(href);
    } catch (e) {
      try { window.location.href = href; } catch (e2) { /* 放弃 */ }
    }
  }

  function startHero(a, id) {
    var o = buildOverlay(a);
    document.body.appendChild(o);      /* 插入成功 = 后续动作安全的起点 */
    overlay = o;
    o.addEventListener("click", function () { navigateOnce(pendingHref); }, false);

    writeStore(id);                    /* 在 enter 状态记账：中途跳走/返回都不会重播 */
    announce(txtOf(a, ".cname") ? "正在打开 " + txtOf(a, ".cname") : "正在打开角色页");
    /* data-state 只是可观测的调试属性（视觉由 CSS 关键帧驱动）：enter → hero（3 步 = 120ms） */
    timers.push(window.setTimeout(function () {
      if (overlay === o) o.setAttribute("data-state", "hero");
    }, heroEnterMs()));
    timers.push(window.setTimeout(function () { navigateOnce(pendingHref); }, heroTotal()));
  }

  function onCardClick(e) {
    if (e.defaultPrevented) return;
    /* 修饰键 / 非主键：完全不拦截，「新标签打开」等原生能力优先 */
    if (e.metaKey || e.ctrlKey || e.shiftKey || e.altKey) return;
    if (typeof e.button === "number" && e.button !== 0) return;

    var a = cardOf(e.target);
    if (!a) return;
    var href = attrOf(a, "href");
    if (!href) return;

    if (overlay) {                       /* 过场中再次触发：视为「跳过」 */
      pendingHref = href;
      if (e.preventDefault) e.preventDefault();
      navigateOnce(href);
      return;
    }
    if (reduceMotion()) {                /* reduced-motion：不插层、不记账，直接原生跳转 */
      try { a.className = a.className ? a.className + " hero-static" : "hero-static"; }
      catch (err) { /* 忽略 */ }
      return;
    }

    var id = cardId(a);
    if (!id) return;                      /* 解析不出实体 id → 原生跳转 */
    var seen = readStore();
    if (seen === null) return;            /* 存储不可用 → 视为已看过 */
    if (seen.indexOf(id) >= 0) return;     /* 本会话已播过 → 原生跳转（不重播） */

    pendingHref = href;
    try {
      startHero(a, id);
    } catch (err) {
      dropOverlay();                      /* 失败即清理，然后放行原生跳转 */
      return;
    }
    if (e.preventDefault) e.preventDefault();
  }

  function onKeyDown(e) {
    if (!overlay) return;
    var k = e.key || "";
    if (k !== "Escape" && k !== "Esc" && e.keyCode !== 27) return;
    if (e.preventDefault) e.preventDefault();
    navigateOnce(pendingHref);
  }

  /* 从详情页「返回」时 bfcache 可能带回残留过场层：清掉并复位 */
  function onPageShow(e) {
    if (!e || !e.persisted) return;
    dropOverlay();
    nav = false;
    pendingHref = "";
  }

  panel.addEventListener("click", onCardClick, false);
  document.addEventListener("keydown", onKeyDown, true);
  window.addEventListener("pageshow", onPageShow, false);
})();
