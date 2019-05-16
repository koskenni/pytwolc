
import re, sys

multichars = set()
single_words = set()
compound_forms = {}

nouns = {}
verbs = {}
first_part_nouns = set()

for linenl in sys.stdin:
    line = linenl.strip()
    [word, rest] = line.split(maxsplit=1)
    if not ";" in rest:
        continue
    [entry, feat_str] = rest.split(sep= ";", maxsplit=1)
    [mphon, cont] = entry.split(sep=" ", maxsplit=1)
    entry = entry
    if "+INS" in feat_str:
        continue
    mch_lst = re.findall(r"{[^}]+}", mphon)
    for mch in mch_lst:
        multichars.add(mch)
    if not "{§}" in entry:
        single_words.add(word)
    else:
        if not entry in compound_forms:
            compound_forms[entry] = set()
        compound_forms[entry].add(word)
        continue
    if " /v" in entry:
        if entry not in verbs:
            verbs[entry] = 0
        verbs[entry] += 1
    elif " /s" in entry:
        if entry not in nouns:
            nouns[entry] = 0
        nouns[entry] += 1
        if feat_str == "+N+SG+GEN":
            first_part_nouns.add(word + ' SecondNoun "weight: 10"')
        elif feat_str == "+N+SG+NOM":
            if feat_str.endswith("{ns}{eeØØ}{nØØØ} /s;"):
                first_part_nouns.add(word[0:-3] + 's SecondNoun "weight: 10"')
            else:
                first_part_nouns.add(word + ' SecondNoun "weight: 10"')

print("Multichar_Symbols")
print(" ".join(list(multichars)))
print("LEXICON Nouns")
for entry, count in sorted(nouns.items()):
    print(entry, "; !", count)
print("LEXICON Verbs")
for entry, count in sorted(verbs.items()):
    print(entry, "; !", count)
print("LEXICON FirstPartNouns")
for entry in sorted(list(first_part_nouns)):
    print(entry, ";")
print("LEXICON Compounds")
for entry, forms in sorted(compound_forms.items()):
    if forms < single_words or len(forms) < 10:
        continue
    print(entry, ' "weight: 5"; !', len(forms))



    
    
