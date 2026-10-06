"""Divide os documentos em trechos (cerca de um parágrafo) para a busca e para o modelo de linguagem.

Cada documento ganha um trecho com título + resumo (página 0). Publicações com texto completo ganham também
trechos de cada página do PDF, de até ~900 caracteres, cortados no fim de frase, com a última frase repetida no
trecho seguinte. Ficha catalográfica, expediente, sumário e listas de referências são descartados.

Grava dados/base.parquet (nome esperado por vetores.py): codigo, pagina, texto, texto_modelo, hash.
Uso:  python pipeline/trechos.py
"""
import gzip
import hashlib
import json
import re
from pathlib import Path

import pandas as pd

RAIZ = Path(__file__).resolve().parents[1]
DADOS = RAIZ / "dados"
MODELO = "intfloat/multilingual-e5-base"
PREFIXO = "passage: "
MAX_TOKENS = 512
TAM = 900
MIN = 150
EXPEDIENTE = re.compile(r"catalogação|todos os direitos reservados|comitê (local )?de publicações|supervisão editorial|"
                        r"normalização bibliográfica|editoração eletrônica|tratamento (das|de) ilustrações|"
                        r"projeto gráfico|\bISSN\b|\bISBN\b|\bCDD\b|exemplares desta publicação|fone:|fax:|www\.embrapa\.br/fale-conosco", re.I)
REFERENCIA = re.compile(r"\b(19|20)\d\d[a-z]?\.\s|et al\.|Disponível em:|Acesso em:", re.I)
AUTOR = re.compile(r"\b[A-ZÀ-Ú]{2,}[A-ZÀ-Ú ]*, (?:[A-Z]\. ?){1,3}[;,.]")  # "MING, L.C.;" de lista de referências
FRASE = re.compile(r"(?<=[.!?;:])\s+(?=[A-ZÀ-Ú0-9(\"“])")


def util(t: str) -> bool:
    if len(t) < MIN or t.count(".....") >= 2:
        return False
    if len(EXPEDIENTE.findall(t)) >= 2 or len(REFERENCIA.findall(t)) >= 4 or len(AUTOR.findall(t)) >= 2:
        return False
    letras, digitos = sum(c.isalpha() for c in t), sum(c.isdigit() for c in t)
    return letras / len(t) >= 0.6 and digitos / len(t) < 0.12  # tabelas numéricas ficam de fora


def cortar(texto: str) -> list[str]:
    texto = re.sub(r"\s+", " ", texto.replace("\n", " ")).strip()
    frases, out, atual = FRASE.split(texto), [], ""
    for f in frases:
        if len(atual) + len(f) + 1 > TAM and atual:
            out.append(atual)
            ult = FRASE.split(atual)[-1]
            atual = (ult + " " if len(ult) < 300 else "") + f
        else:
            atual = (atual + " " + f).strip()
        while len(atual) > TAM * 1.6:  # frase enorme (tabela, lista): corta no espaço
            corte = atual.rfind(" ", 0, TAM)
            out.append(atual[:corte])
            atual = atual[corte + 1:]
    if atual:
        out.append(atual)
    return out


def main() -> None:
    docs = pd.read_parquet(DADOS / "documentos.parquet")
    textos = {}
    arq = DADOS / "cache" / "textos.jsonl.gz"
    if arq.exists():
        with gzip.open(arq, "rt", encoding="utf-8") as f:
            for l in f:
                r = json.loads(l)
                if r["situacao"] == "ok":
                    textos[r["codigo"]] = r["paginas"]

    linhas = []
    for d in docs.itertuples():
        base = d.resumo or d.palavras
        for t in cortar(base) if base else [""]:
            linhas.append((d.codigo, 0, t, d.titulo))
        for pg, txt in enumerate(textos.get(d.codigo, []), 1):
            for t in cortar(txt):
                if util(t):
                    linhas.append((d.codigo, pg, t, d.titulo))
    b = pd.DataFrame(linhas, columns=["codigo", "pagina", "texto", "titulo"])
    b["texto_modelo"] = PREFIXO + (b.titulo.str.rstrip(".") + ". " + b.texto).str.strip()
    b["hash"] = [hashlib.sha1(f"{MODELO}|{MAX_TOKENS}|{t}".encode("utf-8")).hexdigest() for t in b.texto_modelo]
    b = b.drop(columns="titulo")
    b.to_parquet(DADOS / "base.parquet", index=False)
    print(f"{len(docs)} documentos ({len(textos)} com texto completo) | {len(b)} trechos "
          f"({(b.pagina > 0).sum()} do texto completo) | {b.texto.str.len().sum() / 1e6:.1f} milhões de caracteres")


if __name__ == "__main__":
    main()
