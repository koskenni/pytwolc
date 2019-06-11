
import sys

#fil = open("vns-word-guess-test.text", "r")
#fil = open("vns-word-guesses-nv.text", "r")

entries = {}
words = {}

for line in sys.stdin:
    if not ":" in line:
        print(">>>" + line)
        continue
    [entry,word_weight] = line.strip().split(":")
    [word, weight] = word_weight.split("\t")
    if int(weight) >= 10:
        continue
    if entry not in words:
        words[entry] = set()
    words[entry].add(word)
    if word not in entries:
        entries[word] = set()
    entries[word].add(entry)

def kompar(en):
    return len(words[en])

def delete_entry(e):
    for w in words[e]:
        entries[w].discard(e)
    del words[e]
    
def delete_all_words(entry, w_lst):
    #print("deleting:", w_lst)###
    siz = len(words[entry])
    for w in w_lst:
        for e in entries[w]:
            if e in words and siz > len(words[e]):
                words[e].discard(w)
        if not entries[w]:
            del entries[w]

for entry in sorted(words.keys(), key=kompar, reverse=True):
    for word in words[entry]:
        for e in entries[word]:
            if words[entry] < words[e]:
                delete_entry(entry)
                #print("deleting", entry, "which is inferior to", e)###
                break # the innermost loop
        else:
            continue # the middle loop
        break # the middle loop

sz = 200
#print("largest set of words", sz)

delta = 1
while sz > 4:
    del_ent_lst = []
    for entry in words:
        #print(sz, entry, words[entry])###
        if entry in words and len(words[entry]) >= sz - delta:
            print(entry, "--", " ".join(sorted(list(words[entry]))))
            delete_all_words(entry, list(words[entry]))
            del_ent_lst.append(entry)
    for ent in del_ent_lst:
        del words[ent]
    sz = sz - delta
