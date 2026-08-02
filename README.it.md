# BIP39-D20 — Genera una Frase Seme con un Dado a 20 Facce

[English](README.md) · [Español](README.es.md) · **Italiano** · [Português (BR)](README.pt-BR.md)

Un kit stampabile di due pagine per generare una frase seme [BIP-39](https://github.com/bitcoin/bips/blob/master/bip-0039/bip-0039.mediawiki) di 12 parole usando soltanto un dado a 20 facce (D20), penna e carta:

- **Foglio di istruzioni** (fronte) — disponibile in inglese, spagnolo, italiano e portoghese brasiliano.
- **Tabella di consultazione** (retro) — le 2048 parole BIP-39 organizzate come un sistema di coordinate 8 × 16 × 16.

Ogni lancio che registri è entropia che hai visto con i tuoi occhi. Nessun generatore elettronico di numeri casuali partecipa alla scelta delle tue parole.

## Perché entropia verificabile (e perché adesso)

A luglio 2026, più di mille BTC sono stati svuotati in pochi minuti da portafogli i cui semi erano stati generati da dispositivi Coldcard. Un difetto del firmware presente da marzo 2021 deviava silenziosamente la generazione del seme verso un PRNG software prevedibile invece dell'RNG hardware, per cui quei semi contenevano molto meno dei 128 bit di entropia promessi ([CoinDesk](https://www.coindesk.com/tech/2026/07/31/major-bitcoin-wallet-flaw-drains-594-btc-in-25-minute-sweep), [The Hacker News](https://thehackernews.com/2026/08/coldcard-hardware-wallet-flaw-linked-to.html)).

Due fatti di quell'incidente inquadrano questo tutorial:

1. **La lezione è la classe di guasto, non il marchio.** Il produttore ha corretto in un giorno. Ma nessun utente avrebbe potuto *vedere* il difetto: l'entropia elettronica è invisibile per natura. Qualsiasi dispositivo, di qualsiasi produttore, chiede la stessa fiducia cieca al momento di generare il seme.
2. **I dadi non sono mai stati a rischio.** L'avviso ufficiale del produttore stesso segnala che i semi generati con 50 o più lanci onesti di dadi non sono stati colpiti. La casualità fisica che vedi accadere è l'unica fonte di entropia che non richiede audit.

Questo metodo produce tutti i 128 bit di un seme di 12 parole a partire da ~35 lanci validi di D20, con uniformità garantita dal campionamento con rigetto (i lanci da 17 a 20 vengono scartati).

## Come funziona

Ogni parola BIP-39 è indirizzata da tre lanci del dado, conservando solo i risultati da 1 a 16:

| Coordinata | Seleziona | Risultati validi per esito | Bit |
|-----------|-----------|----------------------------|-----|
| **D1** | una delle 8 sezioni della pagina | 2 (sezioni etichettate "1,2" … "15,16") | 3 |
| **D2** | una delle 16 righe | 1 | 4 |
| **D3** | una delle 16 colonne | 1 | 4 |

Undici parole si lanciano per intero (11 × 11 = 121 bit). Per la dodicesima parola si lanciano solo D1 e D2 (altri 7 bit, per un totale di 128); la sua colonna codifica il *checksum* di 4 bit, quindi esattamente una delle 16 parole della riga selezionata completa un seme valido — la si trova per tentativi nell'assistente di inserimento del seme del portafoglio.

I due esempi stampati nelle istruzioni sono verificati automaticamente da [`tools/verify_tutorial.py`](tools/verify_tutorial.py) rispetto alla lista di parole ufficiale e all'algoritmo di checksum.

**L'integrità della tabella è strutturale, non dichiarata.** In questo repository non esiste alcuna copia della lista di parole: la compilazione legge `bip-0039/english.txt` direttamente dal repository canonico [`bitcoin/bips`](https://github.com/bitcoin/bips), montato in `external/bips` come sottomodulo git fissato a un commit esatto e scaricato in modalità sparse, cosicché solo `bip-0039/` arriva su disco — così le parole della tabella stampata sono ancorate, tramite l'hashing stesso di git, alla storia upstream, e `make verify` verifica inoltre il file rispetto allo SHA-256 di riferimento del BIP-39. Verificalo tu stesso: `git submodule status` e `sha256sum external/bips/bip-0039/english.txt`.

## Il sistema di colori

Le celle della tabella sono ombreggiate perché l'occhio possa seguire le coordinate in una griglia densa di 2048 celle. Tre bit di parità selezionano una di otto tonalità:

- **Parità di colonna → tinta**: colonne dispari gialle, pari arancioni.
- **Parità di riga → luminosità** (scalino grande) e **parità di sezione → luminosità** (scalino piccolo).

Le celle di etichetta di riga, etichetta di sezione e intestazione seguono la stessa logica con saturazioni diverse, e la colonna delle etichette D1 è ombreggiata secondo la parità della sezione lungo tutto il suo blocco di 16 righe. Lo schema è implementato in modo programmatico al momento della compilazione: lo stesso [`table/bip39-table.tex`](table/bip39-table.tex) legge la lista ufficiale direttamente dal sottomodulo `bitcoin/bips` fissato per commit e deriva la parola e il colore di ogni cella dalle sue coordinate (sezione, riga, colonna) con cicli nel documento stesso --- senza intermedi generati né parole codificate a mano. Regolare la palette significa modificare il blocco di parametri in cima a quel file.

## Compilazione

Richiede TeX Live (con `fontawesome5`, `qrcode`, `tcolorbox` e i pacchetti lingua di babel) e Python 3. Su Debian/Ubuntu:

```sh
sudo apt-get install --no-install-recommends \
  texlive-latex-base texlive-latex-recommended texlive-latex-extra \
  texlive-fonts-extra texlive-lang-european texlive-lang-portuguese \
  texlive-lang-spanish texlive-lang-italian latexmk
```

Poi:

```sh
make            # compila la tabella + le quattro edizioni delle istruzioni in dist/
make it         # una sola edizione (en, es, it, pt-br)
make table      # solo la tabella di consultazione
make verify     # integrità della lista + verifica degli esempi
```

La lista di parole proviene dal sottomodulo `bitcoin/bips`, e `make` la scarica automaticamente quando manca — in modo minimale: solo il commit fissato, filtrato per blob, con soltanto `bip-0039/` materializzato nel checkout (poche centinaia di KB, mai l'intero repository). Anche un normale `git clone --recurse-submodules` (shallow) funziona.

La CI esegue `make verify` e ricompila tutti i PDF a ogni push, pubblicandoli come artefatti. I PDF pronti da stampare sono anche versionati in [`dist/`](dist/).

## Struttura del repository

```
instructions/
  common/preamble.tex     layout condiviso, riquadri, spaziatura compatta
  en/ es/ it/ pt-br/      un foglio autonomo per lingua
table/
  bip39-table.tex         computa l'intera tabella dalla lista alla compilazione
external/
  bips/                   bitcoin/bips canonico (sottomodulo git, fissato per commit)
tools/
  verify_tutorial.py      controlli di integrità + esempi
dist/                     PDF pronti da stampare
```

## Stampa

Stampa il foglio di istruzioni nella tua lingua e la tabella fronte-retro (rilegatura sul lato lungo), A4. La tabella è volutamente `\tiny` — stampa in scala 100 %, senza adattamento alla pagina.

## Note di sicurezza

- Esegui la procedura in privato; non fotografare né digitalizzare mai i lanci o i risultati intermedi.
- Digita il seme finale soltanto su un dispositivo *air gapped* fidato e di tua proprietà.
- Se sospetti che un seme esistente provenga da software o firmware difettoso, genera un seme nuovo con questo metodo e sposta i fondi. Aggiornare il firmware non ripara un seme debole.
- Il seme di esempio stampato nelle istruzioni è pubblico. Non usarlo mai.

## Autore e lavori correlati

Di **Yuri da Silva Villas Boas** — autore della [BIP-450 (Formosa)](https://github.com/bitcoin/bips/blob/master/bip-0450.mediawiki) e creatore di **Great Wall**, un protocollo di software libero per l'autocustodia di Bitcoin resistente alla coercizione. Generare un seme forte è solo il primo passo; proteggerlo da furto e coercizione è il resto.

- Great Wall e altri progetti: [github.com/Yuri-SVB](https://github.com/Yuri-SVB)
- Tutorial, corsi, comunità: [www.loudproudandfree.com](https://www.loudproudandfree.com)

Sono in programma video passo-passo di questo tutorial nelle quattro lingue — seguili tramite i link qui sopra.
