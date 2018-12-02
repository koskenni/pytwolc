# wordlist2entriesusingcorpus.py

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
    description="Produces lexicon entries using also corpus but without interaction")
argparser.add_argument(
    "guesser",
    help="a guesser fst produced entry-pattern.py")
argparser.add_argument(
    "corpguesses",
    help="fst composed out of a word list fst and a guesser fst")
argparser.add_argument(
    "-u", "--unique", type=int, default=0,
    help="accept an entry which has at least UNIQUE forms in corpus"
    " and the set is not a subset of any other entry")
argparser.add_argument(
    "-r", "--reject", default=1000000, type=int,
    help="reject candidates with penalty worse than the best by REJECTION or more")
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

def unique_entry(word_form_set, word_form):
    """Returns the set of entries which accept all word forms in word_form_set"""
    remaining_entries = {0}
    first = True
    for word_form in word_form_set | {word_form}:
        entries_and_weights = guesser_fst.lookup(word_form, output="tuple")
        entries = set()
        for e,w in entries_and_weights:
            entries.add(e)
        if remaining_entries == {0}:
            remaining_entries = entries
        else:
            remaining_entries = remaining_entries & entries
        if not remaining_entries:
            break
    return remaining_entries

corp_fil = hfst.HfstInputStream(args.corpguesses)
corp_fst = corp_fil.read()
corp_fil.close()
corp_fst.minimize()
corp_fst.lookup_optimize()

def check_corp(entry):
    """Finds what word forms in the corpus the 'entry' could have.

Returns a set of word forms occurring corpus which 'entry' would accept.
"""
    result = corp_fst.lookup(entry, output="tuple")
    corp_words = [wd for wd,wg in result]
    return set(corp_words)

def nextline():
    linenl = sys.stdin.readline()
    if not linenl:
        exit()
    return linenl.strip()

def comparer(rec):
    (e,ws,w,u) = rec
    key = "{:4d}{:4.1f}{}".format(100-len(ws), 1000000-w, "A" if u else "B")
    return key

if args.verbosity >= 1:
    print("\nENTER FORMS OF A WORD:\n")
while True:
    word_form = nextline()
    #
    entry_weight_tuple_lst = guesser_fst.lookup(word_form, output="tuple")
    #
    if not entry_weight_tuple_lst:
        print("!!!", word_form)
        continue
    remaining_entries = set()
    weights = {}
    word_form_sets = {}
    for (entry, weight) in entry_weight_tuple_lst:
        remaining_entries.add(entry)
        weights[entry] = weight
        word_form_set = check_corp(entry) # words in the corpus that 'entry' accepts
        word_form_sets[entry] = word_form_set
    # now 'remaining_entries' is the set of entries which would accept 'word_form'
    entry_list = []
    for entry in remaining_entries:
        #
        ent_set = unique_entry(word_form_sets[entry], word_form) # this and possibly other entries which accept 'word_form_set'
        #
        # 'word_form_sets[entry]' uniquely defines 'entry' if 'ent_set' is {'entry'}
        entry_list.append((entry, word_form_sets[entry], weights[entry], len(ent_set)==1))
    entry_lst = sorted(entry_list, key=comparer)
    # ordered primarily so that entries with most matches in corpus are at top,
    # secondarily so that entries with less penalty weight come first
    # finally, entries which are uniquely by their matching words precede those that are not
    #
    i = 0
    for (entry, word_form_set, weight, uniq) in entry_lst:
        i = i + 1
        word_form_lst = list(word_form_set)
        if i == 1 and uniq and len(word_form_set) >= args.unique:
            print("{} ! {} = [{}]".format(entry, word_form, " ".join(word_form_lst)))
            break
        elif len(entry_lst) == 1:
            print("{} ! {} : {} = [{}]".format(entry, weight, word_form, " ".join(word_form_lst)))
        elif len(word_form_lst) >= args.unique:
            print("! {} ! {} : {} [{}]".format(word_form, entry, weight, " ".join(word_form_lst)))
        else:
            print("!! {} ! {} : {} [{}]".format(word_form, entry, weight, " ".join(word_form_lst)))


