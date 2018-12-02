pref = finv
corp = sktp
wordlist = ksk-v-samp.dic

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

$(pref)-affix-guess.lexc : $(pref)-affixes.csv
	python3 ../affixcsv2guesslexc.py -d ';' $< $@

$(pref)-lemmatizer.fst : $(pref)-analy-lexicon.fst rul.m2s.fst
	hfst-compose-intersect -1 $< -2 rul.m2s.fst | hfst-compose -2 delete.fst | hfst-invert | hfst-compose-intersect -2 rul.m2s.fst | hfst-compose -2 delete.fst | hfst-minimize | hfst-fst2fst -O -o $@

$(pref)-analyzer.fst : $(pref)-analy-lexicon.fst rul.m2s.fst
	hfst-compose-intersect -1 $< -2 rul.m2s.fst | hfst-compose -2 delete.fst | hfst-invert | hfst-minimize | hfst-fst2fst -O -o $@

$(pref)-analy-lexicon.fst : $(pref)-analy-entries.lexc $(pref)-affix-analy.lexc
	hfst-lexc -o $@ $< $(pref)-affix-analy.lexc

$(pref)-analy-entries.lexc : $(pref)-pattern-conv.fst $(pref)-codes.text
	python3 ../wordlist2entries.py $(wordlist) $< $(pref)-codes.text $@

$(pref)-pattern-conv.fst : $(pref)-pattern-conv.lexc
	hfst-lexc -o $@ $<

$(pref)-pattern-conv.lexc : $(pref)-pattern.csv
	python3 ../entry-pattern.py $< $@ -d ';' --classes $(pref)-codes.text

$(pref)-affix-analy.lexc : $(pref)-affixes.csv
	python3 ../affixcsv2analylexc.py -d ';' $< $@

rul.m2s.fst : rul.m2s.twolc
	hfst-twolc < $< -D -o $@

delete.fst :
	echo "Ø -> 0" | hfst-regexp2fst -f openfst-tropical -o delete.fst

