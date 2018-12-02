# wordlist2entries :
# converts KSK entries into LEXC entries

import re, sys, hfst, argparse
argparser = argparse.ArgumentParser("python3 wordlist2entries.py",
    description="Converts a word list of entries into entries in "
        "LEXC format according to converter")
argparser.add_argument("wordlist",
    help="list of base forms and attached inflection codes",
    default="~/Dropbox/lang/fin/ksk/ksk-v.dic")
argparser.add_argument("converter", default="finv-pattern-conv.fst",
    help="a converter FST made out of patterns")
argparser.add_argument("codes", default="finv-codes.text",
    help="a space-separated list of inflection codes found in the patterns. "
        "Entries in wordlist with other inflection codes are ignored.")
argparser.add_argument("lexentries", default="finv-words.lexc",
    help="entries converted into LEXC format with appropriate morphophonemes and continuations")
argparser.add_argument("-v", "--verbosity", default=0, type=int,
    help="level of diagnostic output")
args = argparser.parse_args()


converter_file = hfst.HfstInputStream(args.converter)
converter_fst = converter_file.read()
converter_fst.lookup_optimize()
infl_set =  set(open(args.codes).read().split())
#print("infl_set =", infl_set) ###
entrylist = []
multiharacters = set()

def find_multichars(str):
    lst = re.findall(r"\{[a-zåäöšžØ']+\}", str)
    for sym in lst:
        multiharacters.add(sym)

wordlist_file = open(args.wordlist, "r")
linenum = 0
for linenl in wordlist_file:
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
        print("word: <" + word + ">")
    if len(lst) > 2 and lst[2][0] == "*":
        infl = lst[1] + "*"
    else:
        infl = lst[1]
    if args.verbosity >= 10:
        print("infl: <" + infl + ">")
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
    if args.verbosity >= 10:
        print("symtup: ", symtup)
    res = converter_fst.lookup(symtup)
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

outf = open(args.lexentries, "w")
print("Multichar_Symbols", file=outf)
print(" ".join(sorted(multiharacters)), file=outf)
print("LEXICON Root", file=outf)
for entry in entrylist:
    print(entry, ';', file=outf)
