POS=v

ofi-$(POS).ofst: ofi-lex-$(POS).fst ofi-rules.fst ofi-examples.pstr delete.fst
	hfst-compose-intersect -a -1 $< -2 ofi-rules.fst |\
	hfst-compose -2 delete.fst |\
	hfst-invert |\
	hfst-minimize |\
	hfst-fst2fst -O -o $@

ofi-lex-$(POS).fst: ofi-lex-$(POS).lexc ofi-analy-aff.lexc
	hfst-lexc -o $@ ofi-analy-aff.lexc $<

ofi-lex-$(POS).lexc: ofi-conv-$(POS).fst ksk2lexc.py Makefile
	python3 ksk2lexc.py --codes=classes.txt ~/Dropbox/lang/fin/ksk/ksk-$(POS).dic $< Nouns $@ > ofi-lex-$(POS).log

ofi-conv-$(POS).fst: ofi-conv-$(POS).lexc
	hfst-lexc -o $@ $<

ofi-conv-$(POS).lexc: ofi-pat-$(POS).csv ../pat-proc.py
	python3 ../pat-proc.py -c classes.txt -m c -n Root $< > $@

ofi-guess-$(POS).fst: ofi-guess-lex-$(POS).fst ofi-rules.fst Makefile
	hfst-compose-intersect -a -1 $< -2 ofi-rules.fst |\
	hfst-compose -2 delete.fst |\
	hfst-minimize > $@

ofi-guess-lex-$(POS).fst: ofi-guess-lex-$(POS).lexc ofi-guess-aff.lexc
	hfst-lexc -o $@ ofi-guess-aff.lexc $<

ofi-guess-lex-n.lexc : ofi-pat-$(POS).csv
	python3 ../pat-proc.py -m g -n Nouns $< > $@

ofi-guess-lex-v.lexc : ofi-pat-$(POS).csv
	python3 ../pat-proc.py -m g -n Verbs $< > $@

ofi-guess-aff.lexc: ofi-affixes.csv
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
