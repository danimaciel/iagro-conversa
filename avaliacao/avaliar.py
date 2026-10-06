"""Avalia o IAgro Conversa com o gabarito, comparando modelos de linguagem pequenos.

Reproduz o que a página faz: busca os 5 trechos mais próximos (no máximo 2 por documento), monta o mesmo prompt
(site/prompt.txt + trechos + pergunta) e pede a resposta ao modelo. Aqui o modelo roda pelo Ollama, no
processador; na página roda no navegador (WebLLM), com os mesmos modelos em versão quantizada.

Mede, por pergunta: a busca trouxe um documento esperado? o modelo citou um trecho desse documento?
disse "não encontrei"? (nas perguntas fora do tema, é o certo). A leitura humana das respostas fica na planilha.

Uso (com o Ollama rodando, depois de baixar os dados e o cache do fluxo):
  python avaliacao/avaliar.py --modelos qwen2.5:1.5b qwen2.5:3b gemma2:2b
Saída: avaliacao/resultado_<modelo>.csv e um resumo na tela.
"""
import argparse
import os
import re
import time
from pathlib import Path

import numpy as np
import pandas as pd
import requests

os.environ.setdefault("HF_HUB_OFFLINE", "1")
RAIZ = Path(__file__).resolve().parents[1]
DADOS = RAIZ / "dados"
NOME_TIPO = {"PUB": "Publicação", "TEC": "Solução tecnológica", "PRJ": "Projeto"}
NAO_SEI = re.compile(r"não encontrei", re.I)

ap = argparse.ArgumentParser()
ap.add_argument("--modelos", nargs="+", default=["qwen2.5:3b"])
ap.add_argument("--n", type=int, default=0, help="só as n primeiras perguntas (0 = todas)")
ap.add_argument("--threads", type=int, default=0, help="núcleos do processador para o Ollama (0 = todos)")
ap.add_argument("--limiar", type=float, default=0.857,
                help="abaixo deste cosseno do melhor trecho não chama o modelo (equivale a 0,852 na página, que usa o e5 q8)")
args = ap.parse_args()

docs = pd.read_parquet(DADOS / "documentos.parquet").set_index("codigo")
tr = pd.read_parquet(DADOS / "base.parquet")
h = pd.read_parquet(DADOS / "cache" / "e5_hash.parquet")["hash"]
E = np.load(DADOS / "cache" / "e5.npy")
pos = pd.Series(np.arange(len(h)), index=h.to_numpy())
tr = tr[tr.hash.isin(pos.index)].reset_index(drop=True)
V = E[pos[tr.hash].to_numpy()].astype(np.float32)
regras = (RAIZ / "site" / "prompt.txt").read_text(encoding="utf-8")
g = pd.read_csv(RAIZ / "avaliacao" / "gabarito_territorial.csv", dtype=str).fillna("")
if args.n:
    g = g.head(args.n)

from sentence_transformers import SentenceTransformer

m = SentenceTransformer("intfloat/multilingual-e5-base")
Q = m.encode(["query: " + p for p in g.pergunta], normalize_embeddings=True)


def fontes(q):
    s = V @ q
    ordem = np.argsort(-s)[:200]
    if s[ordem[0]] < args.limiar:  # como a página: relação fraca, não chama o modelo
        return None
    por, out = {}, []
    for i in ordem:
        c = tr.codigo[i]
        if por.get(c, 0) >= 2:
            continue
        por[c] = por.get(c, 0) + 1
        out.append(i)
        if len(out) == 5:
            break
    return out


def prompt(pergunta, ids):
    ctx = []
    for k, i in enumerate(ids, 1):
        d = docs.loc[tr.codigo[i]]
        pg = f", p. {tr.pagina[i]}" if tr.pagina[i] else ""
        ctx.append(f"[{k}] {d.titulo} ({NOME_TIPO[d.tipo]}, {d.ano or 's.d.'}{pg})\n{tr.texto[i]}")
    return [{"role": "system", "content": regras},
            {"role": "user", "content": "TRECHOS:\n\n" + "\n\n".join(ctx) + f"\n\nPERGUNTA: {pergunta}\n\n"
                                         "Responda à pergunta usando os trechos acima e indique o número de cada trecho usado, como [1]."}]


resumo = []
for modelo in args.modelos:
    linhas = []
    for (_, r), q in zip(g.iterrows(), Q):
        ids = fontes(q)
        esp = set(filter(None, r.docs_esperados.split(";")))
        t0 = time.time()
        if ids is None:
            cods, resp = [], "Não encontrei esse assunto nos documentos da Embrapa Territorial. (filtro de relação fraca)"
        else:
            cods = [tr.codigo[i] for i in ids]
            x = requests.post("http://localhost:11434/api/chat", timeout=900, json={
                "model": modelo, "messages": prompt(r.pergunta, ids), "stream": False,
                "options": {"temperature": 0.2, "num_predict": 450, "num_ctx": 4096,
                            **({"num_thread": args.threads} if args.threads else {})}}).json()
            resp = x["message"]["content"]
        citados = {cods[int(k) - 1] for k in re.findall(r"\[(\d+)\]", resp) if 1 <= int(k) <= len(cods)}
        linhas.append({"id": r.id, "avaliacao": r.avaliacao, "pergunta": r.pergunta, "resposta": resp,
                       "fontes": ";".join(cods), "esperados": r.docs_esperados,
                       "busca_trouxe": bool(esp & set(cods)), "citou_esperado": bool(esp & citados),
                       "citou_algo": bool(citados), "nao_encontrei": bool(NAO_SEI.search(resp)),
                       "segundos": round(time.time() - t0, 1)})
        print(f"{modelo} {r.id} {linhas[-1]['segundos']}s citou_esperado={linhas[-1]['citou_esperado']} "
              f"nao_encontrei={linhas[-1]['nao_encontrei']}", flush=True)
    df = pd.DataFrame(linhas)
    df.to_csv(RAIZ / "avaliacao" / f"resultado_{re.sub(r'[^\w.-]', '_', modelo)}.csv", index=False, encoding="utf-8")
    com, sem = df[df.avaliacao != "X"], df[df.avaliacao == "X"]
    resumo.append({"modelo": modelo, "busca trouxe esperado": f"{com.busca_trouxe.sum()}/{len(com)}",
                   "citou esperado": f"{com.citou_esperado.sum()}/{len(com)}",
                   "'não encontrei' indevido": f"{com.nao_encontrei.sum()}/{len(com)}",
                   "fora do tema: disse não encontrei": f"{sem.nao_encontrei.sum()}/{len(sem)}",
                   "tempo médio (s)": round(df.segundos.mean(), 1)})
print(pd.DataFrame(resumo).to_string(index=False))
