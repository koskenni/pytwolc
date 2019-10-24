BASE = afe
LGS = fi,et
SRC = fi
TRG = et
RECURS = 5000
VERB = 0

$(SRC)2$(TRG).fst : $(BASE)-rules.fst zero2eps.fst eps2zero.fst trivials
	hfst-compose -1 eps2zero.fst -2 $(SRC)2$(BASE).fst | \
	hfst-compose-intersect -2 $(BASE)-rules.fst | \
	hfst-compose -2 $(BASE)2$(TRG).fst | \
	hfst-compose -2 zero2eps.fst -o $@

$(BASE)-rules.fst : $(BASE).rules
	python3 ../twol.py $(BASE).algh $(BASE).rules \
	-r $(RECURS) -t 2 -o $@ -w $(BASE)-wrong.fst \
	-v 2 2>&1 -v $(VERB) > $(BASE)-rules.log

$(BASE).rules : $(BASE).algh $(BASE).alpha ../histdiscov.py
	python3 ../histdiscov.py $(BASE).algh \
	-g $(BASE).alpha 2>&1 > $(BASE).rules

$(BASE).algh : $(BASE).cogn $(BASE).alpha
	python3 ../multialign.py -a $(BASE).alpha -l horizontal \
	< $(BASE).cogn > $(BASE).algh

zero2eps.fst :
	echo 'Ø -> 0' | hfst-regexp2fst -o zero2eps.fst

eps2zero.fst :
	hfst-invert -i zero2eps.fst -o eps2zero.fst

trivials :
	python3 algh2x.py $(BASE).algh $(LGS) -v 1 2>&1

$(SRC).words : $(BASE).tsv
	cut $(BASE).tsv -f 1 > $(SRC).words


#
# $ python3 csv2cogset.py < sovh.tsv > ov.cogn
#
# $ python3 ../multialign.py < ov.cogn > ov.algh -l horizontal -a ovh.alpha
