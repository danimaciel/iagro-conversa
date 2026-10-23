# iAgro Conversa: instruções para o Claude

Assistente "Pergunte à Embrapa Territorial" (nome curto **iAgro**): RAG que roda inteiro no navegador, sobre
publicações (com texto completo da Infoteca-e), soluções tecnológicas e projetos da Embrapa Territorial.
Página: https://danimaciel.github.io/iagro-conversa/ · repo público danimaciel/iagro-conversa.

**Comece lendo `estado.md`** (o que está no ar, decisões e pendências) e atualize-o ao fim de cada sessão.

## Família iAgro (três repositórios irmãos, mesma pasta-mãe)

| Repo | Pasta | O que é |
|---|---|---|
| danimaciel/iagro | `../IAGRO` | Piloto Territorial: busca no navegador + agente local (Google ADK + Ollama). Tem `Dados/` local e privado |
| danimaciel/iagro-embrapa | `../iagro-embrapa` | Busca por significado em toda a Embrapa (~185 mil documentos), com mapa por estado |
| danimaciel/iagro-conversa | esta pasta | Conversa (RAG) da Territorial, com modo incorporado ao portal |

Os três consomem **produtos e localização** do Observatório de Pesquisa da Embrapa (repo
danimaciel/observatorio_embrapa, pasta `../observatorio de P&D Embrapa`), pela release pública
`enriquecimento-AAAA-MM`. Regras de produto e estado mudam lá, nunca aqui.

Para trabalhar de outro computador: clonar os três repositórios na mesma pasta-mãe. Os dados (`dados/`,
`site/dados/`) não vão para o git: são gerados pelo GitHub Actions, que guarda tudo como anexos de release.

## Como funciona

- `pipeline/`: redape.py → documentos.py → pdfs.py → trechos.py → vetores.py (e5, cache por hash) →
  site_dados.py (bits de 1 bit + vetores int8 lidos por HTTP Range + textos em blocos). Detalhes em `README.md`
  e `docs/METODO.md`.
- `site/index.html`: busca 200 candidatos, 5 trechos (até 2 por documento), vaga para projeto/solução,
  filtro de relação fraca (`LIMIAR = 0.852`, calibrado só para a Territorial), resposta rápida extrativa e,
  sob pedido, texto da IA via WebLLM (`ia-worker.js`; Gemma 2 2B padrão; Gemma 3 1B no celular).
- Modo incorporado: `?embed` (iframe no portal) e `?embed&balao` (`site/balao.js`); demonstração em
  `site/exemplo-portal.html`.
- Registro das perguntas: só na página do GitHub, nunca no modo incorporado (`docs/REGISTRO.md`,
  `registro/apps_script.gs`, constante `REGISTRO_URL`).
- Publicação: push em `site/**` dispara `pagina.yml` (1–2 min, reaproveita `site-dados.tar.gz` da release
  `cache`); `atualizar.yml` reprocessa tudo (dia 12 de cada mês ou manual).

## Regras da usuária

- Escopo: **só a Embrapa Territorial** e o que ela produziu e produz. Nada de SAF (do projeto SAF/SAC veio só o
  método). Fora do escopo ou atendimento → SAC da Embrapa.
- Demonstração com dados públicos; **não é serviço oficial** e não usa a marca oficial da Embrapa.
- **Nunca testar a WebLLM (geração da IA) no navegador do painel do Claude**: travou o PC da usuária (GPU
  integrada). A busca e5 pode ser testada. Avaliações com Ollama: `--threads 6`.
- Números sempre com a fonte e a etapa (exportação do Redape, arquivo do pipeline ou da avaliação), nunca de memória.
- Documentar sempre: `.md` + `.docx` para documentos que vão a outras pessoas (`docs/`). Gerador:
  `../observatorio de P&D Embrapa/documentacao/ferramentas/md2docx.js` (`node md2docx.js entrada.md saida.docx`).
- LGPD: registros de perguntas e qualquer dado bruto ficam restritos; só resultados agregados são públicos.
- Português do Brasil em textos, código e mensagens de commit. Publicar (push) depois do OK da usuária.
