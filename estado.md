# Estado do iAgro Conversa

Atualizado em 23/10/2026.

## No ar

- https://danimaciel.github.io/iagro-conversa/ com a exportação do Redape de **outubro de 2026**
  (base da página: 2.137 documentos da Embrapa Territorial em 36.498 trechos, segundo `site/dados/info.json`).
- Design conversacional aplicado (`docs/design_conversacional.{md,docx}`): nome "Pergunte à Embrapa
  Territorial", 12 sugestões por público, fluxos por regras (saudação, atendimento → SAC, recomendação
  individual, pessoas, fora do tema).
- Modo incorporado ao portal (`?embed`, balão) publicado; nota técnica para a equipe do portal em
  `docs/nota_tecnica_portal.{md,docx}`.
- Favicon e selo do topo iguais nos três iAgros (globo com ponto verde-claro), em 19/10.
- Link "Ver no mapa ↗" em cada resposta: abre o iAgro Embrapa com a pergunta, a Territorial e os filtros (20/10).

## Avaliação (gabarito da Territorial, Gemma 2 2B via Ollama, 20/10/2026)

Citou o documento esperado em 20 de 23 perguntas; reconheceu 5 de 7 perguntas fora do tema (6 de 7 com as
regras da página). Arquivos em `avaliacao/`; anexo na nota técnica.

## Registro das perguntas (23/10/2026)

Pronto no código, **desligado** (`REGISTRO_URL = ""`). Decisão da usuária: só na página do GitHub; no modo
incorporado ao portal nada é enviado. Testado de ponta a ponta com um receptor local: pergunta, saudação,
pergunta fora do tema e avaliações chegaram; CPF trocado por `[cpf]`; com "Não registrar as minhas" e no
modo `?embed` nada foi enviado.

**Falta:** a usuária criar a planilha e o Apps Script (`docs/REGISTRO.md`) e enviar o endereço `/exec`;
depois, colocar em `REGISTRO_URL` e publicar.

## Pendências

- Registro: endereço do Apps Script (acima).
- Testar em 2 ou 3 celulares reais (incluindo um Android simples) antes de divulgar amplamente.
- Equipe do portal: versão do Liferay, política de segurança de conteúdo (CSP) e página onde entra.
- Perguntas fora do tema que passam pelo filtro (2 de 7 no gabarito): revisar com as perguntas reais do registro.
- Mapa pequeno ao lado das fontes: adiado; decidir depois de usar o link "Ver no mapa".
- Avisar a coordenação antes de divulgação ampla.
