POS=v

ofi-$(POS).ofst: ofi-lex-$(POS).fst ofi-rules.fst ofi-examples.pstr delete.fst
	hfst-compose-intersect -a -1 $< -2 ofi-rules.fst |\
	hfst-compose -2 delete.fst |\
	hfst-invert |\
	hfst-minimize |\
	hfst-fst2fst -O -o $@

ofi-lex-$(POS).fst: ofi-lex-$(POS).lexc ofi-analy-aff.lexc Makefile
	hfst-lexc -f openfst-tropical -o $@ ofi-analy-aff.lexc $< ofi-pref-nom.lexc ofi-pref-gen.lexc

ofi-lex-$(POS).lexc: ofi-conv-$(POS).fst ksk2lexc.py Makefile
	python3 ksk2lexc.py --codes=classes.txt ~/Dropbox/lang/fin/ksk/ksk-$(POS).dic $< Nouns $@ > ofi-lex-$(POS).log

ofi-conv-$(POS).fst: ofi-conv-$(POS).lexc
	hfst-lexc -f openfst-tropical -o $@ $<

ofi-conv-$(POS).lexc: ofi-pat-$(POS).csv ../pat-proc.py
	python3 ../pat-proc.py -c classes.txt -m c -n Root $< > $@

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
	rm ofi-*.lexc ofi-*.fst


features: ksk-zerofilled.csv
	cat $< | cut -d ',' -f 1 | cut -d ' ' -s -f 2,3 | tr ' ' '\n' | sort | uniq

rawlist: ksk-raw-examp.csv
	cat $< | cut -d ',' -f 4 | tr ' ' '\n' | sort | egrep '...' | uniq > raw_mphons.str
