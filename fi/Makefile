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

ofi-guess-n.ofst: ofi-guess-lex-n.fst ofi-rules.fst Makefile
	hfst-compose-intersect -e -a -1 $< -2 ofi-rules.fst |\
	hfst-compose -2 delete.fst |\
	hfst-invert |\
	hfst-minimize -o ofi-guess-n.fst
	hfst-fst2fst -w -i ofi-guess-n.fst -o $@

ofi-guess-v.ofst: ofi-guess-lex-v.fst ofi-rules.fst Makefile
	hfst-compose-intersect -e -a -1 $< -2 ofi-rules.fst |\
	hfst-compose -2 delete.fst |\
	hfst-invert |\
	hfst-minimize -o ofi-guess-v.fst
	hfst-fst2fst -w -i ofi-guess-v.fst -o $@

ofi-guess-lex-n.fst: ofi-guess-lex-n.lexc ofi-guess-aff.lexc
	hfst-lexc -E -f openfst-tropical -o $@ ofi-guess-aff.lexc $<

ofi-guess-lex-v.fst: ofi-guess-lex-v.lexc ofi-guess-aff.lexc
	hfst-lexc -E -f openfst-tropical -o $@ ofi-guess-aff.lexc $<

ofi-guess-lex-n.lexc : ofi-guespat-n.text
	python3 guespat2lexc.py < $< > $@

#ofi-guess-lex-n.lexc : ofi-pat-n.csv ../pat-proc.py
#	python3 ../pat-proc.py -m g -n Verbs $< > $@

ofi-guess-lex-v.lexc : ofi-pat-v.csv ../pat-proc.py
	python3 ../pat-proc.py -m g -n Verbs $< > $@

ofi-guess-aff.lexc: ofi-affixes.csv ../affixes2guessing.py
	python3 ../affixes2guessing.py $< $@

ofi-analy-aff.lexc: ofi-affixes.csv ../affixes2analysis.py Makefile
	python3 ../affixes2analysis.py -e $< $@

ofi-rules.fst: ksk-rules.twol ofi-examples.pstr
	python3 ../twol.py -t 2 -v 1 -w ofi-wrong.fst -l ofi-lost.fst -o $@ ofi-examples.pstr $< > ofi-rules.log

delete.fst:
	echo "Ø -> 0" | hfst-regexp2fst -o $@

clean:
	rm -f ofi-*.fst ofi-*.ofst
	rm -f ofi-lexic-*.lexc
	rm -f ofi-guess*.lexc


features: ksk-zerofilled.csv
	cat $< | cut -d ',' -f 1 | cut -d ' ' -s -f 2,3 | tr ' ' '\n' | sort | uniq

rawlist: ksk-raw-examp.csv
	cat $< | cut -d ',' -f 4 | tr ' ' '\n' | sort | egrep '...' | uniq > raw_mphons.str
