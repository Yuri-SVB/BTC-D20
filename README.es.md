# BIP39-D20 — Genera una Frase Semilla con un Dado de 20 Caras

[English](README.md) · **Español** · [Italiano](README.it.md) · [Português (BR)](README.pt-BR.md)

Un kit imprimible de dos páginas para generar una frase semilla [BIP-39](https://github.com/bitcoin/bips/blob/master/bip-0039/bip-0039.mediawiki) de 12 palabras usando solamente un dado de 20 caras (D20), bolígrafo y papel:

- **Hoja de instrucciones** (anverso) — disponible en inglés, español, italiano y portugués de Brasil.
- **Tabla de consulta** (reverso) — las 2048 palabras BIP-39 organizadas como un sistema de coordenadas 8 × 16 × 16.

Cada tirada que registras es entropía que viste con tus propios ojos. Ningún generador electrónico de números aleatorios participa en la elección de tus palabras.

## Por qué entropía verificable (y por qué ahora)

En julio de 2026, más de mil BTC fueron vaciados en minutos de billeteras cuyas semillas habían sido generadas por dispositivos Coldcard. Un defecto de firmware presente desde marzo de 2021 desviaba silenciosamente la generación de la semilla hacia un PRNG predecible de software en lugar del RNG de hardware, por lo que esas semillas contenían mucho menos que los 128 bits de entropía prometidos ([CoinDesk](https://www.coindesk.com/tech/2026/07/31/major-bitcoin-wallet-flaw-drains-594-btc-in-25-minute-sweep), [The Hacker News](https://thehackernews.com/2026/08/coldcard-hardware-wallet-flaw-linked-to.html)).

Dos hechos de ese incidente enmarcan este tutorial:

1. **La lección es la clase de fallo, no la marca.** El fabricante corrigió en un día. Pero ningún usuario podría haber *visto* el defecto: la entropía electrónica es invisible por naturaleza. Cualquier dispositivo, de cualquier fabricante, exige la misma confianza ciega al generar la semilla.
2. **Los dados nunca estuvieron en riesgo.** El propio aviso del fabricante señala que las semillas generadas con 50 o más tiradas honestas de dados no fueron afectadas. La aleatoriedad física que ves suceder es la única fuente de entropía que no necesita auditoría.

Este método produce los 128 bits completos de una semilla de 12 palabras a partir de ~35 tiradas válidas de D20, con uniformidad garantizada por muestreo con rechazo (las tiradas de 17 a 20 se descartan).

## Cómo funciona

Cada palabra BIP-39 se direcciona con tres tiradas del dado, conservando solo los resultados de 1 a 16:

| Coordenada | Selecciona | Resultados válidos por salida | Bits |
|-----------|-----------|-------------------------------|------|
| **D1** | una de las 8 secciones de la página | 2 (secciones etiquetadas "1,2" … "15,16") | 3 |
| **D2** | una de las 16 filas | 1 | 4 |
| **D3** | una de las 16 columnas | 1 | 4 |

Once palabras se tiran por completo (11 × 11 = 121 bits). Para la duodécima palabra solo se tiran D1 y D2 (7 bits más, totalizando 128); su columna codifica el *checksum* de 4 bits, de modo que exactamente una de las 16 palabras de la fila seleccionada completa una semilla válida — se encuentra por ensayo y error en el asistente de entrada de semilla de la billetera.

Los dos ejemplos impresos en las instrucciones están verificados por máquina mediante [`tools/verify_tutorial.py`](tools/verify_tutorial.py) contra la lista de palabras oficial y el algoritmo de checksum.

**La integridad de la tabla es estructural, no afirmada.** No existe copia de la lista de palabras en este repositorio: la compilación lee `bip-0039/english.txt` directamente del repositorio canónico [`bitcoin/bips`](https://github.com/bitcoin/bips), montado en `external/bips` como submódulo git fijado a un commit exacto y descargado de forma dispersa, de modo que solo `bip-0039/` llega al disco — así las palabras de la tabla impresa quedan ancladas, por el propio hashing de git, al historial upstream, y `make verify` además coteja el archivo contra el SHA-256 de referencia del BIP-39. Audítalo tú mismo: `git submodule status` y `sha256sum external/bips/bip-0039/english.txt`.

## El sistema de colores

Las celdas de la tabla están sombreadas para que el ojo siga las coordenadas en una cuadrícula densa de 2048 celdas. Tres bits de paridad seleccionan uno de ocho tonos:

- **Paridad de columna → matiz**: columnas impares amarillas, pares naranjas.
- **Paridad de fila → brillo** (salto grande) y **paridad de sección → brillo** (salto pequeño).

Las celdas de etiqueta de fila, etiqueta de sección y cabecera siguen la misma lógica con saturaciones distintas, y la columna de etiquetas D1 se sombrea según la paridad de la sección a lo largo de todo su bloque de 16 filas. El esquema está implementado de forma programática en tiempo de compilación: el propio [`table/bip39-table.tex`](table/bip39-table.tex) lee la lista oficial directamente del submódulo `bitcoin/bips` fijado por commit y deriva la palabra y el color de cada celda a partir de sus coordenadas (sección, fila, columna) con bucles en el propio documento --- sin intermediarios generados ni palabras codificadas a mano. Ajustar la paleta significa editar el bloque de parámetros al inicio de ese archivo.

## Compilación

Requiere TeX Live (con `fontawesome5`, `qrcode`, `tcolorbox` y los paquetes de idioma de babel) y Python 3. En Debian/Ubuntu:

```sh
sudo apt-get install --no-install-recommends \
  texlive-latex-base texlive-latex-recommended texlive-latex-extra \
  texlive-fonts-extra texlive-lang-european texlive-lang-portuguese \
  texlive-lang-spanish texlive-lang-italian latexmk
```

Luego:

```sh
make            # compila la tabla + las cuatro ediciones de instrucciones en dist/
make es         # una sola edición (en, es, it, pt-br)
make table      # solo la tabla de consulta
make verify     # integridad de la lista + verificación de los ejemplos
```

La lista de palabras proviene del submódulo `bitcoin/bips`, y `make` la descarga automáticamente cuando falta — de forma mínima: solo el commit fijado, filtrado por blobs, con únicamente `bip-0039/` materializado en el checkout (unos cientos de KB, nunca el repositorio entero). Un `git clone --recurse-submodules` normal (superficial) también funciona.

La CI ejecuta `make verify` y recompila todos los PDF en cada push, publicándolos como artefactos. Los PDF listos para imprimir también están versionados en [`dist/`](dist/).

## Estructura del repositorio

```
instructions/
  common/preamble.tex     diseño compartido, cajas, espaciado compacto
  en/ es/ it/ pt-br/      una hoja autocontenida por idioma
table/
  bip39-table.tex         computa la tabla completa desde la lista al compilar
external/
  bips/                   bitcoin/bips canónico (submódulo git, fijado por commit)
tools/
  verify_tutorial.py      comprobaciones de integridad + ejemplos
dist/                     PDF listos para imprimir
```

## Impresión

Imprime la hoja de instrucciones en tu idioma y la tabla a doble cara (encuadernación por el borde largo), A4. La tabla es intencionadamente `\tiny` — imprime a escala 100 %, sin ajustar a la página.

## Notas de seguridad

- Realiza el procedimiento en privado; nunca fotografíes ni digitalices tiradas ni resultados intermedios.
- Escribe la semilla final únicamente en un dispositivo *air gapped* de confianza y de tu propiedad.
- Si sospechas que una semilla existente proviene de software o firmware defectuoso, genera una semilla nueva con este método y transfiere los fondos. Actualizar el firmware no repara una semilla débil.
- La semilla de ejemplo impresa en las instrucciones es pública. Nunca la uses.

## Autor y trabajos relacionados

Por **Yuri da Silva Villas Boas** — autor de la [BIP-450 (Formosa)](https://github.com/bitcoin/bips/blob/master/bip-0450.mediawiki) y creador de **Great Wall**, un protocolo de software libre para la autocustodia de Bitcoin resistente a la coerción. Generar una semilla fuerte es el primer paso; protegerla contra el robo y la coerción es el resto.

- Great Wall y otros proyectos: [github.com/Yuri-SVB](https://github.com/Yuri-SVB)
- Tutoriales, cursos, comunidad: [www.loudproudandfree.com](https://www.loudproudandfree.com)

Hay vídeos paso a paso de este tutorial planificados en los cuatro idiomas — síguelos en los enlaces de arriba.
