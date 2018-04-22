

ksk-renam-examp.fst: ksk-renam-examp.pstr
	python3 ../twexamp.py $< $@

ksk-renam-examp.pstr: ksk-raw-examp.csv ksk-raw2named.csv ../raw2named.py
	python3 ../raw2named.py $< $@ ksk-raw2named.csv

ksk-raw-examp.csv: ksk-zerofilled.csv ../zerofilled2rawmphon.py
	python3 ../zerofilled2rawmphon.py $< $@

ksk-zerofilled.csv: ksk-seg-examp.csv ../segm2zerofilled.py
	python3 ../segm2zerofilled.py $< $@

ksk-seg-examp.csv: ksk-paradigms.csv ../paratab2segcsv.py
	python3 ../paratab2segcsv.py $< $@

#ksk-examp.pstr: ksk-raw-examp.csv
#	cat $< | cut -d ',' -f 5 | egrep ' ' > $@

features: ksk-zerofilled.csv
	cat $< | cut -d ',' -f 1 | cut -d ' ' -s -f 2,3 | tr ' ' '\n' | sort | uniq

rawlist: ksk-raw-examp.csv
	cat $< | cut -d ',' -f 4 | tr ' ' '\n' | sort | egrep '...' | uniq > raw_mphons.str
