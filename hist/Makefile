ALGH = afe
LGS = fi,et
SRC = fi
TRG = et

$(SRC)2$(TRG).fst : $(ALGH)-rules.fst zero2eps.fst eps2zero.fst trivials
	hfst-compose -1 eps2zero.fst -2 $(SRC)2$(ALGH).fst | \
	hfst-compose-intersect -2 $(ALGH)-rules.fst | \
	hfst-compose -2 $(ALGH)2$(TRG).fst | \
	hfst-compose -2 zero2eps.fst -o $@

$(ALGH)-rules.fst : $(ALGH).rules
	python3 ../twol.py $(ALGH).algh $(ALGH).rules \
	-r 10000 -t 2 -o $@ -w $(ALGH)-wrong.fst \
	-v 2 2>&1 > $(ALGH)-rules.log

$(ALGH).rules : $(ALGH).algh $(ALGH).alpha ../histdiscov.py
	python3 ../histdiscov.py $(ALGH).algh -g $(ALGH).alpha 2>&1 > $(ALGH).rules

zero2eps.fst :
	echo 'Ø -> 0' | hfst-regexp2fst -o zero2eps.fst

eps2zero.fst :
	hfst-invert -i zero2eps.fst -o eps2zero.fst

trivials :
	python3 algh2x.py $(ALGH).algh $(LGS) -v 1 2>&1

