import re, sys

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

inside_defs = True
for line in line_lst:
    if line.startswith("LEXICON"):
        inside_defs = False
    if inside_defs or line.startswith("<"):
        line = re.sub(r"([{}])", r"%\1", line)
    print(line)
