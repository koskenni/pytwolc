# guessbygenerating.py

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

import hfst, sys, argparse

argparser = argparse.ArgumentParser(
    "python3 gyessbygenerating.py",
    description="Guess lexicon entries from generated forms of them")
argparser.add_argument(
    "guesser", help="Guesser file FST", default="ofi-guess-n.fst")
argparser.add_argument(
    "rules", 
    help="name of the two-level rule file")
argparser.add_argument(
    "-v", "--verbosity", default=0, type=int,
    help="level of diagnostic output")
args = argparser.parse_args()

guesser_fil = hfst.HfstInputStream(args.guesser)
guesser_fst = guesser_fil.read()
guesser_fil.close()
#guesser_fst.invert()
guesser_fst.minimize()
guesser_fst.lookup_optimize()

import sys, re
import generate

suf = {"/s": ["", "n", "{nrs}{aä}", "{ij}{Øt}{aä}"]}

for line_nl in sys.stdin:
    line = line_nl.strip()
    res = guesser_fst.lookup(line, output="tuple")
    if args.verbosity >= 10:
        print("lookup result =", res)
    entry_lst = [entry for entry, weight in res]
    stem_next_lst = [ent.split(" ") for ent in entry_lst]
    i = 0
    for [stem, next] in stem_next_lst:
        print(stem, next)
        suffix_lst = suf.get(next, "")
        word_lst = []
        for suffix in suffix_lst:
            results = generate.generate(stem+suffix)
            for r in results:
                #print("r =", r)###
                word = "".join(r).replace("Ø", "")
                word_lst.append(word)
        i += 1
        print("  ({})".format(i), " ".join(word_lst))
    print()
