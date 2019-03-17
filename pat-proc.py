""" pat-proc.py: produces either a converter or a guesser from *pat.csv

Copyright © 2017, Kimmo Koskenniemi

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or (at
your option) any later version.

This program is distributed in the hope that it will be useful, but
WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""
import csv, re, argparse
from collections import OrderedDict

multichs = set()

definitions = OrderedDict()

patterns = OrderedDict()
pattern_lst = [] # a list of tuples (cont, iclass, expr, weight, comment)
singleton_lst = [] # list of tuples (cont, iclass, input, output, weight, comment)
cont_set = set()
iclass_set = set()

def extract_multichs(regexp):
    global multichs, definitions
    rege = re.sub(r"([][()|\$\&\-\+*: ]|\.[iul]|\.o\.)+", ",", regexp)
    lst = re.split(r",", rege)
    for nm in lst:
        if len(nm) > 1 and (nm not in definitions):
            multichs.add(nm)
    return

def add_perc(str):
    return re.sub(r"([{'}])", r"%\1", str)

def proj_down_regex(str):
    lst = re.split(r"([\]\[\|\-\+\* ]+|\.[iul]|\.o\.)", str)
    downlst = [re.sub(r"([a-zåäö'øØ0]):({[a-zåäö'øØ]+}|0)", r"\2", el) for el in lst]
    reslst = [re.sub(r"^0$", r"", el) for el in downlst]
    res = "".join(reslst)
    res = re.sub(r"\s+\[\s*\|\s*\]\s*", r" ", res)
    res = re.sub(r"\s+", r" ", res)
    res = re.sub(r"\s+$", r"", res)
    return res

def ksk2entrylex(root_lex_name):
    global multichs
    for cont in cont_set:
        multichs.add(cont)
    multichs = multichs | iclass_set
    print("Multichar_Symbols")
    print(" ", " ".join(sorted(multichs)))
    print("Definitions")
    for dn in definitions.keys():
        print(" ", dn, "=", add_perc(definitions[dn]), ";")
    print("LEXICON", root_lex_name)
    for cont, iclass, input, output, weight, comment in singleton_lst:
        w = ' "weight: ' + weight + '"' if weight else ""
        i_class = re.sub(r"([*])", r"%\1", iclass)
        print(input + i_class + ":" + output ,
                  cont, w, '; !', comment)
    for cont, iclass, pat, weight, comment in pattern_lst:
        ##w = ' "weight: ' + weight + '"' if weight else ""
        w = "::" + weight if weight else ""
        i_class = re.sub(r"([*])", r"%\1", iclass)
        print("<", add_perc(pat[1:-1]),
                  i_class + ":0" + w + " >",
                  cont, "; !", comment)
    for cont in sorted(list(cont_set)):
        print("LEXICON", cont)
        print(":% " + cont, "# ;")
    return

def ksk2guesserlex(root_lex_name):
    import affixmultich
    print("Multichar_Symbols")
    print(" ", " ".join(sorted(multichs |
                                   affixmultich.nexts |
                                   affixmultich.multichars)))
    print("Definitions")
    for dn in definitions.keys():
        downde = proj_down_regex(definitions[dn])
        print(" ", dn, "=", add_perc(downde), ";")
    print("LEXICON", root_lex_name)
    for cont, iclass, input, output, weight, comment in singleton_lst:
        w = ' "weight: ' + weight + '"' if weight else ""
        print(output, cont, w, '; !', comment)
    for cont, iclass, pat, weight, comment in pattern_lst:
        w = '"weight: '+weight+'"' if weight else ""
        downpat = proj_down_regex(pat[1:-1])
        print("<", add_perc(downpat), ">", cont, w, ";")
    return

argparser = argparse.ArgumentParser(
    "python3 di2mi-to-di2mi.py",
    description="Writes either a converter or a guesser")
argparser.add_argument(
    "patterns",
    help="A csv input file containing the patterns")
argparser.add_argument(
    "-c", "--classes",
    default="infl-codes.text",
    help="output file containing inflectional classes found in the patterns")
argparser.add_argument(
    "-n", "--root-lexicon-name",
    default="words",
    help="name of the initial lexicon to be written")
argparser.add_argument(
    "-m", "--mode", choices = ['c', 'g'],
    help="'g' for guesser, 'c' for converter",
    default="c")
argparser.add_argument(
    "-v", "--verbosity", default=0, type=int,
    help="level of diagnostic output")
args = argparser.parse_args()

patfile = open(args.patterns, "r")
pat_rdr = csv.DictReader(patfile, delimiter=',')
prevID = ";;;"
for r in pat_rdr:
    if args.verbosity >= 10:
        print(r)
    cont, i_class, mfon, comment = r['CONT'], r['ICLASS'], r['MPHON'], r['COMMENT']
    if cont != "" and cont[0] == '!':
        if args.verbosity >= 10:
            print("- it is a comment line")
        continue
    if cont == "Define":
        if args.verbosity >= 10:
            print("- it is a definition")
        definitions[i_class] = mfon
    else:
        cont_set.add(cont)
        iclass_set.add(i_class)
        m = re.match(r"^\s*(<.*>)\s*([0-9]*)\s*$", mfon)
        if m:                             # it looks like a reg ex pattern
            if args.verbosity >= 10:
                print("- it is a pattern")
            regex = m.group(1)
            weight = m.group(2)
            pattern_lst.append((cont, i_class, regex, weight, comment))
            continue
        m = re.match(r"^\s*([a-zåäöšž']+):([a-zåäöšžA-ZÅÄÖŠŽ{Ø'}]+)\s*([0-9]*)\s*$", mfon)
        #print(cont, i_class, mfon)###
        if m:                             # it looks like a direct result for a single entry
            if args.verbosity >= 10:
                print("- it is a single entry")
            singleton_lst.append((cont, i_class,
                                      m.group(1), m.group(2), m.group(3),
                                      comment))
        else:                             # not valid at all
            print("***", r, "***")

patfile.close()
#print(singleton_lst)###

for cont, iclass, pat, weight, comment in pattern_lst:
    extract_multichs(pat[1:-1])
for dn,pe in definitions.items():
    extract_multichs(pe)

if args.mode == 'c':
    ksk2entrylex(args.root_lexicon_name)
elif args.mode == 'g':
    ksk2guesserlex(args.root_lexicon_name)
else:
    print("value of --mode must be either 'g' or 'c'")
    exit()
if args.classes:
    class_file = open(args.classes, "w")
    print(" ".join(list(iclass_set)), file=class_file)
    class_file.close()
