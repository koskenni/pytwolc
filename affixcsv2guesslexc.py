"""affixcsv2guesslexc.py:

builds a lexc file for guessing out of a csv file of affixes
"""

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

import re, csv

multichars = set()

def collect_multichars(str):
    if len(str) < 2: return
    lst = re.findall(r"[{][a-zåäöšžVCØ]+[}]", str)
    for mch in lst:
        multichars.add(mch)
    return

import argparse
argparser = argparse.ArgumentParser(
    "python3 affixcsv2guesslexc.py",
    description="Converts an affix CSV file into a guesser affix LEXC file")
argparser.add_argument(
    "infile", help="A input CSV file containing the affix data")
argparser.add_argument(
    "outfile", help="A output LEXC file of the affix data")
argparser.add_argument("-d", "--delimiter", default=",",
    help="CSV field delimiter (default is ',')")
argparser.add_argument("-v", "--verbosity", default=0, type=int,
    help="level of diagnostic output")
args = argparser.parse_args()

out_lst = []
features = set()
nexts = set()
lexicon_lst = []
infile = open(args.infile, "r")
rdr = csv.DictReader(infile, delimiter=args.delimiter)
prevID = ",,"
for r in rdr:
    #print(r)####
    if r["NEXT"] == '' or r["NEXT"][0] == '!':
        continue
    ide = prevID if r["ID"] == '' else r["ID"]
    if prevID != ide:
        prevID = ide
        if "/" in ide:
            lexicon_lst.append(ide)
        out_lst.append("LEXICON %s" % ide)
    collect_multichars(r["MPHON"])
    for next in re.split(" +", r["NEXT"]):
        if next == '': continue
        if "/" in ide:
            nexts.add(next)
            out_lst.append("% {}:{} {};".format(ide, r['MPHON'], next))
        elif r['MPHON'] == "":
            out_lst.append(" {};".format(next))
        else:
            out_lst.append(":{} {};".format(r['MPHON'], next))

outfile = open(args.outfile, "w")
print("Multichar_Symbols", file=outfile)
multichar_lst = sorted(list(multichars))
print(" ".join(multichar_lst), file=outfile)
print(" ".join(lexicon_lst), file=outfile)
for line in out_lst:
    print(line, file=outfile)
outfile.close()
    
