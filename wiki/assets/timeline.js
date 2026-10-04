/* timeline.js — 剧情时间线的**增量增强**（W-4.6-85）
 *
 * 设计原则：静态优先。
 *   - 时间线本体、版本轴、子任务展开（<details>）全部由 build_wiki.py 静态渲染 → 无 JS 也可读；
 *   - 本脚本只做一件静态做不到的事：**按大版本段筛选**（1.x / 2.x / 3.x / 4.x）；
 *   - 因此筛选条由 JS 动态插入 —— 无 JS 时不会出现点了没反应的死按钮。
 *
 * 零依赖 · 不请求网络 · 不改动任何静态内容。
 */
(function () {
  "use strict";

  var root = document.getElementById("timeline-root");
  if (!root) return;

  var list = root.querySelector("ol.tl");
  if (!list) return;

  var items = Array.prototype.slice.call(list.querySelectorAll("li.tl-item"));
  if (!items.length) return;

  /* 按出现顺序收集大版本段（数据已按官方发布顺序排好） */
  var majors = [];
  items.forEach(function (li) {
    var m = (li.getAttribute("data-major") || "").trim();
    if (!m) return;
    if (majors.indexOf(m) === -1) majors.push(m);
  });
  if (majors.length < 2) {
    /* 只有一个大版本段时筛选没有意义，直接不插筛选条 */
    items.forEach(function (li, i) { li.style.setProperty("--i", i); });
    return;
  }

  var bar = document.createElement("div");
  bar.className = "tl-filters";
  bar.setAttribute("role", "group");
  bar.setAttribute("aria-label", "按版本段筛选剧情时间线");

  var info = document.createElement("p");
  info.className = "tl-count";
  info.setAttribute("aria-live", "polite");

  var buttons = [];

  function apply(value) {
    var shown = 0;
    items.forEach(function (li) {
      var m = (li.getAttribute("data-major") || "").trim();
      var hit = value === "all" || m === value;
      li.hidden = !hit;
      if (hit) shown++;
    });
    buttons.forEach(function (b) {
      b.setAttribute("aria-pressed", b.getAttribute("data-major") === value ? "true" : "false");
    });
    info.textContent =
      value === "all"
        ? "显示全部 " + shown + " 个剧情单元"
        : "显示 " + value + ".x 的 " + shown + " 个剧情单元";
  }

  function makeButton(label, value) {
    var b = document.createElement("button");
    b.type = "button";
    b.textContent = label;
    b.setAttribute("data-major", value);
    b.setAttribute("aria-pressed", "false");
    b.addEventListener("click", function () { apply(value); });
    bar.appendChild(b);
    buttons.push(b);
    return b;
  }

  makeButton("全部", "all");
  majors.forEach(function (m) { makeButton(m + ".x", m); });

  root.insertBefore(info, list);
  root.insertBefore(bar, info);

  /* 错峰入场用序号（静态渲染的 --i 已够用；此处兜底补一次） */
  items.forEach(function (li, i) { li.style.setProperty("--i", i); });

  apply("all");
})();
