# guessfromforms.py

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
import csv

argparser = argparse.ArgumentParser(
    "python3 gyessfromforms.py",
    description="Guess lexicon entries out of sets of forms")
argparser.add_argument(
    "guesser", help="Guesser file FST")
argparser.add_argument(
    "forms", help="sets of word forms")
argparser.add_argument(
    "-r", "--reject", default=1000000, type=int,
    help="reject candidates which are worse than the best by REJECTION or more")
argparser.add_argument(
    "-v", "--verbosity", default=0, type=int,
    help="level of diagnostic output")
args = argparser.parse_args()

guesser_fil = hfst.HfstInputStream(args.guesser)
guesser_fst = guesser_fil.read()
#guesser_fil.close()
#guesser_fst.invert()
#guesser_fst.minimize()
#guesser_fst.lookup_optimize()

forms_file = open(args.forms, "r")
forms_reader = csv.reader(forms_file, delimiter=",")
for row in forms_reader:
    common_entries = set()
    form_lst = row[1].split()
    for form in form_lst:
        res = set(guesser_fst.lookup(form, output="tuple"))
        if args.verbosity >= 10:
            print("lookup result[{}] ={}".format(form, res))
        if not common_entries:
            common_entries = res
        else:
            common_entries = common_entries & res
        if args.verbosity >= 10:
            print("common_entries = {}".format(common_entries))
        if len(common_entries) == 0:
            break               # no entry generates the whole set of forms

    best_weight = min([w for e,w in common_entries], default=0)
    top_entry_lst = [(e,w) for e,w in common_entries
                     if w <= best_weight + args.reject]
    if args.verbosity >= 5:
        print(top_entry_lst)
    entries = " | ".join("{} {:.1f}".format(e,w) for e,w in top_entry_lst)
    print("{},{},{}".format(row[0], entries, row[1]))
