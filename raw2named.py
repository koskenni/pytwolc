import re
import csv
import argparse
argparser = argparse.ArgumentParser(
    "python3 raw2named.py",
    description="joins and renames raw morphophonemes")
argparser.add_argument(
    "input",
    default="ksk-raw-examp.csv",
    help="aligned examples as a CSV file")
argparser.add_argument(
    "output",
    default="ksk-renam-examp.pstr",
    help="renamed examples as a space separated pair symbol strings")
argparser.add_argument(
    "names",
    default="raw_mphons.csv",
    help="mapping from raw to neat morphophonemes as a CSV file")
argparser.add_argument(
    "-d", "--delimiter",
    default=",",
    help="delimiter between raw name and new name fields")
args = argparser.parse_args()

mphon_name = { }

# [a-zšžŋđõäöáâ`´]

with open(args.names) as namefile:
    reader = csv.reader(namefile, delimiter=args.delimiter)
    for row in reader:
        if not row or (not row[0].strip()):
            continue
        if row[1].strip():
            mphon_name[row[0].strip()] = row[1].strip()

#print(mphon_name)###

outfil = open(args.output, "w")
            
with open(args.input) as csvfile:
    reader = csv.DictReader(csvfile, delimiter=args.delimiter)
    for row in reader:
        #print(row)###
        raw_pair_str = row["PAIRSYMS"]
        raw_pair_lst = raw_pair_str.split(" ")
        clean_pair_lst = []
        for raw_pair in raw_pair_lst:
            m = re.fullmatch(r"([^:]+):([^:]+)", raw_pair)
            if m:
                mf, sf = m.groups()
                clean_mf = mphon_name.get(mf, mf)
                clean_pair = clean_mf + ":" + sf
            else:
                clean_pair = raw_pair
            clean_pair_lst.append(clean_pair)
        morpheme_lst = row["MORPHEMES"].strip().split(" ")
        if len(morpheme_lst) > 1:
            morpheme = re.sub(r"\+", r"", morpheme_lst[1])
            clean_pair_lst.append(morpheme + ":Ø")
        clean_pair_str = " ".join(clean_pair_lst)
        print(clean_pair_str, file=outfil)
