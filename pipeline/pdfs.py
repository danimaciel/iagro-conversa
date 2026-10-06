"""Baixa os PDFs com texto completo, extrai o texto página a página e guarda só o texto.

O PDF é descartado logo após a extração. O texto fica em cache (dados/cache/textos.jsonl.gz, um registro por
documento: código, link do PDF, páginas, situação); só PDFs novos ou com link alterado são baixados de novo.
PDF escaneado (sem camada de texto) fica marcado como "sem_texto" e o documento segue só com o resumo.
Falhas de download não entram no cache: são tentadas de novo na execução seguinte.

Download educado: um PDF por vez em cada parte, com pausa entre eles.

Uso:
  python pipeline/pdfs.py listar --partes 4    o que falta baixar, dividido em partes (imprime PARTES=[...])
  python pipeline/pdfs.py baixar --parte 0     baixa e extrai uma parte
  python pipeline/pdfs.py juntar               junta cache + partes
  python pipeline/pdfs.py tudo                 as três etapas numa máquina só
"""
import argparse
import gzip
import json
import re
import time
from pathlib import Path

import pandas as pd
import requests

RAIZ = Path(__file__).resolve().parents[1]
DADOS = RAIZ / "dados"
CACHE = DADOS / "cache" / "textos.jsonl.gz"
PARTES = DADOS / "textos_partes"
PAUSA = 1.0  # segundos entre PDFs, em cada parte
CAB = {"User-Agent": "iAgro (projeto experimental com dados publicos da Embrapa; github.com/danimaciel/iagro-conversa)"}


def ler_cache() -> dict:
    if not CACHE.exists():
        return {}
    with gzip.open(CACHE, "rt", encoding="utf-8") as f:
        return {(r := json.loads(l))["codigo"]: r for l in f}


def limpar(t: str) -> str:
    t = re.sub(r"-\n(?=[a-zà-ú])", "", t)          # palavra quebrada no fim da linha
    t = re.sub(r"[ \t]+", " ", t)
    t = re.sub(r" ?\n ?", "\n", t)
    return re.sub(r"\n{3,}", "\n\n", t).strip()


def extrair(conteudo: bytes) -> list[str]:
    import fitz  # PyMuPDF

    with fitz.open(stream=conteudo, filetype="pdf") as d:
        return [limpar(p.get_text()) for p in d]


def listar(n_partes: int) -> list[int]:
    docs = pd.read_parquet(DADOS / "documentos.parquet")
    docs = docs[docs.texto_completo]
    cache = ler_cache()
    falta = docs[[not (c in cache and cache[c]["pdf"] == u) for c, u in zip(docs.codigo, docs.pdf)]]
    n = min(n_partes, len(falta)) if len(falta) else 0
    falta = falta.assign(parte=[i % n for i in range(len(falta))] if n else [])
    falta[["codigo", "pdf", "parte"]].to_parquet(DADOS / "pdfs_faltam.parquet", index=False)
    print(f"com texto completo {len(docs)} | no cache {len(docs) - len(falta)} | faltam {len(falta)} em {n} partes")
    return list(range(n))


def baixar(parte: int) -> None:
    f = pd.read_parquet(DADOS / "pdfs_faltam.parquet")
    f = f[f.parte == parte]
    PARTES.mkdir(parents=True, exist_ok=True)
    ok = sem = erro = 0
    with open(PARTES / f"parte_{parte}.jsonl", "w", encoding="utf-8") as saida:
        for k, r in enumerate(f.itertuples(), 1):
            for tentativa in range(3):
                try:
                    x = requests.get(r.pdf, headers=CAB, timeout=180)
                    x.raise_for_status()
                    if not x.content.startswith(b"%PDF"):
                        raise ValueError("não é PDF")
                    paginas = extrair(x.content)
                    tem = sum(len(p) for p in paginas) >= 300
                    saida.write(json.dumps({"codigo": r.codigo, "pdf": r.pdf, "situacao": "ok" if tem else "sem_texto",
                                            "paginas": paginas if tem else []}, ensure_ascii=False) + "\n")
                    ok, sem = ok + tem, sem + (not tem)
                    break
                except Exception as ex:  # tenta de novo; na terceira falha, segue
                    if tentativa == 2:
                        erro += 1
                        print(f"  falhou {r.codigo}: {type(ex).__name__}: {str(ex)[:120]}")
                    time.sleep(5 * (tentativa + 1))
            if k % 25 == 0:
                print(f"parte {parte}: {k}/{len(f)}", flush=True)
            time.sleep(PAUSA)
    print(f"parte {parte}: {ok} com texto, {sem} sem texto (escaneados), {erro} falhas")


def juntar() -> None:
    cache = ler_cache()
    for p in sorted(PARTES.glob("parte_*.jsonl")) if PARTES.exists() else []:
        for l in open(p, encoding="utf-8"):
            r = json.loads(l)
            cache[r["codigo"]] = r
    atuais = set(pd.read_parquet(DADOS / "documentos.parquet").codigo)
    CACHE.parent.mkdir(parents=True, exist_ok=True)
    with gzip.open(CACHE, "wt", encoding="utf-8") as f:
        for c, r in cache.items():
            if c in atuais:
                f.write(json.dumps(r, ensure_ascii=False) + "\n")
    regs = [r for c, r in cache.items() if c in atuais]
    print(f"cache de textos: {len(regs)} documentos | com texto {sum(r['situacao'] == 'ok' for r in regs)} | "
          f"{CACHE.stat().st_size / 1e6:.1f} MB")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("acao", choices=["listar", "baixar", "juntar", "tudo"])
    ap.add_argument("--partes", type=int, default=4)
    ap.add_argument("--parte", type=int, default=0)
    a = ap.parse_args()
    if a.acao == "listar":
        print("PARTES=" + json.dumps(listar(a.partes)))
    elif a.acao == "baixar":
        baixar(a.parte)
    elif a.acao == "juntar":
        juntar()
    else:
        for k in listar(1):
            baixar(k)
        juntar()
