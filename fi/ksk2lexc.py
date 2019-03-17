# ksk2lexc :
# converts KSK entries into LEXC entries

import re, sys, hfst, argparse
argparser = argparse.ArgumentParser(
    "python3 ksk2lexc.py",
    description="Converts KSK entries into LEXC format")
argparser.add_argument(
    "-k", "--ksk",
    default="~/Dropbox/lang/fin/ksk/ksk-v.dic")
argparser.add_argument(
    "-l", "--lexc", default="ksk-words.lexc")
argparser.add_argument(
    "-f", "--fst", default="fin-conv.fst")
argparser.add_argument(
    "-c", "--codes", default="infl-codes.text")
args = argparser.parse_args()


fstfile = hfst.HfstInputStream(args.fst)
fst = fstfile.read()
fst.lookup_optimize()
outf = open(args.lexc, "w")
infl_set =  set(open(args.codes).read().split())
#print("infl_set =", infl_set) ###
entrylist = []
multiharacters = set()

def find_multichars(str):
    lst = re.findall(r"\{[a-zåäöšžØ']+\}", str)
    for sym in lst:
        multiharacters.add(sym)

import affixmultich

linenum = 0
for linenl in sys.stdin:
    linenum += 1
    line = linenl.strip()
    #print("line:", line) ###
    if re.search(r"[/!Y]", line):
        continue
    lst = line.split(" ")
    if len(lst) < 2:
        print("LINE", linenum,
                  "HAS NOT ENOUGH FIELDS:", '"' + line + '"')
        continue
    word = re.sub(r"[0-9]+$", r"", lst[0]).strip()
    #print("word: <" + word + ">") ###
    if len(lst) > 2 and lst[2][0] == "*":
        infl = lst[1] + "*"
    else:
        infl = lst[1]
    #print("infl: <" + infl + ">") ###
    if infl not in infl_set:
        continue
    if not (re.match(r"^[a-zšžåäö']+$", word)):
        print(linenum, "word not ok:", '"' + line + '"')
        continue
    if not (re.match(r"^[VS][0-9][0-9][*]?", infl)):
        print(linenum, "infl not ok:", '"' + line + '"')
        continue
    #if infl == "V41" and re.match(r"^[hjklmnprstv]*[äöye].*t[aä]$", word):
    #    infl = "V41ä"
    #elif infl == "V42" and re.match(r"^.*nt(aa|ää)$", word):
    #    infl = "V42n"
    iclass = infl#.replace('0', 'O')
    symlist = list(word)
    symlist.append(iclass)
    symtup = tuple(symlist)
    #print("symtup: ", symtup) ###
    res = fst.lookup(symtup)
    if not res:
        print(linenum, ':', line)
        continue
    best_w = min([w for r, w in res])
    for r, w in res:
        if w > best_w:
            continue
        mf, cont = re.split(r" +", r)
        find_multichars(mf)
        entrylist.append(r)

for sym in affixmultich.features:
    multiharacters.add(sym)
for sym in affixmultich.multichars:
    multiharacters.add(sym)
print("Multichar_Symbols", file=outf)
print(" ".join(sorted(multiharacters)), file=outf)
print("LEXICON Root", file=outf)
for entry in entrylist:
    print(entry, ';', file=outf)
