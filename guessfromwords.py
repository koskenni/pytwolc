
import sys

fil = open("vns-word-guess-test.text", "r")

entries = {}
words = {}

for line in fil:
    [entry,word] = line.strip().split(":")
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
    
for entry in sorted(words.keys(), key=kompar, reverse=True):
    for word in words[entry]:
        for e in entries[word]:
            #print("\nwords[{}] = {}".format(entry, words[entry]))###
            #print("words[{}] = {}".format(e, words[e]))###
            if words[entry] < words[e]:
                delete_entry(entry)
                print("deleting", entry, "which is inferior to", e)###
                break # nothing more to do with this entry
            else:
                continue # to the next word in the middle loop
        break # nothing else to be done for the words for the deleted entry

#print("\n\nentries", entries)###
for e in sorted(words.keys()):
    if e in words:
        print(e, "--", " ".join(list(words[e])))
    
