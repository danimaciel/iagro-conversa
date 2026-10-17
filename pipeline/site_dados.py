"""Gera os dados da página do IAgro Conversa (site/dados/) a partir dos documentos, trechos e vetores.

  site/dados/docs.json       documentos: título, ano, tipo, detalhe, link, unidade, autores, onde encontrar
  site/dados/trechos.json    de cada trecho: índice do documento e página (0 = título + resumo)
  site/dados/bits.bin        vetor de cada trecho em 1 bit por dimensão (96 bytes), já centrado
  site/dados/vet/NN.bin      vetor completo de cada trecho em int8, lido só nas linhas dos candidatos (HTTP Range)
  site/dados/tx/NNNN.json    texto dos trechos em blocos de 256, baixados só quando usados
  site/dados/info.json       totais, média dos vetores, escala, data da exportação

Produtos e localização (desde 17/10/2026): do Observatório de Pesquisa da Embrapa (release pública
"enriquecimento-AAAA-MM" em danimaciel/observatorio_embrapa, baixada para dados/enriquecimento/ pelo fluxo).
Só produtos de força "principal" (título ou palavras-chave). Em docs.json: pp (produtos), uf (estados), bi (biomas).

Uso:  python pipeline/site_dados.py 2026-10
"""
import json
import shutil
import sys
from pathlib import Path

import numpy as np
import pandas as pd

RAIZ = Path(__file__).resolve().parents[1]
DADOS = RAIZ / "dados"
SAIDA = RAIZ / "site" / "dados"
BLOCO = 256
LINHAS_VET = 32768
TIPOS = ["PUB", "TEC", "PRJ"]
MESES = "janeiro fevereiro março abril maio junho julho agosto setembro outubro novembro dezembro".split()


def enriquecimento(docs: pd.DataFrame):
    pasta = DADOS / "enriquecimento"
    if not (pasta / "enriquecimento.csv.gz").exists():
        print("sem arquivo de enriquecimento: página sem produtos e localização")
        return None, None
    e = pd.read_csv(pasta / "enriquecimento.csv.gz", dtype=str).fillna("").set_index("doc_uid")
    reg = pd.read_csv(pasta / "registro_obra.csv.gz", dtype=str)
    obra = dict(zip(reg.registro.str[2:], reg.obra_id))
    tax = pd.read_csv(pasta / "produtos.csv", dtype=str).fillna("")

    def uid(cod):
        t, n = cod.split()
        return obra.get(n, "OB:" + n) if t == "PUB" else ("P:" if t == "PRJ" else "T:") + n
    return e.reindex([uid(c) for c in docs.codigo]).fillna(""), tax


def main(mes: str) -> None:
    docs = pd.read_parquet(DADOS / "documentos.parquet").reset_index(drop=True)
    tr = pd.read_parquet(DADOS / "base.parquet")
    h = pd.read_parquet(DADOS / "cache" / "e5_hash.parquet")["hash"]
    E = np.load(DADOS / "cache" / "e5.npy")
    pos = pd.Series(np.arange(len(h)), index=h.to_numpy())
    tr = tr[tr.hash.isin(pos.index)].reset_index(drop=True)
    idoc = {c: i for i, c in enumerate(docs.codigo)}

    V = E[pos[tr.hash].to_numpy()].astype(np.float32)
    mu = V.mean(0)
    escala = float(np.abs(V).max())

    if SAIDA.exists():
        shutil.rmtree(SAIDA)
    for sub in ("vet", "tx"):
        (SAIDA / sub).mkdir(parents=True)
    np.packbits(V - mu > 0, axis=1).tofile(SAIDA / "bits.bin")
    v8 = np.round(V / escala * 127).astype(np.int8)
    for k in range(0, len(v8), LINHAS_VET):
        v8[k:k + LINHAS_VET].tofile(SAIDA / "vet" / f"{k // LINHAS_VET:02d}.bin")
    for k in range(0, len(tr), BLOCO):
        (SAIDA / "tx" / f"{k // BLOCO:04d}.json").write_text(
            json.dumps(tr.texto.iloc[k:k + BLOCO].tolist(), ensure_ascii=False, separators=(",", ":")), encoding="utf-8")

    enr, tax = enriquecimento(docs)
    produtos = {}
    if enr is not None:
        usados = {x for v in enr.produtos for x in v.split(";") if x}
        produtos = {r.produto_id: {"nome": r.produto, "cat": r.categoria_ampla}
                    for r in tax.itertuples() if r.produto_id in usados}
    lista = []
    for n, d in enumerate(docs.itertuples()):
        x = {"c": d.codigo, "t": d.titulo, "a": d.ano, "k": TIPOS.index(d.tipo), "d": d.detalhe, "l": d.link, "u": d.unidade}
        if d.autores:
            x["au"] = d.autores if len(d.autores) <= 160 else d.autores[:160].rsplit(";", 1)[0] + "; et al."
        if d.onde:
            x["o"] = d.onde
        if d.texto_completo:
            x["pdf"] = d.pdf
        if enr is not None:
            linha = enr.iloc[n]
            for chave, col in (("pp", "produtos"), ("uf", "ufs"), ("bi", "biomas")):
                v = [y for y in linha[col].split(";") if y]
                if v:
                    x[chave] = v
        lista.append(x)
    (SAIDA / "docs.json").write_text(json.dumps(lista, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    (SAIDA / "trechos.json").write_text(json.dumps({"d": [idoc[c] for c in tr.codigo], "p": tr.pagina.astype(int).tolist()},
                                                   separators=(",", ":")), encoding="utf-8")
    com_texto = tr[tr.pagina > 0].codigo.nunique()
    info = {
        "exportacao": f"{MESES[int(mes[5:]) - 1]} de {mes[:4]}", "mes": mes,
        "unidades": sorted(docs.unidade.unique().tolist()),
        "n": len(tr), "dim": int(V.shape[1]), "bloco": BLOCO, "linhas_vet": LINHAS_VET, "escala": escala,
        "documentos": len(docs), "publicacoes": int((docs.tipo == "PUB").sum()), "solucoes": int((docs.tipo == "TEC").sum()),
        "projetos": int((docs.tipo == "PRJ").sum()), "com_texto_completo": int(com_texto),
        "media": [round(float(x), 6) for x in mu],
        "produtos": produtos,
    }
    (SAIDA / "info.json").write_text(json.dumps(info, ensure_ascii=False), encoding="utf-8")
    tam = sum(f.stat().st_size for f in SAIDA.rglob("*") if f.is_file()) / 1e6
    print(f"{len(docs)} documentos ({com_texto} com texto completo) | {len(tr)} trechos | total {tam:.0f} MB")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "2026-10")
