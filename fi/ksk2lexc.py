# ksk2lexc :
# converts KSK entries into LEXC entries

import re, sys, hfst, argparse

argparser = argparse.ArgumentParser(
    "python3 ksk2lexc.py",
    description="Converts KSK entries into LEXC format")
argparser.add_argument(
    "ksk",
    help="input file, e.g. ~/Dropbox/lang/fin/ksk/ksk-v.dic")
argparser.add_argument(
    "fst", help=" conversion fst, e.g. ofi-conv-n.fst")
argparser.add_argument(
    "name", help="name of the lexicon for entries created")
argparser.add_argument(
    "lexc", help="output file, e.g. ofi-words-n.lexc")
argparser.add_argument(
    "-c", "--codes", help="infl-codes.text")
argparser.add_argument(
    "-v", "--verbosity", type=int, default=0,
    help="level of diagnostic info printed")
args = argparser.parse_args()

ksk_file = open(args.ksk, "r")

fstfile = hfst.HfstInputStream(args.fst)
fst = fstfile.read()
fst.lookup_optimize()

outf = open(args.lexc, "w")

infl_set =  set(open(args.codes).read().split())
if args.verbosity >= 5:
    print("infl_set =", infl_set) ###

entrylist = []

multiharacters = set()

def find_multichars(str):
    lst = re.findall(r"\{[^{}:\s]+\}", str)
    for sym in lst:
        multiharacters.add(sym)

linenum = 0
for linenl in ksk_file:
    linenum += 1
    line = linenl.strip()
    if args.verbosity >= 10:
        print("line:", line)
    if re.search(r"[/!Y]", line):
        continue
    lst = line.split(" ")
    if len(lst) < 2:
        print("LINE", linenum,
                  "HAS NOT ENOUGH FIELDS:", '"' + line + '"')
        continue
    word = re.sub(r"[0-9]+$", r"", lst[0]).strip()
    if args.verbosity >= 10:
        print("word: <" + word + ">") ###
    if len(lst) > 2 and lst[2][0] == "*":
        infl = lst[1] + "*"
    else:
        infl = lst[1]
    if args.verbosity >= 10:
        print("infl: <" + infl + ">") ###
    if infl not in infl_set:
        continue
    if not (re.match(r"^[a-zšžåäö']+$", word)):
        print(linenum, "word not ok:", '"' + line + '"')
        continue
    if not (re.match(r"^[VS][0-9][0-9][*]?", infl)):
        print(linenum, "infl not ok:", '"' + line + '"')
        continue
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

print("Multichar_Symbols", file=outf)
print(" ".join(sorted(multiharacters)), file=outf)
print("LEXICON", args.name, file=outf)
for entry in entrylist:
    print(entry, ';', file=outf)
