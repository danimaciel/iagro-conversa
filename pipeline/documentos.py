"""Lista os documentos da(s) unidade(s) do IAgro Conversa a partir das exportações do Redape.

Grava dados/documentos.parquet: publicações, soluções tecnológicas e projetos, com o link do PDF.
Texto completo só para publicações cujo PDF está na Infoteca-e (publicações técnicas editadas pela
própria Embrapa: folhetos, livros, folders, mapas, relatórios). As do Alice (artigos de periódicos,
trabalhos de eventos, teses, capítulos em livros de outras editoras) ficam com título e resumo.

Uso:  python pipeline/documentos.py 2026-10
      UNIDADES="Embrapa Territorial;Embrapa Solos" python pipeline/documentos.py 2026-10
"""
import os
import re
import sys
from pathlib import Path

import pandas as pd

RAIZ = Path(__file__).resolve().parents[1]
UNIDADES = [u.strip() for u in os.getenv("UNIDADES", "Embrapa Territorial").split(";") if u.strip()]


def limpo(t) -> str:
    return re.sub(r"\s+", " ", str(t)).strip() if isinstance(t, str) else ""


def da_unidade(col: pd.Series) -> pd.Series:
    return col.fillna("").map(lambda u: any(x in u for x in UNIDADES))


def main(mes: str) -> None:
    d = RAIZ / "dados" / mes
    ler = lambda nome: pd.read_csv(d / f"{nome}-da-embrapa-{mes}.csv", dtype=str)
    linhas = []

    pub = ler("publicacoes")
    for _, r in pub[da_unidade(pub["Unidade"])].iterrows():
        pdf = limpo(r["URL do arquivo"])
        linhas.append({
            "codigo": f"PUB {r['ID']}", "tipo": "PUB", "titulo": limpo(r["Título"]), "resumo": limpo(r["Resumo"]),
            "ano": limpo(r["Ano de publicação"]), "detalhe": limpo(r["Tipo de publicação"]),
            "unidade": limpo(r["Unidade"]), "autores": limpo(r["Autores"]), "palavras": limpo(r["Palavras-chave"]),
            "link": limpo(r["Página da publicação no Portal Embrapa"]), "onde": "", "bioma": "",
            "pdf": pdf, "texto_completo": "infoteca.cnptia.embrapa.br" in pdf,
        })
    prj = ler("projetos")
    for _, r in prj[da_unidade(prj["Unidade líder"])].iterrows():
        linhas.append({
            "codigo": f"PRJ {r['ID']}", "tipo": "PRJ", "titulo": limpo(r["Título"]), "resumo": limpo(r["Resumo"]),
            "ano": limpo(r["mês/ano de início"])[-4:],
            "detalhe": f"{limpo(r['Situação'])}; {limpo(r['mês/ano de início'])} a {limpo(r['mês/ano de finalização'])}",
            "unidade": limpo(r["Unidade líder"]), "autores": "", "palavras": limpo(r["Palavras-chave"]),
            "link": limpo(r["Página do projeto no Portal Embrapa"]), "onde": "", "bioma": "", "pdf": "", "texto_completo": False,
        })
    tec = ler("solucoes-tecnologicas")
    for _, r in tec[da_unidade(tec["Unidade responsável"])].iterrows():
        linhas.append({
            "codigo": f"TEC {r['ID']}", "tipo": "TEC", "titulo": limpo(r["Nome"]), "resumo": limpo(r["Descrição"]),
            "ano": limpo(r["Ano de lançamento"]), "detalhe": " - ".join(x for x in (limpo(r["Tipo"]), limpo(r["Subtipo"])) if x),
            "unidade": limpo(r["Unidade responsável"]), "autores": "", "palavras": limpo(r["Palavras-chave"]),
            "link": limpo(r["Página da tecnologia no Portal Embrapa"]), "onde": limpo(r["Onde encontrar"]),
            "bioma": limpo(r["Bioma"]), "pdf": "", "texto_completo": False,
        })
    b = pd.DataFrame(linhas)
    b.to_parquet(RAIZ / "dados" / "documentos.parquet", index=False)
    print(f"{'; '.join(UNIDADES)} | {len(b)} documentos {b.tipo.value_counts().to_dict()} | "
          f"com texto completo (Infoteca): {int(b.texto_completo.sum())}")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "2026-10")
