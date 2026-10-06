# iAgro Conversa

**Página:** https://danimaciel.github.io/iagro-conversa/

Projeto experimental: converse com o que a Embrapa Territorial produziu e produz. A pessoa pergunta do seu
jeito; a busca por significado encontra os trechos mais relevantes das publicações (inclusive o texto completo
das publicações técnicas da Embrapa), soluções tecnológicas e projetos; e um modelo de linguagem aberto, rodando
no próprio navegador, escreve a resposta citando as fontes [1], [2]...

> O iAgro é um projeto experimental, feito com dados públicos da Embrapa, que busca apoiar o desenvolvimento da
> agricultura brasileira facilitando o acesso às tecnologias e aos conhecimentos produzidos pela pesquisa
> agropecuária pública. Não é um serviço oficial da Embrapa. Respostas geradas por inteligência artificial podem
> conter erros: confira sempre a publicação original.

- **Custo zero, sem servidor.** Busca (multilingual-e5) e modelo de linguagem (Qwen 2.5 ou Gemma 2, via
  [WebLLM](https://github.com/mlc-ai/web-llm)) rodam no navegador de quem usa; nenhuma pergunta sai do computador.
  O modelo de linguagem é opcional e precisa de navegador com WebGPU (Chrome ou Edge atualizados, no computador).
- **Texto completo só das publicações técnicas da Embrapa** (PDF na Infoteca-e: folhetos, livros, folders, mapas,
  relatórios). Artigos de periódicos, trabalhos de eventos, teses e capítulos em livros de outras editoras
  (PDF no Alice) entram com título e resumo, com link para o original.
- **Atualização automática** todo mês pelo GitHub Actions: exportação do Redape → PDFs novos → trechos → vetores → página.

Projetos irmãos: [iagro](https://github.com/danimaciel/iagro) (piloto e agente ADK) e
[iagro-embrapa](https://github.com/danimaciel/iagro-embrapa) (busca em toda a Embrapa).

## Como funciona

```
pipeline/redape.py       baixa a exportação mais recente do Redape
pipeline/documentos.py   documentos da unidade (UNIDADES) e quais têm texto completo
pipeline/pdfs.py         baixa os PDFs novos, extrai o texto por página e descarta o PDF (cache de textos)
pipeline/trechos.py      trechos de ~1 parágrafo; descarta ficha catalográfica, sumário, referências e tabelas
pipeline/vetores.py      vetores e5 só dos trechos novos (cache por hash)
pipeline/site_dados.py   bits (busca rápida) + vetores int8 (lidos por trecho, HTTP Range) + textos em blocos
site/index.html          conversa: busca os 5 trechos mais relevantes (até 2 por documento) e a IA responde com eles
```

Rodar no próprio computador:

```
pip install -r pipeline/requirements-base.txt -r pipeline/requirements-vetores.txt
python pipeline/redape.py
python pipeline/documentos.py 2026-10
python pipeline/pdfs.py tudo         # ~3 h para os 526 PDFs da Territorial (download lento)
python pipeline/trechos.py
python pipeline/vetores.py tudo
python pipeline/site_dados.py 2026-10
python -m http.server 8000 --directory site
```
