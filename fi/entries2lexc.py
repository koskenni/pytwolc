import re, sys, argparse

argparser = argparse.ArgumentParser(
    "python3 entries2lexc.py",
    description="List of mphonemic entries and continuations into a lexc lexicon")
argparser.add_argument(
    "lexname", help="name of the lexicon to be made out of the input entries")
args = argparser.parse_args()


mch_set = set()
line_lst = []

for line_nl in sys.stdin:
    line = line_nl.strip()
    line_lst.append(line)
    mch_lst = re.findall(r"{[^}]+}", line)
    for mch in mch_lst:
        mch_set.add(mch)

print("Multichar_Symbols")
mch_lst = sorted(list(mch_set))
print(" ".join(mch_lst))

print("LEXICON", args.lexname)

for line in line_lst:
    if not line:
        continue
    if line.startswith("<"):
        line = re.sub(r"([{}])", r"%\1", line)
    tok_lst = line.split()
    if len(tok_lst) >= 2:
        print(tok_lst[0], tok_lst[1], ";")
    else:
        print("** error on line:", line, tok_lst)
