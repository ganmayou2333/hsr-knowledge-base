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
