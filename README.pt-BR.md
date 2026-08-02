# BIP39-D20 — Gere uma Frase Semente com um Dado de 20 Faces

[English](README.md) · [Español](README.es.md) · [Italiano](README.it.md) · **Português (BR)**

Um kit imprimível de duas páginas para gerar uma frase semente [BIP-39](https://github.com/bitcoin/bips/blob/master/bip-0039/bip-0039.mediawiki) de 12 palavras usando apenas um dado de 20 faces (D20), caneta e papel:

- **Folha de instruções** (frente) — disponível em inglês, espanhol, italiano e português do Brasil.
- **Tabela de consulta** (verso) — as 2048 palavras BIP-39 organizadas como um sistema de coordenadas 8 × 16 × 16.

Cada rolagem que você registra é entropia que você viu com os próprios olhos. Nenhum gerador eletrônico de números aleatórios participa da escolha das suas palavras.

## Por que entropia verificável (e por que agora)

Em julho de 2026, mais de mil BTC foram varridos em minutos de carteiras cujas sementes haviam sido geradas por dispositivos Coldcard. Um defeito de firmware presente desde março de 2021 desviava silenciosamente a geração da semente para um PRNG previsível de software em vez do RNG de hardware, de modo que aquelas sementes carregavam muito menos do que os 128 bits de entropia prometidos ([CoinDesk](https://www.coindesk.com/tech/2026/07/31/major-bitcoin-wallet-flaw-drains-594-btc-in-25-minute-sweep), [The Hacker News](https://thehackernews.com/2026/08/coldcard-hardware-wallet-flaw-linked-to.html)).

Dois fatos desse incidente enquadram este tutorial:

1. **A lição é a classe de falha, não a marca.** O fabricante corrigiu em um dia. Mas nenhum usuário poderia ter *visto* o defeito: entropia eletrônica é invisível por natureza. Qualquer dispositivo, de qualquer fabricante, pede a mesma confiança cega na hora de gerar a semente.
2. **Dados físicos nunca estiveram em risco.** O próprio aviso do fabricante registra que sementes geradas com 50 ou mais rolagens honestas de dados não foram afetadas. Aleatoriedade física que você vê acontecer é a única fonte de entropia que dispensa auditoria.

Este método produz os 128 bits completos de uma semente de 12 palavras a partir de ~35 rolagens válidas de D20, com uniformidade garantida por amostragem com rejeição (rolagens de 17 a 20 são descartadas).

## Como funciona

Cada palavra BIP-39 é endereçada por três rolagens do dado, mantendo apenas resultados de 1 a 16:

| Coordenada | Seleciona | Resultados válidos por saída | Bits |
|-----------|-----------|------------------------------|------|
| **D1** | uma das 8 seções da página | 2 (seções rotuladas "1,2" … "15,16") | 3 |
| **D2** | uma das 16 linhas | 1 | 4 |
| **D3** | uma das 16 colunas | 1 | 4 |

Onze palavras são roladas por completo (11 × 11 = 121 bits). Para a décima segunda palavra, rolam-se apenas D1 e D2 (mais 7 bits, totalizando 128); a coluna dela codifica o *checksum* de 4 bits, de modo que exatamente uma das 16 palavras da linha selecionada completa uma semente válida — encontrada por tentativa e erro no assistente de entrada de semente da carteira.

Os dois exemplos impressos nas instruções são verificados por máquina pelo [`tools/verify_tutorial.py`](tools/verify_tutorial.py) contra a lista de palavras oficial e o algoritmo de checksum.

**A integridade da tabela é estrutural, não afirmada.** Não existe cópia da lista de palavras neste repositório: a compilação lê o `bip-0039/english.txt` diretamente do repositório canônico [`bitcoin/bips`](https://github.com/bitcoin/bips), montado em `external/bips` como submódulo git fixado em um commit exato e baixado de forma esparsa, de modo que apenas o `bip-0039/` chega ao disco — assim as palavras da tabela impressa ficam ancoradas, pelo próprio hashing do git, ao histórico upstream, e o `make verify` ainda confere o arquivo contra o SHA-256 de referência do BIP-39. Audite você mesmo: `git submodule status` e `sha256sum external/bips/bip-0039/english.txt`.

## O sistema de cores

As células da tabela são sombreadas para que o olho acompanhe coordenadas em uma grade densa de 2048 células. Três bits de paridade selecionam um de oito tons:

- **Paridade da coluna → matiz**: colunas ímpares amarelas, pares laranjas.
- **Paridade da linha → brilho** (degrau grande) e **paridade da seção → brilho** (degrau pequeno).

As células de rótulo de linha, rótulo de seção e cabeçalho seguem a mesma lógica com saturações diferentes, e a coluna de rótulos D1 é sombreada pela paridade da seção ao longo de todo o bloco de 16 linhas. O esquema é implementado programaticamente em tempo de compilação: o próprio [`table/bip39-table.tex`](table/bip39-table.tex) lê a lista de palavras oficial diretamente do submódulo `bitcoin/bips` fixado por commit e deriva a palavra e a cor de cada célula a partir de suas coordenadas (seção, linha, coluna) com laços no próprio documento --- sem intermediários gerados nem palavras codificadas à mão. Ajustar a paleta significa editar o bloco de parâmetros no topo desse arquivo.

## Compilando

Requer TeX Live (com `fontawesome5`, `qrcode`, `tcolorbox` e os pacotes de idioma do babel) e Python 3. Em Debian/Ubuntu:

```sh
sudo apt-get install --no-install-recommends \
  texlive-latex-base texlive-latex-recommended texlive-latex-extra \
  texlive-fonts-extra texlive-lang-european texlive-lang-portuguese \
  texlive-lang-spanish texlive-lang-italian latexmk
```

Depois:

```sh
make            # compila tabela + as quatro edições de instruções em dist/
make pt-br      # uma única edição (en, es, it, pt-br)
make table      # apenas a tabela de consulta
make verify     # integridade da lista + verificação dos exemplos
```

A lista de palavras vem do submódulo `bitcoin/bips`, e o `make` a baixa automaticamente quando ausente — de forma mínima: apenas o commit fixado, filtrado por blobs, com somente o `bip-0039/` materializado no checkout (algumas centenas de KB, nunca o repositório inteiro). Um `git clone --recurse-submodules` normal (raso) também funciona.

A CI roda `make verify` e recompila todos os PDFs a cada push, publicando-os como artefatos. PDFs prontos para impressão também ficam versionados em [`dist/`](dist/).

## Estrutura do repositório

```
instructions/
  common/preamble.tex     layout compartilhado, caixas, espaçamento compacto
  en/ es/ it/ pt-br/      uma folha autocontida por idioma
table/
  bip39-table.tex         computa a tabela inteira da lista de palavras ao compilar
external/
  bips/                   bitcoin/bips canônico (submódulo git, fixado por commit)
tools/
  verify_tutorial.py      checagens de integridade + exemplos
dist/                     PDFs prontos para impressão
```

## Impressão

Imprima a folha de instruções no seu idioma e a tabela em frente e verso (encadernação pela borda longa), A4. A tabela é intencionalmente `\tiny` — imprima em escala 100 %, sem ajuste à página.

## Notas de segurança

- Realize o procedimento em privacidade; nunca fotografe nem digitalize rolagens ou resultados intermediários.
- Só digite a semente final em um dispositivo *air gapped* de confiança e de sua propriedade.
- Se suspeitar que uma semente existente veio de software ou firmware defeituoso, gere uma semente nova com este método e transfira os fundos. Atualização de firmware não conserta semente fraca.
- A semente de exemplo impressa nas instruções é pública. Nunca a use.

## Autor e trabalhos relacionados

Por **Yuri da Silva Villas Boas** — autor da [BIP-450 (Formosa)](https://github.com/bitcoin/bips/blob/master/bip-0450.mediawiki) e criador do **Great Wall**, protocolo de software livre para autocustódia de Bitcoin resistente a coerção. Gerar uma semente forte é o primeiro passo; protegê-la contra roubo e coerção é o resto.

- Great Wall e outros projetos: [github.com/Yuri-SVB](https://github.com/Yuri-SVB)
- Tutoriais, cursos, comunidade: [www.loudproudandfree.com](https://www.loudproudandfree.com)

Estão planejados vídeos passo a passo deste tutorial nos quatro idiomas — acompanhe pelos links acima.
