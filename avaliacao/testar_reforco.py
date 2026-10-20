"""Testa um reforço por palavras do título na ordenação da busca. NÃO ADOTADO (20/10/2026).

Resultado: não piora o gabarito (23/23 em todos os pesos; posição média 1,13 → 1,09 com 0,03), mas não
resolve "Como é feito o escoamento da produção de soja?": premia palavras comuns (produção, soja) e os
documentos de macrologística nem entram entre os 200 candidatos. A página não usa este reforço.

Reproduz a busca da página (5 trechos, no máximo 2 por documento, vaga para projeto/solução) sobre os vetores
completos e soma ao cosseno REFORCO × (fração das palavras da pergunta presentes no título do documento).
Mede, no gabarito e em perguntas extras: o documento esperado aparece entre as 5 fontes? em que posição?

Uso: python avaliacao/testar_reforco.py
"""
import re
import unicodedata
from pathlib import Path

import numpy as np
import pandas as pd
from sentence_transformers import SentenceTransformer

RAIZ = Path(__file__).resolve().parents[1]
DADOS = RAIZ / "dados"
PARADAS = set("a o as os de da do das dos e em no na nos nas um uma para por com sem que qual quais como onde tem "
              "existe sobre ao aos se sua seu ou mais menos ser sao foi pode podem esta este essa esse isso".split())


def sem_acento(t):
    t = unicodedata.normalize("NFD", str(t).lower())
    return "".join(c for c in t if unicodedata.category(c) != "Mn")


def palavras(t):
    return {w for w in re.findall(r"[a-z0-9]+", sem_acento(t)) if len(w) > 3 and w not in PARADAS}


radical = lambda w: w[:5] if len(w) > 5 else w

docs = pd.read_parquet(DADOS / "documentos.parquet").set_index("codigo")
tr = pd.read_parquet(DADOS / "base.parquet")
h = pd.read_parquet(DADOS / "cache" / "e5_hash.parquet")["hash"]
E = np.load(DADOS / "cache" / "e5.npy")
pos = pd.Series(np.arange(len(h)), index=h.to_numpy())
tr = tr[tr.hash.isin(pos.index)].reset_index(drop=True)
V = E[pos[tr.hash].to_numpy()].astype(np.float32)
PT = np.where(tr.codigo.str[:3].isin(["PRJ", "TEC"]))[0]
tk_doc = {c: {radical(w) for w in palavras(t)} for c, t in docs.titulo.items()}
tk = np.array([tk_doc.get(c, set()) for c in tr.codigo], dtype=object)

g = pd.read_csv(RAIZ / "avaliacao" / "gabarito_territorial.csv", dtype=str).fillna("")
g = g[g.avaliacao != "X"]
extras = pd.DataFrame([  # formulações do teste da usuária (20/10/2026): esperado = macrologística/escoamento
    ("E01", "Como é feito o escoamento da produção de soja?"),
    ("E02", "como escoar produção de soja?"),
    ("E03", "Logística de escoamento da soja no Brasil"),
], columns=["id", "pergunta"])
m = SentenceTransformer("intfloat/multilingual-e5-base")
Qg = m.encode(["query: " + p for p in g.pergunta], normalize_embeddings=True)
Qe = m.encode(["query: " + p for p in extras.pergunta], normalize_embeddings=True)


def fontes(q, texto, lam):
    s = V @ q
    cand = np.argsort(-s)[:200]
    ch = list({radical(w) for w in palavras(texto)})
    if lam and ch:
        bonus = np.array([sum(c in tk[i] for c in ch) / len(ch) for i in cand])
        cand = cand[np.argsort(-(s[cand] + lam * bonus), kind="stable")]
    por, out = {}, []
    for i in cand:
        c = tr.codigo[i]
        if por.get(c, 0) >= 2:
            continue
        por[c] = por.get(c, 0) + 1
        out.append(i)
        if len(out) == 5:
            break
    if not any(tr.codigo[i][:3] in ("PRJ", "TEC") for i in out):
        b = PT[np.argmax(s[PT])]
        if s[b] >= s[out[-1]] - 0.015:
            out[-1] = b
    return [tr.codigo[i] for i in out]


print("Gabarito (23 perguntas com resposta):")
for lam in [0, 0.01, 0.02, 0.03, 0.05, 0.08]:
    trouxe, posicoes, perdeu = 0, [], []
    for (r, q) in zip(g.itertuples(), Qg):
        esp = set(r.docs_esperados.split(";"))
        cods = fontes(q, r.pergunta, lam)
        k = next((n for n, c in enumerate(cods) if c in esp), None)
        if k is not None:
            trouxe += 1
            posicoes.append(k + 1)
        else:
            perdeu.append(r.id)
    print(f"  reforço {lam:<5} trouxe {trouxe}/{len(g)} · posição média do 1º esperado {np.mean(posicoes):.2f}"
          + (f" · perdeu: {', '.join(perdeu)}" if perdeu else ""))

print("\nFormulações de escoamento da soja (títulos das 3 primeiras fontes):")
for lam in [0, 0.02, 0.03, 0.05]:
    print(f"  reforço {lam}")
    for (r, q) in zip(extras.itertuples(), Qe):
        cods = fontes(q, r.pergunta, lam)[:3]
        print(f"    {r.pergunta[:48]:48} → " + " || ".join(str(docs.titulo.get(c, c))[:45] for c in cods))
