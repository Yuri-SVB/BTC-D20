# Build the BIP39-D20 kit: the lookup table plus one instruction sheet per
# language. Final PDFs land in dist/ (committed for convenience; CI rebuilds
# them from source on every push).
#
#   make            build everything into dist/
#   make table      lookup table only
#   make en         one instruction edition (en, es, it, pt-br)
#   make verify     run integrity + worked-example checks
#   make clean      remove LaTeX build clutter (keeps dist/)

LANGS    := en es it pt-br
LATEXMK  := latexmk -pdf -interaction=nonstopmode -halt-on-error
DIST     := dist
WORDLIST := external/bips/bip-0039/english.txt

INSTRUCTION_PDFS := $(foreach l,$(LANGS),$(DIST)/instructions-$(l).pdf)

.PHONY: all table instructions verify wordlist clean $(LANGS)

all: table instructions

table: $(DIST)/bip39-table.pdf

instructions: $(INSTRUCTION_PDFS)

$(LANGS): %: $(DIST)/instructions-%.pdf

$(DIST)/bip39-table.pdf: table/bip39-table.tex $(WORDLIST)
	cd table && $(LATEXMK) bip39-table.tex
	@mkdir -p $(DIST)
	cp table/bip39-table.pdf $@

# The word data lives in the canonical bitcoin/bips repository, mounted as a
# commit-pinned submodule. Fetch it minimally when absent: only the pinned
# commit (blob-filtered) with only bip-0039/ checked out -- a few hundred KB,
# not the whole repository. A regular `git clone --recurse-submodules`
# (shallow) works too and simply skips this rule.
$(WORDLIST):
	@echo "fetching pinned bitcoin/bips bip-0039/ (sparse, blob-filtered)" && \
	pin=$$(git rev-parse HEAD:external/bips) && \
	url=$$(git config -f .gitmodules submodule.external/bips.url) && \
	git -C external/bips init -q && \
	git -C external/bips sparse-checkout set --no-cone /bip-0039/ && \
	git -C external/bips fetch -q --depth 1 --filter=blob:none $$url $$pin && \
	git -C external/bips checkout -q FETCH_HEAD

wordlist: $(WORDLIST)

# One explicit rule per language (a pattern rule cannot repeat '%' inside a
# single prerequisite path like instructions/%/instructions-%.tex).
define INSTR_RULE
$(DIST)/instructions-$(1).pdf: instructions/$(1)/instructions-$(1).tex instructions/common/preamble.tex
	cd instructions/$(1) && $(LATEXMK) instructions-$(1).tex
	@mkdir -p $(DIST)
	cp instructions/$(1)/instructions-$(1).pdf $$@
endef
$(foreach l,$(LANGS),$(eval $(call INSTR_RULE,$(l))))

verify:
	python3 tools/verify_tutorial.py

clean:
	cd table && latexmk -C bip39-table.tex || true
	for l in $(LANGS); do (cd instructions/$$l && latexmk -C instructions-$$l.tex) || true; done
