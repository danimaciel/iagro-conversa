# Pergunte à Embrapa Territorial · iAgro

Nota técnica para a equipe do portal — incorporação do assistente na página da Embrapa Territorial (Liferay)

Descreve o que é o assistente, como funciona, as duas formas de incorporá-lo ao portal, os requisitos, a segurança e a privacidade, e o que se pede à equipe do portal.

**Versão:** 1
**Data:** 20 de outubro de 2026
**Responsável:** Daniela Maciel Pinto — Embrapa Territorial
**Destinatários:** equipe do portal (Comunicação e Tecnologia da Informação)

---

## 1. O que é

O **iAgro · Pergunte à Embrapa Territorial** é um assistente de perguntas e respostas sobre o que a Embrapa Territorial produziu e produz. A pessoa pergunta do seu jeito; o assistente encontra os trechos mais relevantes das **publicações, soluções tecnológicas e projetos** da unidade e mostra a resposta **sempre com as fontes** (título, tipo, ano e link para o Portal Embrapa ou para o PDF).

- **Acervo:** 2.137 documentos da Embrapa Territorial (2.054 publicações, 63 projetos e 20 soluções tecnológicas), com o texto completo de 472 publicações técnicas da Infoteca-e — 36.498 trechos pesquisáveis. Dados públicos do Redape e da Infoteca-e, exportação de outubro de 2026.
- **Público:** estudantes; gestores públicos e privados; pesquisadores; produtores e extensionistas.
- **Fora do escopo** (atendimento, serviços, preços, contatos, outras unidades): o assistente informa que não trata do assunto e encaminha ao **SAC da Embrapa** (https://www.embrapa.br/fale-conosco/sac).
- O comportamento e os textos seguem o documento de design conversacional (`docs/design_conversacional.docx`).

## 2. Como funciona

| Componente | Onde roda | Observação |
|---|---|---|
| Página do assistente | Página estática (HTML e JavaScript) hospedada no GitHub Pages | Sem servidor de aplicação e sem banco de dados |
| Busca por significado | No navegador de quem usa (modelo multilingual-e5, cerca de 110 MB, baixado na primeira visita) | Funciona em computador e celular |
| Resposta rápida | No navegador: frases dos documentos mais próximas da pergunta, com as fontes | Sempre disponível |
| Texto redigido por IA (opcional) | No navegador, por WebGPU (modelo aberto Gemma 2, cerca de 1,5 GB, baixado só se a pessoa pedir) | Só em Chrome ou Edge atualizados, no computador; sem suporte, a pessoa continua com a resposta rápida |
| Atualização dos dados | Automática, todo mês (GitHub Actions): baixa a exportação do Redape e os PDFs novos e regera a busca | Sem intervenção da equipe do portal |

**Consequências práticas:** não há chave de API, servidor ou custo de operação; a página do portal não precisa de nenhuma integração de dados.

## 3. Formas de incorporar ao portal

### 3.1 Forma A — bloco numa página (recomendada para começar)

Incluir, na página escolhida (por exemplo, "Pergunte à Embrapa Territorial"), um bloco de **iframe**. No Liferay, isso pode ser feito com o widget de iframe ou com um fragmento HTML, conforme a versão:

```
<iframe src="https://danimaciel.github.io/iagro-conversa/?embed=1"
        title="Pergunte à Embrapa Territorial — iAgro"
        style="width:100%; height:760px; border:0;"
        loading="lazy" allow="clipboard-write"></iframe>
```

- `?embed=1` ativa o modo incorporado: topo compacto, sem título próprio, tema claro.
- Altura recomendada: 700 a 800 px (a área de conversa rola por dentro).
- `allow="clipboard-write"` permite o botão "Copiar" das respostas.

### 3.2 Forma B — balão em todas as páginas da unidade

Incluir **uma única vez**, no modelo das páginas do site da unidade (página mestra, tema ou fragmento global), a linha:

```
<script src="https://danimaciel.github.io/iagro-conversa/balao.js" defer></script>
```

- Aparece um botão "Pergunte à Embrapa Territorial" no canto inferior direito; ao clicar, abre um painel com o assistente. Em telas pequenas, o painel ocupa a tela toda.
- **O assistente só é carregado quando a pessoa abre o balão**: a navegação no site não baixa nada.
- Opções no próprio `<script>`: `data-titulo` (texto do botão), `data-cor` (cor do botão), `data-posicao="esquerda"`.
- Acessibilidade: botão e painel com rótulos para leitor de tela; tecla Esc fecha o painel.

### 3.3 Demonstração

A página `https://danimaciel.github.io/iagro-conversa/exemplo-portal.html` simula uma página de unidade com as duas formas funcionando (bloco e balão).

## 4. Requisitos e compatibilidade

| Situação | O que a pessoa recebe |
|---|---|
| Computador com Chrome ou Edge atualizados (WebGPU) | Busca, resposta rápida com fontes e, se pedir, texto redigido pela IA |
| Computador com outro navegador, ou sem placa de vídeo compatível | Busca e resposta rápida com fontes; aviso de que a IA de redação não está disponível |
| Celular | Busca e resposta rápida com fontes |

Na primeira visita, a busca baixa cerca de 110 MB (guardados no navegador para as próximas visitas). A IA de redação, se usada, baixa cerca de 1,5 GB uma única vez.

## 5. Segurança

- O assistente é **conteúdo estático**: não recebe dados, não tem formulário que envie informações a servidor e não usa cookies próprios.
- O que o portal precisa permitir (política de segurança de conteúdo, se houver):

| Forma | Permissão no portal |
|---|---|
| A — bloco | `frame-src https://danimaciel.github.io` |
| B — balão | `script-src https://danimaciel.github.io` e `frame-src https://danimaciel.github.io` |

- Dentro do iframe, a página do assistente carrega bibliotecas de `cdn.jsdelivr.net` e o modelo de busca de `huggingface.co`; isso ocorre no contexto do iframe e não exige permissão do portal.
- Links para fontes, PDFs e SAC abrem em nova aba.
- Código aberto: https://github.com/danimaciel/iagro-conversa

## 6. Privacidade (LGPD)

- **Nenhuma pergunta sai do computador de quem usa**: a busca e a IA rodam no navegador; não há registro de perguntas nem coleta de dados pessoais.
- O navegador guarda localmente os arquivos do modelo e da base (armazenamento do próprio navegador), apenas para não baixá-los de novo.
- O acervo é composto de **documentos públicos** da Embrapa (Redape e Infoteca-e). Nomes de autores aparecem nas fontes como constam nas publicações.
- A página não usa cookies, armazenamento de sessão nem ferramentas de análise de acesso.
- Como qualquer hospedagem, o GitHub Pages (e os serviços de onde a página baixa bibliotecas e o modelo de busca) registra acessos técnicos — por exemplo, o endereço IP de quem carrega a página —, conforme suas próprias políticas. As perguntas não fazem parte desses acessos.
- O texto "Sobre" do assistente informa isso ao usuário.

## 7. Transparência e limites

- O assistente identifica-se como **inteligência artificial** e exibe o aviso: "Respostas geradas por inteligência artificial podem conter erros. Confira sempre a fonte original."
- Responde **somente** com base nos documentos da unidade e sempre cita as fontes; quando não encontra, diz que não encontrou e encaminha ao SAC.
- Não faz recomendações para propriedades específicas e não informa preços, prazos ou contatos.
- Avaliação de qualidade com perguntas-teste da Embrapa Territorial: resultados no Anexo.

## 8. Hospedagem e manutenção

- **Hoje:** GitHub Pages (gratuito), com atualização mensal automática.
- **Futuro, se desejado:** a mesma página pode ser hospedada em servidor da Embrapa sem mudanças no funcionamento — basta copiar a pasta `site/` e apontar o iframe ou o script para o novo endereço.
- **Responsável técnica:** Daniela Maciel Pinto (Embrapa Territorial).

## 9. O que se pede à equipe do portal

1. Confirmar a **versão do Liferay** e se é possível incluir **iframe** (forma A) e, futuramente, **script no modelo do site** (forma B).
2. Informar se há **política de segurança de conteúdo** que precise das permissões da seção 5.
3. Indicar a **página** onde o bloco será colocado (sugestão: "Pergunte à Embrapa Territorial", no menu da unidade).
4. Validar com a **Comunicação** o nome ("iAgro · Pergunte à Embrapa Territorial"), os textos de boas-vindas e os avisos.
5. Agendar um teste conjunto na página de homologação do portal, se houver.

## Anexo — Avaliação com perguntas-teste (20/10/2026)

Gabarito de 30 perguntas sobre a Embrapa Territorial (`avaliacao/gabarito_territorial.csv`): 23 com resposta no acervo (20 temáticas e 3 que a base responde só em parte) e 7 fora do tema. Modelo Gemma 2 2B (o recomendado na página), executado no processador pelo Ollama com as mesmas instruções e os mesmos 5 trechos que a página usa.

| Medida | Resultado |
|---|---|
| A busca trouxe um documento esperado | 23 de 23 |
| A IA citou um trecho de documento esperado | 20 de 23 |
| A IA disse "não encontrei" sem motivo | 1 de 23 |
| Fora do tema: a IA disse "não encontrei" | 5 de 7 |
| Fora do tema, contando as regras da página (encaminhamento ao SAC) | 6 de 7 |
| Tempo médio para redigir (processador; no navegador com WebGPU tende a ser menor) | 41 s |

Nota: as instruções revisadas mantiveram os mesmos resultados da versão anterior (20/23, 1/23, 5/7), sem piora. Leitura das falhas: em uma pergunta a resposta estava correta, mas citou outro trecho do mesmo assunto; em uma pergunta sobre custo por hectare a IA interpretou mal um número — na página essa pergunta é encaminhada ao SAC pelas regras de atendimento e não chega à IA; um pedido de compra também é encaminhado ao SAC pelas regras. A resposta rápida (frases dos documentos com as fontes), disponível para todos os usuários, não depende da IA.
