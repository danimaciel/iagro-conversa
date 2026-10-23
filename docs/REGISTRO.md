# Registro das perguntas do iAgro Conversa

Versão de 23/10/2026. Registro mínimo, para saber o que as pessoas perguntam, onde o assistente erra e se as
respostas ajudam. Decisão da responsável pelo projeto: **só na página pública do GitHub**
(https://danimaciel.github.io/iagro-conversa/). No modo incorporado ao portal (`?embed`), nada é enviado,
como diz a nota técnica (`docs/nota_tecnica_portal.md`, seção 6).

## Como funciona

A página é estática (GitHub Pages) e não grava nada. Cada evento vai, por `fetch`, para um script do Google
(Apps Script), que acrescenta uma linha numa planilha da responsável pelo projeto. Se o envio falhar, a conversa
segue normalmente.

| Evento | Quando | O que vai |
|---|---|---|
| `pergunta` | a cada pergunta | texto (sem e-mail, CPF e telefone), consulta usada quando é continuação, tipo de fluxo, filtros de produto e estado, relação fraca, sem documento no filtro, maior cosseno, códigos dos documentos-fonte, tempo da busca |
| `ia` | quando a pessoa pede o texto da IA | modelo, segundos, velocidade de escrita, se deu certo (ou o erro) |
| `avaliacao` | botão "Ajudou / Não ajudou" | sim ou não |

**Não vai:** endereço IP (o Apps Script não o entrega ao script), cookies, identificador de pessoa ou de aparelho.
O campo `pid` é um código aleatório criado a cada pergunta, só para ligar os três eventos da mesma pergunta.

**Antes do envio**, a página troca e-mails, CPFs, telefones e sequências de 8 ou mais dígitos por marcadores
(`[e-mail]`, `[cpf]`, `[telefone]`, `[número]`) e corta o texto em 500 caracteres. O script ainda impede que um
texto vire fórmula na planilha e limita a 300 envios por minuto.

**Para quem usa:** um aviso sob a caixa de pergunta ("As perguntas são guardadas sem identificar quem
perguntou…") com o botão **Não registrar as minhas** (a escolha fica guardada no navegador), e o parágrafo de
privacidade da janela Sobre explica o que é guardado e por quanto tempo.

## Guarda e uso (LGPD)

- A planilha é **dado bruto e restrito**: fica na conta da responsável, sem compartilhamento público.
- Prazo: **12 meses**; a função `apagarAntigos` apaga o que passar disso (acionador mensal, abaixo).
- Podem ser divulgados **resumos agregados** (temas mais perguntados, taxa de "não ajudou", perguntas fora do
  tema), nunca as perguntas uma a uma.
- Base legal sugerida (a referendar com o encarregado de dados, se o projeto virar serviço): legítimo
  interesse, para melhoria do serviço, com aviso e opção de recusa na própria página.

## Instalação (uma vez, cerca de 10 minutos)

1. Em https://sheets.new, crie uma planilha, por exemplo **iAgro Conversa · registro**.
2. Menu **Extensões > Apps Script**. Apague o conteúdo de `Código.gs` e cole o arquivo
   `registro/apps_script.gs` deste repositório. Salve (ícone de disquete).
3. Teste: no topo do editor, escolha a função `testar` e clique em **Executar**. Na primeira vez, o Google pede
   autorização: **Revisar permissões** > sua conta > **Avançado** > **Acessar (não seguro)** > **Permitir**
   (o aviso aparece porque o script é seu e não foi verificado pelo Google). Volte à planilha: deve haver uma
   aba `registro` com uma linha "teste do registro". Pode apagar essa linha.
4. **Implantar > Nova implantação** > engrenagem > **App da Web**.
   - Descrição: `registro iAgro`
   - Executar como: **Eu**
   - Quem pode acessar: **Qualquer pessoa**
   - **Implantar** e copie o **URL do app da Web** (termina em `/exec`).
5. Acionador de limpeza: no Apps Script, ícone de relógio (**Acionadores**) > **Adicionar acionador** >
   função `apagarAntigos`, origem **Baseado no tempo**, **Contador de meses**, dia 1 > **Salvar**.
6. Envie o endereço `/exec` para o Claude (ou cole em `REGISTRO_URL`, no início do script de
   `site/index.html`) e publique a página.

O endereço `/exec` não dá acesso à planilha: ele só aceita gravar linhas novas. Ainda assim, quem o conhecer
pode enviar linhas falsas; o limite por minuto reduz o dano. Se isso acontecer, faça uma nova implantação
(novo endereço) e troque na página.

**Se mudar o script:** **Implantar > Gerenciar implantações** > lápis > Versão: **Nova versão** > Implantar
(o endereço continua o mesmo).

## Como analisar

Na planilha, filtre `evento = pergunta` para as perguntas; `fraca = true` mostra as que o assistente
considerou fora do tema. Para ligar pergunta, uso da IA e avaliação, use o `pid` (por exemplo, `PROCV` ou uma
tabela dinâmica). Os códigos em `fontes` são os documentos do Redape que apareceram como fonte.

## Para desligar

Deixe `REGISTRO_URL = ""` em `site/index.html` e publique: a página volta a não enviar nada, e os textos de
privacidade voltam ao original automaticamente.
