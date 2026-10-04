/* home.js — 首页仪表盘（W-4.6-87）
 *
 * 职责：把 build_wiki.py 生成的 data/stats.js 渲染到首页的三个容器里。
 * 设计原则（与时间线一致）：
 *   - 静态优先：路径/入口/降级文案都在 HTML 里，无 JS 也能看清站点有什么；
 *   - 本脚本只填「统计数字」与「最新收录」这两块需要构建期数据的区域；
 *   - 零依赖、不请求网络、不改动静态内容。
 */
(function () {
  "use strict";

  var S = window.STATS;
  var root = document.getElementById("dash-root");
  if (!root || !S) return;

  function set(id, text) {
    var el = document.getElementById(id);
    if (el) el.textContent = text;
  }

  /* 1) 概览条：库内最高版本 / 页数 / 最近更新 */
  set("dash-version", S.latestVersion || "—");
  set("dash-pages", (S.pages || 0).toLocaleString("zh-CN"));
  set("dash-updated", S.updatedMax || "—");

  /* 2) 版本与日期覆盖（次级信息，避免单值误读） */
  var dist = Object.keys(S.versions || {}).map(function (v) {
    return v + " × " + S.versions[v].toLocaleString("zh-CN");
  }).join(" ｜ ");
  set("dash-versions", dist || "—");
  if (S.versionedPages != null && S.pages) {
    var note = document.getElementById("dash-coverage");
    if (note) {
      note.textContent = "带版本标记 " + S.versionedPages.toLocaleString("zh-CN")
        + " / " + S.pages.toLocaleString("zh-CN") + " 页；带时间标记 "
        + (S.datedPages || 0).toLocaleString("zh-CN") + " 页";
    }
  }

  /* 3) 最新收录：按 `> 更新时间：` 倒序（构建期已排好序） */
  var list = document.getElementById("dash-recent");
  if (!list) return;
  var recent = (S.recent || []).slice(0, 12);
  if (!recent.length) {
    list.innerHTML = '<li class="dash-empty">暂无带更新时间的条目。</li>';
    return;
  }

  function safe(s) {
    return String(s == null ? "" : s)
      .replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;");
  }
  /* 与 app.js 一致：按段 encodeURIComponent，避免中文/空格/保留字符破链 */
  function href(p) {
    return "pages/" + String(p).split("/").map(encodeURIComponent).join("/");
  }

  var html = "";
  recent.forEach(function (r) {
    html += '<li class="dash-item">'
      + '<a class="dash-link" href="' + safe(href(r.path)) + '">' + safe(r.title) + '</a>'
      + '<span class="dash-tag">' + safe(r.categoryLabel || r.category || "—") + '</span>'
      + '<span class="dash-date">' + safe(r.updated) + '</span>'
      + '</li>';
  });
  list.innerHTML = html;
  list.setAttribute("data-count", String(recent.length));
})();
