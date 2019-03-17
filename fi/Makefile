
ofi-conv-lex.fst: ofi-conv-n.lexc
	hfst-lexc -o $@ $<

ofi-conv-n.lexc: ofi-pat-n.csv
	python3 ../pat-proc.py ofi-pat-n.csv -c classes.txt -m c -n Root > ofi-conv-n.lexc

ofi-analy-aff.lexc: ofi-affixes.csv
	python3 ../affixes2analysis.py -n Root $< $@

clean:
	rm ofi-*.lexc ofi-*.fst


features: ksk-zerofilled.csv
	cat $< | cut -d ',' -f 1 | cut -d ' ' -s -f 2,3 | tr ' ' '\n' | sort | uniq

rawlist: ksk-raw-examp.csv
	cat $< | cut -d ',' -f 4 | tr ' ' '\n' | sort | egrep '...' | uniq > raw_mphons.str
