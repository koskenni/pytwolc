import sys
d = {}
for line_nl in sys.stdin:
    line = line_nl.strip()
    lst = line.split("\t")
    if len(lst) != 3:
        continue
    [word, analysis, weight] = lst
    entry = analysis.split(sep="+", maxsplit=1)[0]
    if entry in d:
        d[entry].append(word)
    else:
        d[entry] = [word]

for entry in sorted(d.keys()):
    print("{},{}".format(entry, " ".join(d[entry])))
