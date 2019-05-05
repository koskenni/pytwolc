POS=v

LEX=ofi-lexic-n.lexc ofi-lexic-v.lexc

all: ofi-analy.ofst ofi-guess-n.ofst ofi-guess-v.ofst

ofi-analy.ofst: ofi-lexic.fst ofi-rules.fst delete.fst
	hfst-compose-intersect -a -1 $< -2 ofi-rules.fst |\
	hfst-compose -2 delete.fst |\
	hfst-invert |\
	hfst-minimize -o ofi-analy.fst
	hfst-fst2fst -i ofi-analy.fst -O -o $@

ofi-lexic.fst: ofi-analy-aff.lexc $(LEX) Makefile
	hfst-lexc -f openfst-tropical -o $@ ofi-analy-aff.lexc $(LEX)

ofi-lexic-n.lexc: ofi-lexic-n.text
	python3 entries2lexc.py Nouns < ofi-lexic-n.text > ofi-lexic-n.lexc

ofi-lexic-v.lexc: ofi-lexic-v.text
	python3 entries2lexc.py Verbs < ofi-lexic-v.text > ofi-lexic-v.lexc

ofi-guess-$(POS).ofst: ofi-guess-lex-$(POS).fst ofi-rules.fst Makefile
	hfst-compose-intersect -e -a -1 $< -2 ofi-rules.fst |\
	hfst-compose -2 delete.fst |\
	hfst-invert |\
	hfst-minimize -o ofi-guess-$(POS).fst
	hfst-fst2fst -w -i ofi-guess-$(POS).fst -o $@

ofi-guess-lex-$(POS).fst: ofi-guess-lex-$(POS).lexc ofi-guess-aff.lexc
	hfst-lexc -E -f openfst-tropical -o $@ ofi-guess-aff.lexc $<

ofi-guess-lex-n.lexc : ofi-pat-$(POS).csv ../pat-proc.py
	python3 ../pat-proc.py -m g -n Nouns $< > $@

ofi-guess-lex-v.lexc : ofi-pat-$(POS).csv ../pat-proc.py
	python3 ../pat-proc.py -m g -n Verbs $< > $@

ofi-guess-aff.lexc: ofi-affixes.csv ../affixes2guessing.py
	python3 ../affixes2guessing.py $< $@

ofi-analy-aff.lexc: ofi-affixes.csv ../affixes2analysis.py Makefile
	python3 ../affixes2analysis.py $< $@

ofi-rules.fst: ksk-rules.twol ofi-examples.pstr
	python3 ../twol.py -w ofi-wrong.fst -l ofi-lost.fst -o $@ ofi-examples.pstr $< > ofi-rules.log

ofi-examples.pstr: ofi-examples-n.pstr ofi-examples-v.pstr ofi-tests.pstr
	cat ofi-examples-n.pstr ofi-examples-v.pstr ofi-tests.pstr > $@

delete.fst:
	echo "Ø -> 0" | hfst-regexp2fst -o $@

clean:
	rm ofi-*.fst ofi-*.ofst
	rm ofi-lexic-*.lexc
	rm ofi-guess*.lexc


features: ksk-zerofilled.csv
	cat $< | cut -d ',' -f 1 | cut -d ' ' -s -f 2,3 | tr ' ' '\n' | sort | uniq

rawlist: ksk-raw-examp.csv
	cat $< | cut -d ',' -f 4 | tr ' ' '\n' | sort | egrep '...' | uniq > raw_mphons.str
