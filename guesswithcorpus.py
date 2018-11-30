# entryharvester.py

copyright = """Copyright © 2017, Kimmo Koskenniemi

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

import hfst, sys, argparse, pprint
pp = pprint.PrettyPrinter(indent=1, compact=True)

argparser = argparse.ArgumentParser(
    "python3 corpguesser.py",
    description="Produces lexicon entries using also corpus data")
argparser.add_argument(
    "guesser",
    help="a guesser fst produced entry-pattern.py")
argparser.add_argument(
    "corpguesses",
    help="fst composed out of a word list fst and a guesser fst")
argparser.add_argument(
    "-u", "--unique", type=int, default=0,
    help="if > 0 then accept an entry which has a sufficient set of word forms in corpus")
argparser.add_argument(
    "-v", "--verbosity", type=int, default=0,
    help="level of  diagnostic output")
args = argparser.parse_args()

guesser_fil = hfst.HfstInputStream(args.guesser)
guesser_fst = guesser_fil.read()
guesser_fil.close()
guesser_fst.invert()
guesser_fst.minimize()
guesser_fst.lookup_optimize()

def unique_entry(word_forms):
    """Returns the set of entries which accept all word forms in word_forms"""
    remaining = {0}
    first = True
    for word_form in word_forms:
        entries_and_weights = guesser_fst.lookup(word_form, output="tuple")
        entries = set()
        for e,w in entries_and_weights:
            entries.add(e)
        if remaining == {0}:
            remaining = entries
        else:
            remaining = remaining & entries
        if not remaining:
            break
    return remaining

corp_fil = hfst.HfstInputStream(args.corpguesses)
corp_fst = corp_fil.read()
corp_fil.close()
corp_fst.minimize()
corp_fst.lookup_optimize()

def check_corp(entry, word_form):
    """Finds what word forms in the corpus the entry could have.

Returns a list of word forms including the one given as the second parameter.
"""
    result = corp_fst.lookup(entry, output="tuple")
    corp_words = [wd for wd,wg in result]
    word_form_set = set(corp_words)
    word_form_set.add(word_form)
    word_forms = list(word_form_set)
    return word_forms

def nextline():
    linenl = sys.stdin.readline()
    if not linenl:
        exit()
    return linenl.strip()

def comparer(rec):
    (e,ws,w,u) = rec
    key = "{:4d}{:4.1f}{}".format(100-len(ws), 1000-w, "A" if u else "B")
    return key

if args.verbosity >= 0:
    print("\nENTER FORMS OF A WORD:\n")
while True:
    word_form = nextline()
    entry_weight_tuple = guesser_fst.lookup(word_form, output="tuple")
    remaining = set()
    weight = {}
    for (entry,w) in entry_weight_tuple:
        remaining.add(entry)
        weight[entry] = w
    # now 'remaining' is the set of entries which would accept 'word_form'
    # the solution is among the entries in 'remaining'
    dic = {}
    for entry in remaining:
        word_forms = check_corp(entry, word_form)
        # 'word_forms' are the word forms in the corpus which would be accepted by 'entry'
        dic[entry] = set(word_forms)
    ce_list = [(entry, word_forms) for (entry, word_forms) in list(dic.items()) if word_forms]
    if args.verbosity >= 10:
        print("ce_list:", ce_list)
    entry_list = []
    for entry, word_forms in ce_list:
        ents = unique_entry(list(word_forms)) # this and possibly other entries which accept 'word_forms'
        # the forms of 'entry' found in the corpus would define 'entry'
        entry_list.append((entry, word_forms, weight[entry], len(ents)==1))
    entry_lst = sorted(entry_list, key=comparer)
    i = 0
    for (entry, word_forms, w, uniq) in entry_lst:
        i = i + 1
        print("    ({:d}) {} : {} {:.1f} {}".format(i, entry, "OK" if uniq else "", w, word_forms))
        if i == 1 and uniq and args.unique > 1:
            remaining = set([entry])
        elif args.unique > 5:
            remaining = set()
            break

    if args.verbosity >= 0:
        print()
    while len(remaining) > 1:
        line = nextline()
        if line == "":
            print("GIVING UP THIS WORD\n\n")
            break
        elif line.isdigit():
            i = int(line)
            if i > len(entry_lst):
                print("OUT OF RANGE! IGNORED")
                continue
            e, ws, w, u = entry_lst[i-1]
            #print("**", i, e, ws, w, u)###
            remaining = set([e])
            if args.verbosity >= 10:
                print("remaining:", remaining)
            break
        if line[0] == '-':
            res = guesser_fst.lookup(line[1:], output="tuple")
        else:
            res = guesser_fst.lookup(line, output="tuple")
        entries = set([r for r,w in res])
        saved = remaining
        if line[0] == '-':
            remaining = remaining - entries
        else:
            remaining = remaining & entries
        if not remaining:
            print("DOES NOT FIT! IGNORED.")
            remaining = saved
        elif len(remaining) > 1:
            print(" "*8, [(e, weight[e]) for e in remaining], "\n")

    if len(remaining) == 1:
        e = list(remaining)[0]
        if args.verbosity >= 0:
            print("\n" + "="*18)
        print(e, ";", weight[e])
        if args.verbosity >= 0:
            print("="*18 + "\n")
