pref = finv
corp = sktp

$(pref)-$(corp)-guess.fst: ../../guessing/sktp-2plus.fst $(pref)-guess.fst
	hfst-compose -2 $< -1 $(pref)-guess.fst -o $@

$(pref)-guesser.fst : $(pref)-guess.fst
	hfst-invert -i $< | hfst-minimize | hfst-fst2fst -w -o $@

$(pref)-guess.fst : $(pref)-guess-lexicon.fst rul.m2s.fst delete.fst
	hfst-compose-intersect -1 $< -2 rul.m2s.fst | hfst-compose -2 delete.fst | hfst-minimize -o $@

$(pref)-guess-lexicon.fst : $(pref)-pattern-guess.lexc $(pref)-affix-guess.lexc
	hfst-lexc -o $@ $(pref)-pattern-guess.lexc $(pref)-affix-guess.lexc

$(pref)-pattern-guess.lexc : $(pref)-pattern.csv
	python3 ../entry-pattern.py $< $@ -d ';'

$(pref)-pattern-analy.lexc : $(pref)-pattern.csv
	python3 ../entry-pattern.py $< $@ -d ';' --classes $(pref)-codes.text

$(pref)-affix-guess.lexc : $(pref)-affixes.csv
	python3 ../affixcsv2guesslexc.py -d ';' $< $@

rul.m2s.fst : rul.m2s.twolc
	hfst-twolc < $< -D -o $@

delete.fst :
	echo "Ø -> 0" | hfst-regexp2fst -f openfst-tropical -o delete.fst

