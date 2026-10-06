# Método e avaliação do IAgro Conversa

## O que é

Um RAG (*retrieval-augmented generation*) que roda inteiro no navegador:
1. **Corpus:** publicações, soluções tecnológicas e projetos da Embrapa Territorial (exportação do Redape) e o
   texto completo das publicações técnicas da Embrapa (PDF na Infoteca-e).
2. **Trechos:** ~1 parágrafo (até ~900 caracteres), com a página de origem. Cada documento tem também um trecho
   título + resumo. Ficha catalográfica, expediente, sumário, listas de referências e tabelas numéricas são descartados.
3. **Vetores:** multilingual-e5-base (`passage:` nos trechos, `query:` na pergunta).
4. **Recuperação:** vetores de 1 bit selecionam 200 candidatos; vetores int8 (lidos por HTTP Range) os reordenam;
   ficam os 5 melhores trechos, no máximo 2 por documento. **Vaga para projetos e soluções:** eles viram poucos trechos
   (192, contra 36.306 de publicações) e perdiam as vagas em temas amplos. Se nenhum dos 5 for projeto ou solução, o
   melhor deles entra no lugar do 5º quando estiver a até 0,015 dele. No gabarito, o projeto/solução esperado passou a
   estar entre as fontes em 19 de 20 perguntas (antes, 16), sem perder nenhum documento esperado.
   **Quadro "Projetos e soluções relacionados":** além das fontes, cada resposta mostra até 3 projetos/soluções
   da unidade cujo melhor trecho esteja a até 0,03 do melhor trecho geral (fora do que já está nas fontes).
   Não vai para o modelo; serve para a pessoa ver o que a unidade fez sobre o tema.
5. **Filtro de relação fraca:** se o melhor trecho tem cosseno abaixo de 0,852, a base não trata do assunto — a página
   diz que não encontrou, sem chamar o modelo, e oferece a busca em toda a Embrapa.
6. **Geração:** modelo aberto no navegador (WebLLM), com as instruções de `site/prompt.txt`, os 5 trechos numerados e
   a pergunta. A resposta cita [1], [2]...; cada citação leva ao trecho, ao Portal e ao PDF na página.

## Base (exportação de outubro de 2026)

2.137 documentos da Embrapa Territorial (2.054 publicações, 20 soluções, 63 projetos). Dos 526 PDFs da Infoteca-e,
472 têm texto e 54 são escaneados (ficam com o resumo); nenhuma falha de download. 36.498 trechos (32.775 do texto
completo), 25 milhões de caracteres. Página: 59 MB, baixados aos poucos.

## Avaliação

Gabarito: 30 perguntas (`avaliacao/gabarito_territorial.csv`): 20 que a base responde, 3 em parte, 7 fora do tema.
`avaliacao/avaliar.py` reproduz a página e chama o modelo pelo Ollama (no processador). Na busca, um documento
esperado esteve entre os 5 trechos em 23 de 23 perguntas, em todas as versões.

| Versão | Modelo | Citou documento esperado | "Não encontrei" indevido | Fora do tema: não encontrei | Tempo médio |
|---|---|---|---|---|---|
| v1: resumos + 25 PDFs | Qwen 2.5 3B | 16/23 | 9/23 | 7/7 | 43 s |
| v1 | Qwen 2.5 1,5B | 12/23 | 1/23 | 1/7 | 28 s |
| v1 | Gemma 2 2B | 20/23 | 2/23 | 6/7 | 32 s |
| v2: base completa, sem filtro | Gemma 2 2B | 19/23 | 1/23 | 2/7 | 47 s* |
| **v3: base completa, filtro 0,852 + instruções revistas** | **Gemma 2 2B** | **20/23** | **1/23** | **5/7** | **35 s*** |

| v3, 3 trechos para o modelo, até 300 palavras | Gemma 2 2B | 20/23 | 1/23 | 5/7 | 22 s* |
| v3, 3 trechos, até 300 palavras | Gemma 3 1B | 18/23 | 6/23 | 5/7 | 18 s* |

\* com metade do processador.

**Modo celular** (aparelho móvel ou com até 4 GB de memória): a página pré-seleciona o Gemma 3 1B (cerca de 700 MB,
metade do Gemma 2 2B, que costuma faltar memória no celular), entrega 3 trechos ao modelo em vez de 5 e limita a
resposta. Na avaliação, 3 trechos não pioram o Gemma 2 2B e reduzem o tempo em 37%. O Gemma 3 1B é mais fraco
(diz "não encontrei" quando a base responde em 6 de 23), por isso é só a opção leve. Se a IA falhar, a página
oferece "Tentar com o modelo leve".

Decisões:
- **Gemma 2 2B é o modelo padrão.** Qwen 2.5 3B é cauteloso demais (diz "não encontrei" quando a base responde);
  Qwen 2.5 1,5B responde perguntas fora do tema (retirado da página).
- **Filtro de relação fraca.** Com o texto completo, quase sempre há algum trecho que menciona o assunto de passagem,
  e o modelo pequeno respondia com ele (na v2, inventou uma explicação de enxertia). Nesta base, o cosseno do melhor
  trecho separa bem: perguntas com resposta ≥ 0,859; fora do tema ≤ 0,856, exceto calcário (0,888; a base tem um
  texto sobre cálculo de calagem, e a resposta veio dele) e compra de mudas de eucalipto (0,870). Medido com o
  modelo do navegador (e5 q8). **Recalibrar ao incluir outras unidades.**
- Ponto fraco conhecido: "onde comprar mudas de eucalipto" passa pelo filtro e o modelo cita uma empresa mencionada
  num trecho como se fosse fornecedora.

As planilhas de cada versão estão em `avaliacao/` (`v1/`, `v2_sem_filtro/` e a atual).
