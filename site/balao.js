/*
 * iAgro · balão de conversa para portais (ex.: página da Embrapa Territorial no Liferay).
 *
 * Uso — colar uma única vez no modelo das páginas (ou num fragmento HTML):
 *   <script src="https://danimaciel.github.io/iagro-conversa/balao.js" defer></script>
 *
 * Opções (atributos no próprio <script>, todas opcionais):
 *   data-titulo="Pergunte à Embrapa Territorial"   texto do botão e do painel
 *   data-cor="#1f6b45"                            cor do botão
 *   data-posicao="direita" | "esquerda"            canto da tela
 *
 * O chatbot só é carregado quando a pessoa abre o balão: navegar pelo site não baixa nada.
 * A busca e a IA rodam no navegador de quem usa; nenhuma pergunta é enviada a servidor.
 */
(function () {
  "use strict";
  if (window.__iagroBalao) return;            // evita dois balões se o script for incluído duas vezes
  window.__iagroBalao = true;

  var script = document.currentScript || document.querySelector('script[src*="balao.js"]');
  var base = script ? new URL(".", script.src).href : "https://danimaciel.github.io/iagro-conversa/";
  var opt = (script && script.dataset) || {};
  var titulo = opt.titulo || "Pergunte à Embrapa Territorial";
  var cor = opt.cor || "#1f6b45";
  var lado = opt.posicao === "esquerda" ? "left" : "right";

  var css = document.createElement("style");
  css.textContent =
    ".iagro-bt{position:fixed;bottom:20px;" + lado + ":20px;z-index:2147483000;display:flex;align-items:center;gap:8px;" +
    "border:0;border-radius:999px;padding:12px 18px 12px 14px;background:" + cor + ";color:#fff;cursor:pointer;" +
    "font:600 15px/1 system-ui,-apple-system,Segoe UI,Roboto,sans-serif;box-shadow:0 6px 20px rgba(0,0,0,.25)}" +
    ".iagro-bt:hover{filter:brightness(1.08)}.iagro-bt:focus-visible{outline:3px solid #a9cf6e;outline-offset:3px}" +
    ".iagro-bt svg{flex:none}" +
    ".iagro-pn{position:fixed;bottom:84px;" + lado + ":20px;z-index:2147483000;width:420px;height:min(680px,calc(100vh - 110px));" +
    "background:#fff;border-radius:16px;overflow:hidden;box-shadow:0 18px 50px rgba(0,0,0,.30);display:none;flex-direction:column}" +
    ".iagro-pn.aberto{display:flex}" +
    ".iagro-pn header{display:flex;align-items:center;gap:8px;padding:10px 12px;background:" + cor + ";color:#fff;" +
    "font:600 14px system-ui,-apple-system,Segoe UI,Roboto,sans-serif}" +
    ".iagro-pn header span{flex:1}" +
    ".iagro-pn header button{all:unset;cursor:pointer;font-size:20px;line-height:1;padding:2px 6px;border-radius:6px}" +
    ".iagro-pn header button:focus-visible{outline:2px solid #fff}" +
    ".iagro-pn iframe{flex:1;border:0;width:100%}" +
    "@media (max-width:600px){.iagro-pn{left:0;right:0;bottom:0;width:auto;height:100%;border-radius:0}" +
    ".iagro-bt.aberto{display:none}}";
  document.head.appendChild(css);

  var bt = document.createElement("button");
  bt.type = "button";
  bt.className = "iagro-bt";
  bt.setAttribute("aria-expanded", "false");
  bt.setAttribute("aria-controls", "iagro-painel");
  bt.innerHTML =
    '<svg width="22" height="22" viewBox="0 0 24 24" aria-hidden="true"><path fill="currentColor" d="M4 4h16a2 2 0 0 1 2 2v10a2 2 0 0 1-2 2H9l-5 4v-4H4a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2zm3 6.5a1.5 1.5 0 1 0 0 3 1.5 1.5 0 0 0 0-3zm5 0a1.5 1.5 0 1 0 0 3 1.5 1.5 0 0 0 0-3zm5 0a1.5 1.5 0 1 0 0 3 1.5 1.5 0 0 0 0-3z"/></svg>' +
    "<span></span>";
  bt.querySelector("span").textContent = titulo;

  var pn = document.createElement("div");
  pn.className = "iagro-pn";
  pn.id = "iagro-painel";
  pn.setAttribute("role", "dialog");
  pn.setAttribute("aria-label", titulo);
  pn.innerHTML = '<header><span></span><button type="button" aria-label="Fechar">×</button></header>';
  pn.querySelector("header span").textContent = titulo + " · iAgro";

  var carregado = false;
  function abrir(sim) {
    pn.classList.toggle("aberto", sim);
    bt.classList.toggle("aberto", sim);
    bt.setAttribute("aria-expanded", String(sim));
    if (sim && !carregado) {                  // carrega o chatbot só no primeiro clique
      var fr = document.createElement("iframe");
      fr.src = base + "?embed=1&balao=1";
      fr.title = titulo;
      fr.setAttribute("allow", "clipboard-write");
      pn.appendChild(fr);
      carregado = true;
    }
    if (sim) pn.querySelector("header button").focus(); else bt.focus();
  }
  bt.addEventListener("click", function () { abrir(!pn.classList.contains("aberto")); });
  pn.querySelector("header button").addEventListener("click", function () { abrir(false); });
  document.addEventListener("keydown", function (e) {
    if (e.key === "Escape" && pn.classList.contains("aberto")) abrir(false);
  });

  function montar() { document.body.appendChild(pn); document.body.appendChild(bt); }
  if (document.body) montar(); else document.addEventListener("DOMContentLoaded", montar);
})();
