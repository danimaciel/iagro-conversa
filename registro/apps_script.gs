/**
 * iAgro Conversa: registro mínimo das perguntas numa planilha Google.
 *
 * Como instalar: docs/REGISTRO.md. Resumo: crie uma planilha, abra Extensões > Apps Script, cole este
 * arquivo, implante como "App da Web" (executar como: eu; acesso: qualquer pessoa) e coloque o endereço
 * "…/exec" em REGISTRO_URL, no site/index.html.
 *
 * A página envia três tipos de evento, sem IP, cookie ou identificador de pessoa:
 *   pergunta  — texto (já sem e-mail, CPF e telefone), filtros, se a relação foi fraca, documentos-fonte
 *   ia        — modelo usado, tempo, se deu certo
 *   avaliacao — "ajudou" ou "não ajudou"
 * O campo pid é um código aleatório por pergunta, só para ligar os três eventos.
 */

const ABA = "registro";
const COLUNAS = ["quando", "evento", "pid", "pergunta", "consulta", "tipo", "produto", "estado", "fraca",
  "sem_filtro", "melhor_cos", "fontes", "ms_busca", "modelo", "segundos_ia", "ia_ok", "tokens_s", "erro",
  "ajudou", "versao"];
const EVENTOS = ["pergunta", "ia", "avaliacao"];
const LIMITE_POR_MINUTO = 300;   // proteção simples contra envio em massa
const MESES_GUARDA = 12;

function doPost(e) {
  try {
    if (!e || !e.postData || e.postData.contents.length > 5000) return texto("ignorado");
    const d = JSON.parse(e.postData.contents);
    if (EVENTOS.indexOf(d.ev) < 0) return texto("ignorado");
    if (!dentroDoLimite()) return texto("limite");
    const fontes = Array.isArray(d.fontes) ? d.fontes.slice(0, 10).join(" ") : "";
    const linha = [new Date(), d.ev, d.pid, d.q, d.consulta, d.tipo, d.p, d.e, d.fraca, d.semFiltro, d.melhor,
      fontes, d.ms, d.modelo, d.seg, d.ok, d.tok, d.erro, d.util, d.v].map((v, k) => k === 0 ? v : celula(v));
    const trava = LockService.getScriptLock();
    trava.waitLock(5000);
    try { aba().appendRow(linha); } finally { trava.releaseLock(); }
    return texto("ok");
  } catch (err) {
    return texto("erro");
  }
}

// texto curto e nunca interpretado como fórmula (=, +, -, @ no início viram texto)
function celula(v) {
  if (v === undefined || v === null) return "";
  let s = String(v).slice(0, 500);
  if (/^[=+\-@]/.test(s)) s = "'" + s;
  return s;
}

function aba() {
  const planilha = SpreadsheetApp.getActiveSpreadsheet();
  let a = planilha.getSheetByName(ABA);
  if (!a) {
    a = planilha.insertSheet(ABA);
    a.appendRow(COLUNAS);
    a.setFrozenRows(1);
  }
  return a;
}

function dentroDoLimite() {
  const cache = CacheService.getScriptCache();
  const chave = "n" + Math.floor(Date.now() / 60000);
  const n = Number(cache.get(chave) || 0) + 1;
  cache.put(chave, String(n), 120);
  return n <= LIMITE_POR_MINUTO;
}

function texto(t) {
  return ContentService.createTextOutput(t);
}

/** Apaga registros com mais de 12 meses. Programe um acionador mensal para esta função (docs/REGISTRO.md). */
function apagarAntigos() {
  const a = aba();
  const limite = new Date();
  limite.setMonth(limite.getMonth() - MESES_GUARDA);
  const datas = a.getRange(2, 1, Math.max(a.getLastRow() - 1, 0), 1).getValues();
  let n = 0;
  while (n < datas.length && datas[n][0] instanceof Date && datas[n][0] < limite) n++;
  if (n > 0) a.deleteRows(2, n);
}

/** Teste rápido pelo editor: grava uma linha de exemplo. */
function testar() {
  doPost({postData: {contents: JSON.stringify({ev: "pergunta", v: 1, pid: "teste", q: "teste do registro", tipo: "busca"})}});
}
