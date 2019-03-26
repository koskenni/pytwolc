# lookuptest.py

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
    "python3 gyessbyasking.py",
    description="Guess lexicon entries by asking forms from the user")
argparser.add_argument(
    "guesser", help="Guesser file FST", default="finv-guess.fst")
argparser.add_argument(
    "-r", "--reject", default=1000000, type=int,
    help="reject candidates which are worse than the best by REJECTION or more")
argparser.add_argument(
    "-v", "--verbosity", default=0, type=int,
    help="level of diagnostic output")
args = argparser.parse_args()

guesser_fil = hfst.HfstInputStream(args.guesser)
guesser_fst = guesser_fil.read()
guesser_fil.close()
guesser_fst.invert()
guesser_fst.minimize()
guesser_fst.lookup_optimize()

print("\nENTER FORMS OF A WORD:\n")
while True:
    remaining = set()
    weight = {}
    first = True
    while True:
        linenl = sys.stdin.readline()
        if not linenl: exit()
        line = linenl.strip()
        if line == "":
            print("GIVING UP THIS WORD\n\n")
            break
        if line[0] == '-':
            res = guesser_fst.lookup(line[1:], output="tuple")
        else:
            res = guesser_fst.lookup(line, output="tuple")
        if args.verbosity >= 10:
            print("lookup result =", res)
        if len(res) == 0:
            print("FITS NO PATTERN! INGORED.")
            continue
        entries = set()
        for entry, w in res:
            entries.add(entry)
            if entry in weight:
                weight[entry] = min(w, weight[entry])
            else:
                weight[entry] = w
        if first:
            first = False
            remain = entries
        elif line[0] == '-':
            remain = remaining - entries
        else:
            remain = remaining & entries
        best_weight = min([weight[e] for e in remain], default=0)
        rema = set()
        for e in remain:
            if weight[e] <= best_weight + args.reject:
                rema.add(e)
        if len(rema) == 1:
            print("\n" + "="*18)
            print(list(rema)[0], ";")
            print("="*18 + "\n")
            break
        elif not rema:
            print("DOES NOT FIT! IGNORED.")
        else:
            rml = [(entry, weight[entry]) for entry in rema]
            print("        ", rml)
            remaining = rema



